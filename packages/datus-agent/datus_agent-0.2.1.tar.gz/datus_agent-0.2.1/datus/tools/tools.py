# Copyright 2025-present DatusAI, Inc.
# Licensed under the Apache License, Version 2.0.
# See http://www.apache.org/licenses/LICENSE-2.0 for details.

# -*- coding: utf-8 -*-
import json
from dataclasses import dataclass
from fnmatch import fnmatchcase
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence

from agents import FunctionTool, Tool, function_tool
from pydantic import BaseModel, Field

from datus.configuration.agent_config import AgentConfig
from datus.schemas.agent_models import SubAgentConfig
from datus.storage.metric.store import SemanticMetricsRAG
from datus.storage.schema_metadata.store import SchemaWithValueRAG
from datus.tools.db_tools import BaseSqlConnector
from datus.tools.db_tools.db_manager import db_manager_instance
from datus.utils.compress_utils import DataCompressor
from datus.utils.constants import SUPPORT_DATABASE_DIALECTS, SUPPORT_SCHEMA_DIALECTS, DBType


class FuncToolResult(BaseModel):
    success: int = Field(
        default=1, description="Whether the execution is successful or not, 1 is success, 0 is failure", init=True
    )
    error: Optional[str] = Field(
        default=None, description="Error message: field is not empty when success=0", init=True
    )
    result: Optional[Any] = Field(default=None, description="Result of the execution", init=True)


def trans_to_function_tool(bound_method: Callable) -> FunctionTool:
    """
    Transfer a bound method to a function tool.
    This method is to solve the problem that '@function_tool' can only be applied to static methods
    """
    tool_template = function_tool(bound_method)

    corrected_schema = json.loads(json.dumps(tool_template.params_json_schema))
    if "self" in corrected_schema.get("properties", {}):
        del corrected_schema["properties"]["self"]
    if "self" in corrected_schema.get("required", []):
        corrected_schema["required"].remove("self")

    # The invoker MUST be an 'async' function.
    # We define a closure to correctly capture the 'bound_method' for each iteration.
    def create_async_invoker(method_to_call: Callable) -> Callable:
        async def final_invoker(tool_ctx, args_str: str) -> dict:
            """
            This is an async wrapper for tool methods.
            The agent framework will 'await' this coroutine.
            """
            # The actual work (JSON parsing, method call)
            args_dict = json.loads(args_str)
            result_dict = method_to_call(**args_dict)

            if isinstance(result_dict, FuncToolResult):
                result_dict = result_dict.model_dump()
            return result_dict

        return final_invoker

    async_invoker = create_async_invoker(bound_method)

    final_tool = FunctionTool(
        name=tool_template.name,
        description=tool_template.description,
        params_json_schema=corrected_schema,
        on_invoke_tool=async_invoker,  # <--- Assign the async function
    )
    return final_tool


@dataclass
class TableCoordinate:
    catalog: str = ""
    database: str = ""
    schema: str = ""
    table: str = ""


@dataclass(frozen=True)
class ScopedTablePattern:
    raw: str
    catalog: str = ""
    database: str = ""
    schema: str = ""
    table: str = ""

    def matches(self, coordinate: TableCoordinate) -> bool:
        return all(
            _pattern_matches(getattr(self, field), getattr(coordinate, field))
            for field in ("catalog", "database", "schema", "table")
        )


def _pattern_matches(pattern: str, value: str) -> bool:
    if not pattern or pattern in ("*", "%"):
        return True
    normalized_pattern = pattern.replace("%", "*")
    return fnmatchcase(value or "", normalized_pattern)


class DBFuncTool:
    def __init__(
        self,
        connector: BaseSqlConnector,
        agent_config: Optional[AgentConfig] = None,
        *,
        sub_agent_name: Optional[str] = None,
        scoped_tables: Optional[Iterable[str]] = None,
    ):
        self.connector = connector
        self.compressor = DataCompressor()
        self.agent_config = agent_config
        self.sub_agent_name = sub_agent_name
        self.schema_rag = SchemaWithValueRAG(agent_config, sub_agent_name) if agent_config else None
        self._field_order = self._determine_field_order()
        self._scoped_patterns = self._load_scoped_patterns(scoped_tables)
        self._semantic_storage = SemanticMetricsRAG(agent_config, sub_agent_name) if agent_config else None
        self.has_schema = self.schema_rag and self.schema_rag.schema_store.table_size() > 0
        self.has_semantic_models = self._semantic_storage and self._semantic_storage.get_semantic_model_size() > 0

    def _reset_database_for_rag(self, database_name: str = "") -> str:
        if self.connector.dialect in (DBType.SQLITE, DBType.DUCKDB):
            return self.connector.database_name
        else:
            return database_name

    def _determine_field_order(self) -> Sequence[str]:
        dialect = getattr(self.connector, "dialect", "") or ""
        fields: List[str] = []
        if DBType.support_catalog(dialect):
            fields.append("catalog")
        if DBType.support_database(dialect) or dialect == DBType.SQLITE:
            fields.append("database")
        if DBType.support_schema(dialect):
            fields.append("schema")
        fields.append("table")
        return fields

    def _load_scoped_patterns(self, explicit_tokens: Optional[Iterable[str]]) -> List[ScopedTablePattern]:
        tokens: List[str] = []
        if explicit_tokens:
            tokens.extend(explicit_tokens)
        else:
            tokens.extend(self._resolve_scoped_context_tables())

        patterns: List[ScopedTablePattern] = []
        for token in tokens:
            scoped_pattern = self._parse_scope_token(token)
            if scoped_pattern:
                patterns.append(scoped_pattern)
        return patterns

    def _resolve_scoped_context_tables(self) -> Sequence[str]:
        if not self.agent_config:
            return []
        scoped_entries: List[str] = []

        if self.sub_agent_name:
            sub_agent_config = self._load_sub_agent_config(self.sub_agent_name)
            if sub_agent_config and sub_agent_config.scoped_context and sub_agent_config.scoped_context.tables:
                scoped_entries.extend(sub_agent_config.scoped_context.as_lists().tables)

        return scoped_entries

    def _load_sub_agent_config(self, sub_agent_name: str) -> Optional[SubAgentConfig]:
        if not self.agent_config:
            return None
        try:
            config = self.agent_config.sub_agent_config(sub_agent_name)
        except Exception:
            return None

        if not config:
            return None
        if isinstance(config, SubAgentConfig):
            return config

        try:
            return SubAgentConfig.model_validate(config)
        except Exception:
            return None

    def _parse_scope_token(self, token: str) -> Optional[ScopedTablePattern]:
        token = (token or "").strip()
        if not token:
            return None
        parts = [self._normalize_identifier_part(part) for part in token.split(".") if part.strip()]
        if not parts:
            return None
        values: Dict[str, str] = {field: "" for field in self._field_order}
        for idx, part in enumerate(parts[: len(self._field_order)]):
            field = self._field_order[idx]
            values[field] = part
        return ScopedTablePattern(raw=token, **values)

    def _get_semantic_model(
        self, catalog: str = "", database: str = "", schema: str = "", table_name: str = ""
    ) -> Dict[str, Any]:
        if not self.has_semantic_models:
            return {}
        result = self._semantic_storage.get_semantic_model(
            catalog_name=catalog,
            database_name=database,
            schema_name=schema,
            table_name=table_name,
            select_fields=["dimensions", "measures", "semantic_model_desc"],
        )
        return {} if not result else result[0]

    @staticmethod
    def _normalize_identifier_part(value: Optional[str]) -> str:
        if value is None:
            return ""
        normalized = str(value).strip()
        if not normalized:
            return ""
        # Strip common quoting characters
        return normalized.strip("`\"'[]")

    def _default_field_value(self, field: str, explicit: Optional[str]) -> str:
        if field not in self._field_order:
            return ""
        if explicit:
            return self._normalize_identifier_part(explicit)

        fallback_attr_map = {
            "catalog": "catalog_name",
            "database": "database_name",
            "schema": "schema_name",
        }
        fallback_attr = fallback_attr_map.get(field)
        if fallback_attr and hasattr(self.connector, fallback_attr):
            return self._normalize_identifier_part(getattr(self.connector, fallback_attr))
        return ""

    def _build_table_coordinate(
        self,
        raw_name: str,
        catalog: Optional[str] = "",
        database: Optional[str] = "",
        schema: Optional[str] = "",
    ) -> TableCoordinate:
        coordinate = TableCoordinate(
            catalog=self._default_field_value("catalog", catalog),
            database=self._default_field_value("database", database),
            schema=self._default_field_value("schema", schema),
            table=self._normalize_identifier_part(raw_name),
        )
        parts = [self._normalize_identifier_part(part) for part in raw_name.split(".") if part.strip()]
        if parts:
            coordinate.table = parts[-1]
            idx = len(parts) - 2
            for field in reversed(self._field_order[:-1]):
                if idx < 0:
                    break
                setattr(coordinate, field, parts[idx])
                idx -= 1
        return coordinate

    def _coordinate_from_row(self, row: Dict[str, Any]) -> TableCoordinate:
        raw_name = row.get("table_name") or row.get("identifier") or ""
        return self._build_table_coordinate(
            raw_name=raw_name,
            catalog=row.get("catalog_name", ""),
            database=row.get("database_name", ""),
            schema=row.get("schema_name", ""),
        )

    def _table_matches_scope(self, coordinate: TableCoordinate) -> bool:
        if not self._scoped_patterns:
            return True
        return any(pattern.matches(coordinate) for pattern in self._scoped_patterns)

    def _filter_metadata_rows(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not self._scoped_patterns:
            return rows
        filtered: List[Dict[str, Any]] = []
        for row in rows:
            if self._table_matches_scope(self._coordinate_from_row(row)):
                filtered.append(row)
        return filtered

    def _filter_table_entries(
        self,
        entries: Sequence[Dict[str, Any]],
        catalog: Optional[str],
        database: Optional[str],
        schema: Optional[str],
    ) -> List[Dict[str, Any]]:
        if not self._scoped_patterns:
            return list(entries)

        filtered: List[Dict[str, Any]] = []
        for entry in entries:
            coordinate = self._build_table_coordinate(
                raw_name=str(entry.get("name", "")),
                catalog=catalog,
                database=database,
                schema=schema,
            )
            if self._table_matches_scope(coordinate):
                filtered.append(entry)
        return filtered

    def _matches_catalog_database(self, pattern: ScopedTablePattern, catalog: str, database: str) -> bool:
        if pattern.catalog and not _pattern_matches(pattern.catalog, catalog):
            return False
        if pattern.database and not _pattern_matches(pattern.database, database):
            return False
        return True

    def _database_matches_scope(self, catalog: Optional[str], database: str) -> bool:
        if not self._scoped_patterns:
            return True
        catalog_value = self._default_field_value("catalog", catalog or "")
        database_value = self._default_field_value("database", database or "")

        wildcard_allowed = False
        for pattern in self._scoped_patterns:
            if not self._matches_catalog_database(pattern, catalog_value, database_value):
                continue
            if pattern.database:
                if _pattern_matches(pattern.database, database_value):
                    return True
                continue
            wildcard_allowed = True
        return wildcard_allowed

    def _schema_matches_scope(self, catalog: Optional[str], database: Optional[str], schema: str) -> bool:
        if not self._scoped_patterns:
            return True
        catalog_value = self._default_field_value("catalog", catalog or "")
        database_value = self._default_field_value("database", database or "")
        schema_value = self._default_field_value("schema", schema or "")

        wildcard_allowed = False
        for pattern in self._scoped_patterns:
            if not self._matches_catalog_database(pattern, catalog_value, database_value):
                continue
            if pattern.schema:
                if _pattern_matches(pattern.schema, schema_value):
                    return True
                continue
            wildcard_allowed = True
        return wildcard_allowed

    def available_tools(self) -> List[Tool]:
        bound_tools = []
        methods_to_convert: List[Callable] = [self.list_tables, self.describe_table]

        if self.schema_rag:
            methods_to_convert.append(self.search_table)

        methods_to_convert.extend(
            [
                self.read_query,
                self.get_table_ddl,
            ]
        )

        if self.connector.dialect in SUPPORT_DATABASE_DIALECTS:
            bound_tools.append(trans_to_function_tool(self.list_databases))

        if self.connector.dialect in SUPPORT_SCHEMA_DIALECTS:
            bound_tools.append(trans_to_function_tool(self.list_schemas))

        for bound_method in methods_to_convert:
            bound_tools.append(trans_to_function_tool(bound_method))
        return bound_tools

    def search_table(
        self,
        query_text: str,
        catalog_name: str = "",
        database_name: str = "",
        schema_name: str = "",
        top_n: int = 5,
        simple_sample_data: bool = True,
    ) -> FuncToolResult:
        """
        Retrieve table candidates by semantic similarity over stored schema metadata and optional sample rows.
        Use this tool  when the agent needs tables matching a natural-language description.
        This tool  helps find relevant tables by searching through table names, schemas (DDL),
        and sample data using semantic search.

        Use this tool when you need to:
        - Find tables related to a specific business concept or domain
        - Discover tables containing certain types of data
        - Locate tables for SQL query development
        - Understand what tables are available in a database

        **Application Guidance**:
        1. If table matches (via definition/description/dimensions/measures/sample_data), use it directly
        2. If partitioned (e.g., date-based in definition), explore correct partition via describe_table
        3. If no match, use list_tables for broader exploration

        Args:
            query_text: Description of the table you want (e.g. "daily active users per country").
            catalog_name: Optional catalog filter to narrow the search.
            database_name: Optional database filter to narrow the search.
            schema_name: Optional schema filter to narrow the search.
            top_n: Maximum number of rows to return after scoping filters.
            simple_sample_data: If True, sample rows omit catalog/database/schema fields for brevity.

        Returns:
            FuncToolResult where:
                - success=1 with result={"metadata": [...], "sample_data": [...]} when matches remain after filtering.
                - success=1 with result=[] and error message when no candidates survive the filters.
                - success=0 with error text if schema storage is unavailable or lookup fails.
        """
        if not self.has_schema:
            return FuncToolResult(success=0, error="Table search is unavailable because schema storage is not ready.")

        try:
            metadata, sample_values = self.schema_rag.search_similar(
                query_text,
                catalog_name=catalog_name,
                database_name=self._reset_database_for_rag(database_name),
                schema_name=schema_name,
                table_type="full",
                top_n=top_n,
            )
            result_dict: Dict[str, List[Dict[str, Any]]] = {"metadata": [], "sample_data": []}

            metadata_rows: List[Dict[str, Any]] = []
            if metadata:
                metadata_rows = metadata.select(
                    [
                        "catalog_name",
                        "database_name",
                        "schema_name",
                        "table_name",
                        "table_type",
                        "definition",
                        "identifier",
                        "_distance",
                    ]
                ).to_pylist()
            metadata_rows = self._filter_metadata_rows(metadata_rows)
            # Enforce post-filter limit
            metadata_rows = metadata_rows[:top_n]
            if not metadata_rows:
                return FuncToolResult(success=1, result=[], error="No metadata rows found.")

            current_has_semantic = False
            if self.has_semantic_models:
                for metadata_row in metadata_rows:
                    semantic_model = self._get_semantic_model(
                        metadata_row["catalog_name"],
                        metadata_row["database_name"],
                        metadata_row["schema_name"],
                        metadata_row["table_name"],
                    )
                    if semantic_model:
                        current_has_semantic = True
                        metadata_row["description"] = semantic_model["semantic_model_desc"]
                        metadata_row["dimensions"] = semantic_model["dimensions"]
                        metadata_row["measures"] = semantic_model["measures"]
                        # Only enrich the top match to prioritize the most relevant table
                        break

            result_dict["metadata"] = metadata_rows
            if current_has_semantic:
                return FuncToolResult(success=1, result=result_dict)

            sample_rows: List[Dict[str, Any]] = []
            if sample_values:
                if simple_sample_data:
                    selected_fields = ["identifier", "table_type", "sample_rows", "_distance"]
                else:
                    selected_fields = [
                        "identifier",
                        "catalog_name",
                        "database_name",
                        "schema_name",
                        "table_type",
                        "table_name",
                        "sample_rows",
                        "_distance",
                    ]
                sample_rows = sample_values.select(selected_fields).to_pylist()
            sample_rows = self._filter_metadata_rows(sample_rows)
            result_dict["sample_data"] = sample_rows
            return FuncToolResult(result=result_dict)
        except Exception as e:
            return FuncToolResult(success=0, error=str(e))

    def list_databases(self, catalog: Optional[str] = "", include_sys: Optional[bool] = False) -> FuncToolResult:
        """
        Enumerate databases accessible through the current connection.

        Args:
            catalog: Optional catalog to scope the lookup (dialect dependent).
            include_sys: Set True to include system databases; defaults to False.

        Returns:
            FuncToolResult with result as a list of database names ordered by the connector. On failure success=0 with
            an explanatory error message.
        """
        try:
            databases = self.connector.get_databases(catalog, include_sys=include_sys)
            filtered = [db for db in databases if self._database_matches_scope(catalog, db)]
            return FuncToolResult(result=filtered)
        except Exception as e:
            return FuncToolResult(success=0, error=str(e))

    def list_schemas(
        self, catalog: Optional[str] = "", database: Optional[str] = "", include_sys: bool = False
    ) -> FuncToolResult:
        """
        List schema names under the supplied catalog/database coordinate.

        Args:
            catalog: Optional catalog filter. Leave blank to rely on connector defaults.
            database: Optional database filter. Leave blank to rely on connector defaults.
            include_sys: Set True to include system schemas; defaults to False.

        Returns:
            FuncToolResult with result holding the schema name list. On failure success=0 with an explanatory message.
        """
        try:
            if database and not self._database_matches_scope(catalog, database):
                return FuncToolResult(result=[])
            schemas = self.connector.get_schemas(catalog, database, include_sys=include_sys)
            filtered = [schema for schema in schemas if self._schema_matches_scope(catalog, database, schema)]
            return FuncToolResult(result=filtered)
        except Exception as e:
            return FuncToolResult(success=0, error=str(e))

    def list_tables(
        self,
        catalog: Optional[str] = "",
        database: Optional[str] = "",
        schema_name: Optional[str] = "",
        include_views: Optional[bool] = True,
    ) -> FuncToolResult:
        """
        Return table-like objects (tables, views, materialized views) visible to the connector.
        Args:
            catalog: Optional catalog filter.
            database: Optional database filter.
            schema_name: Optional schema filter.
            include_views: When True (default) also include views and materialized views.

        Returns:
            FuncToolResult with result=[{"type": "table|view|materialized_view", "name": str}, ...]. On failure
            success=0 with an explanatory error message.
        """
        try:
            result = []
            for tb in self.connector.get_tables(catalog, database, schema_name):
                result.append({"type": "table", "name": tb})

            if include_views:
                # Add views
                try:
                    views = self.connector.get_views(catalog, database, schema_name)
                    for view in views:
                        result.append({"type": "view", "name": view})
                except (NotImplementedError, AttributeError):
                    # Some connectors may not support get_views
                    pass

                # Add materialized views
                try:
                    materialized_views = self.connector.get_materialized_views(catalog, database, schema_name)
                    for mv in materialized_views:
                        result.append({"type": "materialized_view", "name": mv})
                except (NotImplementedError, AttributeError):
                    # Some connectors may not support get_materialized_views
                    pass

            filtered_result = self._filter_table_entries(result, catalog, database, schema_name)
            return FuncToolResult(result=filtered_result)
        except Exception as e:
            return FuncToolResult(success=0, error=str(e))

    def describe_table(
        self,
        table_name: str,
        catalog: Optional[str] = "",
        database: Optional[str] = "",
        schema_name: Optional[str] = "",
    ) -> FuncToolResult:
        """
        Fetch detailed column metadata (and optional semantic model info) for the given table.
        When semantic models exist for the table, `table_info`
        includes additional description/dimension/measure fields.

        Args:
            table_name: Table identifier to describe; can be partially qualified.
            catalog: Optional catalog override. Leave blank to rely on connector defaults.
            database: Optional database override. Leave blank to rely on connector defaults.
            schema_name: Optional schema override. Leave blank to rely on connector defaults.

        Returns:
            FuncToolResult with result={"table_info": {...}, "columns": [...]}. Scope violations or connector errors
            surface as success=0 with an explanatory message.
        """
        try:
            coordinate = self._build_table_coordinate(
                raw_name=table_name,
                catalog=catalog,
                database=database,
                schema=schema_name,
            )
            if not self._table_matches_scope(coordinate):
                return FuncToolResult(
                    success=0,
                    error=f"Table '{table_name}' is outside the scoped context.",
                )
            column_result = self.connector.get_schema(
                catalog_name=catalog, database_name=database, schema_name=schema_name, table_name=table_name
            )
            table_info = {}
            if self.has_semantic_models:
                semantic_model = self._get_semantic_model(catalog, database, schema_name, table_name)
                if semantic_model:
                    table_info["description"] = semantic_model["semantic_model_desc"]
                    table_info["dimensions"] = semantic_model["dimensions"]
                    table_info["measures"] = semantic_model["measures"]
            return FuncToolResult(result={"table_info": table_info, "columns": column_result})
        except Exception as e:
            return FuncToolResult(success=0, error=str(e))

    def read_query(self, sql: str) -> FuncToolResult:
        """
        Execute arbitrary SQL and return the result rows (optionally compressed).

        Args:
            sql: SQL text to run against the connector.

        Returns:
            FuncToolResult with result=self.compressor.compress(rows) when successful. On failure success=0 with the
            underlying error message from the connector.
        """
        try:
            result = self.connector.execute_query(
                sql, result_format="arrow" if self.connector.dialect == DBType.SNOWFLAKE else "list"
            )
            if result.success:
                data = result.sql_return
                return FuncToolResult(result=self.compressor.compress(data))
            else:
                return FuncToolResult(success=0, error=result.error)
        except Exception as e:
            return FuncToolResult(success=0, error=str(e))

    def get_table_ddl(
        self,
        table_name: str,
        catalog: Optional[str] = "",
        database: Optional[str] = "",
        schema_name: Optional[str] = "",
    ) -> FuncToolResult:
        """
        Return the connector's DDL definition for the requested table.

        Use this when the agent needs a full CREATE statement (e.g. for semantic modelling or schema verification).

        Args:
            table_name: Target table identifier (supports partial qualification).
            catalog: Optional catalog override.
            database: Optional database override.
            schema_name: Optional schema override.

        Returns:
            FuncToolResult with result containing identifier/catalog/database/schema/table_name/table_type/definition.
            Scoped-context mismatches or connector failures surface as success=0 with an explanatory message.
        """
        try:
            coordinate = self._build_table_coordinate(
                raw_name=table_name,
                catalog=catalog,
                database=database,
                schema=schema_name,
            )
            if not self._table_matches_scope(coordinate):
                return FuncToolResult(
                    success=0,
                    error=f"Table '{table_name}' is outside the scoped context.",
                )
            # Get tables with DDL
            tables_with_ddl = self.connector.get_tables_with_ddl(
                catalog_name=catalog, database_name=database, schema_name=schema_name, tables=[table_name]
            )

            if not tables_with_ddl:
                return FuncToolResult(success=0, error=f"Table '{table_name}' not found or no DDL available")

            # Return the first (and only) table's DDL
            table_info = tables_with_ddl[0]
            return FuncToolResult(result=table_info)

        except Exception as e:
            return FuncToolResult(success=0, error=str(e))


def db_function_tool_instance(
    agent_config: AgentConfig, database_name: str = "", sub_agent_name: Optional[str] = None
) -> DBFuncTool:
    db_manager = db_manager_instance(agent_config.namespaces)
    return DBFuncTool(
        db_manager.get_conn(agent_config.current_namespace, database_name or agent_config.current_database),
        agent_config=agent_config,
        sub_agent_name=sub_agent_name,
    )


def db_function_tools(
    agent_config: AgentConfig, database_name: str = "", sub_agent_name: Optional[str] = None
) -> List[Tool]:
    return db_function_tool_instance(agent_config, database_name, sub_agent_name).available_tools()
