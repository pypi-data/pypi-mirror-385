from __future__ import annotations

import re
import uuid

import relationalai as rai
import pandas as pd

from typing import Any, Union, Optional, Literal
from snowflake.snowpark import Session

from .. import Compiler
from relationalai import debugging
from relationalai.semantics.metamodel import ir, executor as e, factory as f
from relationalai.clients.result_helpers import sort_data_frame_result
from relationalai.semantics.sql.executor.result_helpers import format_columns
from relationalai.semantics.metamodel.visitor import collect_by_type
from relationalai.semantics.metamodel.typer import typer
from relationalai.tools.constants import USE_DIRECT_ACCESS

class SnowflakeExecutor(e.Executor):
    """Executes SQL using the RAI client."""

    def __init__(
            self,
            database: str,
            schema: str,
            dry_run: bool = False,
            skip_denormalization: bool = False,
            connection: Session | None = None,
            config: rai.Config | None = None,
    ) -> None:
        super().__init__()
        self.database = database
        self.schema = schema
        self.dry_run = dry_run
        self._last_model = None
        self._last_model_sql = None
        self.config = config or rai.Config()
        self.compiler = Compiler(skip_denormalization)
        self.connection = connection
        self._resources = None
        self._provider = None

    @property
    def resources(self):
        if not self._resources:
            with debugging.span("create_session"):
                self.dry_run |= bool(self.config.get("compiler.dry_run", False))
                resource_class = rai.clients.snowflake.Resources
                if self.config.get("use_direct_access", USE_DIRECT_ACCESS):
                    resource_class = rai.clients.snowflake.DirectAccessResources
                self._resources = resource_class(dry_run=self.dry_run, config=self.config, generation=rai.Generation.QB,
                                                 connection=self.connection)
        return self._resources

    @property
    def provider(self):
        if not self._provider:
            self._provider = rai.clients.snowflake.Provider(resources=self.resources)
        return self._provider

    def execute(self, model: ir.Model, task: ir.Task, format:Literal["pandas", "snowpark"]="pandas",
                result_cols: Optional[list[str]] = None, export_to: Optional[str] = None,
                update: bool = False) -> Union[pd.DataFrame, Any]:
        """ Execute the SQL query directly. """

        if self._last_model != model:
            with debugging.span("compile", metamodel=model) as model_span:
                model_sql, _ = self.compiler.compile(model)
                model_span["compile_type"] = "model"
                model_span["sql"] = model_sql
                self._last_model = model
                self._last_model_sql = model_sql

        with debugging.span("compile", metamodel=task) as compile_span:
            # compile into sql and keep the new_task, which is the task model after rewrites,
            # as it may contain results of type inference, which is useful for determining
            # how to format the outputs
            query_sql, new_task = self.compiler.compile(f.compute_model(f.logical([task])), {"query_compilation": True})
            compile_span["compile_type"] = "query"
            compile_span["sql"] = query_sql

        if self.dry_run:
            return pd.DataFrame()

        if format != "pandas":
            raise ValueError(f"Unsupported format: {format}")

        _replace_pattern = re.compile(r"[ /:-]")

        def sanitize_name(value: str) -> str:
            return _replace_pattern.sub("_", value)

        database = sanitize_name(self.database)
        schema = sanitize_name(self.schema)
        unique_id = sanitize_name(str(uuid.uuid4()).lower())
        db_name = f"{database}_{unique_id}"
        db_query = f"CREATE OR REPLACE DATABASE {db_name};"
        schema_query = f"CREATE OR REPLACE SCHEMA {db_name}.{schema};"
        use_schema_query = f"USE SCHEMA {db_name}.{schema};"

        full_model_sql = f"{db_query}\n{schema_query}\n{use_schema_query}\n{self._last_model_sql}\n{query_sql}"

        try:
            result = self.provider.resources._session.connection.execute_string(full_model_sql) # type: ignore

            # Assuming that `task` is a single SQL query per model, and we have it always at the end of the generated SQL.
            rows = result[-1].fetchall()
            result_metadata = result[-1].description

            df = pd.DataFrame(rows, columns=[col.name for col in result_metadata])
            if df.empty:
                # return empty df without column names if it's empty
                return df.iloc[:, 0:0]

            df = format_columns(df, result_metadata, self._collect_columns_metadata(new_task))
            return sort_data_frame_result(df)

        finally:
            self.provider.sql(f"DROP DATABASE IF EXISTS {db_name};")

    def _collect_columns_metadata(self, task: ir.Task) -> dict[str, Optional[ir.Type]]:
        if not task:
            return {}

        outputs = collect_by_type(ir.Output, task)

        assert len(outputs) == 1
        return {
            alias.lower(): typer.to_base_primitive(var.type)
            for alias, var in outputs[0].aliases
            if alias and isinstance(var, ir.Var)
        }
