"""
Tests for the __main__.py module entry point
"""

import runpy
import subprocess
import sys
from unittest.mock import patch


def test_main_module_execution():
    """Test running 'python -m artmeta' without arguments"""
    # This test is kept to ensure the subprocess execution works as expected
    # but it won't contribute to coverage measurement of __main__
    result = subprocess.run(
        [sys.executable, "-m", "artmeta"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "usage: artmeta" in result.stdout


def test_main_module_with_help():
    """Test running 'python -m artmeta --help'"""
    result = subprocess.run(
        [sys.executable, "-m", "artmeta", "--help"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Gestionnaire de métadonnées" in result.stdout


def test_main_module_with_version():
    """Test running 'python -m artmeta --version'"""
    result = subprocess.run(
        [sys.executable, "-m", "artmeta", "--version"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "artmeta" in result.stdout


def test_main_entrypoint_for_coverage():
    """Test the __main__ entrypoint using runpy to ensure coverage."""
    with patch.object(sys, "argv", ["artmeta"]):
        with patch.object(sys, "exit") as mock_exit:
            runpy.run_module("artmeta", run_name="__main__", alter_sys=True)

    # main() with no args exits with 1
    mock_exit.assert_called_once_with(1)
