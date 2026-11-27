"""Launch file for G1 telemetry, Mid-360 LiDAR, and RViz2 visualisation."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    """Generate the G1 visualisation launch description."""
    # Locate the synthesized URDF package from the underlay workspace
    g1_description_pkg = get_package_share_directory("g1_description")
    urdf_file = os.path.join(g1_description_pkg, "g1_29dof_with_hand_rev_1_0.urdf")

    # Read the URDF physical constraints for the robot_state_publisher
    with open(urdf_file, "r") as infp:
        robot_description_content = infp.read()

    # Fix broken relative mesh paths in the Unitree URDF
    robot_description_content = robot_description_content.replace(
        'filename="meshes/', 'filename="package://g1_description/meshes/'
    )

    robot_description = {"robot_description": robot_description_content}

    # Prefer the workspace Mid-360 config, falling back to the underlay install
    workspace_livox_config = "/workspace/config/MID360_config.json"
    if os.path.isfile(workspace_livox_config):
        livox_config = workspace_livox_config
    else:
        livox_config = os.path.join(
            get_package_share_directory("livox_ros_driver2"),
            "config",
            "MID360_config.json",
        )

    enable_livox_arg = DeclareLaunchArgument(
        "enable_livox",
        default_value="true",
        description="Launch livox_ros_driver2 for the Mid-360 LiDAR",
    )

    # Locate the RViz config shipped with this package
    cognitive_pkg = get_package_share_directory("g1_cognitive_nodes")
    rviz_config = os.path.join(cognitive_pkg, "config", "g1_default.rviz")

    livox_driver_node = Node(
        package="livox_ros_driver2",
        executable="livox_ros_driver2_node",
        name="livox_lidar_publisher",
        output="screen",
        condition=IfCondition(LaunchConfiguration("enable_livox")),
        parameters=[
            {"xfer_format": 0},
            {"multi_topic": 0},
            {"data_src": 0},
            {"publish_freq": 10.0},
            {"output_data_type": 0},
            {"frame_id": "mid360_link"},
            {"user_config_path": livox_config},
        ],
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", rviz_config],
    )

    return LaunchDescription([
        enable_livox_arg,
        # Launch the standard robot_state_publisher to compute the TF tree
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            output="screen",
            parameters=[robot_description, {"use_sim_time": False}],
        ),
        # Launch your custom cognitive telemetry bridge
        Node(
            package="g1_cognitive_nodes",
            executable="g1_telemetry_listener",
            name="g1_telemetry_listener",
            output="screen",
            parameters=[{"use_sim_time": False}],
        ),
        livox_driver_node,
        # Delay RViz2 to ensure robot_state_publisher is fully up and has
        # published /robot_description and /tf_static before RViz connects.
        TimerAction(
            period=3.0,
            actions=[rviz_node],
        ),
    ])
