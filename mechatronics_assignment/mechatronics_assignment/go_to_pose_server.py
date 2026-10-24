import math

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, GoalResponse, CancelResponse
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup

from geometry_msgs.msg import Twist
from turtlesim.msg import Pose

from mechatronics_interfaces.action import GoToPose


class GoToPoseServer(Node):

    def __init__(self):
        super().__init__('go_to_pose_server')

        # Allow subscription and action callbacks to run concurrently.
        self.callback_group = ReentrantCallbackGroup()

        # Maximum speed parameters.
        self.declare_parameter('max_linear_speed', 2.0)
        self.declare_parameter('max_angular_speed', 2.0)

        self.current_pose = None

        # Subscribe to the turtle's current pose.
        self.pose_subscriber = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10,
            callback_group=self.callback_group
        )

        # Publish velocity commands.
        self.velocity_publisher = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )

        # Create the action server.
        self.action_server = ActionServer(
            self,
            GoToPose,
            'goToPose',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
            callback_group=self.callback_group
        )

        self.get_logger().info('goToPose action server is ready.')

    def pose_callback(self, msg):
        self.current_pose = msg

    def goal_callback(self, goal_request):
        self.get_logger().info('Received a goToPose goal.')
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        self.get_logger().info('Received a cancellation request.')
        return CancelResponse.ACCEPT

    @staticmethod
    def normalize_angle(angle):
        return math.atan2(math.sin(angle), math.cos(angle))

    def publish_velocity(self, linear, angular):
        msg = Twist()
        msg.linear.x = float(linear)
        msg.angular.z = float(angular)
        self.velocity_publisher.publish(msg)

    def execute_callback(self, goal_handle):
        self.get_logger().info('Executing goToPose goal.')

        result = GoToPose.Result()
        feedback = GoToPose.Feedback()
        target = goal_handle.request.target_pose

        position_tolerance = 0.05
        angle_tolerance = 0.05

        try:
            while rclpy.ok():

                if goal_handle.is_cancel_requested:
                    self.publish_velocity(0.0, 0.0)
                    goal_handle.canceled()
                    result.success = False
                    result.message = 'Goal canceled.'
                    return result

                pose = self.current_pose

                if pose is None:
                    self.publish_velocity(0.0, 0.0)
                    rclpy.spin_once(self, timeout_sec=0.05)
                    continue

                dx = target.x - pose.x
                dy = target.y - pose.y

                distance = math.sqrt(dx * dx + dy * dy)
                feedback.distance_remaining = distance

                max_linear = self.get_parameter(
                    'max_linear_speed'
                ).value

                max_angular = self.get_parameter(
                    'max_angular_speed'
                ).value

                # First, move to the target position.
                if distance > position_tolerance:

                    desired_heading = math.atan2(dy, dx)

                    heading_error = self.normalize_angle(
                        desired_heading - pose.theta
                    )

                    feedback.angle_error = heading_error
                    goal_handle.publish_feedback(feedback)

                    if abs(heading_error) > 0.15:
                        linear_velocity = 0.0
                    else:
                        linear_velocity = min(
                            max_linear,
                            1.5 * distance
                        )

                    angular_velocity = max(
                        -max_angular,
                        min(max_angular, 4.0 * heading_error)
                    )

                    self.publish_velocity(
                        linear_velocity,
                        angular_velocity
                    )

                else:
                    # Position reached: align with the requested yaw.
                    yaw_error = self.normalize_angle(
                        target.yaw - pose.theta
                    )

                    feedback.distance_remaining = distance
                    feedback.angle_error = yaw_error
                    goal_handle.publish_feedback(feedback)

                    if abs(yaw_error) <= angle_tolerance:
                        self.publish_velocity(0.0, 0.0)

                        goal_handle.succeed()
                        result.success = True
                        result.message = 'Target pose reached.'

                        self.get_logger().info(
                            'Target pose reached successfully.'
                        )
                        return result

                    angular_velocity = max(
                        -max_angular,
                        min(max_angular, 4.0 * yaw_error)
                    )

                    self.publish_velocity(0.0, angular_velocity)

                # Yield execution so other callbacks can process.
                import time
                time.sleep(0.033)

        finally:
            self.publish_velocity(0.0, 0.0)

        result.success = False
        result.message = 'ROS 2 stopped before reaching the goal.'
        return result


def main(args=None):
    rclpy.init(args=args)

    node = GoToPoseServer()
    executor = MultiThreadedExecutor(num_threads=3)
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.publish_velocity(0.0, 0.0)
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
