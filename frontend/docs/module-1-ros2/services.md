---
sidebar_position: 3
---

# ROS 2 Services & Actions

ROS 2 provides two important communication patterns for request-response interactions: **services** for quick, blocking operations and **actions** for long-running, interruptible tasks.

## Services: Request-Response Pattern

Services enable **synchronous** communication between nodes. A client sends a request and waits for a response from the server.

### Key Concepts

1. **Blocking Calls**: The client waits until the server responds
2. **Single Response**: Each request gets exactly one response
3. **Best For**: Quick operations like getting sensor data or toggling states

### Example: Basic Service

```python
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts

class MinimalService(Node):
    def __init__(self):
        super().__init__('minimal_service')
        self.srv = self.create_service(
            AddTwoInts,
            'add_two_ints',
            self.add_two_ints_callback
        )

    def add_two_ints_callback(self, request, response):
        response.sum = request.a + request.b
        self.get_logger().info(f'Request: {request.a} + {request.b} = {response.sum}')
        return response

def main():
    rclpy.init()
    service_node = MinimalService()
    rclpy.spin(service_node)
    rclpy.shutdown()
```

## Actions: Long-Running Tasks

Actions are designed for **asynchronous** tasks that take time to complete. They provide feedback during execution and can be canceled.

### Key Concepts

1. **Non-Blocking**: Client can continue other work while action runs
2. **Feedback**: Server sends progress updates during execution
3. **Cancelable**: Client can cancel the action before completion
4. **Best For**: Navigation, motion planning, long computations

### Example: Simple Action Server

```python
import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node
from example_interfaces.action import Fibonacci

class FibonacciActionServer(Node):
    def __init__(self):
        super().__init__('fibonacci_action_server')
        self._action_server = ActionServer(
            self,
            Fibonacci,
            'fibonacci',
            self.execute_callback
        )

    def execute_callback(self, goal_handle):
        self.get_logger().info('Executing goal...')

        feedback_msg = Fibonacci.Feedback()
        feedback_msg.sequence = [0, 1]

        for i in range(1, goal_handle.request.order):
            feedback_msg.sequence.append(
                feedback_msg.sequence[i] + feedback_msg.sequence[i-1]
            )
            self.get_logger().info(f'Feedback: {feedback_msg.sequence}')
            goal_handle.publish_feedback(feedback_msg)

        goal_handle.succeed()
        result = Fibonacci.Result()
        result.sequence = feedback_msg.sequence
        return result

def main():
    rclpy.init()
    action_server = FibonacciActionServer()
    rclpy.spin(action_server)
```

## When to Use Services vs Actions

| Feature | Service | Action |
|---------|---------|--------|
| **Duration** | Fast (&lt;1 second) | Slow (seconds to minutes) |
| **Feedback** | None | Progress updates |
| **Cancelable** | No | Yes |
| **Blocking** | Yes | No |
| **Example Use** | Get sensor reading | Navigate to goal |

## Try It Yourself

Ask the chatbot:
- "How do I create a service client in ROS 2?"
- "What's the difference between services and actions?"
- "Can actions be canceled mid-execution?"
