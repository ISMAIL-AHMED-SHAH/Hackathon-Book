"""
Add test data to Qdrant using HTTP API directly.

This bypasses any gRPC/client library issues on Windows.
"""

import json
import os
import sys

import requests
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()


def main() -> None:
    """Add sample test data to Qdrant collection."""
    # Set UTF-8 encoding for Windows console
    if sys.platform == "win32":
        import io

        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

    print("=" * 80)
    print("Adding Test Data to Qdrant")
    print("=" * 80)

    # Load settings
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    collection_name = os.getenv("VECTOR_COLLECTION_NAME", "textbook-chapters")
    embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    print(f"\n[1/4] Initializing OpenAI client...")
    openai_client = OpenAI(api_key=openai_api_key)
    print("  ✓ OpenAI client initialized")

    # Sample textbook content (ROS 2 fundamentals)
    sample_chunks = [
        {
            "chunk_id": "ch-ros2-fundamentals_chunk_0001",
            "content": (
                "ROS 2 nodes are the fundamental building blocks of ROS applications. "
                "Each node is a process that performs computation. Nodes communicate "
                "with each other using topics, services, and actions. A node can publish "
                "messages to topics, subscribe to topics, provide services, or call services."
            ),
            "chapter_id": "ch-ros2-fundamentals",
            "page_number": 42,
            "section_title": "Understanding ROS 2 Nodes",
        },
        {
            "chunk_id": "ch-ros2-fundamentals_chunk_0002",
            "content": (
                "Creating a ROS 2 node in Python requires importing the rclpy library "
                "and creating a class that inherits from Node. You then initialize the "
                "node using rclpy.init() and spin it using rclpy.spin() to start processing "
                "callbacks. Here's a minimal example: class MinimalNode(Node): def __init__(self): "
                "super().__init__('minimal_node'). This creates a node named 'minimal_node'."
            ),
            "chapter_id": "ch-ros2-fundamentals",
            "page_number": 45,
            "section_title": "Creating Your First Node in Python",
        },
        {
            "chunk_id": "ch-ros2-fundamentals_chunk_0003",
            "content": (
                "ROS 2 topics provide a publish-subscribe communication pattern. Publishers "
                "send messages to a topic without knowing who will receive them. Subscribers "
                "receive messages from topics they're interested in. Topics are identified by "
                "names like '/robot/speed' or '/sensor/camera/image'. Messages are typed using "
                "ROS 2 message definitions (.msg files)."
            ),
            "chapter_id": "ch-ros2-fundamentals",
            "page_number": 52,
            "section_title": "Topics and Message Passing",
        },
        {
            "chunk_id": "ch-ros2-fundamentals_chunk_0004",
            "content": (
                "ROS 2 services provide request-reply communication. Unlike topics, services "
                "are synchronous - the client sends a request and waits for a response from "
                "the server. Services are useful for remote procedure calls like '/reset_robot' "
                "or '/get_position'. Each service has a service type defined in .srv files."
            ),
            "chapter_id": "ch-ros2-fundamentals",
            "page_number": 58,
            "section_title": "Services and Client-Server Pattern",
        },
        {
            "chunk_id": "ch-ros2-fundamentals_chunk_0005",
            "content": (
                "ROS 2 actions combine topics and services for long-running tasks. An action "
                "client sends a goal to an action server, which provides feedback during execution "
                "and a result when complete. Actions can be preempted (canceled). Examples include "
                "'/navigate_to_pose' for robot navigation or '/pick_object' for manipulation tasks."
            ),
            "chapter_id": "ch-ros2-fundamentals",
            "page_number": 65,
            "section_title": "Actions for Long-Running Tasks",
        },
    ]

    print(f"\n[2/4] Generating embeddings for {len(sample_chunks)} chunks...")
    points = []

    for i, chunk in enumerate(sample_chunks, start=1):
        # Generate embedding using OpenAI
        print(f"  [{i}/{len(sample_chunks)}] {chunk['chunk_id']}")
        response = openai_client.embeddings.create(model=embedding_model, input=chunk["content"])
        embedding = response.data[0].embedding

        # Create point for Qdrant
        point = {
            "id": i,  # Simple sequential IDs for test data
            "vector": embedding,
            "payload": chunk,
        }
        points.append(point)

    print(f"  ✓ Generated {len(points)} embeddings")

    # Upload to Qdrant using HTTP API
    print(f"\n[3/4] Uploading to Qdrant collection '{collection_name}'...")
    url = f"{qdrant_url}/collections/{collection_name}/points"
    headers = {"api-key": qdrant_api_key, "Content-Type": "application/json"}

    # Upload in batches
    batch_size = 2
    for i in range(0, len(points), batch_size):
        batch = points[i : i + batch_size]
        payload = {"points": batch}

        try:
            response = requests.put(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            print(f"  → Uploaded batch {i//batch_size + 1}/{(len(points)-1)//batch_size + 1}")
        except requests.exceptions.RequestException as e:
            print(f"  ✗ Upload failed: {e}")
            if hasattr(e, "response") and e.response:
                print(f"  Response: {e.response.text}")
            sys.exit(1)

    print(f"  ✓ Uploaded {len(points)} points successfully")

    # Verify upload
    print("\n[4/4] Verifying upload...")
    try:
        verify_url = f"{qdrant_url}/collections/{collection_name}"
        response = requests.get(verify_url, headers=headers, timeout=30)
        response.raise_for_status()
        collection_info = response.json()
        points_count = collection_info["result"]["points_count"]
        print(f"  ✓ Collection now has {points_count} points")
    except Exception as e:
        print(f"  ⚠ Could not verify: {e}")

    # Print next steps
    print("\n" + "=" * 80)
    print("Test Data Added Successfully!")
    print("=" * 80)
    print("\nYou can now test the query endpoint:")
    print("\n  PowerShell:")
    print("  $body = @{")
    print('    query_text = "What are ROS 2 nodes?"')
    print('    chapter_id = "ch-ros2-fundamentals"')
    print('    user_id = "550e8400-e29b-41d4-a716-446655440000"')
    print("  } | ConvertTo-Json")
    print("  Invoke-RestMethod -Uri http://localhost:8000/v1/query -Method Post `")
    print("    -ContentType 'application/json' -Body $body")
    print("\n  Or visit: http://localhost:8000/v1/docs")
    print("=" * 80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCanceled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
