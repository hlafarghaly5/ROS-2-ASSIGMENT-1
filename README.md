# ROS-2-ASSIGMENT-1
ROS 2 mechatronics assignment using Turtlesim, custom interfaces, actions, services, and launch files
# ROS 2 Mechatronics Assignment

## 1. Team Members

| Name | University ID |
|---|---|
| [Team member 1] | [University ID] |
| [Team member 2] | [University ID] |
| [Add other members] | [University ID] |

## 2. Project Overview

This project implements a ROS 2 system using Turtlesim. It includes a custom target-pose message, two action servers, two services, configurable motion-speed parameters, and a launch file.

The system can move the turtle to a specified pose, reset its position and drawing, draw a square, and change its maximum linear and angular speeds at runtime.

## 3. Package Descriptions

### `mechatronics_interfaces`

Defines the custom ROS 2 interfaces:

- `TargetPose.msg`: Contains the target `x`, `y`, and `yaw`.
- `GoToPose.action`: Defines the target-pose movement action, its result, and feedback.
- `Square.action`: Defines the square-drawing action.
- `ChangeSpeed.srv`: Updates the maximum linear and angular speeds.

### `mechatronics_assignment`

Contains the Python nodes:

- `go_to_pose_server.py`: Moves the turtle to a requested pose.
- `reset_service_server.py`: Clears the drawing and returns the turtle to the center.
- `change_speed_server.py`: Changes the motion-speed parameters at runtime.
- `square_action_server.py`: Coordinates the reset service and four GoToPose goals to draw a square.

The package also contains the launch file `assignment.launch.py`.

## 4. Prerequisites

- Ubuntu 24.04
- ROS 2 Jazzy
- Python 3
- Turtlesim
- Colcon build tools

## 5. Build Instructions

Clone this repository into the `src` directory of a ROS 2 workspace, then build the packages.

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
git clone <YOUR_REPOSITORY_URL>
cd ~/ros2_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
```

Replace `<YOUR_REPOSITORY_URL>` with the URL of this repository.

## 6. Run the System

Launch Turtlesim and all four servers:

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 launch mechatronics_assignment assignment.launch.py
```

To configure the initial speed limits:

```bash
ros2 launch mechatronics_assignment assignment.launch.py max_linear_speed:=1.0 max_angular_speed:=1.0
```

## 7. Test Commands

### R1 — Run Turtlesim

The launch file starts Turtlesim and the required server nodes.

### R2 — Custom Message

Inspect the custom message definition:

```bash
ros2 interface show mechatronics_interfaces/msg/TargetPose
```

### R3 — GoToPose Action

```bash
ros2 action send_goal /goToPose mechatronics_interfaces/action/GoToPose "{target_pose: {x: 8.0, y: 8.0, yaw: 1.57}}" --feedback
```

### R4 — Reset Service

```bash
ros2 service call /reset_turtle std_srvs/srv/Empty "{}"
```

### R5 — Square Action

```bash
ros2 action send_goal /draw_square mechatronics_interfaces/action/Square "{start: true}" --feedback
```

### R6 — Launch File

```bash
ros2 launch mechatronics_assignment assignment.launch.py
```

### R7 — Parameters and Runtime Speed Changes

Inspect the parameters:

```bash
ros2 param get /go_to_pose_server max_linear_speed
ros2 param get /go_to_pose_server max_angular_speed
```

Change the speeds while the system is running:

```bash
ros2 service call /change_speed mechatronics_interfaces/srv/ChangeSpeed "{max_linear_speed: 1.0, max_angular_speed: 1.0}"
```

### R8 — Package Structure

Inspect the packages:

```bash
ros2 pkg list | grep mechatronics
```

## 8. Design Pattern Bonus

The square action server coordinates a higher-level task by calling the reset service and then sending four goals to the GoToPose action server. This can be described as a coordinator or orchestrator approach to composing ROS 2 operations.

This section describes the coordination structure; it should not be presented as a formal implementation of a named design pattern unless the code supports that claim.

## 9. Rosbag Bonus

A rosbag was recorded during testing using the turtle's pose and velocity topics.

Topics recorded:

- `/turtle1/pose`
- `/turtle1/cmd_vel`

Record a test run:

```bash
ros2 bag record -o square_test --topics /turtle1/pose /turtle1/cmd_vel
```

Inspect the recorded bag:

```bash
ros2 bag info square_test
```

Play it back:

```bash
ros2 bag play square_test
```

The recorded bag was tested, and playback produced turtle movement. The recorded bag and its metadata should be retained with the submission if required by the instructor.

## 10. Testing Summary

The following functionality was tested:

- Turtlesim launched successfully.
- GoToPose reached requested target poses.
- The reset service cleared the drawing and returned the turtle to the center.
- The square action completed four sides.
- The speed-change service updated the speed parameters successfully.
- The launch file started Turtlesim and the four server nodes.
- Rosbag recording and playback produced turtle movement.
