---
sidebar_position: 1
---

# ROS 2 Nodes

ROS 2 nodes are the basic building blocks of robot applications. A node is a process that performs a specific task, like controlling motors or reading sensor data.

## What is a Node?

A **node** is an independent program that runs on your robot. Each node has one clear job. For example:
- A camera node captures images
- A motor control node moves wheels
- A planning node decides where to go

Nodes work together by sending messages to each other. This lets you build complex robots from simple parts.

## Why Use Nodes?

Breaking your robot software into nodes has several benefits:

1. **Modularity**: Each node does one thing well
2. **Reusability**: You can use the same node in different robots
3. **Testing**: Test each node separately before combining them
4. **Debugging**: If something breaks, you know which node to fix
5. **Distribution**: Nodes can run on different computers

## Creating Your First Node

Here's a simple Python node that prints a message every second:

```python
import rclpy
from rclpy.node import Node

class HelloNode(Node):
    def __init__(self):
        super().__init__('hello_node')
        self.timer = self.create_timer(1.0, self.timer_callback)
        self.counter = 0

    def timer_callback(self):
        self.get_logger().info(f'Hello ROS 2! Count: {self.counter}')
        self.counter += 1

def main(args=None):
    rclpy.init(args=args)
    node = HelloNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### How This Code Works

1. **Import rclpy**: This is the ROS 2 Python library
2. **Create a class**: `HelloNode` inherits from `Node`
3. **Initialize**: Set up a timer that runs every 1.0 seconds
4. **Timer callback**: This function runs every second
5. **Spin**: Keep the node running and handle callbacks
6. **Cleanup**: Destroy the node and shutdown when done

## Node Lifecycle

Every ROS 2 node goes through these states:

1. **Unconfigured**: Node is created but not ready
2. **Inactive**: Node is configured but not running
3. **Active**: Node is running and doing work
4. **Finalized**: Node is shutting down

Most simple nodes skip straight to Active. Advanced nodes use all states for controlled startup and shutdown.

## Running Multiple Nodes

Real robots run many nodes at once. Here's how they communicate:

```python
# Publisher node (sends data)
publisher = self.create_publisher(String, 'robot_status', 10)
msg = String()
msg.data = 'Robot is moving'
publisher.publish(msg)

# Subscriber node (receives data)
def listener_callback(self, msg):
    self.get_logger().info(f'Received: {msg.data}')

subscription = self.create_subscription(
    String,
    'robot_status',
    self.listener_callback,
    10
)
```

## Key Concepts Summary

- **Node**: An independent program with one job
- **rclpy**: The Python library for ROS 2
- **Timer**: Runs a function at regular intervals
- **Logger**: Prints messages for debugging
- **Lifecycle**: Nodes have states (unconfigured, active, etc.)

## Try It Yourself

Ask the chatbot to explain:
- "How do I run this node?"
- "What does rclpy.spin() do?"
- "Can one node have multiple timers?"

---

**Next Chapter**: Learn how nodes communicate using Topics and Publishers/Subscribers.
