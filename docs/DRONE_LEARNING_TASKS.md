# Learning Tasks: Gazebo and ROS 2 Through the Drone Control Goal

Every task below teaches you something new AND moves the project closer to
manual drone control. Nothing is abstract busywork. By the end you will
understand Gazebo, ROS 2, and SDF deeply because you built something real
with them.

Prerequisites: Linux terminal, Git basics, and the ability to run
`lotusim build` and `lotusim run` successfully.

---

## Phase 1: Understand What You Already Have

Goal: learn how LOTUSim worlds work by reading the ones that already exist.
No code changes yet, just reading and observing.

### Task 1.1 -- Run the default world and observe

**What to do:**

```bash
lotusim build
lotusim run lotusim.world
```

Look around the Gazebo GUI. Notice:

- What objects are in the scene.
- The entity tree on the left panel.
- The play/pause button and simulation time.

**What you learn:** How Gazebo launches, what the GUI looks like, how the
LOTUSim build/run pipeline works.

**Progress toward goal:** You confirm your development environment works.

### Task 1.2 -- Read the aerial world file line by line

Open `assets/worlds/aerialWorld.world` and answer these questions by reading
the XML:

1. What is the world name?
2. What is the gravity set to? (hint: it is wrong for flight)
3. What physics engine is used and at what step size?
4. What coordinate system is defined?
5. Which plugins are loaded?
6. Is the x500 drone included in this world?

Write your answers down somewhere. You will fix the problems you found in
Phase 2.

**What you learn:** SDF world file structure (`<world>`, `<physics>`,
`<gravity>`, `<spherical_coordinates>`, `<plugin>`).

**Progress toward goal:** You now know exactly what is broken in the aerial
world.

### Task 1.3 -- Read the x500 drone model

Open `assets/models/x500/model.sdf` and answer:

1. How many links does the model have? What are their names?
2. How many joints? What type are they?
3. What sensors are already attached? To which link?
4. What plugins are loaded on the model? What do they do?
5. What is the `commandSubTopic` for the motor models?
6. Which rotors spin clockwise and which counterclockwise?

**What you learn:** SDF model structure (`<model>`, `<link>`, `<joint>`,
`<sensor>`, `<plugin>`, `<inertial>`). You also learn how a quadcopter is
modeled: 1 body + 4 rotors connected by revolute joints.

**Progress toward goal:** You understand the drone you will be controlling.

### Task 1.4 -- Compare with a ship world

Open `assets/worlds/circling_ship_example.world` and compare it with
`aerialWorld.world`. Notice:

- This world includes a model using `<include>` and `<uri>model://...</uri>`.
- This world uses `<lotus_param>` to configure behavior.
- This world loads the waypoint follower plugin.

**What you learn:** How models are included in worlds, how LOTUSim plugins
are configured via SDF.

**Progress toward goal:** You learn the pattern you will use to add the x500
to the aerial world.

---

## Phase 2: Fix the Aerial World for Flight

Goal: make changes to world and model files. Every edit teaches a new SDF
concept.

### Task 2.1 -- Fix gravity

Open `assets/worlds/aerialWorld.world`.

Change:

```xml
<gravity>0 0 0</gravity>
```

To:

```xml
<gravity>0 0 -9.8066</gravity>
```

Run the aerial world and observe that objects now fall.

**What you learn:** The `<gravity>` tag and how it affects all entities in
the world. Gazebo uses ENU (East-North-Up) coordinates, so negative Z is
downward.

**Progress toward goal:** The drone world now has real gravity, which is
required for flight physics.

### Task 2.2 -- Fix physics timing

Still in `aerialWorld.world`, change the physics block:

```xml
<physics type="ode">
  <max_step_size>0.004</max_step_size>
  <real_time_update_rate>250</real_time_update_rate>
  <real_time_factor>1</real_time_factor>
</physics>
```

**What you learn:** `max_step_size` is how many seconds each simulation tick
advances (smaller = more accurate but slower). `real_time_update_rate` is how
many times per second the simulation steps. `real_time_factor` of 1 means the
sim tries to run at real time speed. Flight control needs fast, small steps
because a quadcopter that is updated only 5 times per second will be
unstable.

**Progress toward goal:** The simulation is now fast enough for stable drone
flight.

### Task 2.3 -- Add the x500 drone to the world

Add this inside the `<world>` tag in `aerialWorld.world`:

```xml
<include>
  <uri>model://x500</uri>
  <name>x500_drone</name>
  <pose>0 0 0.5 0 0 0</pose>
</include>
```

Run the world. You should see the drone appear and immediately fall due to
gravity (that is expected, there is no controller yet).

**What you learn:** The `<include>` pattern, `model://` URI resolution
(Gazebo searches paths in `GZ_SIM_RESOURCE_PATH`), and model naming.

**Progress toward goal:** The drone is now in the simulation world.

### Task 2.4 -- Add a ground plane so the drone has somewhere to land

Add a simple ground plane model to the world so the drone does not fall
forever:

```xml
<model name="ground_plane">
  <static>true</static>
  <link name="link">
    <collision name="collision">
      <geometry>
        <plane>
          <normal>0 0 1</normal>
          <size>100 100</size>
        </plane>
      </geometry>
    </collision>
    <visual name="visual">
      <geometry>
        <plane>
          <normal>0 0 1</normal>
          <size>100 100</size>
        </plane>
      </geometry>
      <material>
        <ambient>0.8 0.8 0.8 1</ambient>
        <diffuse>0.8 0.8 0.8 1</diffuse>
      </material>
    </visual>
  </link>
</model>
```

Run the world. The drone should fall and land on the ground.

**What you learn:** Inline model definitions, `<static>` models, the
difference between `<collision>` (physics) and `<visual>` (rendering),
`<material>` for appearance.

**Progress toward goal:** You have a usable test environment.

---

## Phase 3: Learn Gazebo Topics by Inspecting the Drone

Goal: understand how Gazebo communicates internally using transport topics.
This is the bridge between "things exist in the world" and "code can read
and control those things."

### Task 3.1 -- List Gazebo transport topics

With the aerial world running, open a new terminal and run:

```bash
gz topic -l
```

This lists all Gazebo transport topics. Find topics that contain the drone
name or sensor names (imu, air_pressure).

**What you learn:** Gazebo has its own message bus (gz-transport) separate
from ROS 2. Sensors and plugins publish data here.

**Progress toward goal:** You discover the exact topic names you will need
to bridge to ROS 2 later.

### Task 3.2 -- Echo a sensor topic

Pick the IMU topic from the list and echo it:

```bash
gz topic -e -t /world/aerialWorld/model/x500_drone/link/base_link/sensor/imu_sensor/imu
```

(The exact path may differ. Use the output from `gz topic -l` to find it.)

You should see IMU data streaming (angular velocity, linear acceleration).

**What you learn:** How to inspect live simulation data. The IMU outputs
orientation, angular velocity, and linear acceleration, which are the
fundamental measurements a flight controller uses to keep the drone stable.

**Progress toward goal:** You confirm sensors are working and producing
data.

### Task 3.3 -- Try sending a motor command (it will not fly yet)

The x500 motor models listen on a Gazebo topic. Try publishing a motor
speed command:

```bash
gz topic -t /model/x500_drone/command/motor_speed -m gz.msgs.Actuators \
  -p 'velocity: [100, 100, 100, 100]'
```

Observe what happens. The rotors should spin but the drone likely will not
hover stably because these are raw motor speeds with no controller.

**What you learn:** How Gazebo actuator commands work. You see firsthand why
a velocity controller is needed -- raw motor speed commands are unusable for
a human.

**Progress toward goal:** You understand the control gap that needs filling.

---

## Phase 4: Add Missing Sensors to the Drone

Goal: learn SDF sensor definitions by adding real sensors the flight
controller needs.

### Task 4.1 -- Add a magnetometer sensor

Open `assets/models/x500/model.sdf`. Inside the `<link name="base_link">`
block, after the existing sensors, add:

```xml
<sensor name="magnetometer_sensor" type="magnetometer">
  <always_on>true</always_on>
  <update_rate>50</update_rate>
  <visualize>false</visualize>
</sensor>
```

Rebuild and run. Verify the sensor appears with `gz topic -l`.

**What you learn:** How to add sensors to an SDF model. A magnetometer
measures Earth's magnetic field and gives the drone a heading reference
(like a compass).

**Progress toward goal:** PX4 requires a magnetometer for attitude
estimation.

### Task 4.2 -- Add a GPS (NavSat) sensor

Still in the `base_link`, add:

```xml
<sensor name="navsat_sensor" type="navsat">
  <always_on>true</always_on>
  <update_rate>10</update_rate>
</sensor>
```

Note: the `<spherical_coordinates>` block in the world file defines the
reference point for GPS. The one in `aerialWorld.world` is already set to a
location in Singapore.

Rebuild and verify the topic appears.

**What you learn:** NavSat sensors simulate GPS by combining the model's
position in the world with the world's geographic reference. The 10 Hz
rate mimics real GPS update frequency.

**Progress toward goal:** PX4 requires GPS for position hold and return-to-
launch modes.

### Task 4.3 -- Verify all four sensors are publishing

Run the world and confirm you can echo data from all four sensors:

1. IMU (already existed)
2. Air pressure (already existed)
3. Magnetometer (you added)
4. GPS/NavSat (you added)

Write down each topic name. You will need them in Phase 6.

**What you learn:** How to systematically verify simulation outputs.

**Progress toward goal:** The sensor suite is complete for flight control.

---

## Phase 5: Add the Velocity Controller Plugin

Goal: learn how Gazebo plugins are configured by adding the multicopter
velocity controller. This is the plugin that converts human-friendly velocity
commands ("go up", "go forward") into the four motor speeds.

### Task 5.1 -- Understand the existing motor model plugins

Re-read the bottom section of `assets/models/x500/model.sdf`. Each
`MulticopterMotorModel` plugin has:

- `jointName`: which rotor joint it drives.
- `motorNumber`: 0-3.
- `turningDirection`: cw or ccw.
- `motorConstant`: converts rotation speed to thrust force.
- `momentConstant`: converts thrust to torque.
- `commandSubTopic`: the Gazebo topic it listens on.

These plugins turn speed commands into physics forces. But there is nothing
that decides WHAT speeds to command.

**What you learn:** The two-layer multicopter control architecture:
low-level motor models (already exist) and high-level velocity controller
(missing).

### Task 5.2 -- Add MulticopterVelocityControl plugin

Add this plugin block to `assets/models/x500/model.sdf`, inside the
`<model>` tag after the motor model plugins:

```xml
<plugin
  filename="gz-sim-multicopter-control-system"
  name="gz::sim::systems::MulticopterVelocityControl">
  <robotNamespace>x500_drone</robotNamespace>
  <commandSubTopic>cmd_vel</commandSubTopic>
  <enableSubTopic>enable</enableSubTopic>
  <comLinkName>base_link</comLinkName>
  <velocityGain>
    <linear>5 5 5</linear>
    <angular>3 3 3</angular>
  </velocityGain>
  <maximumLinearAcceleration>2 2 2</maximumLinearAcceleration>
  <maximumAngularAcceleration>3 3 3</maximumAngularAcceleration>
  <maximumLinearVelocity>5 5 5</maximumLinearVelocity>
  <maximumAngularVelocity>3 3 3</maximumAngularVelocity>
  <rotorConfiguration>
    <rotor>
      <jointName>rotor_0_joint</jointName>
      <forceConstant>8.54858e-06</forceConstant>
      <momentConstant>0.016</momentConstant>
      <direction>-1</direction>
    </rotor>
    <rotor>
      <jointName>rotor_1_joint</jointName>
      <forceConstant>8.54858e-06</forceConstant>
      <momentConstant>0.016</momentConstant>
      <direction>-1</direction>
    </rotor>
    <rotor>
      <jointName>rotor_2_joint</jointName>
      <forceConstant>8.54858e-06</forceConstant>
      <momentConstant>0.016</momentConstant>
      <direction>1</direction>
    </rotor>
    <rotor>
      <jointName>rotor_3_joint</jointName>
      <forceConstant>8.54858e-06</forceConstant>
      <momentConstant>0.016</momentConstant>
      <direction>1</direction>
    </rotor>
  </rotorConfiguration>
</plugin>
```

Rebuild and run.

**What you learn:** How Gazebo system plugins are configured through SDF.
The velocity controller is a feedback loop: it reads the drone's current
velocity, compares it to the commanded velocity, and computes motor speeds
to reduce the error. The `velocityGain` values are PID-like tuning
parameters.

**Progress toward goal:** The drone now has a controller that accepts
velocity commands.

### Task 5.3 -- Fly the drone from the command line

With the world running, first enable the controller:

```bash
gz topic -t /model/x500_drone/enable -m gz.msgs.Boolean -p 'data: true'
```

Then command it to go up:

```bash
gz topic -t /model/x500_drone/cmd_vel -m gz.msgs.Twist \
  -p 'linear: {x: 0, y: 0, z: 0.5}'
```

The drone should lift off. Try different values. Try adding yaw rotation:

```bash
gz topic -t /model/x500_drone/cmd_vel -m gz.msgs.Twist \
  -p 'linear: {x: 0, y: 0, z: 0.5}, angular: {x: 0, y: 0, z: 0.3}'
```

If the drone is unstable, you will tune the gains in the next task.

**What you learn:** Twist messages (linear xyz velocity + angular xyz
velocity) are the standard way to command robot movement in the
Gazebo/ROS ecosystem. This is the same interface a joystick node will use.

**Progress toward goal:** You can manually fly the drone. This is the
first working demonstration of the internship goal.

### Task 5.4 -- Tune the velocity controller gains

If the drone oscillates, overshoots, or drifts, adjust the gains. Start
with lower values and increase:

- `velocityGain/linear`: controls how aggressively it corrects position
  velocity errors. Too high = oscillation. Too low = sluggish.
- `velocityGain/angular`: same for rotation.
- `maximumLinearAcceleration`: caps how fast it can accelerate.

Change values, rebuild, re-test. Repeat until hover is stable.

**What you learn:** Basic control system tuning. This is the same process
used on real drones (PID tuning), just at a higher level.

**Progress toward goal:** Stable flight behavior.

---

## Phase 6: Learn ROS 2 by Bridging Gazebo to It

Goal: learn ROS 2 fundamentals by connecting the already-working Gazebo
simulation to the ROS 2 world. After this phase, you can control the drone
using ROS 2 tools.

### Task 6.1 -- Learn the three essential ROS 2 commands

With any ROS 2 workspace sourced, try:

```bash
ros2 topic list
ros2 topic echo /some_topic
ros2 topic pub /some_topic std_msgs/msg/String '{data: "hello"}'
```

These three commands (list, echo, pub) are 80% of what you need for
debugging. They are the ROS 2 equivalent of `gz topic -l`, `gz topic -e`,
and `gz topic -t`.

**What you learn:** ROS 2 topic fundamentals. Topics are named streams
of typed messages. Publishers send, subscribers receive.

### Task 6.2 -- Install and understand ros_gz_bridge

The `ros_gz_bridge` package translates between Gazebo transport and ROS 2
topics. Install it:

```bash
sudo apt install ros-${ROS_DISTRO}-ros-gz-bridge
```

(Replace `${ROS_DISTRO}` with `humble` or `jazzy` as appropriate.)

**What you learn:** Gazebo and ROS 2 are separate systems with separate
message buses. The bridge is needed to connect them.

### Task 6.3 -- Bridge the velocity command topic

Run the bridge for cmd_vel:

```bash
ros2 run ros_gz_bridge parameter_bridge \
  /model/x500_drone/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist
```

The syntax means: bridge `/model/x500_drone/cmd_vel`, ROS 2 type
`geometry_msgs/msg/Twist`, direction `]` (ROS 2 to Gazebo), Gazebo type
`gz.msgs.Twist`.

Now you can send commands from ROS 2:

```bash
ros2 topic pub /model/x500_drone/cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 0, y: 0, z: 0.5}}'
```

**What you learn:** How ros_gz_bridge works, its topic-mapping syntax,
and directional bridging (`@` for bidirectional, `[` for GZ-to-ROS,
`]` for ROS-to-GZ).

**Progress toward goal:** The drone can now be commanded from ROS 2.

### Task 6.4 -- Bridge sensor topics to ROS 2

Bridge the IMU:

```bash
ros2 run ros_gz_bridge parameter_bridge \
  /world/aerialWorld/model/x500_drone/link/base_link/sensor/imu_sensor/imu@sensor_msgs/msg/Imu[gz.msgs.IMU
```

Do the same for other sensors (air pressure, magnetometer, navsat). Use
`gz topic -l` to find the exact Gazebo topic names.

Verify with `ros2 topic echo`.

**What you learn:** Sensor message mapping between Gazebo and ROS 2.

**Progress toward goal:** Sensor data is available in ROS 2 for PX4 or
any other subscriber.

### Task 6.5 -- Bridge the enable topic

```bash
ros2 run ros_gz_bridge parameter_bridge \
  /model/x500_drone/enable@std_msgs/msg/Bool]gz.msgs.Boolean
```

Now you can arm/disarm the velocity controller from ROS 2:

```bash
ros2 topic pub --once /model/x500_drone/enable std_msgs/msg/Bool '{data: true}'
```

**What you learn:** Not all bridges are sensor data. Control signals
(enable/disable, arm/disarm) are also bridged.

---

## Phase 7: Add Joystick Control

Goal: learn ROS 2 nodes and message flow by connecting a physical joystick
or keyboard to the drone.

### Task 7.1 -- Install teleop packages

```bash
sudo apt install ros-${ROS_DISTRO}-teleop-twist-joy \
                 ros-${ROS_DISTRO}-teleop-twist-keyboard \
                 ros-${ROS_DISTRO}-joy
```

**What you learn:** The ROS 2 ecosystem has reusable packages. The `joy`
package reads gamepad/joystick hardware and publishes `sensor_msgs/Joy`.
The `teleop_twist_joy` package converts `Joy` messages to `Twist` commands.

### Task 7.2 -- Fly with a keyboard

Run the keyboard teleop node remapped to the drone's topic:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args -r cmd_vel:=/model/x500_drone/cmd_vel
```

Make sure the enable bridge is running and the controller is enabled.
Use the keyboard keys to fly the drone.

**What you learn:** ROS 2 topic remapping (`-r old:=new`). This is how you
connect generic nodes to specific robots without changing code.

**Progress toward goal:** You now have keyboard-based manual control of
the drone. This is a valid deliverable for the internship goal.

### Task 7.3 -- Fly with a gamepad (if available)

If you have a USB gamepad/joystick:

```bash
ros2 launch teleop_twist_joy teleop-launch.py \
  joy_vel:=/model/x500_drone/cmd_vel
```

**What you learn:** ROS 2 launch files and parameter configuration for
hardware input devices.

**Progress toward goal:** Gamepad manual control is more natural than
keyboard for a drone.

---

## Phase 8: Create a Proper Launch Setup

Goal: learn ROS 2 launch files by automating everything you have been
running manually.

### Task 8.1 -- Write a ROS 2 launch file

Create a launch file that starts all bridges and the teleop node together.
This teaches you how ROS 2 launch files work:

- `Node` actions start ROS 2 nodes.
- `ExecuteProcess` can start non-ROS processes.
- Parameters and remappings configure nodes at launch time.

Study existing ROS 2 launch file examples online, then write one that
starts:

1. The ros_gz_bridge for cmd_vel and enable.
2. The ros_gz_bridge for IMU (and other sensors).
3. The teleop keyboard or joy node.

**What you learn:** ROS 2 launch system, which is how real robot systems
are started.

**Progress toward goal:** One-command startup for the full manual control
demo.

---

## Phase 9: Connect to the PX4 Ecosystem (Team Collaboration)

Goal: learn how PX4 SITL integrates with Gazebo. This is where your work
meets the Pixhawk person's work.

### Task 9.1 -- Understand what PX4 SITL is

Read the PX4 documentation at <https://docs.px4.io/main/en/sim_gazebo_gz/>.

Key concepts:

- PX4 is flight controller firmware that normally runs on a Pixhawk board.
- SITL (Software In The Loop) runs PX4 on your computer instead.
- PX4 reads simulated sensors and outputs motor commands.
- It already supports Gazebo Harmonic and the x500 airframe.

**What you learn:** How the real flight stack works and why simulation
matters.

### Task 9.2 -- Understand the PX4-Gazebo sensor/actuator bridge

PX4 communicates with Gazebo Harmonic through gz-transport directly. It
expects sensor topics at specific paths and publishes actuator commands.

Your job is to verify that the sensor topics your x500 publishes match
what PX4 expects, or configure PX4 to use your topic names.

**What you learn:** Integration between independently developed systems
requires agreeing on interfaces (topic names, message types, update rates).

### Task 9.3 -- Test PX4 SITL with your world

Once the Pixhawk person has PX4 SITL built:

1. Start your aerial world with the x500.
2. Start PX4 SITL pointing at your Gazebo instance.
3. Connect QGroundControl.
4. Arm and take off.

Debug any mismatches in topic names, coordinate frames, or timing.

**What you learn:** System integration debugging, which is the most
valuable real-world engineering skill.

**Progress toward goal:** Full realistic manual control with PX4 autopilot.

---

## Summary: What You Learn at Each Phase

| Phase | Gazebo/ROS Concepts Learned | Drone Progress |
|-------|----------------------------|----------------|
| 1 | World files, model SDF, GUI, sensors | Environment verified |
| 2 | Gravity, physics timing, includes, collisions | World ready for flight |
| 3 | gz-transport topics, echo, publish | Understand data flow |
| 4 | SDF sensors (magnetometer, GPS) | Sensor suite complete |
| 5 | Gazebo plugins, Twist messages, control tuning | Drone flies |
| 6 | ROS 2 topics, ros_gz_bridge, message types | ROS 2 control works |
| 7 | teleop nodes, topic remapping, joy input | Manual control works |
| 8 | ROS 2 launch files | One-command demo |
| 9 | PX4 SITL, system integration | Full realistic control |

## Estimated Timeline

- Phase 1-2: First few days (reading + small edits)
- Phase 3-4: Days 3-5 (inspecting topics + adding sensors)
- Phase 5: Days 5-8 (velocity controller + tuning)
- Phase 6-7: Days 8-12 (ROS 2 bridging + teleop)
- Phase 8: Day 12-13 (launch file automation)
- Phase 9: Days 13+ (PX4 integration with team)

These timelines assume part-time work alongside other internship tasks.
Adjust based on your actual pace -- going slower is fine, the ordering
matters more than the speed.
