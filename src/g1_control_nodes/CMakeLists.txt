cmake_minimum_required(VERSION 3.5)
project(g1_control_nodes)

# Default to C++17 standard for modern ROS 2 Humble packages
if(NOT CMAKE_CXX_STANDARD)
    set(CMAKE_CXX_STANDARD 17)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)

# Build the node implementation as a library so tests can link against it
add_library(g1_control_node_lib STATIC src/g1_control_node.cpp)
target_link_libraries(g1_control_node_lib rclcpp::rclcpp)
target_include_directories(g1_control_node_lib PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>)

# Define the executable and link it against the library
add_executable(g1_control_node src/main.cpp)
target_link_libraries(g1_control_node g1_control_node_lib)

# Install executable to a standard ROS 2 lib directory
install(TARGETS
        g1_control_node
        DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_cmake_gtest REQUIRED)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()

  ament_add_gtest(test_g1_control_node test/test_g1_control_node.cpp)
  target_link_libraries(test_g1_control_node g1_control_node_lib)
  target_include_directories(test_g1_control_node PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>)
endif()

ament_package()