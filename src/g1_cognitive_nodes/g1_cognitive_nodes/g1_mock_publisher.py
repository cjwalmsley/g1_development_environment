import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from unitree_hg.msg import LowState, MotorState

class MockPublisher(Node):
    def __init__(self):
        super().__init__('g1_mock_publisher')
        self.pub = self.create_publisher(LowState, '/lowstate', qos_profile_sensor_data)
        self.timer = self.create_timer(0.1, self.timer_callback)

    def timer_callback(self):
        msg = LowState()
        for i in range(35):
            m = MotorState()
            m.q = 0.1
            msg.motor_state[i] = m
        self.pub.publish(msg)

def main():
    rclpy.init()
    node = MockPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
