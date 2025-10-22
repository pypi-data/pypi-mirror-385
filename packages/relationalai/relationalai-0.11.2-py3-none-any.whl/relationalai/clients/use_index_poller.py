from typing import Iterable, Dict, Optional, List, cast, TYPE_CHECKING
import json
import uuid

from relationalai import debugging
from relationalai.clients.cache_store import GraphIndexCache
from relationalai.clients.util import get_pyrel_version, poll_with_specified_overhead
from relationalai.errors import (
    ERPNotRunningError,
    EngineProvisioningFailed,
    SnowflakeChangeTrackingNotEnabledException,
    SnowflakeTableObjectsException,
    SnowflakeTableObject,
)
from relationalai.tools.cli_controls import DebuggingSpan, create_progress
from relationalai.tools.constants import WAIT_FOR_STREAM_SYNC, Generation

if TYPE_CHECKING:
    from relationalai.clients.snowflake import Resources
    from relationalai.clients.snowflake import DirectAccessResources

# Maximum number of items to show individual subtasks for
# If more items than this, show a single summary subtask instead
MAX_INDIVIDUAL_SUBTASKS = 5

# Special engine name for CDC managed engine
CDC_MANAGED_ENGINE = "CDC_MANAGED_ENGINE"

# Maximum number of data source subtasks to show simultaneously
# When one completes, the next one from the queue will be added
MAX_DATA_SOURCE_SUBTASKS = 10

# How often to check ERP status (every N iterations)
# To limit performance overhead, we only check ERP status periodically
ERP_CHECK_FREQUENCY = 5

class UseIndexPoller:
    """
    Encapsulates the polling logic for `use_index` streams.
    """

    def _add_stream_subtask(self, progress, fq_name, status, batches_count):
        """Add a stream subtask if we haven't reached the limit."""
        if fq_name not in self.stream_task_ids and len(self.stream_task_ids) < MAX_DATA_SOURCE_SUBTASKS:
            # Get the position in the stream order (should already be there)
            if fq_name in self.stream_order:
                stream_position = self.stream_order.index(fq_name) + 1
            else:
                # Fallback if not in order (shouldn't happen)
                stream_position = 1

            # Build initial message based on status and batch count
            if status == "synced":
                initial_message = f"{fq_name} already synced"
            elif batches_count > 0:
                # Show stream position (x/y) before batch count
                initial_message = f"Syncing {fq_name} ({stream_position}/{self.total_streams}), batches: {batches_count}"
            else:
                initial_message = f"Syncing {fq_name} ({stream_position}/{self.total_streams})"

            self.stream_task_ids[fq_name] = progress.add_sub_task(initial_message, task_id=fq_name)

            # Complete immediately if already synced
            if status == "synced":
                progress.complete_sub_task(fq_name)

            return True
        return False

    def __init__(
        self,
        resource: "Resources",
        app_name: str,
        sources: Iterable[str],
        model: str,
        engine_name: str,
        engine_size: Optional[str],
        program_span_id: Optional[str],
        headers: Optional[Dict],
        generation: Optional[Generation] = None,
    ):
        self.res = resource
        self.app_name = app_name
        self.sources = list(sources)
        self.model = model
        self.engine_name = engine_name
        self.engine_size = engine_size or self.res.config.get_default_engine_size()
        self.program_span_id = program_span_id
        self.headers = headers or {}
        self.counter = 1
        self.check_ready_count = 0
        self.tables_with_not_enabled_change_tracking: List = []
        self.table_objects_with_other_errors: List = []
        self.engine_errors: List = []
        # Flag to only ensure the engine is created asynchronously the initial call
        self.init_engine_async = True
        # Initially, we assume that cdc is not checked,
        # then on subsequent calls, if we get if cdc is enabled, if it is not, we will check it
        # on every 5th iteration we reset the cdc status, so it will be checked again
        self.should_check_cdc = True

        self.wait_for_stream_sync = self.res.config.get(
            "wait_for_stream_sync", WAIT_FOR_STREAM_SYNC
        )
        current_user = self.res.get_sf_session().get_current_user()
        assert current_user is not None, "current_user must be set"
        data_freshness = self.res.config.get_data_freshness_mins()
        self.cache = GraphIndexCache(current_user, model, data_freshness, self.sources)
        self.sources = self.cache.choose_sources()
        # execution_id is allowed to group use_index call, which belongs to the same loop iteration
        self.execution_id = str(uuid.uuid4())

        self.pyrel_version = get_pyrel_version(generation)

        self.source_info = self.res._check_source_updates(self.sources)

        # Track subtask IDs for streams, engines, and relations across multiple poll iterations
        self.stream_task_ids = {}
        self.engine_task_ids = {}
        self.relations_task_id = None
        self._erp_check_task_id = None

        # Track total number of streams and current stream position for (x/y) progress display
        self.total_streams = 0
        self.stream_position = 0
        self.stream_order = []  # Track the order of streams as they appear in data

    def poll(self) -> None:
        """
        Standard stream-based polling for use_index.
        """
        with create_progress(
            description="Initializing data index",
            success_message="Initialization complete",
            leading_newline=True,
            trailing_newline=True,
        ) as progress:
            progress.update_main_status("Validating data sources")
            self._maybe_delete_stale(progress)

            # Add cache usage subtask
            self._add_cache_subtask(progress)

            progress.update_main_status("Initializing data index")
            self._poll_loop(progress)
            self._post_check(progress)

    def _add_cache_subtask(self, progress) -> None:
        """Add a subtask showing cache usage information only when cache is used."""
        if self.cache.using_cache:
            # Cache was used - show how many sources were cached
            total_sources = len(self.cache.sources)
            cached_sources = total_sources - len(self.sources)
            progress.add_sub_task(f"Using cached data for {cached_sources}/{total_sources} data streams", task_id="cache_usage")
            # Complete the subtask immediately since it's just informational
            progress.complete_sub_task("cache_usage")

    def _maybe_delete_stale(self, progress) -> None:
        with debugging.span("check_sources"):
            # Source tables that have been altered/changed since the last stream creation
            stale_sources = [
                source
                for source, info in self.source_info.items()
                if info["state"] == "STALE"
            ]
        if stale_sources:
            with DebuggingSpan("validate_sources"):
                try:
                    # Delete all stale streams, so use_index could recreate them again
                    from relationalai.clients.snowflake import PYREL_ROOT_DB
                    query = f"CALL {self.app_name}.api.delete_data_streams({stale_sources}, '{PYREL_ROOT_DB}');"

                    # Add subtasks based on count
                    if len(stale_sources) <= MAX_INDIVIDUAL_SUBTASKS:
                        # Add individual subtasks for each stale source
                        for i, source in enumerate(stale_sources):
                            progress.add_sub_task(f"Removing stale stream {source} ({i+1}/{len(stale_sources)})", task_id=f"stale_source_{i}")
                    else:
                        # Add single summary subtask for many sources
                        progress.add_sub_task(f"Removing {len(stale_sources)} stale data sources", task_id="stale_sources_summary")

                    delete_response = self.res._exec(query)
                    delete_json_str = delete_response[0]["DELETE_DATA_STREAMS"].lower()
                    delete_data = json.loads(delete_json_str)
                    deleted_count = delete_data.get("deleted", 0)
                    diff = len(stale_sources) - deleted_count

                    # Complete subtasks
                    if len(stale_sources) <= MAX_INDIVIDUAL_SUBTASKS:
                        # Complete all individual subtasks
                        for i in range(len(stale_sources)):
                            if f"stale_source_{i}" in progress._tasks:
                                progress.complete_sub_task(f"stale_source_{i}")
                    else:
                        # Complete summary subtask
                        if "stale_sources_summary" in progress._tasks:
                            if deleted_count > 0:
                                is_many = deleted_count > 1
                                s = "s" if is_many else ""
                                progress.update_sub_task("stale_sources_summary", f"Removed {deleted_count} stale data source{s}")
                            progress.complete_sub_task("stale_sources_summary")

                    if diff > 0:
                        errors = delete_data.get("errors", None)
                        if errors:
                            raise Exception(f"Error(s) deleting streams with modified sources: {errors}")
                except Exception as e:
                    # Complete any remaining subtasks
                    if len(stale_sources) <= MAX_INDIVIDUAL_SUBTASKS:
                        for i in range(len(stale_sources)):
                            if f"stale_source_{i}" in progress._tasks:
                                progress.complete_sub_task(f"stale_source_{i}")
                    else:
                        if "stale_sources_summary" in progress._tasks:
                            progress.update_sub_task("stale_sources_summary", f"❌ Failed to remove stale sources: {str(e)}")
                            progress.complete_sub_task("stale_sources_summary")

                    # The delete_data_streams procedure will raise an exception if the streams do not exist
                    if "data streams do not exist" in str(e).lower():
                        # Don't raise an error if streams don't exist - this is expected
                        pass
                    else:
                        raise e from None

    def _poll_loop(self, progress) -> None:
        source_references = self.res._get_source_references(self.source_info)
        sources_object_references_str = ", ".join(source_references)

        def check_ready(progress) -> bool:
            self.check_ready_count += 1

            # To limit the performance overhead, we only check if ERP is running every N iterations
            if self.check_ready_count % ERP_CHECK_FREQUENCY == 0:
                with debugging.span("check_erp_status"):
                    # Add subtask for ERP status check
                    if self._erp_check_task_id is None:
                        self._erp_check_task_id = progress.add_sub_task("Checking system status", task_id="erp_check")

                    if not self.res.is_erp_running(self.app_name):
                        progress.update_sub_task("erp_check", "❌ System status check failed")
                        progress.complete_sub_task("erp_check")
                        raise ERPNotRunningError
                    else:
                        progress.update_sub_task("erp_check", "System status check complete")
                        progress.complete_sub_task("erp_check")

            use_index_id = f"{self.model}_{self.execution_id}"

            params = json.dumps({
                "model": self.model,
                "engine": self.engine_name,
                "default_engine_size": self.engine_size, # engine_size
                "user_agent": self.pyrel_version,
                "use_index_id": use_index_id,
                "pyrel_program_id": self.program_span_id,
                "wait_for_stream_sync": self.wait_for_stream_sync,
                "should_check_cdc": self.should_check_cdc,
                "init_engine_async": self.init_engine_async,
            })

            request_headers = debugging.add_current_propagation_headers(self.headers)

            sql_string = f"CALL {self.app_name}.api.use_index([{sources_object_references_str}], PARSE_JSON(?), {request_headers});"

            with debugging.span("wait", counter=self.counter, use_index_id=use_index_id) as span:
                results = self.res._exec(sql_string, [params])

                # Extract the JSON string from the `USE_INDEX` field
                use_index_json_str = results[0]["USE_INDEX"]

                # Parse the JSON string into a Python dictionary
                use_index_data = json.loads(use_index_json_str)
                span.update(use_index_data)

                # Useful to see the full use_index_data on each poll loop
                # print(f"\n\nuse_index_data: {json.dumps(use_index_data, indent=4)}\n\n")

                all_data = use_index_data.get("data", [])
                ready = use_index_data.get("ready", False)
                engines = use_index_data.get("engines", [])
                errors = use_index_data.get("errors", [])
                relations = use_index_data.get("relations", {})
                cdc_enabled = use_index_data.get("cdcEnabled", False)
                if self.check_ready_count % ERP_CHECK_FREQUENCY == 0 or not cdc_enabled:
                    self.should_check_cdc = True
                else:
                    self.should_check_cdc = False

                break_loop = False
                has_stream_errors = False
                has_general_errors = False

                # Update main progress message
                if ready:
                    progress.update_main_status("Done")

                # Handle streams data
                if not ready and all_data:
                    progress.update_main_status("Processing background tasks. This may take a while...")

                    # Build complete stream order first
                    for data in all_data:
                        if data is None:
                            continue
                        fq_name = data.get("fq_object_name", "Unknown")
                        if fq_name not in self.stream_order:
                            self.stream_order.append(fq_name)

                    # Set total streams count based on complete order
                    self.total_streams = len(self.stream_order)

                    # Add new streams as subtasks if we haven't reached the limit
                    for data in all_data:
                        fq_name = data.get("fq_object_name", "Unknown")
                        status = data.get("data_sync_status", "").lower() if data else ""
                        batches_count = data.get("pending_batches_count", 0)

                        # Only add if we haven't seen this stream and we're under the limit
                        self._add_stream_subtask(progress, fq_name, status, batches_count)

                        # Handle errors for existing streams
                        if fq_name in self.stream_task_ids and data.get("errors", []):
                            for error in data.get("errors", []):
                                error_msg = f"{error.get('error')}, source: {error.get('source')}"
                                self.table_objects_with_other_errors.append(
                                    SnowflakeTableObject(error_msg, fq_name)
                                )
                            # Mark stream as failed
                            progress.update_sub_task(fq_name, f"❌ Failed: {fq_name}")
                            has_stream_errors = True

                        # Update stream status (only for streams that aren't already completed)
                        if fq_name in self.stream_task_ids and fq_name in progress._tasks and not progress._tasks[fq_name].completed:
                            # Get the stream position from the stream order
                            if fq_name in self.stream_order:
                                stream_position = self.stream_order.index(fq_name) + 1
                            else:
                                # Fallback to 1 if not in order (shouldn't happen)
                                stream_position = 1

                            # Build status message
                            if batches_count > 0 and status == 'syncing':
                                status_message = f"Syncing {fq_name} ({stream_position}/{self.total_streams}), batches: {batches_count}"
                            else:
                                status_message = f"Pending {fq_name} ({stream_position}/{self.total_streams})..."

                            progress.update_sub_task(fq_name, status_message)

                            # Complete the stream if it's synced
                            if status == "synced":
                                progress.complete_sub_task(fq_name)

                    # Add more streams from the queue if we have space and more streams exist
                    if len(self.stream_task_ids) < MAX_DATA_SOURCE_SUBTASKS:
                        for data in all_data:
                            fq_name = data.get("fq_object_name", "Unknown")
                            status = data.get("data_sync_status", "").lower()
                            batches_count = data.get("pending_batches_count", 0)

                            self._add_stream_subtask(progress, fq_name, status, batches_count)

                    self.counter += 1

                # Handle engines data
                if not ready and engines:
                    # Add new engines as subtasks if they don't exist
                    for engine in engines:
                        if not engine or not isinstance(engine, dict):
                            continue

                        name = engine.get("name", "Unknown")
                        size = self.engine_size
                        if name not in self.engine_task_ids:
                            self.engine_task_ids[name] = progress.add_sub_task(f"Provisioning engine {name} ({size})", task_id=name)

                        state = (engine.get("state") or "").lower()
                        status = (engine.get("status") or "").lower()

                        # Determine engine status message
                        if state == "ready" or status == "ready":
                            status_message = f"Engine {name} ({size}) ready"
                            should_complete = True
                        else:
                            writer = engine.get("writer", False)
                            engine_type = "writer engine" if writer else "engine"
                            status_message = f"Provisioning {engine_type} {name} ({size})"
                            should_complete = False

                        # Only update if the task isn't already completed
                        if name in progress._tasks and not progress._tasks[name].completed:
                            progress.update_sub_task(name, status_message)

                            if should_complete:
                                progress.complete_sub_task(name)

                    # Special handling for CDC_MANAGED_ENGINE - mark ready when any stream starts processing
                    if CDC_MANAGED_ENGINE in self.engine_task_ids:
                        has_processing_streams = any(
                            stream.get("next_batch_status", "") == "processing"
                            for stream in all_data
                        )
                        if has_processing_streams and CDC_MANAGED_ENGINE in progress._tasks and not progress._tasks[CDC_MANAGED_ENGINE].completed:
                            progress.update_sub_task(CDC_MANAGED_ENGINE, f"Engine {CDC_MANAGED_ENGINE} ({self.engine_size}) ready")
                            progress.complete_sub_task(CDC_MANAGED_ENGINE)

                    self.counter += 1

                # Handle relations data
                if not ready and relations and isinstance(relations, dict):
                    txn = relations.get("txn", {}) or {}
                    txn_id = txn.get("id", None)

                    # Only show relations subtask if there is a valid txn object
                    if txn_id:
                        status = relations.get("status", "").upper()
                        state = txn.get("state", "").upper()

                        # Create relations subtask if it doesn't exist
                        if self.relations_task_id is None:
                            self.relations_task_id = progress.add_sub_task("Populating relations", task_id="relations")

                        # Update relations status
                        if state == "COMPLETED":
                            progress.update_sub_task("relations", f"Relations populated (txn: {txn_id})")
                            progress.complete_sub_task("relations")
                        else:
                            progress.update_sub_task("relations", f"Relations populating (txn: {txn_id})")

                        self.counter += 1

                # Handle errors
                if not ready and errors:
                    for error in errors:
                        if error is None:
                            continue
                        if error.get("type") == "data":
                            message = error.get("message", "").lower()
                            if ("change_tracking" in message or "change tracking" in message):
                                err_source = error.get("source")
                                err_source_type = self.source_info.get(err_source, {}).get("type")
                                self.tables_with_not_enabled_change_tracking.append((err_source, err_source_type))
                            else:
                                self.table_objects_with_other_errors.append(
                                    SnowflakeTableObject(error.get("message"), error.get("source"))
                                )
                        elif error.get("type") == "engine":
                            self.engine_errors.append(error)
                        else:
                            # Other types of errors, e.g. "validation"
                            self.table_objects_with_other_errors.append(
                                SnowflakeTableObject(error.get("message"), error.get("source"))
                            )
                    has_general_errors = True

                # If ready, complete all remaining subtasks
                if ready:
                    self.cache.record_update(self.source_info)
                    # Complete any remaining stream subtasks
                    for fq_name in self.stream_task_ids:
                        if fq_name in progress._tasks and not progress._tasks[fq_name].completed:
                            progress.complete_sub_task(fq_name)
                    # Complete any remaining engine subtasks
                    for name in self.engine_task_ids:
                        if name in progress._tasks and not progress._tasks[name].completed:
                            progress.complete_sub_task(name)
                    # Complete relations subtask if it exists and isn't completed
                    if self.relations_task_id and "relations" in progress._tasks and not progress._tasks["relations"].completed:
                        progress.complete_sub_task("relations")
                    break_loop = True
                elif has_stream_errors or has_general_errors:
                    # Break the loop if there are errors, but only after reporting all progress
                    break_loop = True

                return break_loop

        poll_with_specified_overhead(lambda: check_ready(progress), overhead_rate=0.1, max_delay=1)

    def _post_check(self, progress) -> None:
            num_tables_altered = 0

            enabled_tables = []
            if (
                self.tables_with_not_enabled_change_tracking
                and self.res.config.get("ensure_change_tracking", False)
            ):
                tables_to_process = self.tables_with_not_enabled_change_tracking

                # Add subtasks based on count
                if len(tables_to_process) <= MAX_INDIVIDUAL_SUBTASKS:
                    # Add individual subtasks for each table
                    for i, table in enumerate(tables_to_process):
                        fqn, kind = table
                        progress.add_sub_task(f"Enabling change tracking on {fqn} ({i+1}/{len(tables_to_process)})", task_id=f"change_tracking_{i}")
                else:
                    # Add single summary subtask for many tables
                    progress.add_sub_task(f"Enabling change tracking on {len(tables_to_process)} tables", task_id="change_tracking_summary")

                # Process tables
                for i, table in enumerate(tables_to_process):
                    try:
                        fqn, kind = table
                        self.res._exec(f"ALTER {kind} {fqn} SET CHANGE_TRACKING = TRUE;")
                        enabled_tables.append(table)
                        num_tables_altered += 1

                        # Update progress based on subtask type
                        if len(tables_to_process) <= MAX_INDIVIDUAL_SUBTASKS:
                            # Complete individual table subtask
                            progress.complete_sub_task(f"change_tracking_{i}")
                        else:
                            # Update summary subtask with progress
                            progress.update_sub_task("change_tracking_summary",
                                f"Enabling change tracking on {len(tables_to_process)} tables... ({i+1}/{len(tables_to_process)})")
                    except Exception:
                        # Handle errors based on subtask type
                        if len(tables_to_process) <= MAX_INDIVIDUAL_SUBTASKS:
                            # Complete the individual subtask even if it failed
                            if f"change_tracking_{i}" in progress._tasks:
                                progress.complete_sub_task(f"change_tracking_{i}")
                        pass

                # Complete summary subtask if used
                if len(tables_to_process) > MAX_INDIVIDUAL_SUBTASKS and "change_tracking_summary" in progress._tasks:
                    if num_tables_altered > 0:
                        s = "s" if num_tables_altered > 1 else ""
                        progress.update_sub_task("change_tracking_summary", f"Enabled change tracking on {num_tables_altered} table{s}")
                    progress.complete_sub_task("change_tracking_summary")

                # Remove the tables that were successfully enabled from the list of not enabled tables
                # so that we don't raise an exception for them later
                self.tables_with_not_enabled_change_tracking = [
                    t for t in self.tables_with_not_enabled_change_tracking if t not in enabled_tables
                ]

            if self.tables_with_not_enabled_change_tracking:
                progress.update_main_status("Errors found. See below for details.")
                raise SnowflakeChangeTrackingNotEnabledException(
                    self.tables_with_not_enabled_change_tracking
                )

            if self.table_objects_with_other_errors:
                progress.update_main_status("Errors found. See below for details.")
                raise SnowflakeTableObjectsException(self.table_objects_with_other_errors)
            if self.engine_errors:
                progress.update_main_status("Errors found. See below for details.")
                # if there is an engine error, probably auto create engine failed
                # Create a synthetic exception from the first engine error
                first_error = self.engine_errors[0]
                error_message = first_error.get("message", "Unknown engine error")
                synthetic_exception = Exception(f"Engine error: {error_message}")
                raise EngineProvisioningFailed(self.engine_name, synthetic_exception)

            if num_tables_altered > 0:
                self._poll_loop(progress)

class DirectUseIndexPoller(UseIndexPoller):
    """
    Extends UseIndexPoller to handle direct-access prepare_index when no sources.
    """
    def __init__(
        self,
        resource: "DirectAccessResources",
        app_name: str,
        sources: Iterable[str],
        model: str,
        engine_name: str,
        engine_size: Optional[str],
        program_span_id: Optional[str],
        headers: Optional[Dict],
        generation: Optional[Generation] = None,
    ):
        super().__init__(resource, app_name, sources, model, engine_name, engine_size, program_span_id, headers, generation)
        from relationalai.clients.snowflake import DirectAccessResources
        self.res: DirectAccessResources = cast(DirectAccessResources, self.res)

    def poll(self) -> None:
        if not self.sources:
            from relationalai.errors import RAIException
            collected_errors: List[Dict] = []
            attempt = 1

            def check_direct(progress) -> bool:
                nonlocal attempt
                with debugging.span("wait", counter=self.counter) as span:
                    span.update({"attempt": attempt, "engine_name": self.engine_name, "model": self.model})
                    # we are skipping pulling relations here, as direct access only handle non-sources cases
                    # and we don't need to pull relations for that, therefore, we pass empty list for rai_relations
                    # and set skip_pull_relations to True
                    resp = self.res._prepare_index(
                        model=self.model,
                        engine_name=self.engine_name,
                        engine_size=self.engine_size,
                        rai_relations=[],
                        pyrel_program_id=self.program_span_id,
                        skip_pull_relations=True,
                        headers=self.headers,
                    )
                    span.update(resp)
                    caller_engine = resp.get("caller_engine", {})
                    # Handle case where caller_engine might be None
                    ce_status = caller_engine.get("status", "").lower() if caller_engine else ""
                    errors = resp.get("errors", [])

                    ready = resp.get("ready", False)

                    # Update main progress message
                    if ready:
                        progress.update_main_status("Done")
                    else:
                        progress.update_main_status("Preparing your data...")

                    if ready:
                        return True
                    else:
                        if ce_status == "pending":
                            # Add or update engine subtask
                            engine_name = caller_engine.get('name', self.engine_name)
                            if not hasattr(progress, '_engine_task_id'):
                                progress._engine_task_id = progress.add_sub_task(f"Waiting for engine '{engine_name}' to be ready...", task_id=engine_name)
                            else:
                                progress.update_sub_task(engine_name, f"Waiting for engine '{engine_name}' to be ready...")
                        else:
                            # Handle errors as subtasks
                            if errors:
                                progress.update_main_status("Encountered errors during preparation...")
                                for i, err in enumerate(errors):
                                    error_id = f"error_{i}"
                                    if not hasattr(progress, f'_error_task_id_{i}'):
                                        error_msg = err.get('message', 'Unknown error')
                                        setattr(progress, f'_error_task_id_{i}', progress.add_sub_task(f"❌ {error_msg}", task_id=error_id))
                                    else:
                                        error_msg = err.get('message', 'Unknown error')
                                        progress.update_sub_task(error_id, f"❌ {error_msg}")
                                    collected_errors.append(err)

                    attempt += 1
                    return False

            with create_progress(
                description="Preparing your data...",
                success_message="Done",
                leading_newline=True,
                trailing_newline=True,
            ) as progress:
                # Add cache usage subtask
                self._add_cache_subtask(progress)

                with debugging.span("poll_direct"):
                    poll_with_specified_overhead(lambda: check_direct(progress), overhead_rate=0.1, max_delay=1)

                # Run the same post-check logic as UseIndexPoller
                self._post_check(progress)

            if collected_errors:
                msg = "; ".join(e.get("message", "") for e in collected_errors)
                raise RAIException(msg)
        else:
            super().poll()
