#!/usr/bin/env python3

import math
import os
import yaml

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer

from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry

from ament_index_python.packages import get_package_share_directory
from waypoint_follower.action import Mission


class MissionServer(Node):

    def __init__(self):
        super().__init__("mission_server")

        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0

        self.create_subscription(
            Odometry,
            "/odom",
            self.odom_callback,
            10
        )

        self.cmd_pub = self.create_publisher(
            Twist,
            "/cmd_vel",
            10
        )

        self.server = ActionServer(
            self,
            Mission,
            "follow_mission",
            self.execute_callback
        )

    def odom_callback(self, msg):

        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y

        q = msg.pose.pose.orientation

        self.yaw = math.atan2(
            2 * (q.w * q.z + q.x * q.y),
            1 - 2 * (q.y * q.y + q.z * q.z)
        )

    def stop(self):

        self.cmd_pub.publish(Twist())

    def execute_callback(self, goal_handle):

        mission_file = goal_handle.request.mission_file

        path = os.path.join(
            get_package_share_directory("waypoint_follower"),
            "missions",
            mission_file
        )

        with open(path, "r") as f:
            mission = yaml.safe_load(f)

        waypoints = mission["waypoints"]
        base = mission["base"]

        total_distance = 0.0
        completed = 0

        targets = waypoints.copy()

        if mission["return_to_base"]:
            targets.append(base)

        for i, target in enumerate(targets):

            target_x = target["x"]
            target_y = target["y"]

            while True:

                if goal_handle.is_cancel_requested:

                    self.stop()
                    goal_handle.canceled()

                    result = Mission.Result()
                    result.success = False
                    result.total_distance = total_distance
                    result.waypoints_completed = completed

                    return result

                dx = target_x - self.x
                dy = target_y - self.y

                distance = math.sqrt(dx**2 + dy**2)

                if distance < 0.15:

                    self.stop()

                    if i < len(waypoints):
                        completed += 1

                    break

                desired_yaw = math.atan2(dy, dx)

                error = desired_yaw - self.yaw

                error = math.atan2(
                    math.sin(error),
                    math.cos(error)
                )

                cmd = Twist()

                if abs(error) > 0.15:

                    cmd.angular.z = 1.5 * error

                else:

                    cmd.linear.x = min(
                        0.5,
                        0.5 * distance
                    )

                    cmd.angular.z = 1.0 * error

                self.cmd_pub.publish(cmd)

                feedback = Mission.Feedback()

                feedback.current_waypoint_index = i
                feedback.status = (
                    f"en route to waypoint {i + 1}/{len(waypoints)}"
                    if i < len(waypoints)
                    else "returning to base"
                )
                feedback.distance_to_target = distance

                goal_handle.publish_feedback(feedback)

                rclpy.spin_once(
                    self,
                    timeout_sec=0.05
                )

        self.stop()

        goal_handle.succeed()

        result = Mission.Result()
        result.success = True
        result.total_distance = total_distance
        result.waypoints_completed = completed

        return result


def main():

    rclpy.init()

    node = MissionServer()

    rclpy.spin(node)

    rclpy.shutdown()


if __name__ == "__main__":
    main()