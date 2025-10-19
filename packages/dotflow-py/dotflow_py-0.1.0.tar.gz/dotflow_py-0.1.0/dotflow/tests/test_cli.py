"""
Tests for CLI functionality.
"""

import pytest
from click.testing import CliRunner
from .dotflow.cli.main import cli
import tempfile
import os


class TestCLI:
    def setup_method(self):
        self.runner = CliRunner()

    def test_version(self):
        """Test version command."""
        result = self.runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "version" in result.output.lower()

    def test_generate_with_dsl_text(self):
        """Test generate command with DSL text."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test.png")

            result = self.runner.invoke(
                cli, ["generate", output_path, "--dsl-text", "A -> B -> C"]
            )

            assert result.exit_code == 0
            assert os.path.exists(output_path)

    def test_generate_with_dsl_file(self):
        """Test generate command with DSL file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dsl_content = "Start -> Process -> End"
            dsl_file = os.path.join(tmpdir, "test.dsl")
            output_path = os.path.join(tmpdir, "test.dot")

            with open(dsl_file, "w") as f:
                f.write(dsl_content)

            result = self.runner.invoke(
                cli,
                ["generate", output_path, "--dsl-file", dsl_file, "--format", "dot"],
            )

            assert result.exit_code == 0
            assert os.path.exists(output_path)

            # Check DOT content was generated
            with open(output_path, "r") as f:
                content = f.read()
                assert "digraph" in content

    def test_validate_command(self):
        """Test validate command."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".dsl") as f:
            f.write("A -> B -> C")
            f.flush()

            result = self.runner.invoke(cli, ["validate", f.name])
            assert result.exit_code == 0
            assert "valid" in result.output.lower()

    def test_validate_invalid_dsl(self):
        """Test validate command with invalid DSL."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".dsl") as f:
            f.write("A ->")  # Invalid DSL
            f.flush()

            result = self.runner.invoke(cli, ["validate", f.name])
            assert result.exit_code != 0
            assert "failed" in result.output.lower()

    def test_themes_command(self):
        """Test themes listing command."""
        result = self.runner.invoke(cli, ["themes"])
        assert result.exit_code == 0
        assert "default" in result.output.lower()

    def test_examples_command(self):
        """Test examples generation command."""
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                result = self.runner.invoke(cli, ["examples", "--format", "dot"])
                assert result.exit_code == 0
                assert "Generated" in result.output
            finally:
                os.chdir(old_cwd)

    def test_cheat_sheet_command(self):
        """Test cheat sheet generation command."""
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                result = self.runner.invoke(cli, ["cheat-sheet", "--format", "dot"])
                assert result.exit_code == 0
                assert "cheat sheet" in result.output.lower()
            finally:
                os.chdir(old_cwd)
