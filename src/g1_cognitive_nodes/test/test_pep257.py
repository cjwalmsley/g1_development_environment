"""PEP 257 docstring lint test — integrated with colcon test via ament_pep257."""

import pytest


@pytest.mark.linter
@pytest.mark.pep257
def test_pep257():
    try:
        from ament_pep257.main import main
    except ImportError:
        pytest.skip("ament_pep257 not installed")

    rc = main(argv=["--exclude", "test"])
    assert rc == 0, "pep257 found docstring style error(s)"
