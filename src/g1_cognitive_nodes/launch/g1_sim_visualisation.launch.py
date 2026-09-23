import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    # Locate the synthesized URDF package from the underlay workspace
    g1_description_pkg = get_package_share_directory('g1_description')
    urdf_file = os.path.join(g1_description_pkg, 'g1_29dof_with_hand_rev_1_0.urdf')

    # Read the URDF physical constraints for the robot_state_publisher
    with open(urdf_file, 'r') as infp:
        robot_description_content = infp.read()

    robot_description = {'robot_description': robot_description_content}

    return LaunchDescription([
        # Launch the standard robot_state_publisher to compute the TF tree
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[robot_description, {'use_sim_time': True}]
        ),
        # Launch your custom cognitive telemetry bridge
        Node(
            package='g1_cognitive_nodes',
            executable='g1_telemetry_listener',
            name='g1_telemetry_listener',
            output='screen',
            parameters=[{'use_sim_time': True}]
        )
    ])