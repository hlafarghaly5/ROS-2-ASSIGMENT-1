import rclpy

from rclpy.node import Node
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor

from std_srvs.srv import Empty
from turtlesim.srv import SetPen, TeleportAbsolute


class ResetServiceServer(Node):

    def __init__(self):
        super().__init__('reset_service_server')

        self.callback_group = ReentrantCallbackGroup()

        self.clear_client = self.create_client(
            Empty, '/clear',
            callback_group=self.callback_group
        )

        self.pen_client = self.create_client(
            SetPen, '/turtle1/set_pen',
            callback_group=self.callback_group
        )

        self.teleport_client = self.create_client(
            TeleportAbsolute, '/turtle1/teleport_absolute',
            callback_group=self.callback_group
        )

        self.create_service(
            Empty,
            '/reset_turtle',
            self.reset_callback,
            callback_group=self.callback_group
        )

        self.get_logger().info('Reset service ready: /reset_turtle')

    def reset_callback(self, request, response):
        self.get_logger().info('Reset request received.')

        if not self.pen_client.service_is_ready():
            self.get_logger().error('/turtle1/set_pen is unavailable.')
            return response

        pen_request = SetPen.Request()
        pen_request.r = 255
        pen_request.g = 255
        pen_request.b = 255
        pen_request.width = 2
        pen_request.off = 1

        future = self.pen_client.call_async(pen_request)
        future.add_done_callback(
            lambda result: self.on_pen_disabled(result, response)
        )

        return response

    def on_pen_disabled(self, future, response):
        try:
            future.result()
        except Exception as error:
            self.get_logger().error(f'Could not disable pen: {error}')
            return

        self.get_logger().info('Pen disabled; clearing drawing.')

        if not self.clear_client.service_is_ready():
            self.get_logger().error('/clear is unavailable.')
            return

        future = self.clear_client.call_async(Empty.Request())
        future.add_done_callback(
            lambda result: self.on_drawing_cleared(result, response)
        )

    def on_drawing_cleared(self, future, response):
        try:
            future.result()
        except Exception as error:
            self.get_logger().error(f'Could not clear drawing: {error}')
            return

        self.get_logger().info('Drawing cleared; moving turtle to center.')

        if not self.teleport_client.service_is_ready():
            self.get_logger().error(
                '/turtle1/teleport_absolute is unavailable.'
            )
            return

        teleport_request = TeleportAbsolute.Request()
        teleport_request.x = 5.544
        teleport_request.y = 5.544
        teleport_request.theta = 0.0

        future = self.teleport_client.call_async(teleport_request)
        future.add_done_callback(
            lambda result: self.on_turtle_teleported(result, response)
        )

    def on_turtle_teleported(self, future, response):
        try:
            future.result()
        except Exception as error:
            self.get_logger().error(f'Could not teleport turtle: {error}')
            return

        self.get_logger().info('Turtle moved to center; enabling pen.')

        pen_request = SetPen.Request()
        pen_request.r = 255
        pen_request.g = 255
        pen_request.b = 255
        pen_request.width = 2
        pen_request.off = 0

        future = self.pen_client.call_async(pen_request)
        future.add_done_callback(self.on_pen_enabled)

    def on_pen_enabled(self, future):
        try:
            future.result()
            self.get_logger().info('Turtle reset completed successfully.')
        except Exception as error:
            self.get_logger().error(f'Could not enable pen: {error}')


def main(args=None):
    rclpy.init(args=args)

    node = ResetServiceServer()
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
