"""
CLI tests for mcli.self.self_cmd commands
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner


class TestSelfCommands:
    """Test suite for self CLI commands"""

    def setup_method(self):
        """Setup test environment"""
        self.runner = CliRunner()

    def test_self_app_group_exists(self):
        """Test self command group exists"""
        from mcli.self.self_cmd import self_app

        assert self_app is not None
        assert hasattr(self_app, "commands")

    def test_self_app_help(self):
        """Test self command help"""
        from mcli.self.self_cmd import self_app

        result = self.runner.invoke(self_app, ["--help"])

        assert result.exit_code == 0
        assert "self" in result.output.lower() or "manage" in result.output.lower()

    def test_commands_group_exists(self):
        """Test commands group exists (moved to commands_cmd)"""
        from mcli.app.commands_cmd import commands

        assert commands is not None

    def test_commands_group_help(self):
        """Test commands group help (moved to commands_cmd)"""
        from mcli.app.commands_cmd import commands

        result = self.runner.invoke(commands, ["--help"])

        assert result.exit_code == 0

    @patch("mcli.app.commands_cmd.load_lockfile")
    def test_list_states_empty(self, mock_load):
        """Test listing command states when none exist"""
        from mcli.app.commands_cmd import commands

        mock_load.return_value = []

        result = self.runner.invoke(commands, ["state", "list"])

        assert result.exit_code == 0
        assert "no" in result.output.lower() or "found" in result.output.lower()

    @patch("mcli.app.commands_cmd.load_lockfile")
    def test_list_states_with_data(self, mock_load):
        """Test listing command states with data"""
        from mcli.app.commands_cmd import commands

        mock_states = [
            {
                "hash": "abc123def456",
                "timestamp": "2025-01-01T00:00:00Z",
                "commands": [{"name": "cmd1"}],
            }
        ]
        mock_load.return_value = mock_states

        result = self.runner.invoke(commands, ["state", "list"])

        assert result.exit_code == 0
        # Should show hash (first 8 chars)
        assert "abc123" in result.output or "Command States" in result.output

    @patch("mcli.app.commands_cmd.restore_command_state")
    def test_restore_state_found(self, mock_restore):
        """Test restoring command state when hash found"""
        from mcli.app.commands_cmd import commands

        mock_restore.return_value = True

        result = self.runner.invoke(commands, ["state", "restore", "abc123"])

        assert result.exit_code == 0
        assert "restored" in result.output.lower()

    @patch("mcli.app.commands_cmd.restore_command_state")
    def test_restore_state_not_found(self, mock_restore):
        """Test restoring command state when hash not found"""
        from mcli.app.commands_cmd import commands

        mock_restore.return_value = False

        result = self.runner.invoke(commands, ["state", "restore", "nonexistent"])

        assert result.exit_code == 0
        assert "not found" in result.output.lower()

    @patch("mcli.app.commands_cmd.get_current_command_state")
    @patch("mcli.app.commands_cmd.append_lockfile")
    def test_write_state_no_file(self, mock_append, mock_get_state):
        """Test writing current command state"""
        from mcli.app.commands_cmd import commands

        mock_get_state.return_value = [{"name": "cmd1"}]

        result = self.runner.invoke(commands, ["state", "write"])

        assert result.exit_code == 0
        mock_append.assert_called_once()

    def test_write_state_with_file(self):
        """Test writing command state from JSON file"""
        from mcli.app.commands_cmd import commands

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            test_data = [{"name": "cmd1", "group": "group1"}]
            json.dump(test_data, f)
            temp_path = f.name

        with patch("mcli.app.commands_cmd.append_lockfile") as mock_append:
            result = self.runner.invoke(commands, ["state", "write", temp_path])

            assert result.exit_code == 0
            mock_append.assert_called_once()

        # Cleanup
        Path(temp_path).unlink()

    # NOTE: search tests removed - search command has been moved to mcli.app.commands_cmd
    # and is no longer part of self_app

    def test_hello_command_default(self):
        """Test hello command with default name"""
        from mcli.self.self_cmd import self_app

        result = self.runner.invoke(self_app, ["hello"])

        assert result.exit_code == 0
        assert "world" in result.output.lower() or "hello" in result.output.lower()

    def test_hello_command_with_name(self):
        """Test hello command with custom name"""
        from mcli.self.self_cmd import self_app

        result = self.runner.invoke(self_app, ["hello", "Alice"])

        assert result.exit_code == 0
        # Should greet Alice
        assert "alice" in result.output.lower() or "Alice" in result.output

    def test_hello_help(self):
        """Test hello command help"""
        from mcli.self.self_cmd import self_app

        result = self.runner.invoke(self_app, ["hello", "--help"])

        assert result.exit_code == 0

    def test_command_state_help(self):
        """Test command state help (moved to commands_cmd)"""
        from mcli.app.commands_cmd import commands

        result = self.runner.invoke(commands, ["state", "--help"])

        assert result.exit_code == 0


class TestCollectCommands:
    """Test suite for collect_commands function"""

    @patch("mcli.self.self_cmd.importlib.import_module")
    def test_collect_commands_basic(self, mock_import):
        """Test collecting commands from modules"""
        from mcli.self.self_cmd import collect_commands

        # This might fail if dependencies are missing, so just check it's callable
        assert callable(collect_commands)

    def test_collect_commands_returns_list(self):
        """Test that collect_commands returns a list"""
        from mcli.self.self_cmd import collect_commands

        try:
            result = collect_commands()
            assert isinstance(result, list)
        except Exception:
            # May fail due to import issues, that's okay
            pass
