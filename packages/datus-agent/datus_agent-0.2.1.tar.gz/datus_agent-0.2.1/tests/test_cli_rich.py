import uuid
from argparse import Namespace
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import patch

import pytest
import yaml

from datus.cli.repl import DatusCLI
from datus.schemas.node_models import TableSchema


@pytest.fixture
def mock_args():
    """Provides default mock arguments for initializing DatusCLI."""
    return Namespace(
        history_file="~/.datus/sql_history",
        debug=False,
        namespace="bird_school",
        database="california_schools",
        # Add any other required args with default values
        config="tests/conf/agent.yml",
        storage_path="tests/data",
    )


@pytest.fixture
def schema_linking_input() -> List[Dict[str, Any]]:
    """Load test data from YAML file"""
    yaml_path = Path(__file__).parent / "data" / "SchemaLinkingInput.yaml"
    with open(yaml_path, "r") as f:
        return yaml.safe_load(f)


@pytest.fixture
def gen_sql_input() -> List[Dict[str, Any]]:
    """Load test data from YAML file"""
    yaml_path = Path(__file__).parent / "data" / "GenerateSQLInput.yaml"
    with open(yaml_path, "r") as f:
        return yaml.safe_load(f)


# This is now a true integration test
@pytest.mark.acceptance
def test_schema_linking(mock_args, capsys, schema_linking_input: List[Dict[str, Any]]):
    """
    Tests the '!sl' command against the real execution logic.
    Asserts that the command runs and prints the result table structure.
    """
    input_data = schema_linking_input[0]["input"]
    with patch("datus.cli.repl.PromptSession.prompt") as mock_repl_prompt:
        mock_repl_prompt.side_effect = ["!sl", EOFError]

        with patch("datus.cli.repl.DatusCLI.prompt_input") as mock_internal_prompt:
            # Mocks user input for: input_text, database_name, top_n
            mock_internal_prompt.side_effect = [
                input_data["input_text"],
                input_data["database_name"],
                "5",
            ]

            cli = DatusCLI(args=mock_args)
            cli.run()

    captured = capsys.readouterr()
    stdout = captured.out

    assert "Schema Linking" in stdout
    assert "relevant tables and" in stdout and "Schema Linking Results" in stdout
    assert "Error during schema linking" not in stdout


# This is now a true integration test
@pytest.mark.acceptance
def test_search_history(mock_args, capsys, schema_linking_input: List[Dict[str, Any]]):
    """
    Tests the '!sh' command against the real execution logic.
    Asserts that the command runs and prints the result table structure.
    """
    input_data = schema_linking_input[0]["input"]
    with patch("datus.cli.repl.PromptSession.prompt") as mock_repl_prompt:
        mock_repl_prompt.side_effect = ["!sq", EOFError]

        with patch("datus.cli.repl.DatusCLI.prompt_input") as mock_internal_prompt:
            mock_internal_prompt.side_effect = [
                input_data["input_text"],
                "",  # domain
                "",  # layer1
                "",  # layer2
                "5",
            ]

            cli = DatusCLI(args=mock_args)
            cli.run()

    captured = capsys.readouterr()
    stdout = captured.out

    assert "Search Reference SQL" in stdout
    assert "Reference SQL Search Results" in stdout
    assert "Error searching reference sql:" not in stdout


# This is now a true integration test
@pytest.mark.acceptance
def test_search_metrics(mock_args, capsys, schema_linking_input: List[Dict[str, Any]]):
    """
    Tests the '!search_metrics' command against the real execution logic.
    Asserts that the command runs and prints the result table structure.
    """
    input_data = schema_linking_input[0]["input"]
    with patch("datus.cli.repl.PromptSession.prompt") as mock_repl_prompt:
        mock_repl_prompt.side_effect = ["!sm", EOFError]
        with patch("datus.cli.repl.DatusCLI.prompt_input") as mock_internal_prompt:
            mock_internal_prompt.side_effect = [
                input_data["input_text"],
                "",
                "",
                "",
                "5",
            ]
            cli = DatusCLI(args=mock_args)
            cli.run()

    captured = capsys.readouterr()
    stdout = captured.out

    assert "Search Metrics" in stdout
    assert ("Found" in stdout and "Metrics Search Results" in stdout) or "No metrics found." in stdout
    assert "Error searching metrics" not in stdout


def test_run_command(mock_args, capsys, gen_sql_input: List[Dict[str, Any]]):
    input_data = gen_sql_input[0]["input"]
    sql_task = input_data["sql_task"]
    with patch("datus.cli.repl.PromptSession.prompt") as mock_prompt:
        mock_prompt.side_effect = ["!run", EOFError]
        with patch("datus.cli.repl.DatusCLI.prompt_input") as mock_internal_prompt, patch(
            "datus.cli.screen.show_workflow_screen"
        ) as mock_workflow_screen:
            mock_internal_prompt.side_effect = [
                str(uuid.uuid1())[:8],
                sql_task["task"],
                sql_task["database_name"],
                "external_knowledge",
                "",
            ]
            cli = DatusCLI(args=mock_args)
            cli.run()

            mock_workflow_screen.assert_called_once()


@pytest.mark.acceptance
def test_bash_command_allowed(mock_args, capsys):
    with patch("datus.cli.repl.PromptSession.prompt") as mock_prompt, patch("subprocess.run") as mock_run:
        mock_prompt.side_effect = ["!bash ls -l", EOFError]
        cli = DatusCLI(args=mock_args)
        cli.run()
        mock_run.assert_called_once_with("ls -l", shell=True, capture_output=True, text=True, timeout=10)


@pytest.mark.acceptance
def test_bash_command_denied(mock_args, capsys):
    with patch("datus.cli.repl.PromptSession.prompt") as mock_prompt, patch("subprocess.run") as mock_run:
        mock_prompt.side_effect = ["!bash rm -rf ./temp.temp", EOFError]
        cli = DatusCLI(args=mock_args)
        cli.run()
        mock_run.assert_not_called()
        captured = capsys.readouterr()
        assert "Command 'rm' not in whitelist" in captured.out


@pytest.mark.acceptance
def test_databases_command(mock_args, capsys):
    with patch("datus.cli.repl.PromptSession.prompt") as mock_prompt:
        mock_prompt.side_effect = [".databases", EOFError]
        cli = DatusCLI(args=mock_args)
        cli.run()
        captured = capsys.readouterr()
        assert "Databases" in captured.out


@pytest.mark.acceptance
def test_tables_command(mock_args, capsys):
    with patch("datus.cli.repl.PromptSession.prompt") as mock_prompt:
        mock_prompt.side_effect = [".tables", EOFError]
        cli = DatusCLI(args=mock_args)
        cli.run()
        captured = capsys.readouterr()
        assert "Tables in Database" in captured.out


@pytest.mark.acceptance
def test_chat_command(mock_args, capsys, gen_sql_input: List[Dict[str, Any]]):
    """
    Tests the '/<chat>' command for multi-turn conversation and context memory.
    """
    input_data = gen_sql_input[0]["input"]
    sql_task = input_data["sql_task"]
    table_schemas = []
    if "table_schemas" in input_data:
        schemas_list = input_data.get("table_schemas", [])
        table_schemas = [TableSchema.from_dict(item) for item in schemas_list]

    with patch("datus.cli.repl.PromptSession.prompt") as mock_prompt:
        mock_prompt.side_effect = [
            f"/{sql_task['task']}",
            ".chat_info",
            EOFError,
        ]
        with (
            patch("datus.cli.repl.DatusCLI.prompt_input") as mock_internal_prompt,
            patch("datus.cli.repl.AtReferenceCompleter.parse_at_context") as at_data,
        ):
            at_data.return_value = table_schemas, [], []
            mock_internal_prompt.side_effect = ["n"]
            cli = DatusCLI(args=mock_args)

            import time

            # Wait for agent to be ready to avoid flakiness
            timeout = 60  # seconds
            start_time = time.time()
            while not cli.agent_ready:
                if time.time() - start_time > timeout:
                    pytest.fail("Agent initialization timed out.")
                time.sleep(0.5)

            cli.run()

    captured = capsys.readouterr()
    stdout = captured.out

    # Check for "Tool cal" responses
    assert stdout.count("Tool call") > 0, "Should have some tool_call."

    # Check for "Thinking:" responses
    assert stdout.count("Thinking:") > 0, "Should have thinking step."
    assert stdout.count("Generated SQL") == 1, "Should have `Generated SQL`"

    # Check chat info
    assert stdout.count("Chat Session Info:") > 0, "Should have latest chat session info"


@pytest.mark.acceptance
def test_chat_info(mock_args, capsys):
    """
    Tests the '.chat_info' command for last_
    """

    with patch("datus.cli.repl.PromptSession.prompt") as mock_prompt:
        mock_prompt.side_effect = [
            ".chat_info",
            EOFError,
        ]
        cli = DatusCLI(args=mock_args)
        cli.run()

    captured = capsys.readouterr()
    stdout = captured.out

    # print("$$$", stdout)

    # Check for "Tool cal" responses
    assert stdout.strip().endswith("No active session.")
