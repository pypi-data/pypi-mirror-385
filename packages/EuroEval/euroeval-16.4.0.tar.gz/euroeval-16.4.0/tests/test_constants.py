"""Tests for the `constants` module."""

from typing import TypeVar

from euroeval import constants
from euroeval.data_models import Task


def test_all_objects_in_constants_are_constants() -> None:
    """Test that all objects in the `constants` module are constants."""
    for name in dir(constants):
        if name.startswith("__") or name in {"TypeVar", "TaskGroup"}:
            continue
        assert name.isupper() and isinstance(
            getattr(constants, name), (Task, TypeVar, int, float, str, list, dict)
        )
