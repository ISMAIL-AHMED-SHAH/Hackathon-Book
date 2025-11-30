---
sidebar_position: 2
---

# Isaac ROS Integration

**Isaac ROS** is NVIDIA's collection of GPU-accelerated ROS 2 packages for perception, navigation, and manipulation. It bridges Isaac Sim simulations with real robot deployments using hardware-accelerated AI models.

## Why Isaac ROS?

Standard ROS 2 packages run on CPU, limiting real-time performance. Isaac ROS moves heavy computations to GPU:

1. **10-100x Speedup**: GPU acceleration for perception pipelines
2. **Real-Time Performance**: Process high-resolution images at 30+ FPS
3. **Production-Ready AI**: Pre-trained models for common tasks
4. **Sim-to-Real Transfer**: Same code runs in Isaac Sim and on robots
5. **Edge Deployment**: Optimized for NVIDIA Jetson edge devices

## Key Concepts

### 1. GEM (Graph Execution Manager)

Isaac ROS uses **GEM** for optimized compute graphs:
- Schedules GPU operations efficiently
- Minimizes CPU-GPU data transfer
- Supports TensorRT, CUDA, and cuDNN acceleration

### 2. Hardware Acceleration Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Deep Learning** | TensorRT | Optimized neural network inference |
| **Computer Vision** | VPI (Vision Programming Interface) | Stereo, optical flow, filtering |
| **Compute** | CUDA | General GPU computation |
| **Hardware** | Jetson Orin / RTX GPU | Edge or datacenter deployment |

## Core Isaac ROS Packages

### 1. Visual SLAM (Simultaneous Localization and Mapping)

```bash
# Install Isaac ROS Visual SLAM
sudo apt-get install ros-humble-isaac-ros-visual-slam

# Launch visual SLAM with RealSense camera
ros2 launch isaac_ros_visual_slam isaac_ros_visual_slam_realsense.launch.py
```

**What it does:**
- Tracks camera pose in 3D space
- Builds a map of the environment
- Runs at 60+ FPS on Jetson Orin

### 2. Object Detection (DOPE - Deep Object Pose Estimation)

Detect and estimate 6D pose of known objects:

```python
import rclpy
from rclpy.node import Node
from vision_msgs.msg import Detection3DArray

class ObjectDetectionSubscriber(Node):
    def __init__(self):
        super().__init__('object_detection_subscriber')
        self.subscription = self.create_subscription(
            Detection3DArray,
            '/detections_output',
            self.detection_callback,
            10
        )

    def detection_callback(self, msg):
        for detection in msg.detections:
            # Get object class and pose
            class_id = detection.results[0].hypothesis.class_id
            pose = detection.results[0].pose.pose

            self.get_logger().info(
                f'Detected {class_id} at position '
                f'({pose.position.x:.2f}, {pose.position.y:.2f}, {pose.position.z:.2f})'
            )

def main():
    rclpy.init()
    node = ObjectDetectionSubscriber()
    rclpy.spin(node)
```

### 3. Depth Estimation (Stereo Cameras)

Process stereo camera pairs for depth perception:

```bash
# Launch stereo depth estimation
ros2 launch isaac_ros_stereo_image_proc isaac_ros_stereo_image_pipeline.launch.py \
    left_image_topic:=/left/image_raw \
    right_image_topic:=/right/image_raw \
    camera_info_topic:=/left/camera_info
```

**Output**: Disparity map and point cloud at 30 FPS

### 4. Image Segmentation

Segment images into semantic classes (road, car, person):

```bash
# Run semantic segmentation
ros2 launch isaac_ros_unet isaac_ros_unet_triton.launch.py \
    model_name:=peoplesemsegnet \
    input_topic:=/camera/image_raw \
    output_topic:=/segmentation/output
```

## Isaac Sim + Isaac ROS Workflow

### Step 1: Simulate in Isaac Sim

```python
from omni.isaac.kit import SimulationApp
simulation_app = SimulationApp({"headless": False})

from omni.isaac.core import World
from omni.isaac.sensor import Camera

# Create world with camera
world = World()
camera = Camera(
    prim_path="/World/Camera",
    position=[2, 0, 1],
    frequency=30,
    resolution=(640, 480)
)

# Enable ROS 2 bridge
from omni.isaac.core.utils.extensions import enable_extension
enable_extension("omni.isaac.ros2_bridge")

# Publish camera data to ROS 2 topic
camera.initialize()
camera.add_image_to_ros_bridge(topic_name="/camera/image_raw")

# Run simulation
world.reset()
for i in range(1000):
    world.step(render=True)

simulation_app.close()
```

### Step 2: Process with Isaac ROS

```bash
# Subscribe to simulated camera and run object detection
ros2 launch isaac_ros_dope isaac_ros_dope_triton.launch.py \
    model_name:=Ketchup \
    input_topic:=/camera/image_raw \
    output_topic:=/detections
```

### Step 3: Visualize Results

```bash
# View detection results in RViz
rviz2 -d isaac_ros_dope.rviz

# Or subscribe to detections programmatically
ros2 topic echo /detections
```

## Pre-Trained Models

Isaac ROS provides production-ready models:

| Model | Task | Input | Output |
|-------|------|-------|--------|
| **PeopleSemSegNet** | Semantic segmentation | RGB image | Person masks |
| **DOPE** | 6D object pose | RGB image | 3D bounding boxes |
| **ESS** | Stereo depth | Stereo pair | Disparity map |
| **CenterPose** | Object detection | RGB image | 2D/3D keypoints |
| **PeopleNet** | Person detection | RGB image | Bounding boxes |

## Setting Up Isaac ROS

### Installation on Ubuntu 22.04 (ROS 2 Humble)

```bash
# Install dependencies
sudo apt-get update
sudo apt-get install -y python3-rosdep

# Add Isaac ROS apt repository
sudo apt-add-repository universe
sudo apt-get update

# Install Isaac ROS packages (example: visual SLAM)
sudo apt-get install ros-humble-isaac-ros-visual-slam

# Install NVIDIA container toolkit (for Docker deployment)
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
    sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
```

### Docker Deployment (Recommended)

```bash
# Pull Isaac ROS Docker image
docker pull nvcr.io/nvidia/isaac-ros:humble

# Run Isaac ROS container with GPU access
docker run -it --rm \
    --gpus all \
    --network host \
    --privileged \
    nvcr.io/nvidia/isaac-ros:humble
```

## Performance Comparison

| Task | ROS 2 (CPU) | Isaac ROS (GPU) | Speedup |
|------|-------------|-----------------|---------|
| **Stereo Depth (720p)** | 5 FPS | 60 FPS | 12x |
| **Object Detection** | 2 FPS | 30 FPS | 15x |
| **Visual SLAM** | 15 FPS | 90 FPS | 6x |
| **Semantic Segmentation** | 3 FPS | 45 FPS | 15x |

*Tested on NVIDIA Jetson AGX Orin*

## Best Practices

1. **Use Docker**: Simplifies dependency management and deployment
2. **Test in Sim First**: Validate algorithms in Isaac Sim before deploying
3. **Monitor GPU Usage**: Use `nvidia-smi` to check GPU utilization
4. **Optimize Image Resolution**: Balance accuracy vs. throughput
5. **Leverage Pre-Trained Models**: Fine-tune instead of training from scratch

## Common Use Cases

### Autonomous Navigation

```bash
# Visual SLAM + obstacle avoidance
ros2 launch isaac_ros_visual_slam isaac_ros_visual_slam.launch.py &
ros2 launch isaac_ros_nvblox isaac_ros_nvblox.launch.py &
ros2 launch nav2_bringup navigation_launch.py
```

### Warehouse Automation

```bash
# Object detection + pose estimation for picking
ros2 launch isaac_ros_dope isaac_ros_dope.launch.py model_name:=Box &
ros2 launch moveit2 move_group.launch.py
```

### Agricultural Robotics

```bash
# Semantic segmentation for crop/weed identification
ros2 launch isaac_ros_unet isaac_ros_unet.launch.py model_name:=crop_segmentation
```

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| **Low FPS** | CPU bottleneck | Ensure GPU is being used (check `nvidia-smi`) |
| **No output** | Wrong topic names | Verify topics with `ros2 topic list` |
| **CUDA error** | Incompatible driver | Update NVIDIA driver to 525+ |
| **Out of memory** | Batch size too large | Reduce input image resolution |

## Try It Yourself

Ask the chatbot:
- "How do I set up Isaac ROS on a Jetson Orin?"
- "What's the difference between DOPE and CenterPose?"
- "Can Isaac ROS run without an NVIDIA GPU?"
