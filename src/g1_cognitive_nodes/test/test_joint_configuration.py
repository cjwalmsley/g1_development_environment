"""Tests validating the static joint configuration of G1TelemetryListener.

These tests verify that joint names, counts, ordering, and groupings match
the Unitree G1 29-DOF body + 14-DOF Dex3-1 hand specification.
"""

import pytest

from g1_cognitive_nodes.g1_telemetry_listener import G1TelemetryListener


class TestJointCounts:
    """Verify the correct number of joints are defined."""

    @pytest.fixture(autouse=True)
    def node(self):
        self._node = G1TelemetryListener()
        yield
        self._node.destroy_node()

    def test_body_joint_count_is_29(self):
        assert len(self._node.body_joints) == 29

    def test_hand_joint_count_is_14(self):
        assert len(self._node.hand_joints) == 14

    def test_total_joint_count_is_43(self):
        all_joints = self._node.body_joints + self._node.hand_joints
        assert len(all_joints) == 43

    def test_no_duplicate_joint_names(self):
        all_joints = self._node.body_joints + self._node.hand_joints
        assert len(all_joints) == len(set(all_joints)), (
            f"Duplicate joint names found: "
            f"{[j for j in all_joints if all_joints.count(j) > 1]}"
        )


class TestBodyJointGroups:
    """Verify body joints contain the expected anatomical groups."""

    @pytest.fixture(autouse=True)
    def node(self):
        self._node = G1TelemetryListener()
        yield
        self._node.destroy_node()

    def test_left_leg_joints_present(self):
        expected = [
            "L_LEG_HIP_PITCH",
            "L_LEG_HIP_ROLL",
            "L_LEG_HIP_YAW",
            "L_LEG_KNEE",
            "L_LEG_ANKLE_PITCH",
            "L_LEG_ANKLE_ROLL",
        ]
        for joint in expected:
            assert joint in self._node.body_joints, f"Missing left leg joint: {joint}"

    def test_right_leg_joints_present(self):
        expected = [
            "R_LEG_HIP_PITCH",
            "R_LEG_HIP_ROLL",
            "R_LEG_HIP_YAW",
            "R_LEG_KNEE",
            "R_LEG_ANKLE_PITCH",
            "R_LEG_ANKLE_ROLL",
        ]
        for joint in expected:
            assert joint in self._node.body_joints, f"Missing right leg joint: {joint}"

    def test_waist_joints_present(self):
        expected = ["WAIST_YAW", "WAIST_ROLL", "WAIST_PITCH"]
        for joint in expected:
            assert joint in self._node.body_joints, f"Missing waist joint: {joint}"

    def test_left_arm_joints_present(self):
        expected = [
            "L_SHOULDER_PITCH",
            "L_SHOULDER_ROLL",
            "L_SHOULDER_YAW",
            "L_ELBOW",
            "L_WRIST_ROLL",
            "L_WRIST_PITCH",
            "L_WRIST_YAW",
        ]
        for joint in expected:
            assert joint in self._node.body_joints, f"Missing left arm joint: {joint}"

    def test_right_arm_joints_present(self):
        expected = [
            "R_SHOULDER_PITCH",
            "R_SHOULDER_ROLL",
            "R_SHOULDER_YAW",
            "R_ELBOW",
            "R_WRIST_ROLL",
            "R_WRIST_PITCH",
            "R_WRIST_YAW",
        ]
        for joint in expected:
            assert joint in self._node.body_joints, f"Missing right arm joint: {joint}"

    def test_bilateral_symmetry(self):
        """Left/right body joints should be mirrored (L_ ↔ R_)."""
        left_joints = [j for j in self._node.body_joints if j.startswith("L_")]
        right_joints = [j for j in self._node.body_joints if j.startswith("R_")]
        assert len(left_joints) == len(right_joints), (
            f"Asymmetry: {len(left_joints)} left vs {len(right_joints)} right"
        )
        # Every left joint should have a right counterpart
        for lj in left_joints:
            rj = "R_" + lj[2:]
            assert rj in right_joints, f"No right counterpart for {lj}"


class TestBodyJointOrdering:
    """Verify joints appear in the expected hardware index order."""

    @pytest.fixture(autouse=True)
    def node(self):
        self._node = G1TelemetryListener()
        yield
        self._node.destroy_node()

    def test_left_leg_is_first_group(self):
        """Left leg joints (indices 0-5) come first."""
        assert self._node.body_joints[0] == "L_LEG_HIP_PITCH"
        assert self._node.body_joints[5] == "L_LEG_ANKLE_ROLL"

    def test_right_leg_is_second_group(self):
        """Right leg joints (indices 6-11) come second."""
        assert self._node.body_joints[6] == "R_LEG_HIP_PITCH"
        assert self._node.body_joints[11] == "R_LEG_ANKLE_ROLL"

    def test_waist_is_third_group(self):
        """Waist joints (indices 12-14) come third."""
        assert self._node.body_joints[12] == "WAIST_YAW"
        assert self._node.body_joints[14] == "WAIST_PITCH"

    def test_left_arm_is_fourth_group(self):
        """Left arm joints (indices 15-21) come fourth."""
        assert self._node.body_joints[15] == "L_SHOULDER_PITCH"
        assert self._node.body_joints[21] == "L_WRIST_YAW"

    def test_right_arm_is_fifth_group(self):
        """Right arm joints (indices 22-28) come fifth."""
        assert self._node.body_joints[22] == "R_SHOULDER_PITCH"
        assert self._node.body_joints[28] == "R_WRIST_YAW"


class TestHandJoints:
    """Verify hand joint configuration."""

    @pytest.fixture(autouse=True)
    def node(self):
        self._node = G1TelemetryListener()
        yield
        self._node.destroy_node()

    def test_left_hand_joints_present(self):
        expected = [
            "l_thumb_pitch",
            "l_thumb_roll",
            "l_thumb_yaw",
            "l_index_pitch",
            "l_index_roll",
            "l_middle_pitch",
            "l_middle_roll",
        ]
        for joint in expected:
            assert joint in self._node.hand_joints, f"Missing left hand joint: {joint}"

    def test_right_hand_joints_present(self):
        expected = [
            "r_thumb_pitch",
            "r_thumb_roll",
            "r_thumb_yaw",
            "r_index_pitch",
            "r_index_roll",
            "r_middle_pitch",
            "r_middle_roll",
        ]
        for joint in expected:
            assert (
                joint in self._node.hand_joints
            ), f"Missing right hand joint: {joint}"

    def test_left_hand_before_right_hand(self):
        """Left hand joints should appear before right hand joints."""
        first_right = None
        for i, j in enumerate(self._node.hand_joints):
            if j.startswith("r_"):
                first_right = i
                break
        assert first_right is not None, "No right hand joints found"
        # All joints before first_right should be left hand
        for j in self._node.hand_joints[:first_right]:
            assert j.startswith("l_"), f"Expected left hand joint, got: {j}"

    def test_seven_joints_per_hand(self):
        left = [j for j in self._node.hand_joints if j.startswith("l_")]
        right = [j for j in self._node.hand_joints if j.startswith("r_")]
        assert len(left) == 7, f"Expected 7 left hand joints, got {len(left)}"
        assert len(right) == 7, f"Expected 7 right hand joints, got {len(right)}"
