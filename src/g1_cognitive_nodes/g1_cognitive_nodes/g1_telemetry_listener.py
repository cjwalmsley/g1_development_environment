import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import JointState
from unitree_hg.msg import LowState, HandState
import math

class G1TelemetryListener(Node):
    def __init__(self):
        super().__init__("g1_telemetry_listener")

        self.left_hand_positions = [0.0] * 7
        self.right_hand_positions = [0.0] * 7

        # Subscribers
        self.subscription = self.create_subscription(
            LowState, "/lowstate", self.lowstate_callback, qos_profile_sensor_data
        )

        # Reliable QoS (10) to match the robot's DDS endpoint and prevent discovery crashes
        self.left_hand_sub = self.create_subscription(
            HandState, "/lf/dex3/left/state", self.left_hand_callback, 10
        )
        self.right_hand_sub = self.create_subscription(
            HandState, "/lf/dex3/right/state", self.right_hand_callback, 10
        )

        # Publishers
        self.publisher_ = self.create_publisher(JointState, "/joint_states", 10)

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

    def _map_hand_motors(self, motor_states):
        positions = []
        for i in range(7):
            if i < len(motor_states):
                q = motor_states[i].q
                positions.append(0.0 if math.isnan(q) or math.isinf(q) else q)
            else:
                positions.append(0.0)
        return positions

    def left_hand_callback(self, msg):
        self.left_hand_positions = self._map_hand_motors(msg.motor_state)

    def right_hand_callback(self, msg):
        self.right_hand_positions = self._map_hand_motors(msg.motor_state)

    def lowstate_callback(self, msg):
        joint_state_msg = JointState()
        joint_state_msg.header.stamp = self.get_clock().now().to_msg()
        joint_state_msg.name = self.body_joints + self.hand_joints

        body_positions = []
        for i in range(29):
            if i < len(msg.motor_state):
                q = msg.motor_state[i].q
                body_positions.append(0.0 if math.isnan(q) or math.isinf(q) else q)
            else:
                body_positions.append(0.0)
        
        hand_positions = self.left_hand_positions + self.right_hand_positions
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
