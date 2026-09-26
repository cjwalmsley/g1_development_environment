"""Tests for the g1_sim_visualisation launch file structure.

These tests invoke ``generate_launch_description()`` and inspect the returned
action graph to verify it declares the expected nodes with the correct
configuration.  They require the ``g1_description`` package to be installed
(available inside the Docker container's Unitree underlay).
"""

import os

import pytest

try:
    from ament_index_python.packages import get_package_share_directory

    _HAS_G1_DESCRIPTION = True
    try:
        get_package_share_directory("g1_description")
    except Exception:
        _HAS_G1_DESCRIPTION = False
except ImportError:
    _HAS_G1_DESCRIPTION = False

_skip_reason = (
    "g1_description package not installed — "
    "launch tests require the Unitree underlay (run inside container)"
)


@pytest.mark.skipif(not _HAS_G1_DESCRIPTION, reason=_skip_reason)
class TestLaunchDescription:
    """Validate the structure of g1_sim_visualisation.launch.py."""

    @pytest.fixture(autouse=True)
    def launch_desc(self):
        from g1_cognitive_nodes.launch.g1_sim_visualisation_launch import (
            generate_launch_description,
        )

        self._ld = generate_launch_description()

    def _get_node_actions(self):
        """Extract Node actions from the launch description."""
        from launch_ros.actions import Node as LaunchNode

        return [
            entity
            for entity in self._ld.entities
            if isinstance(entity, LaunchNode)
        ]

    def test_launch_description_returns_three_nodes(self):
        nodes = self._get_node_actions()
        assert len(nodes) == 3, f"Expected 3 nodes, got {len(nodes)}"

    def test_robot_state_publisher_present(self):
        nodes = self._get_node_actions()
        rsp = [
            n
            for n in nodes
            if getattr(n, "_Node__package", None) == "robot_state_publisher"
            or getattr(n, "_package", None) == "robot_state_publisher"
        ]
        assert len(rsp) == 1, "Expected exactly one robot_state_publisher node"

    def test_telemetry_listener_present(self):
        nodes = self._get_node_actions()
        listeners = [
            n
            for n in nodes
            if getattr(n, "_Node__package", None) == "g1_cognitive_nodes"
            or getattr(n, "_package", None) == "g1_cognitive_nodes"
        ]
        assert len(listeners) == 1, "Expected exactly one g1_telemetry_listener node"

    def test_rviz2_present(self):
        nodes = self._get_node_actions()
        rviz = [
            n
            for n in nodes
            if getattr(n, "_Node__package", None) == "rviz2"
            or getattr(n, "_package", None) == "rviz2"
        ]
        assert len(rviz) == 1, "Expected exactly one rviz2 node"
