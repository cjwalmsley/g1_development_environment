"""Integration test: publish LowState → verify JointState output.

This test exercises the full ROS 2 pub/sub pipeline end-to-end by:
1. Starting the G1TelemetryListener node
2. Publishing a synthetic LowState message to /lowstate
3. Subscribing to /joint_states and asserting the output is correct

Requires the Unitree message packages (unitree_hg) to be installed,
so this test is designed to run inside the Docker container.
"""

import threading
import time

import pytest

try:
    from unitree_hg.msg import LowState

    _HAS_UNITREE_HG = True
except ImportError:
    _HAS_UNITREE_HG = False

import rclpy
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import JointState

from g1_cognitive_nodes.g1_telemetry_listener import G1TelemetryListener


@pytest.mark.skipif(not _HAS_UNITREE_HG, reason="unitree_hg not available")
class TestTelemetryIntegration:
    """End-to-end integration test for the telemetry bridge."""

    @pytest.fixture(autouse=True)
    def setup_nodes(self):
        """Set up the telemetry listener, a test publisher, and a test subscriber."""
        self._listener_node = G1TelemetryListener()

        # Create a helper node for publishing test messages and subscribing to output
        self._test_node = rclpy.create_node("test_integration_helper")
        self._publisher = self._test_node.create_publisher(
            LowState, "/lowstate", qos_profile_sensor_data
        )
        self._received_msgs = []
        self._subscriber = self._test_node.create_subscription(
            JointState, "/joint_states", self._joint_state_cb, 10
        )

        yield

        self._listener_node.destroy_node()
        self._test_node.destroy_node()

    def _joint_state_cb(self, msg):
        self._received_msgs.append(msg)

    def _spin_nodes(self, duration_sec=0.5):
        """Spin both nodes for a short duration to process messages."""
        executor = rclpy.executors.MultiThreadedExecutor()
        executor.add_node(self._listener_node)
        executor.add_node(self._test_node)

        end_time = time.time() + duration_sec
        while time.time() < end_time:
            executor.spin_once(timeout_sec=0.05)

        executor.shutdown()

    def test_end_to_end_joint_state_publishing(self):
        """Publish a LowState and verify a JointState arrives with correct data."""
        # Create a LowState message with known motor values
        lowstate_msg = LowState()
        for i in range(min(29, len(lowstate_msg.motor_state))):
            lowstate_msg.motor_state[i].q = float(i) * 0.01

        # Publish the message
        self._publisher.publish(lowstate_msg)

        # Spin to let the callback process
        self._spin_nodes(duration_sec=1.0)

        # Verify we received at least one JointState
        assert len(self._received_msgs) >= 1, (
            "No JointState messages received after publishing LowState"
        )

        result = self._received_msgs[-1]
        assert len(result.name) == 43
        assert len(result.position) == 43

        # Verify body positions match what we published
        for i in range(29):
            assert result.position[i] == pytest.approx(float(i) * 0.01, abs=1e-6)

        # Verify hand positions are zero
        for i in range(29, 43):
            assert result.position[i] == 0.0
