---
sidebar_position: 1
---

# Gazebo Simulation Basics

**Gazebo** is a powerful 3D robot simulator that provides realistic physics, sensors, and environments for testing robots before deploying them in the real world.

## Why Use Simulation?

Simulation offers major advantages during robot development:

1. **Safety**: Test dangerous scenarios without risking hardware
2. **Speed**: Iterate quickly without waiting for physical assembly
3. **Cost**: Reduce wear on expensive robot parts
4. **Repeatability**: Run the same test scenario hundreds of times
5. **Parallel Testing**: Simulate multiple robots at once

## Key Concepts

### 1. Worlds: The Simulation Environment

Worlds define the 3D environment where your robot operates. They include:
- Ground plane and gravity settings
- Lighting and sky appearance
- Static objects (walls, furniture, obstacles)
- Dynamic objects (other robots, moving obstacles)

### 2. Models: Robot and Object Descriptions

Models are URDF or SDF (Simulation Description Format) files that describe:
- Visual appearance (colors, textures, 3D meshes)
- Collision shapes (for physics calculations)
- Inertial properties (mass, center of mass)
- Sensors and actuators

### 3. Plugins: Adding Behavior

Plugins extend Gazebo's functionality:
- **Model plugins**: Control individual robots
- **World plugins**: Modify the entire simulation
- **Sensor plugins**: Process sensor data (cameras, LiDAR)

## Getting Started with Gazebo

### Launching a Basic World

```bash
# Launch an empty world
ros2 launch gazebo_ros gazebo.launch.py

# Launch with a specific world file
ros2 launch gazebo_ros gazebo.launch.py world:=/path/to/my_world.world
```

### Spawning a Robot

```bash
# Spawn a robot from URDF
ros2 run gazebo_ros spawn_entity.py -entity my_robot \
    -file /path/to/robot.urdf \
    -x 0 -y 0 -z 0.5
```

### Example: Simple World File

```xml
<?xml version="1.0"?>
<sdf version="1.6">
  <world name="basic_world">
    <!-- Physics engine settings -->
    <physics type="ode">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1</real_time_factor>
    </physics>

    <!-- Lighting -->
    <light name="sun" type="directional">
      <pose>0 0 10 0 0 0</pose>
      <diffuse>1 1 1 1</diffuse>
      <specular>0.5 0.5 0.5 1</specular>
      <direction>-0.5 -0.5 -1</direction>
    </light>

    <!-- Ground plane -->
    <include>
      <uri>model://ground_plane</uri>
    </include>

    <!-- Simple box obstacle -->
    <model name="box">
      <static>true</static>
      <pose>2 0 0.5 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>1 1 1</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>1 1 1</size>
            </box>
          </geometry>
          <material>
            <ambient>1 0 0 1</ambient>
          </material>
        </visual>
      </link>
    </model>
  </world>
</sdf>
```

## Physics Simulation

Gazebo uses the **ODE (Open Dynamics Engine)** by default:
- **Timestep**: How often physics is calculated (default: 1ms)
- **Real-time factor**: Simulation speed (1.0 = real-time, 0.5 = half-speed)
- **Gravity**: Default is Earth gravity (-9.81 m/s²)

### Adjusting Physics Performance

```xml
<physics type="ode">
  <max_step_size>0.001</max_step_size>  <!-- 1ms timestep -->
  <real_time_factor>1.0</real_time_factor>  <!-- Run at real-time speed -->
  <real_time_update_rate>1000</real_time_update_rate>
</physics>
```

## Gazebo GUI Controls

| Action | Control |
|--------|---------|
| **Rotate view** | Left mouse drag |
| **Pan view** | Middle mouse drag |
| **Zoom** | Scroll wheel |
| **Select object** | Left click |
| **Move object** | Drag with translate tool |
| **Pause/Play** | Bottom toolbar |

## Common Simulation Patterns

### 1. Testing Navigation Algorithms

Spawn obstacles and test path planning without risking real robots.

### 2. Sensor Calibration

Simulate camera and LiDAR data to tune perception algorithms.

### 3. Multi-Robot Coordination

Run multiple robot instances to test swarm behaviors.

### 4. Environmental Testing

Change gravity, friction, and lighting to test edge cases.

## Best Practices

1. **Start simple**: Use basic shapes before adding complex meshes
2. **Monitor performance**: Check real-time factor stays near 1.0
3. **Use appropriate timestep**: Smaller = more accurate but slower
4. **Simplify collision geometry**: Use boxes/cylinders instead of detailed meshes
5. **Version control worlds**: Track simulation environment changes

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **Simulation runs slow** | Reduce model complexity or increase timestep |
| **Robot falls through ground** | Check collision geometry is defined |
| **Sensors return no data** | Verify sensor plugins are loaded |
| **Gravity feels wrong** | Check physics settings and inertial properties |

## Try It Yourself

Ask the chatbot:
- "How do I change the gravity in Gazebo?"
- "What's the difference between SDF and URDF?"
- "How do I pause and resume a simulation?"
