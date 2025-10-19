# Copyright 2025-present DatusAI, Inc.
# Licensed under the Apache License, Version 2.0.
# See http://www.apache.org/licenses/LICENSE-2.0 for details.

from typing import AsyncGenerator, Dict, Optional

from datus.agent.node import Node
from datus.agent.workflow import Workflow
from datus.schemas.action_history import ActionHistory, ActionHistoryManager, ActionRole, ActionStatus
from datus.schemas.search_metrics_node_models import SearchMetricsInput, SearchMetricsResult
from datus.tools.metric_tools.search_metrics import SearchMetricsTool
from datus.utils.loggings import get_logger

logger = get_logger(__name__)


class SearchMetricsNode(Node):
    def setup_input(self, workflow: Workflow) -> Dict:
        logger.info("Setup search metrics input")

        # irrelevant to current node: it should be Start or Reflection node now
        matching_rate = self.agent_config.search_metrics_rate
        matching_rates = ["fast", "medium", "slow"]
        start = matching_rates.index(matching_rate)
        final_matching_rate = matching_rates[min(start + workflow.reflection_round, len(matching_rates) - 1)]
        logger.debug(f"Final matching rate: {final_matching_rate}")

        next_input = SearchMetricsInput(
            input_text=workflow.task.task,
            matching_rate=final_matching_rate,
            sql_task=workflow.task,
            database_type=workflow.task.database_type,
            sql_contexts=workflow.context.sql_contexts,
        )
        self.input = next_input
        return {"success": True, "message": "Search Metrics appears valid"}

    def execute(self):
        self.result = self._execute_search_metrics()

    async def execute_stream(
        self, action_history_manager: Optional[ActionHistoryManager] = None
    ) -> AsyncGenerator[ActionHistory, None]:
        """Execute metrics search with streaming support."""
        async for action in self._search_metrics_stream(action_history_manager):
            yield action

    def _execute_search_metrics(self) -> SearchMetricsResult:
        """Execute schema linking action to analyze database schema.
        Input:
             query - The input query to analyze.
             catalog_name - The catalog name to use.
             database_name - The database name to use.
             schema_name - The schema name to use.
        Returns:
             A validated SchemaLinkingResult containing table schemas and values.
        """
        import os

        path = self.agent_config.rag_storage_path()
        logger.debug(f"Checking if rag storage path exists: {path}")
        if not os.path.exists(path):
            logger.info("RAG storage path does not exist.")
            return self.get_bad_result("RAG storage path does not exist.")
        else:
            try:
                tool = SearchMetricsTool(agent_config=self.agent_config)
                if tool:
                    result = tool.execute(self.input, self.model)
                    logger.info(f"Search metrics result: found {result}")
                    if not result:
                        logger.info("No search result , please check your config or table data")
                        return self.get_bad_result("No search result , please check your config or table data")
                    else:
                        return result
                else:
                    logger.warning("Search metrics tool not found")
                    return self.get_bad_result("Search metrics tool not found")

            except Exception as e:
                logger.warning(f"Search metrics tool initialization failed: {e}")
                return self.get_bad_result(str(e))

    def get_bad_result(self, error_msg: str):
        return SearchMetricsResult(
            success=False,
            error=error_msg,
            sql_task=self.input.sql_task,
            metrics=[],
            metrics_count=0,
        )

    def update_context(self, workflow: Workflow) -> Dict:
        """Update search metrics results to workflow context."""
        result = self.result
        try:
            if len(workflow.context.metrics) == 0:
                workflow.context.metrics = result.metrics
            else:
                pass  # if it's not the first search metrics, wait it after execute_sql

            return {"success": True, "message": "Updated search metrics context"}
        except Exception as e:
            logger.error(f"Failed to update search metrics context: {str(e)}")
            return {"success": False, "message": f"Search metrics context update failed: {str(e)}"}

    async def _search_metrics_stream(
        self, action_history_manager: Optional[ActionHistoryManager] = None
    ) -> AsyncGenerator[ActionHistory, None]:
        """Execute metrics search with streaming support and action history tracking."""
        try:
            # Metrics search action
            search_action = ActionHistory(
                action_id="metrics_search",
                role=ActionRole.WORKFLOW,
                messages="Searching for relevant metrics and business logic",
                action_type="metrics_search",
                input={
                    "input_text": getattr(self.input, "input_text", ""),
                    "matching_rate": getattr(self.input, "matching_rate", "medium"),
                    "database_name": getattr(self.input.sql_task, "database_name", "")
                    if hasattr(self.input, "sql_task")
                    else "",
                },
                status=ActionStatus.PROCESSING,
            )
            yield search_action

            # Execute metrics search
            result = self._execute_search_metrics()

            search_action.status = ActionStatus.SUCCESS if result.success else ActionStatus.FAILED
            search_action.output = {
                "success": result.success,
                "metrics_found": result.metrics_count if hasattr(result, "metrics_count") else 0,
                "error": result.error if hasattr(result, "error") and result.error else None,
            }

            # Store result for later use
            self.result = result

            # Yield the updated action with final status
            yield search_action

        except Exception as e:
            logger.error(f"Metrics search streaming error: {str(e)}")
            raise
