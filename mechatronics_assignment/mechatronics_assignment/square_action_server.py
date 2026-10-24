import math

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, ActionClient
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor

from std_srvs.srv import Empty

from mechatronics_interfaces.action import GoToPose, Square
from mechatronics_interfaces.msg import TargetPose


class SquareActionServer(Node):

    def __init__(self):
        super().__init__('square_action_server')

        self.callback_group = ReentrantCallbackGroup()

        self.reset_client = self.create_client(
            Empty,
            '/reset_turtle',
            callback_group=self.callback_group
        )

        self.go_to_pose_client = ActionClient(
            self,
            GoToPose,
            '/goToPose',
            callback_group=self.callback_group
        )

        self.square_server = ActionServer(
            self,
            Square,
            '/draw_square',
            execute_callback=self.execute_callback,
            callback_group=self.callback_group
        )

        self.get_logger().info(
            'Square action server ready: /draw_square'
        )

    async def execute_callback(self, goal_handle):

        result = Square.Result()

        if not goal_handle.request.start:
            result.success = False
            result.message = 'Goal rejected: start must be true.'
            goal_handle.abort()
            return result

        self.get_logger().info('Starting square drawing.')

        # Wait for the required servers.
        if not self.reset_client.service_is_ready():
            ready = self.reset_client.wait_for_service(
                timeout_sec=5.0
            )
            if not ready:
                result.success = False
                result.message = 'Reset service unavailable.'
                goal_handle.abort()
                return result

        if not self.go_to_pose_client.server_is_ready():
            ready = self.go_to_pose_client.wait_for_server(
                timeout_sec=5.0
            )
            if not ready:
                result.success = False
                result.message = 'GoToPose action server unavailable.'
                goal_handle.abort()
                return result

        # Reset the turtle before drawing.
        reset_future = self.reset_client.call_async(Empty.Request())

        try:
            await reset_future
        except Exception as error:
            result.success = False
            result.message = f'Reset failed: {error}'
            goal_handle.abort()
            return result

        # Allow the reset service's asynchronous operations to finish.
        

        center = 5.544
        side_length = 2.0

        # Four corners, returning to the starting position.
        corners = [
            (center + side_length, center, 0.0),
            (center + side_length, center + side_length, math.pi / 2),
            (center, center + side_length, math.pi),
            (center, center, -math.pi / 2),
        ]

        for index, (x, y, yaw) in enumerate(corners):

            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                result.success = False
                result.message = 'Square drawing canceled.'
                return result

            target = TargetPose()
            target.x = x
            target.y = y
            target.yaw = yaw

            action_goal = GoToPose.Goal()
            action_goal.target_pose = target

            self.get_logger().info(
                f'Moving to corner {index + 1}: '
                f'x={x:.2f}, y={y:.2f}, yaw={yaw:.2f}'
            )

            send_future = self.go_to_pose_client.send_goal_async(
                action_goal
            )

            try:
                goal_response = await send_future
            except Exception as error:
                result.success = False
                result.message = f'Could not send movement goal: {error}'
                goal_handle.abort()
                return result

            if not goal_response.accepted:
                result.success = False
                result.message = (
                    f'GoToPose rejected corner {index + 1}.'
                )
                goal_handle.abort()
                return result

            movement_result = await goal_response.get_result_async()

            if movement_result.status != 4:
                result.success = False
                result.message = (
                    f'Movement failed at corner {index + 1}.'
                )
                goal_handle.abort()
                return result

            if not movement_result.result.success:
                result.success = False
                result.message = (
                    f'GoToPose failed: '
                    f'{movement_result.result.message}'
                )
                goal_handle.abort()
                return result

            feedback = Square.Feedback()
            feedback.sides_completed = index + 1
            feedback.status = (
                f'Completed {index + 1} of 4 sides.'
            )
            goal_handle.publish_feedback(feedback)

            self.get_logger().info(feedback.status)

        result.success = True
        result.message = 'Square completed successfully.'
        goal_handle.succeed()

        self.get_logger().info(result.message)

        return result


def main(args=None):
    rclpy.init(args=args)

    node = SquareActionServer()
    executor = MultiThreadedExecutor(num_threads=4)
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.remove_node(node)
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
