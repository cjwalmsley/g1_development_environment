#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

# Import Unitree custom messages if compiled in your workspace,
# or standard ROS 2 telemetry classes. Here we'll read Unitree's SportModeState
try:
    from unitree_go.msg import SportModeState
except ImportError:
    # Fallback to general ROS 2 messages if G1 messages aren't built yet
    from nav_msgs.msg import Odometry as SportModeState


class G1TelemetryListener(Node):
    def __init__(self):
        super().__init__('g1_telemetry_listener')

        # Subscribe to G1's high-level locomotion state topic
        # (Using QoS profile depth 10 for standard telemetry)
        self.subscription = self.create_subscription(
            SportModeState,
            '/sportmodestate',
            self.telemetry_callback,
            10
        )
        self.get_logger().info('G1 Telemetry Listener initialized. Waiting for robot state packets...')

    def telemetry_callback(self, msg):
        # Read G1's real-time position & velocities published over DDS
        try:
            # Unitree-specific message layout
            pos = msg.position
            vel = msg.velocity
            self.get_logger().info(
                f"Position -> x: {pos:.3f}, y: {pos[14]:.3f}, z: {pos[15]:.3f} | "
                f"Velocity -> vx: {vel:.3f}, vy: {vel[14]:.3f}"
            )
        except AttributeError:
            # Fallback parsing if using standard Odometry
            pos = msg.pose.pose.position
            vel = msg.twist.twist.linear
            self.get_logger().info(
                f"Odom Position -> x: {pos.x:.3f}, y: {pos.y:.3f}, z: {pos.z:.3f} | "
                f"Odom Velocity -> vx: {vel.x:.3f}"
            )


def main(args=None):
    rclpy.init(args=args)
    node = G1TelemetryListener()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down telemetry listener...')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()