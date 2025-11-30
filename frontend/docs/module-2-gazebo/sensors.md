---
sidebar_position: 2
---

# Simulating Sensors in Gazebo

Sensors are the robot's eyes and ears. Gazebo simulates realistic sensor data including cameras, LiDAR, IMUs, and GPS, enabling you to test perception algorithms before deploying to real hardware.

## Why Simulate Sensors?

Sensor simulation offers critical advantages:

1. **Cost Savings**: Test expensive sensors (LiDAR, depth cameras) without buying them
2. **Perfect Ground Truth**: Know exact positions and measurements for algorithm validation
3. **Rapid Iteration**: Change sensor placement instantly without rewiring
4. **Edge Case Testing**: Simulate difficult conditions (fog, darkness, sensor failures)
5. **Parallel Development**: Software team works while hardware team builds robot

## Key Sensor Types

### 1. Camera: Visual Perception

Cameras capture RGB images for object detection, lane following, and visual navigation.

```xml
<sensor name="camera" type="camera">
  <pose>0.2 0 0.3 0 0 0</pose>
  <camera>
    <horizontal_fov>1.047</horizontal_fov>  <!-- 60 degrees -->
    <image>
      <width>640</width>
      <height>480</height>
      <format>R8G8B8</format>
    </image>
    <clip>
      <near>0.1</near>
      <far>100</far>
    </clip>
  </camera>
  <update_rate>30</update_rate>
  <visualize>true</visualize>
  <plugin name="camera_controller" filename="libgazebo_ros_camera.so">
    <ros>
      <namespace>/robot</namespace>
      <argument>--ros-args --remap ~/image_raw:=camera/image_raw</argument>
    </ros>
    <frame_name>camera_link</frame_name>
  </plugin>
</sensor>
```

### 2. LiDAR: Distance Measurement

LiDAR (Light Detection and Ranging) measures distances to objects using laser beams.

```xml
<sensor name="lidar" type="ray">
  <pose>0 0 0.4 0 0 0</pose>
  <ray>
    <scan>
      <horizontal>
        <samples>360</samples>  <!-- 360-degree scan -->
        <resolution>1</resolution>
        <min_angle>-3.14159</min_angle>
        <max_angle>3.14159</max_angle>
      </horizontal>
    </scan>
    <range>
      <min>0.12</min>
      <max>10.0</max>
      <resolution>0.01</resolution>
    </range>
  </ray>
  <update_rate>10</update_rate>
  <plugin name="lidar_controller" filename="libgazebo_ros_ray_sensor.so">
    <ros>
      <namespace>/robot</namespace>
      <argument>--ros-args --remap ~/out:=scan</argument>
    </ros>
    <output_type>sensor_msgs/LaserScan</output_type>
    <frame_name>lidar_link</frame_name>
  </plugin>
</sensor>
```

### 3. IMU: Orientation and Motion

IMU (Inertial Measurement Unit) tracks rotation, acceleration, and angular velocity.

```xml
<sensor name="imu" type="imu">
  <pose>0 0 0.1 0 0 0</pose>
  <imu>
    <angular_velocity>
      <x>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.0002</stddev>
        </noise>
      </x>
      <!-- y and z similar -->
    </angular_velocity>
    <linear_acceleration>
      <x>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.017</stddev>
        </noise>
      </x>
      <!-- y and z similar -->
    </linear_acceleration>
  </imu>
  <update_rate>100</update_rate>
  <plugin name="imu_controller" filename="libgazebo_ros_imu_sensor.so">
    <ros>
      <namespace>/robot</namespace>
      <argument>--ros-args --remap ~/out:=imu/data</argument>
    </ros>
    <frame_name>imu_link</frame_name>
  </plugin>
</sensor>
```

### 4. Depth Camera: 3D Perception

Depth cameras (like RealSense or Kinect) provide RGB images plus depth information.

```xml
<sensor name="depth_camera" type="depth">
  <pose>0.2 0 0.3 0 0 0</pose>
  <camera>
    <horizontal_fov>1.047</horizontal_fov>
    <image>
      <width>640</width>
      <height>480</height>
      <format>R8G8B8</format>
    </image>
    <clip>
      <near>0.1</near>
      <far>10.0</far>
    </clip>
  </camera>
  <update_rate>30</update_rate>
  <plugin name="depth_camera_controller" filename="libgazebo_ros_camera.so">
    <ros>
      <namespace>/robot</namespace>
    </ros>
    <frame_name>depth_camera_link</frame_name>
    <min_depth>0.1</min_depth>
    <max_depth>10.0</max_depth>
  </plugin>
</sensor>
```

## Sensor Noise Models

Real sensors have noise. Gazebo simulates this for realistic testing:

| Noise Type | Description | When to Use |
|------------|-------------|-------------|
| **Gaussian** | Random variation around mean | Camera pixels, IMU drift |
| **Uniform** | Equal probability in range | Distance sensors |
| **Salt & Pepper** | Random outliers | LiDAR false readings |

## Accessing Sensor Data in ROS 2

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan, Image, Imu

class SensorSubscriber(Node):
    def __init__(self):
        super().__init__('sensor_subscriber')

        # Subscribe to LiDAR
        self.lidar_sub = self.create_subscription(
            LaserScan,
            '/robot/scan',
            self.lidar_callback,
            10
        )

        # Subscribe to camera
        self.camera_sub = self.create_subscription(
            Image,
            '/robot/camera/image_raw',
            self.camera_callback,
            10
        )

        # Subscribe to IMU
        self.imu_sub = self.create_subscription(
            Imu,
            '/robot/imu/data',
            self.imu_callback,
            10
        )

    def lidar_callback(self, msg):
        # msg.ranges contains distance measurements
        min_distance = min(msg.ranges)
        self.get_logger().info(f'Closest obstacle: {min_distance:.2f}m')

    def camera_callback(self, msg):
        # msg.data contains image pixels
        self.get_logger().info(f'Camera frame: {msg.width}x{msg.height}')

    def imu_callback(self, msg):
        # msg.linear_acceleration contains acceleration data
        self.get_logger().info(f'Acceleration: {msg.linear_acceleration.x:.2f}')

def main():
    rclpy.init()
    node = SensorSubscriber()
    rclpy.spin(node)
```

## Sensor Placement Best Practices

1. **Camera Height**: Mount at typical viewing height (0.3-0.5m for ground robots)
2. **LiDAR Clearance**: Place above obstacles to avoid blind spots
3. **IMU Location**: Mount near center of mass for accurate readings
4. **Field of View**: Ensure cameras cover intended detection zones
5. **Update Rates**: Match real sensor specs (30 Hz cameras, 10 Hz LiDAR)

## Common Sensor Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| **No data published** | Plugin not loaded | Check plugin filename and ROS namespace |
| **All zero readings** | Sensor inside collision mesh | Adjust sensor pose |
| **Noisy data** | Excessive noise parameters | Reduce stddev in noise model |
| **Low frame rate** | High resolution + complex scene | Reduce image size or scene complexity |

## Visualizing Sensor Data

```bash
# View camera feed
ros2 run rqt_image_view rqt_image_view /robot/camera/image_raw

# View LiDAR scan in RViz
rviz2
# Add Display → LaserScan → Topic: /robot/scan

# Plot IMU data
ros2 run rqt_plot rqt_plot /robot/imu/data/linear_acceleration/x
```

## Try It Yourself

Ask the chatbot:
- "How do I add noise to a camera sensor in Gazebo?"
- "What's the difference between a camera and a depth camera?"
- "How do I visualize LiDAR data in RViz?"
