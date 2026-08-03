import rclpy

from rclpy.action import ActionClient

from geometry_msgs.msg import PoseStamped

from action_msgs.msg import GoalStatus

from rclpy.duration import Duration

from rclpy.node import Node

from geometry_msgs.msg import Twist

from sensor_msgs.msg import LaserScan

from std_srvs.srv import SetBool

import threading

from threading import Timer

import time


class Avoider_Node(Node):
    def __init__(self):
        super().__init__("MyNode")
        self.get_logger().info("I am LIVE !")

        self.is_active = False
        self.LastPrint = 0.0
        self.LastAnglePrint = 0.0
        self.Angular_z = 0.5
        self.Default_Linear_Speed = 0.4
        self.AngleSubtract = 0.002
        self.DefaultFlankingAngular = 0.5
        self.Flanking = False
        self.linear_x = self.Default_Linear_Speed
        self.Flanking_Ended = False

        self.CmdVel_Publisher = self.create_publisher(Twist,"cmd_vel",10)
        self.create_timer(0.1,self.timer_callback)

        self.CmdVel_Sub = self.create_subscription(
            Twist, "cmd_vel",self.cmd_vel_callback,10)

        self.scan_sub = self.create_subscription(
                    LaserScan,
                    '/scan',
                    self.scan_callback,
                    10
                )


        self.toggle_service = self.create_service(SetBool,"/toggle_robot",self.Toggle_Robot_Callback)

    def Toggle_Robot_Callback(self,request,response): #Method of Class therefore outside constructor
                self.is_active =   request.data
                response.success = True
                response.message = "Robot State Updated to " + str(request.data) + " !"
    
                return response
    
    def timer_callback(self): #Method of Class therefore outside constructor
                        msg =  Twist()
                        if (self.is_active == False):
                            msg.linear.x = 0.0
                            msg.angular.z = 0.0
                        else:
                            msg.linear.x = self.linear_x
                            msg.angular.z = max(0.05,self.Angular_z - self.AngleSubtract)
                            if (self.Angular_z == (-self.DefaultFlankingAngular)):
                                 msg.angular.z = -self.DefaultFlankingAngular
                            self.Angular_z = msg.angular.z
            
                        self.CmdVel_Publisher.publish(msg)
    

    def cmd_vel_callback(self, msg):   
        now = time.time()
        if (now - self.LastPrint) > 1.0 :
            self.LastPrint = now
            self.get_logger().info(f'\nLinear= {msg.linear.x}, \t Angular= {msg.angular.z}')
                        

    def StartSpiral(self):
        self.get_logger().warn("I continue spiral !")
        self.AngleSubtract = 0.002

        if self.Flanking_Ended:
            self.Flanking = False
            self.linear_x = self.Default_Linear_Speed
            self.Angular_z = 0.5
            self.Flanking_Ended = False   

    def scan_callback(self, msg):
        if (self.is_active == True):
            count = 0
            Radar = []
            Min_Dist = 1.2 #1.2m
            Min_Dist_Angle = 0
            while True :
                Distance = msg.ranges[count]
                if Distance == float("inf") or Distance == float("-inf"):
                    Distance = 1000.0
                    msg.ranges[count] = Distance

                Radar.append(Distance)

                if (Distance < Min_Dist):
                    Min_Dist = Distance
                    Min_Dist_Angle = count

                if (count >= 358):
                    count = 0
                    break

                count += 1

            if (Min_Dist <= 0.7):
                if (msg.ranges[90] != msg.ranges[270]) and (msg.ranges[45] != msg.ranges[315]):
                    if (not self.Flanking):
                        #Flank
                        self.Flanking = True
                        #check safe direction
                        if (msg.ranges[90] > msg.ranges[270]) or (msg.ranges[45] > msg.ranges[315]):
                            self.Angular_z = self.DefaultFlankingAngular
                            self.AngleSubtract = 0.0
                            self.linear_x = self.Default_Linear_Speed * 3
                            self.get_logger().info(f"I FLANK LEFT ! coz {msg.ranges[90]} > {msg.ranges[270]}")
                        else:
                            self.Angular_z = -self.DefaultFlankingAngular
                            self.AngleSubtract = 0.0
                            self.linear_x = self.Default_Linear_Speed * 3
                            self.get_logger().info(f"I FLANK RIGHT ! {msg.ranges[90]} < {msg.ranges[270]}")

                        self.Flanking_Ended = True
                    else:
                        self.get_logger().warn("I ALREADY FLANKING !")
                    if (time.time() - self.LastAnglePrint) >= 0.75 :
                        self.LastAnglePrint = time.time()
                        self.get_logger().warn(f"I SEE SOMETHING AT angle {Min_Dist_Angle} --- {Min_Dist} meters AHEAD !!")
                else:
                    if (not self.Flanking):
                        self.Flanking = True
                        self.Angular_z = self.DefaultFlankingAngular
                        self.AngleSubtract = 0.0
                        self.linear_x = -self.Default_Linear_Speed*2
                        self.get_logger().info(f"I FLANK RIGHT ! coz obstacle Right Infront")
                        self.Flanking_Ended = True

            else:
                  #Continue Spiral Motion
                self.get_logger().warn("I continue spiral !")
                self.AngleSubtract = 0.002
                if self.Flanking_Ended:
                    self.Flanking = False
                    self.linear_x = self.Default_Linear_Speed
                    self.Angular_z = 0.5
                    self.Flanking_Ended = False

                
        else:
            My_Twist = Twist()
            My_Twist.linear.x = 0.0
            My_Twist.angular.z = 0.0
            self.CmdVel_Publisher.publish(My_Twist)
            return

def main(args=None):

    rclpy.init(args=args)

    node = Avoider_Node()

    rclpy.spin(node)

    rclpy.shutdown()


if __name__ == "__main__":
    main()
