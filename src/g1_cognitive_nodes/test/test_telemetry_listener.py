"""Unit tests for G1TelemetryListener node callback and pub/sub wiring."""

from unittest.mock import MagicMock, patch

import pytest
from sensor_msgs.msg import JointState

from g1_cognitive_nodes.g1_telemetry_listener import G1TelemetryListener


# ---------------------------------------------------------------------------
# Helper: build a mock LowState message with N motor_state entries
# ---------------------------------------------------------------------------
def _make_lowstate_msg(motor_positions, total_motors=35):
    """Return a mock LowState whose motor_state[:N] carry the given positions.

    The real ``unitree_hg.msg.LowState.motor_state`` is a fixed-length array
    of MotorState structs.  We replicate just enough of the interface (the
    ``.q`` attribute on each element) for the callback under test.

    Parameters
    ----------
    motor_positions : list[float]
        Position values to assign to the first len(motor_positions) motors.
    total_motors : int
        Total length of the motor_state array (extras are zero-filled).
    """
    msg = MagicMock()
    motors = []
    for i in range(total_motors):
        motor = MagicMock()
        motor.q = motor_positions[i] if i < len(motor_positions) else 0.0
        motors.append(motor)
    msg.motor_state = motors
    return msg


class TestTelemetryListenerNode:
    """Tests that exercise the G1TelemetryListener ROS 2 node."""

    @pytest.fixture(autouse=True)
    def node(self):
        """Create a fresh node for each test and destroy it afterwards."""
        self._node = G1TelemetryListener()
        yield self._node
        self._node.destroy_node()

    def test_node_name(self):
        assert self._node.get_name() == "g1_telemetry_listener"

    def test_subscriber_exists(self):
        """Node must have at least one subscription (to /lowstate)."""
        subs = self._node.subscriptions
        assert len(subs) >= 1
        topic_names = [s.topic_name for s in subs]
        assert "/lowstate" in topic_names

    def test_publisher_exists(self):
        """Node must have a publisher on /joint_states."""
        pubs = self._node.publishers
        # Filter out internal /rosout and /parameter_events publishers
        user_pubs = [
            p for p in pubs if p.topic_name not in ("/rosout", "/parameter_events")
        ]
        assert len(user_pubs) >= 1
        topic_names = [p.topic_name for p in user_pubs]
        assert "/joint_states" in topic_names


class TestLowstateCallback:
    """Tests that exercise the lowstate_callback transformation logic."""

    @pytest.fixture(autouse=True)
    def node(self):
        self._node = G1TelemetryListener()
        # Capture published messages
        self._published = []
        self._node.publisher_.publish = lambda msg: self._published.append(msg)
        yield self._node
        self._node.destroy_node()

    def _invoke_callback(self, motor_positions, total_motors=35):
        """Helper: build a mock message, call the callback, return captured output."""
        msg = _make_lowstate_msg(motor_positions, total_motors)
        self._node.lowstate_callback(msg)
        assert len(self._published) == 1, "Callback should publish exactly one message"
        return self._published[0]

    def test_callback_publishes_joint_state(self):
        result = self._invoke_callback([0.0] * 29)
        assert isinstance(result, JointState)

    def test_callback_joint_count_is_43(self):
        result = self._invoke_callback([0.0] * 29)
        assert len(result.name) == 43
        assert len(result.position) == 43

    def test_callback_name_position_length_match(self):
        result = self._invoke_callback([0.0] * 29)
        assert len(result.name) == len(result.position)

    def test_callback_body_positions_from_motor_state(self):
        """The first 29 positions should come from motor_state[0..28].q."""
        positions = [float(i) * 0.1 for i in range(29)]
        result = self._invoke_callback(positions)
        for i in range(29):
            assert result.position[i] == pytest.approx(
                positions[i]
            ), f"Body joint {i} mismatch"

    def test_callback_hand_positions_are_zero(self):
        """The last 14 positions (hand joints) must all be 0.0."""
        result = self._invoke_callback([1.0] * 29)
        for i in range(29, 43):
            assert result.position[i] == 0.0, f"Hand joint index {i} should be 0.0"

    def test_callback_preserves_motor_values(self):
        """Known float values should appear unchanged in the output."""
        test_values = [0.123, -0.456, 1.789, 0.0, -3.14] + [0.0] * 24
        result = self._invoke_callback(test_values)
        assert result.position[0] == pytest.approx(0.123)
        assert result.position[1] == pytest.approx(-0.456)
        assert result.position[2] == pytest.approx(1.789)
        assert result.position[4] == pytest.approx(-3.14)

    def test_callback_with_more_than_29_motors(self):
        """Motors beyond index 28 should be ignored — only first 29 are used."""
        positions = [float(i) for i in range(35)]
        result = self._invoke_callback(positions, total_motors=35)
        # Should still have 43 joints
        assert len(result.position) == 43
        # Body positions are motor_state[:29]
        for i in range(29):
            assert result.position[i] == pytest.approx(float(i))
        # Extra motors (index 29-34) are NOT included
        # Hand positions are still zeros
        for i in range(29, 43):
            assert result.position[i] == 0.0

    def test_callback_header_stamp_is_set(self):
        """The published message must have a non-default timestamp."""
        result = self._invoke_callback([0.0] * 29)
        stamp = result.header.stamp
        # At least one of sec/nanosec should be non-zero since we're using
        # the node's clock (system time by default)
        assert stamp.sec != 0 or stamp.nanosec != 0

    def test_callback_joint_names_match_node_config(self):
        """Published joint names should exactly match body_joints + hand_joints."""
        result = self._invoke_callback([0.0] * 29)
        expected = self._node.body_joints + self._node.hand_joints
        assert result.name == expected
