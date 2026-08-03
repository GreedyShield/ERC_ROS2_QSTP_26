 Week 1: Sensing, Moving and State Control
 
Welcome to Week 1! Last week, you built a simple Publisher and Subscriber. This week, we are taking our code into **Gazebo**, a powerful 3D physics simulator, and introducing a new architectural concept: **Services**.
 
While Topics handle continuous streams of data (like LiDAR scans), Services act as the "command structure" of your robot, allowing you to trigger specific behaviors and receive confirmation. You will build a node that drives a TurtleBot3 in a spiral and avoids obstacles—but it will only do so when commanded by your custom Service Server.
 
## Workspace Directory Structure
 
Your `~/qstp_ws/src/` directory should be organized as follows by the end of this assignment:
 
```
src
├── echo_chamber
├── obstacle_avoider
├── turtlebot3
├── turtlebot3_gz_sim
└── turtlebot3_simulations
```
 
## 1. Gazebo & TurtleBot3 Setup
 
Please follow the [official documentation](https://gazebosim.org/docs/fortress/install_ubuntu/) to install Gazebo Fortress.
 
We will use a customized TurtleBot3 environment for our testing. Instead of installing the standard ROS packages, you will use the provided source code:
 
1. Download the provided `src.zip` file containing the `turtlebot3`, `turtlebot3_gz_sim`, and `turtlebot3_simulations` packages.
2. Extract the contents directly into your workspace's source directory: `~/qstp_ws/src/`
3. Build the workspace and source the overlay:
```bash
cd ~/qstp_ws
colcon build --symlink-install
source install/setup.bash
```
 
To tell ROS 2 which version of the TurtleBot we are using, add this export command to your `~/.bashrc` file and source it:
 
```bash
echo "export TURTLEBOT3_MODEL=burger" >> ~/.bashrc
source ~/.bashrc
```
 
**Test the Simulator:**
 
Run the following command. Gazebo should open with a 3D environment containing a two-wheeled robot surrounded by boxed obstacles:
 
```bash
ros2 launch turtlebot3_gz_sim bringup.launch.py world:=obstacle.sdf
```
 
## 2. Core Concepts: ROS2 Services
 
While Topics are used for continuous streams of data (like motor speeds or LiDAR scans), Services are used for quick, one-time actions that require a confirmation. A Client sends a Request, the Server executes the logic and sends back a Response. Think of it like a remote function call.
 
In this assignment, you will use a standard service to act as a synchronous ON/OFF switch for your robot's "brain".
 
### ROS2 Topics that you will deal with this week
 
- `geometry_msgs/msg/Twist`: The standard message used to move robots. It contains linear (x, y, z) and angular (x, y, z) velocities. For a two-wheeled robot, you only use `linear.x` (forward/backward) and `angular.z` (turning left/right).
- `sensor_msgs/msg/LaserScan`: The message published by the LiDAR. It contains an array called `ranges`, which holds the distance to obstacles in meters for every degree around the robot (0 to 359).
  - `ranges[0]` is directly in front of the robot.
  - `ranges[90]` is to the left.
  - `ranges[270]` is to the right.
## 3. The ROS 2 CLI Cheat Sheet: Part 2
 
While your simulation is running, open a new terminal and try these:
 
- `ros2 topic echo /scan` - Watch the massive array of LiDAR data stream in.
- `ros2 topic info /scan` - Find out the exact message type of the LiDAR.
- `ros2 interface show geometry_msgs/msg/Twist` - Look at the structure of a Twist message.
- `ros2 service list` - See the active services (synchronous request/response functions).
## 4. Assignment: "Obstacle Avoider"
 
**Objective:** Write a Python node that subscribes to the TurtleBot's LiDAR, processes the distances, and publishes velocity commands to make the robot drive in a spiral until an obstacle is detected, at which point it flanks the obstacle and then continues to move in a spiral trajectory.
 
### Step 1: Create the Package
 
Navigate to your `src` directory and create a new Python package.
 
```bash
cd ~/qstp_ws/src
ros2 pkg create --build-type ament_python obstacle_avoider --dependencies rclpy geometry_msgs sensor_msgs std_srvs
```
 
### Step 2: The Avoider Node (`avoider.py`)
 
Create a Python script inside your package that does the following:
 
**State Management (OOP):**
 
- In your `__init__`, create a variable `self.is_active`. This is your robot's "brain state" which determines if the robot is ON or OFF.
**The Subscriptions & Publishers:**
 
- Create a Publisher to the `/cmd_vel` topic (Type: `Twist`).
- Create a Subscriber to the `/scan` topic (Type: `LaserScan`).
**The Service Server (The Switch):**
 
- Create a Service Server using the built-in `std_srvs/srv/SetBool` interface. Name the service `/toggle_robot`.
- By default, the robot's state should be "OFF" (not moving). When this service is called with `data: true`, the robot turns on.
**The Logic (Inside the LiDAR Callback):**
 
- If the robot is "OFF", publish `0.0` to all velocities.
- If the robot is "ON", read the front sector of the `ranges` array from `/scan` topic.
  - **Clear Path:** If no obstacle is closer than 0.7 meters, drive in a spiral. (Hint: To make a spiral, keep `linear.x` constant and slowly decrease `angular.z` over time, or keep `angular.z` constant and slowly increase `linear.x`. Can you guess why?)
  - **Obstacle Detected:** If an obstacle is closer than 1 meter in front, compare the distance at index 90 (left) and index 270 (right). If left is more open, set a positive `angular.z` (turn left). If right is more open, set a negative `angular.z` (turn right).
### Step 3: Update Configuration Files
 
- Update `setup.py` to include the entry point for your `avoider` executable.
- Update `package.xml` with your details.
### Step 4: Build and Test
 
Run `colcon build` in your workspace (`cd ~/qstp_ws`).
 
**Terminal 1:** Launch the Gazebo world:
 
```bash
ros2 launch turtlebot3_gz_sim bringup.launch.py world:=obstacle.sdf
```
 
**Terminal 2:** Run your node:
 
```bash
ros2 run obstacle_avoider avoider
```
 
**Terminal 3:** Call your service to wake the robot up!
 
```bash
ros2 service call /toggle_robot std_srvs/srv/SetBool "{data: true}"
```
 
## Submission Instructions
 
Stage, commit, and push your Week 1 package (`obstacle_avoider`) to your `ERC_ROS2_QSTP_26` GitHub repository.
 
```bash
cd ~/qstp_ws/src
git add obstacle_avoider/
git commit -m "complete Week 1 Obstacle Avoider assignment"
git push origin main
```
 
In the classroom, submit:
 
1. Your GitHub Repository link.
2. A screen recording showing the robot starting via the terminal service call, spiraling, successfully flanking at least one obstacle in Gazebo, and then turned off using the service call.
 
