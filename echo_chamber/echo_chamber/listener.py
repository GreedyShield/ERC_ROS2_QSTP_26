import rclpy

from rclpy.node import Node

from std_msgs.msg import Float32


class Listener(Node):

    def __init__(self):

        super().__init__("listener")

        self.subscription = self.create_subscription(
            Float32,
            "/random_number",
            self.callback,
            10
        )

    def callback(self, msg):

        doubled = msg.data * 2

        self.get_logger().info(
            f"Received: {msg.data:.2f}. Multiplied value: {doubled:.2f}"
        )


def main(args=None):

    rclpy.init(args=args)

    node = Listener()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()