#include "g1_control_nodes/g1_control_node.hpp"

G1ControlNode::G1ControlNode() : Node("g1_control_node") {
    RCLCPP_INFO(this->get_logger(), "Unitree G1 control node initialized successfully!");
}