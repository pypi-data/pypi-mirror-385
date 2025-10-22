from __future__ import annotations

import duckdb
from pandas import DataFrame
from typing import Any, Union, Literal

from relationalai.semantics.sql import Compiler
from relationalai.semantics.sql.executor.result_helpers import format_duckdb_columns
from relationalai.semantics.metamodel import ir, executor as e

class DuckDBExecutor(e.Executor):

    def __init__(self, skip_denormalization: bool = False) -> None:
        super().__init__()
        self.compiler = Compiler(skip_denormalization)

    def execute(self, model: ir.Model, task: ir.Task, format:Literal["pandas", "snowpark"]="pandas") -> Union[DataFrame, Any]:
        """ Execute the SQL query directly. """
        if format != "pandas":
            raise ValueError(f"Unsupported format: {format}")
        connection = duckdb.connect()
        try:
            sql, _ = self.compiler.compile(model, {"is_duck_db": True})
            arrow_table = connection.query(sql).fetch_arrow_table()
            return format_duckdb_columns(arrow_table.to_pandas(), arrow_table.schema)
        finally:
            connection.close()
