"""Flake8 lint test — integrated with colcon test via ament_flake8."""

import pytest


@pytest.mark.linter
@pytest.mark.flake8
def test_flake8():
    try:
        from ament_flake8.main import main_with_errors
    except ImportError:
        pytest.skip("ament_flake8 not installed")

    rc, errors = main_with_errors(argv=[])
    assert rc == 0, "flake8 found {} error(s):\n".format(len(errors)) + "\n".join(
        errors
    )
