#include "rclcpp/rclcpp.hpp"

class G1ControlNode : public rclcpp::Node {
public:
    G1ControlNode() : Node("g1_control_node") {
        RCLCPP_INFO(this->get_logger(), "Unitree G1 control node initialized successfully!");
    }
};

int main(int argc, char **argv) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<G1ControlNode>();
    RCLCPP_INFO(node->get_logger(), "Hello G1! ROS 2 Humble node is running inside CLion.");
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}