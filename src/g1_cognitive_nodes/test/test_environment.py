"""Environment smoke tests — verify key imports and config are present.

These tests replace and formalise the manual ``src/test_imports.py`` script,
making them colcon-test-integrated via pytest.
"""

import importlib
import os

import pytest


class TestCoreImports:
    """Verify that critical Python packages import successfully."""

    def test_rclpy_import(self):
        mod = importlib.import_module("rclpy")
        assert mod is not None

    def test_rclpy_node_import(self):
        from rclpy.node import Node

        assert Node is not None

    def test_sensor_msgs_import(self):
        from sensor_msgs.msg import JointState

        assert JointState is not None


class TestUnitreeImports:
    """Verify Unitree-specific packages import successfully.

    These may only be available inside the Docker container where the
    Unitree SDK and message packages are installed.
    """

    def test_unitree_hg_lowstate_import(self):
        try:
            from unitree_hg.msg import LowState

            assert LowState is not None
        except ImportError:
            pytest.skip("unitree_hg not available outside container")

    def test_unitree_sdk2py_import(self):
        try:
            import unitree_sdk2py

            assert unitree_sdk2py is not None
        except ImportError:
            pytest.skip("unitree_sdk2py not available outside container")


class TestEnvironmentConfig:
    """Verify critical environment variables and config files.

    These tests validate the runtime environment that ROS 2 nodes depend on.
    They are most meaningful when run inside the Docker container.
    """

    def test_cyclonedds_config_exists(self):
        config_path = "/workspace/config/cyclonedds.xml"
        if not os.path.isfile(config_path):
            # Fall back to workspace-relative path for non-container environments
            repo_config = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "config",
                "cyclonedds.xml",
            )
            # Skip if neither path exists (e.g. running on host without workspace)
            if not os.path.isfile(repo_config):
                pytest.skip("CycloneDDS config not found (not in container)")
            return
        assert os.path.isfile(config_path)

    def test_rmw_implementation_set(self):
        rmw = os.environ.get("RMW_IMPLEMENTATION")
        if rmw is None:
            pytest.skip("RMW_IMPLEMENTATION not set (not in container)")
        assert rmw == "rmw_cyclonedds_cpp"
