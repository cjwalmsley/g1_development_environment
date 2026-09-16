cmake_minimum_required(VERSION 3.5)
project(g1_control_nodes)

# Default to C++17 standard for modern ROS 2 Humble packages
if(NOT CMAKE_CXX_STANDARD)
    set(CMAKE_CXX_STANDARD 17)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)

# Define our executable and link it to the core ROS 2 client library
add_executable(g1_control_node src/g1_control_node.cpp)
target_link_libraries(g1_control_node rclcpp::rclcpp)

# Install executable to a standard ROS 2 lib directory
install(TARGETS
        g1_control_node
        DESTINATION lib/${PROJECT_NAME}
)

ament_package()