---
sidebar_position: 2
---

# ROS 2 Topics & Pub/Sub

Topics are named channels that nodes use to exchange messages. They enable a publish-subscribe pattern where publishers send data and subscribers receive it.

## What is a Topic?

A **topic** is like a radio station. Publishers broadcast messages on a topic, and subscribers tune in to listen. Multiple nodes can publish to the same topic, and multiple nodes can subscribe to it.

### Topic Examples

- `/camera/image`: Camera images
- `/robot/speed`: Current robot velocity
- `/battery/level`: Battery percentage
- `/sensor/temperature`: Temperature readings

## Publisher/Subscriber Pattern

The pub/sub pattern has three parts:

1. **Publisher**: Sends messages on a topic
2. **Topic**: The named channel for messages
3. **Subscriber**: Receives messages from a topic

This pattern is **decoupled**: publishers don't know who subscribes, and subscribers don't know who publishes.

## Creating a Publisher

Here's a node that publishes robot position every second:

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point

class PositionPublisher(Node):
    def __init__(self):
        super().__init__('position_publisher')

        # Create publisher for Point messages
        self.publisher = self.create_publisher(Point, 'robot/position', 10)

        # Create timer to publish every 1 second
        self.timer = self.create_timer(1.0, self.publish_position)

        self.x = 0.0
        self.y = 0.0

    def publish_position(self):
        msg = Point()
        msg.x = self.x
        msg.y = self.y
        msg.z = 0.0

        self.publisher.publish(msg)
        self.get_logger().info(f'Publishing position: x={msg.x}, y={msg.y}')

        # Move robot forward
        self.x += 0.1
        self.y += 0.1

def main():
    rclpy.init()
    node = PositionPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
```

### Publisher Key Points

- **Topic name**: `'robot/position'` identifies the channel
- **Message type**: `Point` defines the data structure
- **Queue size**: `10` stores recent messages
- **publish()**: Sends the message to subscribers

## Creating a Subscriber

Here's a node that receives position messages:

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point

class PositionSubscriber(Node):
    def __init__(self):
        super().__init__('position_subscriber')

        # Create subscriber for Point messages
        self.subscription = self.create_subscription(
            Point,
            'robot/position',
            self.position_callback,
            10
        )

    def position_callback(self, msg):
        self.get_logger().info(f'Received position: x={msg.x}, y={msg.y}')

        # Check if robot reached target
        if msg.x >= 5.0:
            self.get_logger().warn('Robot reached target!')

def main():
    rclpy.init()
    node = PositionSubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
```

### Subscriber Key Points

- **Callback function**: Runs when a message arrives
- **Same topic name**: Must match the publisher
- **Same message type**: Must match the publisher
- **Asynchronous**: Messages arrive at any time

## Message Types

ROS 2 has many built-in message types:

```python
# Common message types
from std_msgs.msg import String, Int32, Float64, Bool
from geometry_msgs.msg import Point, Pose, Twist
from sensor_msgs.msg import Image, LaserScan, Imu
```

### Creating Custom Messages

You can also define your own message types. Example: `RobotStatus.msg`

```
# Custom message definition
string robot_name
float64 battery_level
bool is_moving
int32 error_count
```

## Quality of Service (QoS)

QoS controls how messages are delivered:

```python
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

qos_profile = QoSProfile(
    reliability=ReliabilityPolicy.RELIABLE,  # Guarantee delivery
    history=HistoryPolicy.KEEP_LAST,         # Keep last N messages
    depth=10                                 # Queue size
)

publisher = self.create_publisher(Point, 'topic', qos_profile)
```

### QoS Reliability Options

1. **RELIABLE**: Messages always delivered (slower)
2. **BEST_EFFORT**: Fast delivery, may lose messages

Use RELIABLE for critical data (commands), BEST_EFFORT for sensors (images).

## Key Concepts Summary

- **Topic**: Named channel for messages
- **Publisher**: Sends messages on a topic
- **Subscriber**: Receives messages from a topic
- **Message Type**: Defines data structure
- **QoS**: Controls message delivery behavior

## Try It Yourself

Ask the chatbot to explain:
- "What happens if two nodes publish to the same topic?"
- "How do I list all active topics?"
- "When should I use RELIABLE vs BEST_EFFORT QoS?"

---

**Next Chapter**: Learn about Services for request-response communication.
