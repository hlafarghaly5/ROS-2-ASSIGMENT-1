# ROS 2 Mechatronics Assignment

## Overview

This project implements a ROS 2 system using Turtlesim. It includes a custom message, two action servers, reset and speed-change services, configurable speed parameters, and a launch file.

## Packages

- `mechatronics_interfaces`: Contains custom messages, actions, and services.
- `mechatronics_assignment`: Contains the Python nodes and launch file.

## Interfaces

### Custom Message
`TargetPose.msg`
- `float64 x`
- `float64 y`
- `float64 yaw`

### Actions
- `GoToPose.action`: Moves the turtle to a target pose and reports feedback and a result.
- `Square.action`: Draws a square using four calls to the GoToPose action server.

### Services
- `/reset_turtle`: Clears the drawing and returns the turtle to the center.
- `/change_speed`: Updates the maximum linear and angular speeds while the system is running.

## Build

Open a terminal and run:

```bash
source /opt/ros/jazzy/setup.bash
cd ~/ros2_ws
colcon build --symlink-install
```

Then source the workspace:

```bash
source ~/ros2_ws/install/setup.bash
export AMENT_PREFIX_PATH="$HOME/ros2_ws/install/mechatronics_assignment:$AMENT_PREFIX_PATH"
```

The export command works around the current workspace package-discovery issue in this environment.

## Launch

```bash
ros2 launch mechatronics_assignment assignment.launch.py
```

To set the initial speed parameters:

```bash
ros2 launch mechatronics_assignment assignment.launch.py max_linear_speed:=1.0 max_angular_speed:=1.0
```

## Test the GoToPose Action

```bash
ros2 action send_goal /goToPose mechatronics_interfaces/action/GoToPose "{target_pose: {x: 8.0, y: 8.0, yaw: 1.57}}" --feedback
```

## Test the Reset Service

```bash
ros2 service call /reset_turtle std_srvs/srv/Empty "{}"
```

## Test the Square Action

```bash
ros2 action send_goal /draw_square mechatronics_interfaces/action/Square "{start: true}" --feedback
```

## Change Speeds at Runtime

```bash
ros2 service call /change_speed mechatronics_interfaces/srv/ChangeSpeed "{max_linear_speed: 1.0, max_angular_speed: 1.0}"
```

## Design Pattern

The square action server coordinates multiple operations: it requests a reset and then sends four goals to the GoToPose action server. This demonstrates a coordinator/orchestrator approach to composing ROS 2 actions and services into a higher-level behavior.

## Testing Results

- The GoToPose action successfully moved the turtle to requested poses.
- The reset service successfully cleared the drawing and reset the turtle's position.
- The square action successfully completed four sides.
- The speed-change service successfully updated the linear and angular speed parameters.
- The launch file successfully started Turtlesim and all four server nodes.
