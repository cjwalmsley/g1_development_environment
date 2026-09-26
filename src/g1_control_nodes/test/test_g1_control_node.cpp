#include <gtest/gtest.h>

#include "g1_control_nodes/g1_control_node.hpp"
#include "rclcpp/rclcpp.hpp"

class G1ControlNodeTest : public ::testing::Test {
protected:
    static void SetUpTestSuite() {
        if (!rclcpp::ok()) {
            rclcpp::init(0, nullptr);
        }
    }

    static void TearDownTestSuite() {
        if (rclcpp::ok()) {
            rclcpp::shutdown();
        }
    }
};

TEST_F(G1ControlNodeTest, TestNodeCreation) {
    ASSERT_NO_THROW({
        auto node = std::make_shared<G1ControlNode>();
    });
}

TEST_F(G1ControlNodeTest, TestNodeName) {
    auto node = std::make_shared<G1ControlNode>();
    EXPECT_EQ(std::string(node->get_name()), "g1_control_node");
}

TEST_F(G1ControlNodeTest, TestLoggerExists) {
    auto node = std::make_shared<G1ControlNode>();
    auto logger = node->get_logger();
    // Logger name follows the node name
    EXPECT_EQ(std::string(logger.get_name()), "g1_control_node");
}

TEST_F(G1ControlNodeTest, TestNodeIsRclcppNode) {
    auto node = std::make_shared<G1ControlNode>();
    // Verify it is a valid rclcpp::Node via the base class interface
    rclcpp::Node *base_ptr = node.get();
    ASSERT_NE(base_ptr, nullptr);
    EXPECT_EQ(std::string(base_ptr->get_name()), "g1_control_node");
}
