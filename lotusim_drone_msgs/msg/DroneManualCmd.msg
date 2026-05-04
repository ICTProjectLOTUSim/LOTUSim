# Manual stick command from UI to manual_control_node.
# All channels are normalized to [-1, 1]; throttle follows PX4 convention
# (-1 = minimum thrust, +1 = full thrust). Published at ~20 Hz on
# /lotusim/ui/drone_manual_cmd.

float32 throttle
float32 roll
float32 pitch
float32 yaw
