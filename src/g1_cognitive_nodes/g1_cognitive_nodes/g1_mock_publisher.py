import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from unitree_hg.msg import LowState, MotorState, HandState
import math

class MockPublisher(Node):
    def __init__(self):
        super().__init__('g1_mock_publisher')
        self.pub = self.create_publisher(LowState, '/lowstate', qos_profile_sensor_data)
        # Use Reliable QoS (10) to match the real robot
        self.left_hand_pub = self.create_publisher(HandState, '/lf/dex3/left/state', 10)
        self.right_hand_pub = self.create_publisher(HandState, '/lf/dex3/right/state', 10)
        self.timer = self.create_timer(0.1, self.timer_callback)
        self.t = 0.0

    def timer_callback(self):
        self.t += 0.1
        
        msg = LowState()
        for i in range(35):
            m = MotorState()
            m.q = 0.1
            msg.motor_state[i] = m
        self.pub.publish(msg)

        # Mock hand states with a slight sine wave to verify movement in RViz
        hand_msg_l = HandState()
        hand_msg_r = HandState()
        for i in range(7):
            m_l = MotorState()
            m_l.q = 0.1 + 0.1 * math.sin(self.t)
            hand_msg_l.motor_state.append(m_l)
            
            m_r = MotorState()
            m_r.q = 0.1 + 0.1 * math.cos(self.t)
            hand_msg_r.motor_state.append(m_r)
            
        self.left_hand_pub.publish(hand_msg_l)
        self.right_hand_pub.publish(hand_msg_r)

def main():
    rclpy.init()
    node = MockPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
