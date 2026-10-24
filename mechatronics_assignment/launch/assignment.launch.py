from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    max_linear_speed = LaunchConfiguration('max_linear_speed')
    max_angular_speed = LaunchConfiguration('max_angular_speed')

    return LaunchDescription([
        DeclareLaunchArgument(
            'max_linear_speed',
            default_value='2.0',
            description='Maximum linear speed of the turtle'
        ),
        DeclareLaunchArgument(
            'max_angular_speed',
            default_value='2.0',
            description='Maximum angular speed of the turtle'
        ),

        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='turtlesim',
            output='screen'
        ),
        Node(
            package='mechatronics_assignment',
            executable='go_to_pose_server',
            parameters=[{
                'max_linear_speed': max_linear_speed,
                'max_angular_speed': max_angular_speed
            }],
            output='screen'
        ),
        Node(
            package='mechatronics_assignment',
            executable='reset_service_server',
            output='screen'
        ),
        Node(
            package='mechatronics_assignment',
            executable='change_speed_server',
            output='screen'
        ),
        Node(
            package='mechatronics_assignment',
            executable='square_action_server',
            output='screen'
        ),
    ])
