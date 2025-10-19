# Copyright 2025-present DatusAI, Inc.
# Licensed under the Apache License, Version 2.0.
# See http://www.apache.org/licenses/LICENSE-2.0 for details.

from __future__ import annotations

import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Literal, Optional, Sequence

from datus.configuration.agent_config import AgentConfig
from datus.schemas.agent_models import ScopedContextLists, SubAgentConfig
from datus.storage.lancedb_conditions import Node, and_, build_where, eq, in_, like, or_
from datus.storage.metric.store import SemanticMetricsRAG
from datus.storage.schema_metadata.store import SchemaWithValueRAG
from datus.storage.sql_history.store import SqlHistoryRAG
from datus.utils.constants import DBType
from datus.utils.exceptions import DatusException, ErrorCode
from datus.utils.loggings import get_logger
from datus.utils.reference_paths import normalize_reference_path

logger = get_logger(__name__)

SUPPORTED_COMPONENTS = ("metadata", "metrics", "reference_sql")
COMPONENT_DIRECTORIES = {
    "metadata": ("schema_metadata.lance", "schema_value.lance"),
    "metrics": ("semantic_model.lance", "metrics.lance"),
    "reference_sql": ("sql_history.lance",),
}
# TODO: Implement incremental strategy for partial updates
SubAgentBootstrapStrategy = Literal["overwrite", "plan"]


@dataclass(slots=True)
class ComponentResult:
    component: str
    status: Literal["success", "skipped", "error", "plan"]
    message: str
    details: Optional[Dict[str, Any]] = None


@dataclass(slots=True)
class BootstrapResult:
    should_bootstrap: bool
    reason: Optional[str]
    storage_path: str
    strategy: SubAgentBootstrapStrategy
    results: List[ComponentResult]


def _slugify(value: str) -> str:
    text = value.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    return text or "sub-agent"


def _replace_wildcard(value: str) -> str:
    return value.replace("*", "%")


class SubAgentBootstrapper:
    def __init__(
        self,
        agent_config: AgentConfig,
        sub_agent: Optional[SubAgentConfig] = None,
        sub_agent_name: Optional[str] = None,
        check_exists: bool = True,
    ):
        """
        :param agent_config: Agent configuration
        :param sub_agent: Subagent configuration
        :param sub_agent_name: Subagent name
        :param check_exists: Check if sub_agent exists in agent_config
        """
        self.agent_config = agent_config
        self._valid_sub_agent(sub_agent_name, sub_agent, check_exists)

        # used for sqlite
        self.dialect = self.agent_config.db_type
        self.storage_path = self.agent_config.sub_agent_storage_path(self.sub_agent.system_prompt)

    def _valid_sub_agent(
        self,
        sub_agent_name: Optional[str] = None,
        sub_agent: Optional[SubAgentConfig] = None,
        check_exists: bool = True,
    ):
        if sub_agent:
            self.sub_agent_name = sub_agent.system_prompt
            if check_exists:
                self._valid_sub_agent_in_main(self.sub_agent_name)
            self.sub_agent = sub_agent
        elif sub_agent_name:
            self.sub_agent_name = sub_agent_name
            self.sub_agent = SubAgentConfig.model_validate(self._valid_sub_agent_in_main(sub_agent_name))
        else:
            raise DatusException(
                code=ErrorCode.COMMON_FIELD_REQUIRED,
                message="Subagent name and configuration cannot be empty at the same time",
            )

    def _valid_sub_agent_in_main(self, sub_agent_name: str) -> Dict[str, Any]:
        sub_in_main_config = self.agent_config.sub_agent_config(sub_agent_name)
        if not sub_in_main_config:
            raise DatusException(
                ErrorCode.COMMON_VALIDATION_FAILED,
                message=f"Subagent configuration named `{sub_agent_name}` not found in agent configuration",
            )
        return sub_in_main_config

    def run(
        self,
        selected_components: Optional[List[str]] = None,
        strategy: SubAgentBootstrapStrategy = "plan",
    ) -> BootstrapResult:
        if not self.sub_agent.has_scoped_context():
            return BootstrapResult(
                should_bootstrap=False,
                reason="Scope context is empty, no need to execute",
                storage_path=self.storage_path,
                strategy=strategy,
                results=[],
            )
        # Incremental mode is not supported at the moment
        if strategy not in ("overwrite", "plan"):
            raise ValueError(f"Unsupported strategy '{strategy}'. Expected 'overwrite', 'incremental', or 'plan'.")
        # effective_strategy = "overwrite" if strategy == "incremental" else strategy
        if not selected_components:
            selected_components = SUPPORTED_COMPONENTS

        normalized_components = list(dict.fromkeys([c.lower() for c in selected_components]))
        results: List[ComponentResult] = []
        context_lists = self._context_lists()

        if strategy != "plan":
            os.makedirs(self.storage_path, exist_ok=True)

        handlers = {
            "metadata": ("tables", self._handle_metadata),
            "metrics": ("metrics", self._handle_metrics),
            "reference_sql": ("sqls", self._handle_sql_history),
        }
        for component in normalized_components:
            attr_name, handler = handlers[component]
            try:
                result = handler(getattr(context_lists, attr_name), strategy)
            except Exception as exc:  # pragma: no cover - safety net
                logger.exception("Failed to bootstrap %s component", component)
                result = ComponentResult(
                    component=component,
                    status="error",
                    message=str(exc),
                )
            results.append(result)

        if strategy != "plan" and any(r.status == "success" for r in results) and not self.sub_agent.scoped_kb_path:
            self.sub_agent.scoped_kb_path = self.storage_path

        return BootstrapResult(
            storage_path=self.storage_path, strategy=strategy, results=results, should_bootstrap=True, reason=None
        )

    # --------------------------------------------------------------------- #
    # Helpers
    # --------------------------------------------------------------------- #
    def _context_lists(self) -> ScopedContextLists:
        if self.sub_agent.scoped_context:
            return self.sub_agent.scoped_context.as_lists()
        return ScopedContextLists()

    def _ensure_source_ready(self, db_path: str, component: str) -> bool:
        if os.path.isdir(db_path):
            return True
        message = f"Global storage path '{db_path}' not found for component '{component}'."
        logger.warning(message)
        return False

    def clear_all_components(self):
        target_path = self.agent_config.sub_agent_storage_path(self.sub_agent.system_prompt)
        target_path = Path(target_path)
        if target_path.exists() and target_path.is_dir():
            shutil.rmtree(target_path)

    def clear_components(self, components: Sequence[str]):
        for component in components:
            self._clear_component(component)

    def _clear_component(self, component: str):
        if component not in COMPONENT_DIRECTORIES:
            return
        for segment in COMPONENT_DIRECTORIES[component]:
            target = os.path.join(self.storage_path, segment)
            if os.path.isdir(target):
                shutil.rmtree(target, ignore_errors=True)

    def _count_rows(self, storage, condition: Optional[Node]) -> int:
        try:
            storage._ensure_table_ready()
            where_clause = build_where(condition)
            return storage.table.count_rows(where_clause)
        except Exception:
            return 0

    # --------------------------------------------------------------------- #
    # Metadata
    # --------------------------------------------------------------------- #
    def _handle_metadata(
        self,
        tables: List[str],
        strategy: SubAgentBootstrapStrategy,
    ) -> ComponentResult:
        if not tables:
            return ComponentResult(
                component="metadata",
                status="skipped",
                message="No tables defined in scoped context.",
            )

        global_path = self.agent_config.rag_storage_path()
        if not self._ensure_source_ready(global_path, "metadata"):
            return ComponentResult(
                component="metadata",
                status="error",
                message="Global metadata store is not initialized.",
            )

        source = SchemaWithValueRAG(self.agent_config)
        condition_map, invalid_tokens = self._metadata_conditions(tables)

        if not condition_map:
            message = "No valid table filters resolved from scoped context."
            details = {"invalid": invalid_tokens} if invalid_tokens else None
            return ComponentResult(component="metadata", status="skipped", message=message, details=details)

        aggregate_condition = self._combine_conditions(condition_map)
        schema_table = source.schema_store._search_all(
            where=aggregate_condition,
            select_fields=[
                "identifier",
                "catalog_name",
                "database_name",
                "schema_name",
                "table_name",
                "table_type",
                "definition",
            ],
        )
        value_table = source.value_store._search_all(
            where=aggregate_condition,
            select_fields=[
                "identifier",
                "catalog_name",
                "database_name",
                "schema_name",
                "table_name",
                "table_type",
                "sample_rows",
            ],
        )
        schema_rows = schema_table.to_pylist()
        value_rows = value_table.to_pylist()

        missing = self._missing_tokens(source.schema_store, condition_map)

        if strategy == "plan":
            details = {
                "match_count": len(schema_rows),
                "tables": [self._format_table_identifier(item) for item in schema_rows[:20]],
                "missing": missing,
                "invalid": invalid_tokens,
            }
            return ComponentResult(
                component="metadata",
                status="plan",
                message="Metadata plan generated.",
                details=details,
            )

        if not schema_rows and not value_rows:
            return ComponentResult(
                component="metadata",
                status="skipped",
                message="No metadata rows matched scoped context.",
                details={"missing": missing, "invalid": invalid_tokens},
            )

        self._clear_component("metadata")

        target = SchemaWithValueRAG(self.agent_config, self.sub_agent.system_prompt)
        target.store_batch(schema_rows, value_rows)
        target.after_init()

        details = {
            "stored_tables": len(schema_rows),
            "stored_values": len(value_rows),
            "missing": missing,
            "invalid": invalid_tokens,
        }
        return ComponentResult(
            component="metadata",
            status="success",
            message=f"Stored {len(schema_rows)} metadata entries and {len(value_rows)} sample sets.",
            details=details,
        )

    def _metadata_conditions(self, tokens: Iterable[str]) -> tuple[List[tuple[str, Node]], List[str]]:
        mapped: List[tuple[str, Node]] = []
        invalid: List[str] = []
        for raw in tokens:
            token = raw.strip()
            if not token:
                continue
            condition = self._metadata_condition_for_token(token)
            if condition is None:
                invalid.append(token)
            else:
                mapped.append((token, condition))
        return mapped, invalid

    def _metadata_condition_for_token(self, token: str) -> Optional[Node]:
        parts = [p.strip() for p in token.split(".") if p.strip()]
        if not parts:
            return None

        dialect = self.dialect or ""

        field_order: List[str] = []
        if DBType.support_catalog(dialect):
            field_order.append("catalog_name")
        if DBType.support_database(dialect) or dialect == DBType.SQLITE:
            field_order.append("database_name")
        if DBType.support_schema(dialect):
            field_order.append("schema_name")
        field_order.append("table_name")

        values: Dict[str, str] = {field: "" for field in field_order}
        for idx, part in enumerate(parts[: len(field_order)]):
            values[field_order[idx]] = part
        conditions: List[Node] = []
        for field, value in values.items():
            if not value:
                continue
            conditions.append(self._value_condition(field, value))

        if not conditions:
            return None
        return conditions[0] if len(conditions) == 1 else and_(*conditions)

    def _combine_conditions(self, condition_map: List[tuple[str, Node]]) -> Optional[Node]:
        if not condition_map:
            return None
        nodes = [node for _, node in condition_map]
        if len(nodes) == 1:
            return nodes[0]
        return or_(*nodes)

    def _missing_tokens(self, storage, condition_map: List[tuple[str, Node]]) -> List[str]:
        missing: List[str] = []
        for token, node in condition_map:
            if self._count_rows(storage, node) == 0:
                missing.append(token)
        return missing

    @staticmethod
    def _format_table_identifier(row: Dict[str, Any]) -> str:
        return ".".join(
            filter(
                None,
                [
                    row.get("catalog_name"),
                    row.get("database_name"),
                    row.get("schema_name"),
                    row.get("table_name"),
                ],
            )
        )

    # --------------------------------------------------------------------- #
    # Metrics
    # --------------------------------------------------------------------- #
    def _handle_metrics(
        self,
        metrics: List[str],
        strategy: SubAgentBootstrapStrategy,
    ) -> ComponentResult:
        if not metrics:
            return ComponentResult(
                component="metrics",
                status="skipped",
                message="No metrics defined in scoped context.",
            )

        global_path = self.agent_config.rag_storage_path()
        if not self._ensure_source_ready(global_path, "metrics"):
            return ComponentResult(
                component="metrics",
                status="error",
                message="Global metrics store is not initialized.",
            )

        source = SemanticMetricsRAG(self.agent_config)
        condition_map, invalid_tokens = self._hierarchical_conditions(metrics, ("domain", "layer1", "layer2", "name"))

        if not condition_map:
            details = {"invalid": invalid_tokens} if invalid_tokens else None
            return ComponentResult(
                component="metrics",
                status="skipped",
                message="No valid metric filters resolved from scoped context.",
                details=details,
            )

        aggregate_condition = self._combine_conditions(condition_map)

        metric_table = source.metric_storage._search_all(where=aggregate_condition)

        metric_rows = metric_table.to_pylist()
        missing = self._missing_tokens(source.metric_storage, condition_map)

        if strategy == "plan":
            details = {
                "match_count": len(metric_rows),
                "metrics": [self._format_metric_identifier(row) for row in metric_rows[:20]],
                "missing": missing,
                "invalid": invalid_tokens,
            }
            return ComponentResult(
                component="metrics",
                status="plan",
                message="Metrics plan generated.",
                details=details,
            )

        if not metric_rows:
            return ComponentResult(
                component="metrics",
                status="skipped",
                message="No metrics matched scoped context.",
                details={"missing": missing, "invalid": invalid_tokens},
            )

        semantic_names = sorted(
            {row.get("semantic_model_name") for row in metric_rows if row.get("semantic_model_name")}
        )
        semantic_rows: List[Dict[str, Any]] = []
        if semantic_names:
            semantic_condition = in_("semantic_model_name", semantic_names)
            semantic_table = source.semantic_model_storage._search_all(where=semantic_condition)
            semantic_rows = semantic_table.to_pylist()

        self._clear_component("metrics")

        target = SemanticMetricsRAG(self.agent_config, self.sub_agent.system_prompt)
        target.store_batch(semantic_rows, metric_rows)
        target.after_init()

        details = {
            "stored_metrics": len(metric_rows),
            "stored_semantic_models": len(semantic_rows),
            "missing": missing,
            "invalid": invalid_tokens,
        }
        return ComponentResult(
            component="metrics",
            status="success",
            message=f"Stored {len(metric_rows)} metrics and {len(semantic_rows)} semantic models.",
            details=details,
        )

    def _hierarchical_conditions(
        self,
        tokens: Iterable[str],
        fields: Sequence[str],
    ) -> tuple[List[tuple[str, Node]], List[str]]:
        """
        Applies to Metrics and Historical SQL
        """
        mapped: List[tuple[str, Node]] = []
        invalid: List[str] = []
        max_depth = len(fields)
        for raw in tokens:
            token = normalize_reference_path(raw)
            if not token:
                continue
            parts = [p.strip() for p in token.split(".") if p.strip()]
            if not parts:
                continue
            parts = parts[:max_depth]
            conditions: List[Node] = []
            for idx, part in enumerate(parts):
                conditions.append(self._value_condition(fields[idx], part))
            if not conditions:
                invalid.append(token)
                continue
            node = conditions[0] if len(conditions) == 1 else and_(*conditions)
            mapped.append((token, node))
        return mapped, invalid

    @staticmethod
    def _format_metric_identifier(row: Dict[str, Any]) -> str:
        return ".".join(
            filter(
                None,
                [
                    row.get("domain"),
                    row.get("layer1"),
                    row.get("layer2"),
                    row.get("name"),
                ],
            )
        )

    # --------------------------------------------------------------------- #
    # reference SQL
    # --------------------------------------------------------------------- #
    def _handle_sql_history(
        self,
        historical_sql: List[str],
        strategy: SubAgentBootstrapStrategy,
    ) -> ComponentResult:
        if not historical_sql:
            return ComponentResult(
                component="reference_sql",
                status="skipped",
                message="No reference SQL identifiers defined in scoped context.",
            )

        global_path = self.agent_config.rag_storage_path()
        if not self._ensure_source_ready(global_path, "reference_sql"):
            return ComponentResult(
                component="reference_sql",
                status="error",
                message="Global reference SQL store is not initialized.",
            )

        source = SqlHistoryRAG(self.agent_config)
        condition_map, invalid_tokens = self._hierarchical_conditions(
            historical_sql,
            ("domain", "layer1", "layer2", "name"),
        )

        if not condition_map:
            details = {"invalid": invalid_tokens} if invalid_tokens else None
            return ComponentResult(
                component="reference_sql",
                status="skipped",
                message="No valid reference SQL filters resolved from scoped context.",
                details=details,
            )

        aggregate_condition = self._combine_conditions(condition_map)
        sql_table = source.sql_history_storage._search_all(where=aggregate_condition)
        sql_rows = sql_table.to_pylist()

        missing = self._missing_tokens(source.sql_history_storage, condition_map)

        if strategy == "plan":
            details = {
                "match_count": len(sql_rows),
                "entries": [self._format_sql_identifier(row) for row in sql_rows[:20]],
                "missing": missing,
                "invalid": invalid_tokens,
            }
            return ComponentResult(
                component="reference_sql",
                status="plan",
                message="reference SQL plan generated.",
                details=details,
            )

        if not sql_rows:
            return ComponentResult(
                component="reference_sql",
                status="skipped",
                message="No reference SQL entries matched scoped context.",
                details={"missing": missing, "invalid": invalid_tokens},
            )

        self._clear_component("reference_sql")

        target = SqlHistoryRAG(self.agent_config, self.sub_agent.system_prompt)
        target.store_batch(sql_rows)
        target.after_init()

        details = {
            "stored_sqls": len(sql_rows),
            "missing": missing,
            "invalid": invalid_tokens,
        }
        return ComponentResult(
            component="reference_sql",
            status="success",
            message=f"Stored {len(sql_rows)} reference SQL entries.",
            details=details,
        )

    @staticmethod
    def _format_sql_identifier(row: Dict[str, Any]) -> str:
        return ".".join(
            filter(
                None,
                [
                    row.get("domain"),
                    row.get("layer1"),
                    row.get("layer2"),
                    row.get("name"),
                ],
            )
        )

    # --------------------------------------------------------------------- #
    # Condition helpers
    # --------------------------------------------------------------------- #
    def _value_condition(self, field: str, value: str) -> Node:
        value = value.strip()
        if not value:
            return eq(field, "")
        if "*" in value:
            return like(field, _replace_wildcard(value))
        return eq(field, value)

    def rename_scoped_kb_directory(
        self,
        existing_config: Optional[SubAgentConfig],
        new_name: str,
        *,
        previous_name: Optional[str] = None,
    ) -> Optional[Path]:
        source_path = self._resolve_scoped_kb_path(existing_config, previous_name)
        target_path = Path(self.agent_config.sub_agent_storage_path(new_name))

        if not source_path or not source_path.exists():
            return None
        if source_path == target_path:
            return target_path
        if target_path.exists():
            raise FileExistsError(f"Target scoped KB path '{target_path}' already exists.")
        try:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source_path), str(target_path))
        except Exception as exc:
            logger.error("Failed to move scoped KB from '%s' to '%s': %s", source_path, target_path, exc)
            raise
        return target_path

    def _resolve_scoped_kb_path(
        self,
        config: Optional[SubAgentConfig],
        name_hint: Optional[str] = None,
    ) -> Optional[Path]:
        if config and config.scoped_kb_path:
            return Path(config.scoped_kb_path)
        candidate_name = name_hint or (config.system_prompt if config else None)
        if not candidate_name:
            return None
        return Path(self.agent_config.sub_agent_storage_path(candidate_name))
