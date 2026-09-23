import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
# Note: Replace 'unitree_ros2_messages' with the actual package name of your compiled LowState message
from unitree_ros2_messages.msg import LowState


class G1TelemetryListener(Node):
    def __init__(self):
        super().__init__('g1_telemetry_listener')

        # Subscribes to the raw DDS telemetry replayed from the bag file
        self.subscription = self.create_subscription(
            LowState,
            '/lowstate',
            self.lowstate_callback,
            10
        )

        # Publishes the standard joint states for the robot_state_publisher
        self.publisher_ = self.create_publisher(JointState, '/joint_states', 10)

        # Define the exact 29 main body joints in hardware index order
        self.body_joints = [
            'L_LEG_HIP_PITCH', 'L_LEG_HIP_ROLL', 'L_LEG_HIP_YAW', 'L_LEG_KNEE', 'L_LEG_ANKLE_PITCH', 'L_LEG_ANKLE_ROLL',
            'R_LEG_HIP_PITCH', 'R_LEG_HIP_ROLL', 'R_LEG_HIP_YAW', 'R_LEG_KNEE', 'R_LEG_ANKLE_PITCH', 'R_LEG_ANKLE_ROLL',
            'WAIST_YAW', 'WAIST_ROLL', 'WAIST_PITCH',
            'L_SHOULDER_PITCH', 'L_SHOULDER_ROLL', 'L_SHOULDER_YAW', 'L_ELBOW', 'L_WRIST_ROLL', 'L_WRIST_PITCH',
            'L_WRIST_YAW',
            'R_SHOULDER_PITCH', 'R_SHOULDER_ROLL', 'R_SHOULDER_YAW', 'R_ELBOW', 'R_WRIST_ROLL', 'R_WRIST_PITCH',
            'R_WRIST_YAW'
        ]

        # Define the 14 Dex3-1 hand joints (7 per hand)
        # You must cross-reference these exact string names with your g1_29dof_with_hand_rev_1_0.urdf file
        self.hand_joints = [
            'l_thumb_pitch', 'l_thumb_roll', 'l_thumb_yaw', 'l_index_pitch', 'l_index_roll', 'l_middle_pitch',
            'l_middle_roll',
            'r_thumb_pitch', 'r_thumb_roll', 'r_thumb_yaw', 'r_index_pitch', 'r_index_roll', 'r_middle_pitch',
            'r_middle_roll'
        ]

    def lowstate_callback(self, msg):
        joint_state_msg = JointState()
        joint_state_msg.header.stamp = self.get_clock().now().to_msg()
        joint_state_msg.name = self.body_joints + self.hand_joints

        # Extract the 29 position values (q) from LowState and append 14 static zeros for the hands
        body_positions = list(msg.q)[:29]
        hand_positions = [0.0] * 14

        joint_state_msg.position = body_positions + hand_positions
        self.publisher_.publish(joint_state_msg)


def main(args=None):
    rclpy.init(args=args)
    node = G1TelemetryListener()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
