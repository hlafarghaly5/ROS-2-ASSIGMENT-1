import rclpy

from rclpy.node import Node
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.parameter_client import AsyncParameterClient

from mechatronics_interfaces.srv import ChangeSpeed


class ChangeSpeedServer(Node):

    def __init__(self):
        super().__init__('change_speed_server')

        self.callback_group = ReentrantCallbackGroup()

        self.parameter_client = AsyncParameterClient(
            self,
            '/go_to_pose_server',
            callback_group=self.callback_group
        )

        self.service = self.create_service(
            ChangeSpeed,
            '/change_speed',
            self.change_speed_callback,
            callback_group=self.callback_group
        )

        self.get_logger().info(
            'Change-speed service ready: /change_speed'
        )

    def change_speed_callback(self, request, response):
        # Validate the requested speeds.
        if request.max_linear_speed <= 0.0:
            response.success = False
            response.message = 'Maximum linear speed must be positive.'
            return response

        if request.max_angular_speed <= 0.0:
            response.success = False
            response.message = 'Maximum angular speed must be positive.'
            return response

        # Check whether the action server's parameter services are ready.
        if not self.parameter_client.services_are_ready():
            response.success = False
            response.message = (
                'The go-to-pose action server parameter services '
                'are unavailable.'
            )
            return response

        # Prepare the new parameter values.
        parameters = [
            rclpy.parameter.Parameter(
                'max_linear_speed',
                rclpy.Parameter.Type.DOUBLE,
                request.max_linear_speed
            ),
            rclpy.parameter.Parameter(
                'max_angular_speed',
                rclpy.Parameter.Type.DOUBLE,
                request.max_angular_speed
            ),
        ]

        # Request the parameter update asynchronously.
        future = self.parameter_client.set_parameters(parameters)

        # Wait for the asynchronous request to complete.
        import threading

        event = threading.Event()
        future.add_done_callback(lambda _: event.set())

        if not event.wait(timeout=5.0):
            response.success = False
            response.message = 'Timed out updating speed parameters.'
            return response

        # Retrieve the service response.
        try:
            results = future.result()
        except Exception as error:
            response.success = False
            response.message = f'Parameter update failed: {error}'
            return response

        # Check whether both parameters were updated successfully.
        if not all(result.successful for result in results.results):
            response.success = False
            response.message = (
                'The action server rejected a parameter update.'
            )
            return response

        # Return success to the caller.
        response.success = True
        response.message = (
            f'Speeds updated: linear={request.max_linear_speed}, '
            f'angular={request.max_angular_speed}.'
        )

        self.get_logger().info(response.message)

        return response


def main(args=None):
    rclpy.init(args=args)

    node = ChangeSpeedServer()

    executor = MultiThreadedExecutor(num_threads=3)
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.remove_node(node)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

