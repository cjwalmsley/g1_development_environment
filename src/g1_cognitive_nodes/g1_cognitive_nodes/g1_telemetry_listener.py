import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data  # Import the required QoS profile
from sensor_msgs.msg import JointState
from unitree_hg.msg import LowState  # Ensure humanoid IDL is used


class G1TelemetryListener(Node):
    def __init__(self):
        super().__init__("g1_telemetry_listener")

        # Subscribe using the Best Effort Sensor Data QoS profile
        self.subscription = self.create_subscription(
            LowState, "/lowstate", self.lowstate_callback, qos_profile_sensor_data
        )

        # Publishes the standard joint states for the robot_state_publisher
        self.publisher_ = self.create_publisher(JointState, "/joint_states", 10)

        # Define the exact 29 main body joints in hardware index order.
        # Names must match the URDF joint names exactly for
        # robot_state_publisher to compute the TF tree.
        self.body_joints = [
            "left_hip_pitch_joint",
            "left_hip_roll_joint",
            "left_hip_yaw_joint",
            "left_knee_joint",
            "left_ankle_pitch_joint",
            "left_ankle_roll_joint",
            "right_hip_pitch_joint",
            "right_hip_roll_joint",
            "right_hip_yaw_joint",
            "right_knee_joint",
            "right_ankle_pitch_joint",
            "right_ankle_roll_joint",
            "waist_yaw_joint",
            "waist_roll_joint",
            "waist_pitch_joint",
            "left_shoulder_pitch_joint",
            "left_shoulder_roll_joint",
            "left_shoulder_yaw_joint",
            "left_elbow_joint",
            "left_wrist_roll_joint",
            "left_wrist_pitch_joint",
            "left_wrist_yaw_joint",
            "right_shoulder_pitch_joint",
            "right_shoulder_roll_joint",
            "right_shoulder_yaw_joint",
            "right_elbow_joint",
            "right_wrist_roll_joint",
            "right_wrist_pitch_joint",
            "right_wrist_yaw_joint",
        ]

        # Define the 14 Dex3-1 hand joints (7 per hand).
        # Names must match the URDF joint names exactly.
        self.hand_joints = [
            "left_hand_thumb_0_joint",
            "left_hand_thumb_1_joint",
            "left_hand_thumb_2_joint",
            "left_hand_index_0_joint",
            "left_hand_index_1_joint",
            "left_hand_middle_0_joint",
            "left_hand_middle_1_joint",
            "right_hand_thumb_0_joint",
            "right_hand_thumb_1_joint",
            "right_hand_thumb_2_joint",
            "right_hand_index_0_joint",
            "right_hand_index_1_joint",
            "right_hand_middle_0_joint",
            "right_hand_middle_1_joint",
        ]

    def lowstate_callback(self, msg):
        joint_state_msg = JointState()
        joint_state_msg.header.stamp = self.get_clock().now().to_msg()
        joint_state_msg.name = self.body_joints + self.hand_joints

        # Extract the 29 position values (q) from LowState and append 14 static zeros for the hands
        body_positions = [motor.q for motor in msg.motor_state[:29]]
        hand_positions = [0.0] * 14

        joint_state_msg.position = body_positions + hand_positions
        self.publisher_.publish(joint_state_msg)


def main(args=None):
    rclpy.init(args=args)
    node = G1TelemetryListener()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
