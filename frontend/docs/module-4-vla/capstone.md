---
sidebar_position: 2
---

# Capstone Project: Voice-Controlled Delivery Robot

Congratulations on completing the Physical AI & Humanoid Robotics curriculum! This capstone project integrates everything you've learned: **ROS 2**, **Gazebo simulation**, **NVIDIA Isaac**, and **voice commands** to build a fully autonomous delivery robot.

## Project Overview

**Goal**: Build a mobile robot that accepts voice commands to navigate to locations, pick up objects, and deliver them to specified destinations.

**Duration**: 2-4 weeks

**Difficulty**: Intermediate to Advanced

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Voice Command Layer                      │
│  Whisper STT → GPT-4 Intent → Action Planner               │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│                   Navigation Stack (Nav2)                    │
│  SLAM → Path Planning → Obstacle Avoidance                  │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│              Perception & Manipulation                       │
│  Camera → Object Detection → Gripper Control                │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│                    Robot Platform                            │
│  Mobile Base + Robotic Arm (Simulated in Gazebo/Isaac)     │
└─────────────────────────────────────────────────────────────┘
```

## Learning Objectives

By completing this project, you will:

1. ✅ Integrate multiple ROS 2 packages into a cohesive system
2. ✅ Implement voice-based human-robot interaction
3. ✅ Apply SLAM and autonomous navigation in realistic environments
4. ✅ Use computer vision for object detection and localization
5. ✅ Coordinate mobile base and manipulator for pick-and-place tasks
6. ✅ Test and debug a complex robotics system end-to-end

## Phase 1: Setup & Simulation Environment

### 1.1 Choose Your Platform

**Option A: Gazebo + TurtleBot 4**
- Free and open-source
- Wide community support
- Runs on any Linux machine

**Option B: Isaac Sim + Carter Robot**
- Photorealistic simulation
- GPU acceleration
- Requires NVIDIA RTX GPU

### 1.2 Install Dependencies

```bash
# For Gazebo + TurtleBot 4
sudo apt install ros-humble-turtlebot4-desktop
sudo apt install ros-humble-navigation2
sudo apt install ros-humble-nav2-bringup

# For voice control
pip install openai-whisper pyaudio
pip install openai  # For GPT-4 intent parsing

# For perception
sudo apt install ros-humble-vision-msgs
pip install ultralytics  # YOLOv8 for object detection
```

### 1.3 Create Project Workspace

```bash
mkdir -p ~/capstone_ws/src
cd ~/capstone_ws/src
git clone https://github.com/turtlebot/turtlebot4.git
git clone https://github.com/ros-planning/navigation2.git
cd ~/capstone_ws
colcon build
source install/setup.bash
```

## Phase 2: Voice Command Interface

### 2.1 Implement Speech Recognition

```python
# src/voice_controller/voice_controller/voice_node.py
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import whisper
import pyaudio

class VoiceControllerNode(Node):
    def __init__(self):
        super().__init__('voice_controller')
        self.model = whisper.load_model("base")
        self.command_pub = self.create_publisher(String, '/voice_commands', 10)

        # Start listening loop
        self.timer = self.create_timer(5.0, self.listen_and_publish)

    def listen_and_publish(self):
        # Record 3 seconds of audio
        audio_file = self.record_audio(duration=3)

        # Transcribe
        result = self.model.transcribe(audio_file)
        command = result["text"].strip()

        # Publish command
        msg = String()
        msg.data = command
        self.command_pub.publish(msg)
        self.get_logger().info(f"Voice command: {command}")

def main():
    rclpy.init()
    node = VoiceControllerNode()
    rclpy.spin(node)
```

### 2.2 Intent Extraction

```python
import openai

def parse_delivery_command(command):
    """Extract delivery task from natural language"""
    prompt = f"""
    Parse this delivery command: "{command}"

    Extract:
    - action: "deliver" | "pick" | "navigate"
    - object: item to deliver (e.g., "coffee cup")
    - destination: where to deliver (e.g., "office A")

    Return JSON only.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return json.loads(response.choices[0].message.content)
```

**Example**:
- Input: "Deliver the coffee cup to office A"
- Output: `{"action": "deliver", "object": "coffee cup", "destination": "office A"}`

## Phase 3: Autonomous Navigation

### 3.1 Launch SLAM Mapping

```bash
# Start Gazebo simulation
ros2 launch turtlebot4_ignition_bringup ignition.launch.py

# Launch SLAM Toolbox
ros2 launch slam_toolbox online_async_launch.py

# Drive robot around to build map
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

### 3.2 Save Map

```bash
ros2 run nav2_map_server map_saver_cli -f ~/maps/office_map
```

### 3.3 Navigation Node

```python
from nav2_simple_commander.robot_navigator import BasicNavigator
from geometry_msgs.msg import PoseStamped

class DeliveryNavigator:
    def __init__(self):
        self.navigator = BasicNavigator()

        # Define known locations
        self.locations = {
            "office_a": (2.0, 3.0, 0.0),
            "office_b": (-1.0, 2.5, 1.57),
            "charging_station": (0.0, 0.0, 0.0),
        }

    def navigate_to(self, location_name):
        if location_name not in self.locations:
            return False

        goal = PoseStamped()
        goal.header.frame_id = 'map'
        goal.header.stamp = self.navigator.get_clock().now().to_msg()

        x, y, yaw = self.locations[location_name]
        goal.pose.position.x = x
        goal.pose.position.y = y
        goal.pose.orientation.z = np.sin(yaw / 2)
        goal.pose.orientation.w = np.cos(yaw / 2)

        self.navigator.goToPose(goal)

        # Wait for navigation to complete
        while not self.navigator.isTaskComplete():
            rclpy.spin_once(self.navigator, timeout_sec=0.1)

        return self.navigator.getResult() == TaskResult.SUCCEEDED
```

## Phase 4: Object Detection & Manipulation

### 4.1 YOLOv8 Object Detector

```python
from ultralytics import YOLO
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

class ObjectDetectorNode(Node):
    def __init__(self):
        super().__init__('object_detector')
        self.model = YOLO('yolov8n.pt')  # Nano model for speed
        self.bridge = CvBridge()

        self.image_sub = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )

    def image_callback(self, msg):
        # Convert ROS image to OpenCV
        cv_image = self.bridge.imgmsg_to_cv2(msg, "rgb8")

        # Detect objects
        results = self.model(cv_image)

        # Find target object (e.g., "cup")
        for detection in results[0].boxes:
            class_id = int(detection.cls[0])
            class_name = self.model.names[class_id]

            if class_name == "cup":
                # Get bounding box center
                x_center = int((detection.xyxy[0][0] + detection.xyxy[0][2]) / 2)
                y_center = int((detection.xyxy[0][1] + detection.xyxy[0][3]) / 2)

                self.get_logger().info(f"Found cup at ({x_center}, {y_center})")
                # TODO: Convert to 3D coordinates and approach
```

### 4.2 Gripper Control (Placeholder)

```python
class GripperController:
    def __init__(self):
        self.gripper_pub = self.create_publisher(
            Float64,
            '/gripper/position',
            10
        )

    def open_gripper(self):
        msg = Float64()
        msg.data = 0.08  # Fully open
        self.gripper_pub.publish(msg)

    def close_gripper(self):
        msg = Float64()
        msg.data = 0.0  # Fully closed
        self.gripper_pub.publish(msg)
```

## Phase 5: Integration & Testing

### 5.1 Main Orchestrator

```python
class DeliveryRobotOrchestrator:
    def __init__(self):
        self.navigator = DeliveryNavigator()
        self.detector = ObjectDetectorNode()
        self.gripper = GripperController()

    def execute_delivery(self, task):
        # 1. Navigate to object location
        self.get_logger().info(f"Navigating to {task['object']}...")
        success = self.navigator.navigate_to("pickup_zone")
        if not success:
            return False

        # 2. Detect and approach object
        self.get_logger().info(f"Detecting {task['object']}...")
        # TODO: Visual servoing to approach object

        # 3. Pick up object
        self.get_logger().info("Picking up object...")
        self.gripper.open_gripper()
        # TODO: Lower arm, close gripper

        # 4. Navigate to destination
        self.get_logger().info(f"Delivering to {task['destination']}...")
        success = self.navigator.navigate_to(task['destination'])

        # 5. Place object
        self.get_logger().info("Placing object...")
        self.gripper.open_gripper()

        return True
```

### 5.2 Test Scenarios

| Scenario | Command | Expected Behavior |
|----------|---------|-------------------|
| **Basic Delivery** | "Deliver the cup to office A" | Navigate → Pick → Deliver → Return |
| **Multi-Object** | "Pick up the red box and blue ball" | Sequential pick-and-place |
| **Failure Recovery** | "Deliver the cup" (cup not found) | Report error, return to start |
| **Obstacle Avoidance** | Navigate with dynamic obstacles | Replan path around obstacles |

## Success Criteria

Your capstone is complete when your robot can:

1. ✅ Accept voice commands in natural language
2. ✅ Navigate autonomously in a mapped environment
3. ✅ Detect and localize objects using computer vision
4. ✅ Pick up objects with a gripper (or simulated gripper)
5. ✅ Deliver objects to specified locations
6. ✅ Handle at least one failure case gracefully

## Bonus Challenges

Want to take it further?

- 🌟 **Multi-Robot Coordination**: Deploy 2+ robots with task allocation
- 🌟 **Sim-to-Real Transfer**: Deploy on a physical robot (TurtleBot, Fetch, etc.)
- 🌟 **Human Tracking**: Follow a person using skeleton tracking
- 🌟 **Dynamic Re-planning**: Adapt to changing environments in real-time
- 🌟 **Battery Management**: Return to charging station when battery low

## Resources

- **TurtleBot 4 Docs**: https://turtlebot.github.io/turtlebot4-user-manual/
- **Nav2 Tutorials**: https://navigation.ros.org/tutorials/index.html
- **YOLOv8 Docs**: https://docs.ultralytics.com/
- **Whisper GitHub**: https://github.com/openai/whisper
- **Isaac Sim Examples**: https://docs.omniverse.nvidia.com/isaacsim/

## Try It Yourself

Ask the chatbot:
- "How do I integrate Nav2 with voice commands?"
- "What's the best way to tune SLAM parameters for my environment?"
- "Can I deploy this capstone project on a real robot?"

---

**Good luck with your capstone project! You're ready to build intelligent physical AI systems. 🤖**
