"""Packaging regression tests for development extras."""

from pathlib import Path
import tomllib


def test_dev_extra_includes_yaml_for_config_workflows():
    """`pip install -e '.[dev]'` should be enough to run config-related tests."""
    pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text())
    dev = [dep.lower() for dep in data["project"]["optional-dependencies"]["dev"]]

    assert any(dep.startswith("pyyaml") for dep in dev), (
        "dev extra must include PyYAML so remember/config tests run under "
        "`pip install -e '.[dev]'`"
    )
