---
sidebar_position: 1
---

# Voice Commands with Whisper

**Voice-Language-Action (VLA)** models bridge human language and robot actions. Using OpenAI's **Whisper** for speech recognition, you can control robots with natural voice commands instead of code or joysticks.

## Why Voice Commands?

Voice control makes robots more accessible and intuitive:

1. **Natural Interaction**: Speak commands instead of programming
2. **Hands-Free Operation**: Control robots while doing other tasks
3. **Accessibility**: Enable users with limited mobility to operate robots
4. **Rapid Prototyping**: Test behaviors without writing code
5. **Human-Robot Collaboration**: Natural communication in shared workspaces

## Key Concepts

### 1. Whisper: Speech-to-Text

**Whisper** is OpenAI's robust speech recognition model trained on 680,000 hours of multilingual data:
- **99% accuracy** on English speech
- Works in **noisy environments** (factories, outdoors)
- Supports **98 languages**
- Runs **locally** (no cloud API required)
- Multiple model sizes: tiny (39M params) to large (1550M params)

### 2. Language to Action Pipeline

```
[Voice Input] → [Whisper STT] → [Language Model] → [Action Mapper] → [Robot Execution]
```

**Example Flow:**
1. User: "Move forward 2 meters"
2. Whisper transcribes: "move forward 2 meters"
3. Language model extracts intent: `{"action": "move", "direction": "forward", "distance": 2.0}`
4. Action mapper converts to ROS 2 command: `cmd_vel.linear.x = 0.5`
5. Robot moves forward

## Installing Whisper

```bash
# Install Whisper Python package
pip install openai-whisper

# Install additional audio dependencies
sudo apt-get install ffmpeg

# Download a model (one-time, ~500MB for medium model)
whisper --model medium --output_dir models "test.wav"
```

## Basic Voice Command Node

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import whisper
import pyaudio
import wave
import tempfile

class VoiceCommandNode(Node):
    def __init__(self):
        super().__init__('voice_command_node')

        # Load Whisper model (medium = good accuracy, ~5GB RAM)
        self.model = whisper.load_model("medium")

        # Publisher for robot velocity commands
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # Audio recording settings
        self.audio = pyaudio.PyAudio()
        self.sample_rate = 16000
        self.chunk_size = 1024

        self.get_logger().info("Voice command node ready. Listening...")

    def record_audio(self, duration=3):
        """Record audio from microphone for specified duration"""
        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )

        self.get_logger().info("Recording...")
        frames = []
        for i in range(0, int(self.sample_rate / self.chunk_size * duration)):
            data = stream.read(self.chunk_size)
            frames.append(data)

        stream.stop_stream()
        stream.close()

        # Save to temporary WAV file
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        with wave.open(temp_file.name, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(frames))

        return temp_file.name

    def transcribe_audio(self, audio_file):
        """Convert speech to text using Whisper"""
        result = self.model.transcribe(audio_file)
        return result["text"].strip().lower()

    def execute_command(self, command):
        """Parse command and publish robot action"""
        twist = Twist()

        if "forward" in command:
            twist.linear.x = 0.5
            self.get_logger().info("Moving forward")
        elif "backward" in command:
            twist.linear.x = -0.5
            self.get_logger().info("Moving backward")
        elif "left" in command:
            twist.angular.z = 0.5
            self.get_logger().info("Turning left")
        elif "right" in command:
            twist.angular.z = -0.5
            self.get_logger().info("Turning right")
        elif "stop" in command:
            twist.linear.x = 0.0
            twist.angular.z = 0.0
            self.get_logger().info("Stopping")
        else:
            self.get_logger().warn(f"Unknown command: {command}")
            return

        # Publish command for 2 seconds
        for _ in range(20):
            self.cmd_vel_pub.publish(twist)
            rclpy.spin_once(self, timeout_sec=0.1)

    def run(self):
        """Main loop: record → transcribe → execute"""
        while rclpy.ok():
            # Record voice command
            audio_file = self.record_audio(duration=3)

            # Transcribe to text
            command = self.transcribe_audio(audio_file)
            self.get_logger().info(f"Heard: '{command}'")

            # Execute robot action
            self.execute_command(command)

def main():
    rclpy.init()
    node = VoiceCommandNode()
    try:
        node.run()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
```

## Advanced: Intent Extraction with LLMs

Use a language model to extract structured commands:

```python
import openai

def extract_intent(command_text):
    """Use GPT to parse command into structured format"""
    prompt = f"""
    Extract the robot action from this command: "{command_text}"

    Return JSON with:
    - action: move/turn/pick/place/stop
    - direction: forward/backward/left/right (if applicable)
    - distance: meters (if specified)
    - object: object name (if applicable)

    Example: "move forward 2 meters" → {{"action": "move", "direction": "forward", "distance": 2.0}}
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content
```

**Input**: "Pick up the red block on the table"
**Output**:
```json
{
  "action": "pick",
  "object": "red block",
  "location": "table"
}
```

## Multimodal Commands (Vision + Language)

Combine voice commands with camera input:

```python
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

class MultimodalVoiceNode(VoiceCommandNode):
    def __init__(self):
        super().__init__()

        # Subscribe to camera
        self.image_sub = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )
        self.latest_image = None
        self.bridge = CvBridge()

    def image_callback(self, msg):
        self.latest_image = self.bridge.imgmsg_to_cv2(msg, "rgb8")

    def execute_command(self, command):
        if "red" in command and self.latest_image is not None:
            # Detect red objects in image
            red_mask = cv2.inRange(self.latest_image, (0, 0, 100), (50, 50, 255))
            # Find centroid, move towards it
            self.get_logger().info("Targeting red object")
        else:
            super().execute_command(command)
```

**Command**: "Go to the red box"
**Behavior**: Robot detects red objects in camera, navigates to closest one

## Performance Tips

| Model Size | Params | Speed (CPU) | Accuracy | Use Case |
|------------|--------|-------------|----------|----------|
| **tiny** | 39M | ~1s | 85% | Fast prototyping |
| **base** | 74M | ~2s | 92% | Real-time control |
| **small** | 244M | ~5s | 96% | General use |
| **medium** | 769M | ~10s | 98% | High accuracy |
| **large** | 1550M | ~30s | 99% | Offline processing |

**Recommendation**: Use **base** or **small** for real-time robot control.

## Common Voice Commands

| Command | Robot Action | ROS 2 Message |
|---------|--------------|---------------|
| "Move forward" | Linear motion | `cmd_vel.linear.x = 0.5` |
| "Turn left" | Rotate counterclockwise | `cmd_vel.angular.z = 0.5` |
| "Stop" | Halt all motion | `cmd_vel = Twist()` |
| "Pick up the cup" | Grasp object | Call `/pick` action |
| "Go to the table" | Navigate to location | Call `/navigate_to_pose` action |

## Safety Considerations

1. **Confirmation**: Echo back understood command before execution
2. **Emergency Stop**: Always support "stop" command with highest priority
3. **Timeout**: Stop if no command received for N seconds
4. **Validation**: Check if command is safe before executing
5. **Logging**: Record all voice commands for debugging

## Try It Yourself

Ask the chatbot:
- "How do I reduce Whisper's latency for real-time control?"
- "Can Whisper understand commands in noisy environments?"
- "How do I integrate Whisper with a vision-language model?"
