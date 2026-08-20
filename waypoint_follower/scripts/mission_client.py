#!/usr/bin/env python3

import rclpy

from rclpy.node import Node
from rclpy.action import ActionClient

from waypoint_follower.action import Mission


class MissionClient(Node):

    def __init__(self):

        super().__init__("mission_client")

        self.client = ActionClient(
            self,
            Mission,
            "follow_mission"
        )

        self.goal_handle = None

        self.declare_parameter(
            "mission_file",
            "mission_square.yaml"
        )

    def send_goal(self):

        mission_file = self.get_parameter(
            "mission_file"
        ).value

        self.client.wait_for_server()

        goal = Mission.Goal()
        goal.mission_file = mission_file

        future = self.client.send_goal_async(
            goal,
            feedback_callback=self.feedback_callback
        )

        future.add_done_callback(
            self.goal_callback
        )

    def goal_callback(self, future):

        self.goal_handle = future.result()

        if not self.goal_handle.accepted:

            self.get_logger().info(
                "Goal rejected"
            )

            rclpy.shutdown()
            return

        self.get_logger().info(
            "Goal accepted"
        )

        future = self.goal_handle.get_result_async()

        future.add_done_callback(
            self.result_callback
        )

    def feedback_callback(self, msg):

        feedback = msg.feedback

        self.get_logger().info(
            f"{feedback.status} | "
            f"{feedback.distance_to_target:.2f} m"
        )

    def result_callback(self, future):

        result = future.result().result

        self.get_logger().info(
            f"Success: {result.success}"
        )

        self.get_logger().info(
            f"Total distance: {result.total_distance}"
        )

        self.get_logger().info(
            f"Waypoints completed: "
            f"{result.waypoints_completed}"
        )

        rclpy.shutdown()

    def cancel(self):

        if self.goal_handle:

            self.goal_handle.cancel_goal_async()


def main():

    rclpy.init()

    node = MissionClient()

    node.send_goal()

    try:

        rclpy.spin(node)

    except KeyboardInterrupt:

        node.cancel()

        rclpy.spin_once(
            node,
            timeout_sec=1.0
        )

    rclpy.shutdown()


if __name__ == "__main__":
    main()