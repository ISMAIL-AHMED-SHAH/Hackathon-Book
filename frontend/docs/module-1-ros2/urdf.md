---
sidebar_position: 4
---

# Robot Description with URDF

**URDF (Unified Robot Description Format)** is an XML-based format for describing robot geometry, joints, sensors, and visual appearance in ROS 2.

## Why URDF Matters

URDF files are the blueprint of your robot. They define:
- **Physical structure**: Links (rigid bodies) and joints (connections)
- **Visual appearance**: 3D models and colors for simulation
- **Collision geometry**: Shapes for physics calculations
- **Sensor placement**: Where cameras and LiDAR are mounted

## Key Concepts

### 1. Links: Robot Parts

Links represent rigid bodies (wheels, chassis, arms).

```xml
<link name="base_link">
  <visual>
    <geometry>
      <box size="0.5 0.3 0.1"/>
    </geometry>
    <material name="blue">
      <color rgba="0 0 0.8 1"/>
    </material>
  </visual>
  <collision>
    <geometry>
      <box size="0.5 0.3 0.1"/>
    </geometry>
  </collision>
</link>
```

### 2. Joints: Connections Between Parts

Joints define how links move relative to each other.

**Joint Types:**
- `fixed`: No movement (camera mount)
- `revolute`: Rotation with limits (elbow)
- `continuous`: Unlimited rotation (wheel)
- `prismatic`: Linear motion (elevator)

```xml
<joint name="wheel_joint" type="continuous">
  <parent link="base_link"/>
  <child link="wheel_link"/>
  <origin xyz="0.2 0 -0.05" rpy="0 0 0"/>
  <axis xyz="0 1 0"/>
</joint>
```

### 3. Complete Example: Simple Mobile Robot

```xml
<?xml version="1.0"?>
<robot name="simple_robot">
  <!-- Base link -->
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.4 0.3 0.1"/>
      </geometry>
      <material name="gray">
        <color rgba="0.5 0.5 0.5 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.4 0.3 0.1"/>
      </geometry>
    </collision>
  </link>

  <!-- Left wheel -->
  <link name="left_wheel">
    <visual>
      <geometry>
        <cylinder radius="0.05" length="0.03"/>
      </geometry>
      <material name="black">
        <color rgba="0 0 0 1"/>
      </material>
    </visual>
  </link>

  <joint name="left_wheel_joint" type="continuous">
    <parent link="base_link"/>
    <child link="left_wheel"/>
    <origin xyz="0.1 0.15 -0.05" rpy="1.5708 0 0"/>
    <axis xyz="0 0 1"/>
  </joint>

  <!-- Right wheel (mirrored) -->
  <link name="right_wheel">
    <visual>
      <geometry>
        <cylinder radius="0.05" length="0.03"/>
      </geometry>
      <material name="black">
        <color rgba="0 0 0 1"/>
      </material>
    </visual>
  </link>

  <joint name="right_wheel_joint" type="continuous">
    <parent link="base_link"/>
    <child link="right_wheel"/>
    <origin xyz="0.1 -0.15 -0.05" rpy="1.5708 0 0"/>
    <axis xyz="0 0 1"/>
  </joint>
</robot>
```

## Viewing URDF in RViz

To visualize your robot model:

```bash
# Launch RViz with robot state publisher
ros2 launch urdf_tutorial display.launch.py model:=my_robot.urdf
```

## Best Practices

1. **Start simple**: Build basic shapes first, add detail later
2. **Use SI units**: Meters for length, radians for angles
3. **Set collision geometry**: Simplify for better performance
4. **Name consistently**: Use `base_link` as root, descriptive joint names
5. **Test incrementally**: Add one link/joint at a time

## Common Pitfalls

- **Missing parent/child links**: Joints need both
- **Wrong axis definition**: Check rotation direction
- **Incorrect origin**: Links may overlap or disconnect
- **No collision geometry**: Robot won't interact with environment

## Try It Yourself

Ask the chatbot:
- "What's the difference between visual and collision geometry?"
- "How do I define a revolute joint with limits?"
- "What coordinate system does URDF use?"
