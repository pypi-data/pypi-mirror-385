"""MetricFlow Server - Main logic for executing MetricFlow CLI commands."""

import subprocess
from typing import List, Optional

from .config import MetricFlowConfig
from .types import MetricFlowCommandResult


class MetricFlowServer:
    """Server for executing MetricFlow CLI commands."""

    def __init__(self, config: MetricFlowConfig):
        """Initialize the MetricFlow server with configuration."""
        self.config = config

    def _run_mf_command(self, command: List[str]) -> MetricFlowCommandResult:
        """
        Execute a MetricFlow CLI command.

        Args:
            command: List of command arguments (e.g., ['list-metrics'])

        Returns:
            MetricFlowCommandResult with command output and status
        """
        # Build full command with global options first
        full_command = [self.config.mf_path]

        # Add verbose flag if enabled (as global option)
        if self.config.verbose:
            full_command.append("-v")

        # Note: MetricFlow CLI doesn't support --environment parameter
        # Environment variables should be set directly if needed

        # Add the command
        full_command.extend(command)

        try:
            # Execute the command
            process = subprocess.Popen(
                args=full_command,
                cwd=self.config.project_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            output, _ = process.communicate()

            return MetricFlowCommandResult(
                success=process.returncode == 0,
                output=output or "",
                error=None if process.returncode == 0 else output,
                return_code=process.returncode,
            )

        except Exception as e:
            return MetricFlowCommandResult(
                success=False, output="", error=f"Failed to execute command: {e}", return_code=-1
            )

    def list_metrics(self) -> str:
        """List all available metrics."""
        result = self._run_mf_command(["list-metrics"])
        if result.success:
            return result.output
        else:
            return f"Error listing metrics: {result.error}"

    def get_dimensions(self, metrics: Optional[List[str]] = None) -> str:
        """Get dimensions for specified metrics."""
        command = ["list-dimensions"]
        if metrics:
            command.extend(["--metric-names", ",".join(metrics)])

        result = self._run_mf_command(command)
        if result.success:
            return result.output
        else:
            return f"Error getting dimensions: {result.error}"

    def get_entities(self, metrics: Optional[List[str]] = None) -> str:
        """Get entities for specified metrics."""
        # Note: MetricFlow doesn't have a direct list-entities command
        # We'll use a workaround or return a helpful message
        return (
            "MetricFlow CLI doesn't have a direct list-entities command. "
            "Use list-dimensions to see available grouping options."
        )

    def query_metrics(
        self,
        metrics: List[str],
        dimensions: Optional[List[str]] = None,
        order_by: Optional[List[str]] = None,
        where: Optional[str] = None,
        limit: Optional[int] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        explain: bool = True,
    ) -> str:
        """
        Query metrics with specified parameters.

        Args:
            metrics: List of metric names to query
            dimensions: List of dimensions to group by
            order_by: List of fields to order by
            where: WHERE clause filter
            limit: Number of rows to limit
            start_time: Start time for the query
            end_time: End time for the query
            explain: Whether to explain the query

        Returns:
            Query result as string
        """
        command = ["query", "--metrics", ",".join(metrics)]

        if dimensions:
            command.extend(["--dimensions", ",".join(dimensions)])

        if order_by:
            command.extend(["--order", ",".join(order_by)])

        if where:
            command.extend(["--where", where])

        if limit:
            command.extend(["--limit", str(limit)])

        if start_time:
            command.extend(["--start-time", start_time])

        if end_time:
            command.extend(["--end-time", end_time])

        if explain:
            command.append("--explain")

        result = self._run_mf_command(command)
        if result.success:
            return result.output
        else:
            return f"Error querying metrics: {result.error}"

    def validate_configs(self) -> str:
        """Validate MetricFlow configurations."""
        result = self._run_mf_command(["validate-configs"])
        if result.success:
            return result.output
        else:
            return f"Error validating configs: {result.error}"

    def get_dimension_values(self, dimension_name: str, metrics: Optional[List[str]] = None) -> str:
        """Get possible values for a dimension."""
        command = ["get-dimension-values", dimension_name]
        if metrics:
            command.extend(["--metric-names", ",".join(metrics)])

        result = self._run_mf_command(command)
        if result.success:
            return result.output
        else:
            return f"Error getting dimension values: {result.error}"
