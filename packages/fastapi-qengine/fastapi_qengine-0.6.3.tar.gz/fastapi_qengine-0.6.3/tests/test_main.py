"""
Tests for main __init__.py module.
"""

import sys
from io import StringIO

import pytest

import fastapi_qengine


class TestMainModule:
    """Test main module functionality."""

    def test_main_function_output(self):
        """Test that main() function outputs expected information."""
        # Capture stdout
        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            fastapi_qengine.main()
        finally:
            sys.stdout = sys.__stdout__

        output = captured_output.getvalue()
        assert "fastapi-qengine" in output
        assert "Version:" in output
        assert "github.com" in output

    def test_module_exports(self):
        """Test that all expected exports are available."""
        expected_exports = [
            "create_qe_dependency",
            "process_filter_to_ast",
            "FilterAST",
            "FilterInput",
            "QEngineConfig",
            "SecurityPolicy",
            "default_config",
            "QEngineError",
            "ParseError",
            "ValidationError",
            "SecurityError",
            "BeanieQueryEngine",
            "create_response_model",
        ]

        for export in expected_exports:
            assert hasattr(fastapi_qengine, export)

    def test_main_script_execution(self):
        """Test that module can be executed as a script."""
        # The module doesn't have a __main__.py, so we test the main() function directly
        import subprocess
        import sys

        # Test running the main function via -c
        result = subprocess.run(
            [sys.executable, "-c", "from fastapi_qengine import main; main()"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "fastapi-qengine" in result.stdout
