from __future__ import annotations
from collections import defaultdict
import atexit
import re

from pandas import DataFrame
from typing import Any, Optional, Literal
from snowflake.snowpark import Session
import relationalai as rai

from relationalai import debugging
from relationalai.semantics.lqp import result_helpers
from relationalai.semantics.metamodel import ir, factory as f, executor as e
from relationalai.semantics.lqp.compiler import Compiler
from relationalai.semantics.lqp.types import lqp_type_to_sql
from lqp import print as lqp_print, ir as lqp_ir
from lqp.parser import construct_configure
from relationalai.semantics.lqp.ir import convert_transaction, validate_lqp
from relationalai.clients.config import Config
from relationalai.clients.snowflake import APP_NAME
from relationalai.clients.types import TransactionAsyncResponse
from relationalai.clients.util import IdentityParser
from relationalai.tools.constants import USE_DIRECT_ACCESS


class LQPExecutor(e.Executor):
    """Executes LQP using the RAI client."""

    def __init__(
        self,
        database: str,
        dry_run: bool = False,
        keep_model: bool = True,
        wide_outputs: bool = False,
        connection: Session | None = None,
        config: Config | None = None,
    ) -> None:
        super().__init__()
        self.database = database
        self.dry_run = dry_run
        self.keep_model = keep_model
        self.wide_outputs = wide_outputs
        self.compiler = Compiler()
        self.connection = connection
        self.config = config or Config()
        self._resources = None
        self._last_model = None
        self._last_sources_version = (-1, None)

    @property
    def resources(self):
        if not self._resources:
            with debugging.span("create_session"):
                self.dry_run |= bool(self.config.get("compiler.dry_run", False))
                resource_class = rai.clients.snowflake.Resources
                if self.config.get("use_direct_access", USE_DIRECT_ACCESS):
                    resource_class = rai.clients.snowflake.DirectAccessResources
                self._resources = resource_class(dry_run=self.dry_run, config=self.config, generation=rai.Generation.QB, connection=self.connection)
                if not self.dry_run:
                    self.engine = self._resources.get_default_engine_name()
                    if not self.keep_model:
                        atexit.register(self._resources.delete_graph, self.database, True)
        return self._resources

    # Checks the graph index and updates it if necessary
    def prepare_data(self):
        # Has to happen first, so self.dry_run is populated.
        resources = self.resources

        if self.dry_run:
            return

        from relationalai.semantics.snowflake import Table
        table_sources = Table._used_sources
        if not table_sources.has_changed(self._last_sources_version):
            return

        model = self.database
        app_name = resources.get_app_name()
        engine_name = self.engine
        engine_size = self.resources.config.get_default_engine_size()

        program_span_id = debugging.get_program_span_id()
        sources = [t._fqn for t in Table._used_sources]
        self._last_sources_version = Table._used_sources.version()

        assert self.engine is not None

        with debugging.span("poll_use_index", sources=sources, model=model, engine=engine_name):
            resources.poll_use_index(app_name, sources, model, self.engine, engine_size, program_span_id)

    def report_errors(self, problems: list[dict[str, Any]], abort_on_error=True):
        from relationalai import errors
        all_errors = []
        undefineds = []
        pyrel_errors = defaultdict(list)
        pyrel_warnings = defaultdict(list)

        for problem in problems:
            message = problem.get("message", "")
            report = problem.get("report", "")
            # TODO: we need to build source maps
            # path = problem.get("path", "")
            # source_task = self._install_batch.line_to_task(path, problem["start_line"]) or task
            # source = debugging.get_source(source_task) or debugging.SourceInfo()
            source = debugging.SourceInfo()
            severity = problem.get("severity", "warning")
            code = problem.get("code")

            if severity in ["error", "exception"]:
                if code == "UNDEFINED_IDENTIFIER":
                    match = re.search(r'`(.+?)` is undefined', message)
                    if match:
                        undefineds.append((match.group(1), source))
                    else:
                        all_errors.append(errors.RelQueryError(problem, source))
                elif "overflowed" in report:
                    all_errors.append(errors.NumericOverflow(problem, source))
                elif code == "PYREL_ERROR":
                    pyrel_errors[problem["props"]["pyrel_id"]].append(problem)
                elif abort_on_error:
                    e = errors.RelQueryError(problem, source)
                    supplementary_message = "Troubleshooting:\n" + \
                        "  1. Please retry with a new name for your model. This can work around state-related issues.\n" + \
                        "  2. If the error persists, please retry with the `use_lqp` flag set to `False`, for example:\n" + \
                        "       `model = Model(..., use_lqp=False)`\n" + \
                        "     This will switch the execution to the legacy backend, which may avoid the issue with some performance cost.\n"

                    e.content = f"{e.content}{supplementary_message}"
                    all_errors.append(e)
            else:
                if code == "ARITY_MISMATCH":
                    errors.ArityMismatch(problem, source)
                elif code == "IC_VIOLATION":
                    all_errors.append(errors.IntegrityConstraintViolation(problem, source))
                elif code == "PYREL_ERROR":
                    pyrel_warnings[problem["props"]["pyrel_id"]].append(problem)
                else:
                    errors.RelQueryWarning(problem, source)

        if abort_on_error and len(undefineds):
            all_errors.append(errors.UninitializedPropertyException(undefineds))

        if abort_on_error:
            for pyrel_id, pyrel_problems in pyrel_errors.items():
                all_errors.append(errors.ModelError(pyrel_problems))

        for pyrel_id, pyrel_problems in pyrel_warnings.items():
            errors.ModelWarning(pyrel_problems)


        if len(all_errors) == 1:
            raise all_errors[0]
        elif len(all_errors) > 1:
            raise errors.RAIExceptionSet(all_errors)

    def _export(self, txn_id: str, export_info: tuple, dest_fqn: str, actual_cols: list[str], declared_cols: list[str], update:bool):
        # At this point of the export, we assume that a CSV file has already been written
        # to the Snowflake Native App stage area. Thus, the purpose of this method is to
        # copy the data from the CSV file to the destination table.
        _exec = self.resources._exec
        dest_database, dest_schema, dest_table, _ = IdentityParser(dest_fqn, require_all_parts=True).to_list()
        filename = export_info[0]
        result_table_name = filename + "_table"

        with debugging.span("export", txn_id=txn_id, export_info=export_info, dest_table=dest_table):
            with debugging.span("export_to_result_schema"):
                # First, we need to persist from the CSV file to the results schema by calling the
                # `persist_from_stage` stored procedure. This step also cleans up the CSV file in
                # the stage area.
                column_fields = []
                for (col_name, col_type) in export_info[1]:
                    column_fields.append([col_name, lqp_type_to_sql(col_type)])

                # NOTE: the `str(column_fields)` depends on python formatting which surrounds
                # strings with single quotes. If this changes, or if we ever get a single quote in
                # the actual string, then we need to do something more sophisticated.
                exec_str = f"call {APP_NAME}.api.persist_from_stage('{txn_id}', '{filename}', '{result_table_name}', {str(column_fields)})"
                _exec(exec_str)

            with debugging.span("write_table"):
                # The result of the first step above is a table in the results schema,
                # {app_name}.results.{result_table_name}.
                # Second, we need to copy the data from the results schema to the
                # destination table. This step also cleans up the result table.
                out_sample = _exec(f"select * from {APP_NAME}.results.{result_table_name} limit 1;")
                names = self._build_projection(declared_cols, actual_cols, column_fields, out_sample)
                try:
                    if not update:
                        _exec(f"""
                            BEGIN
                                -- Check if table exists
                                IF (EXISTS (
                                    SELECT 1
                                    FROM {dest_database}.INFORMATION_SCHEMA.TABLES
                                    WHERE table_schema = '{dest_schema}'
                                    AND table_name = '{dest_table}'
                                )) THEN
                                    -- Insert into existing table
                                    EXECUTE IMMEDIATE '
                                        BEGIN
                                            TRUNCATE TABLE {dest_fqn};
                                            INSERT INTO {dest_fqn}
                                            SELECT {names}
                                            FROM {APP_NAME}.results.{result_table_name}
                                            {'' if out_sample else 'WHERE 1=0'};
                                        END;
                                    ';
                                ELSE
                                    -- Create table based on the SELECT
                                    EXECUTE IMMEDIATE '
                                        CREATE TABLE {dest_fqn} AS
                                        SELECT {names}
                                        FROM {APP_NAME}.results.{result_table_name};
                                    ';
                                END IF;
                            END;
                        """)
                    else:
                        if out_sample:
                            _exec(f"""
                                BEGIN
                                    INSERT INTO {dest_fqn}
                                    SELECT {names}
                                    FROM {APP_NAME}.results.{result_table_name};
                                END;
                            """)
                finally:
                    # Always try to drop the result table, even if the insert/create failed.
                    _exec(f"call {APP_NAME}.api.drop_result_table('{result_table_name}');")

    def _build_projection(self, declared_cols, actual_cols, column_fields, out_sample=None):
        # map physical col -> type
        col_type_map = {col.lower(): dtype for col, dtype in column_fields}
        sample_keys = {k.lower() for k in out_sample[0].as_dict()} if out_sample else set()

        fields = []
        ix = 0

        for name in declared_cols:
            if name not in actual_cols:
                # Declared but not present in results
                fields.append(f"NULL as \"{name}\"")
                continue

            colname = f"col{ix:03}"
            ix += 1

            if colname in sample_keys:
                # Actual column exists in sample
                fields.append(f"{colname} as \"{name}\"")
            else:
                # No sample or missing key → fall back to type
                dtype = col_type_map.get(colname.lower(), "VARCHAR")
                fields.append(f"CAST(NULL AS {dtype}) as \"{name}\"")

        return ", ".join(fields)

    def compile_lqp(self, model: ir.Model, task: ir.Task):
        model_txn = None
        if self._last_model != model:
            with debugging.span("compile", metamodel=model) as install_span:
                _, model_txn = self.compiler.compile(model, {"fragment_id": b"model"})
                install_span["compile_type"] = "model"
                install_span["lqp"] = lqp_print.to_string(model_txn, {"print_names": True, "print_debug": False, "print_csv_filename": False})
                self._last_model = model

        with debugging.span("compile", metamodel=task) as compile_span:
            query = f.compute_model(f.logical([task]))
            options = {
                "wide_outputs": self.wide_outputs,
                "fragment_id": b"query",
            }
            result, final_model = self.compiler.compile_inner(query, options)
            export_info, query_txn = result
            compile_span["compile_type"] = "query"
            compile_span["lqp"] = lqp_print.to_string(query_txn, {"print_names": True, "print_debug": False, "print_csv_filename": False})

        txn = query_txn
        if model_txn is not None:
            # Merge the two LQP transactions into one. Long term the query bits should all
            # go into a WhatIf action. But for now we just use two separate epochs.
            model_epoch = model_txn.epochs[0]
            query_epoch = query_txn.epochs[0]
            txn = lqp_ir.Transaction(
                epochs=[model_epoch, query_epoch],
                configure=construct_configure({}, None),
                meta=None,
            )

            # Revalidate now that we've joined two epochs
            validate_lqp(txn)

        txn_proto = convert_transaction(txn)
        # TODO (azreika): Should export_info be encoded as part of the txn_proto? [RAI-40312]
        return final_model, export_info, txn_proto

    # TODO (azreika): This should probably be split up into exporting and other processing. There are quite a lot of arguments here...
    def _process_results(self, task: ir.Task, final_model: ir.Model, raw_results: TransactionAsyncResponse, result_cols: Optional[list[str]], export_info: Optional[tuple], export_to: Optional[str], update: bool) -> DataFrame:
        cols, extra_cols = self._compute_cols(task, final_model)

        df, errs = result_helpers.format_results(raw_results, cols)
        self.report_errors(errs)

        # Process exports
        if export_to and not self.dry_run:
            assert cols, "No columns found in the output"
            assert isinstance(raw_results, TransactionAsyncResponse) and raw_results.transaction, "Invalid transaction result"

            if result_cols is not None:
                assert all(col in result_cols or col in extra_cols for col in cols)
            else:
                result_cols = [col for col in cols if col not in extra_cols]
            assert result_cols

            assert export_info, "Export info should be populated if we are exporting results"
            self._export(raw_results.transaction['id'], export_info, export_to, cols, result_cols, update)

        return self._postprocess_df(self.config, df, extra_cols)

    def execute(self, model: ir.Model, task: ir.Task, format: Literal["pandas", "snowpark"] = "pandas",
                result_cols: Optional[list[str]] = None, export_to: Optional[str] = None,
                update: bool = False) -> DataFrame:
        self.prepare_data()
        previous_model = self._last_model

        final_model, export_info, txn_proto = self.compile_lqp(model, task)

        if self.dry_run:
            return DataFrame()

        if format != "pandas":
            raise ValueError(f"Unsupported format: {format}")

        raw_results = self.resources.exec_lqp(
            self.database,
            self.engine,
            txn_proto.SerializeToString(),
            # Current strategy is to run all queries as write transactions, in order to
            # benefit from view caching. This will have to be revisited, because write
            # transactions are serialized.
            readonly=False,
            nowait_durable=True,
        )
        assert isinstance(raw_results, TransactionAsyncResponse)

        try:
            return self._process_results(task, final_model, raw_results, result_cols, export_info, export_to, update)
        except Exception as e:
            # If processing the results failed, revert to the previous model.
            self._last_model = previous_model
            raise e
