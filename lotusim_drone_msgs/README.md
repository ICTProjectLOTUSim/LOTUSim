# lotusim_drone_msgs

ROS2 interface package for the LOTUSim drone integration. Defines messages that
do not exist in `px4_msgs` or `lotusim_msgs` and that we own end-to-end.

## Messages

| Type | File | Used by | Notes |
|---|---|---|---|
| `DroneManualCmd` | `msg/DroneManualCmd.msg` | UI → `manual_control_node` | `float32 throttle, roll, pitch, yaw`, all `[-1, 1]` |

Topic contract for the integration as a whole lives in
[`../docs/topics.md`](../docs/topics.md).

## Build / verify

```bash
colcon build --merge-install --packages-select lotusim_drone_msgs
source install/setup.bash
ros2 interface show lotusim_drone_msgs/msg/DroneManualCmd
```
