"""
Add test data to Qdrant for endpoint testing.

This script adds sample textbook chunks to Qdrant so you can test
the RAG query endpoint without waiting for full content ingestion.

Usage:
    python scripts/add_test_data.py

Requirements:
    - OPENAI_API_KEY in .env
    - QDRANT_URL and QDRANT_API_KEY in .env
    - Qdrant collection already created (run setup_qdrant_collection.py first)
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

from src.core.config import get_settings


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
    settings = get_settings()

    # Initialize clients
    print("\n[1/4] Initializing clients...")
    openai_client = OpenAI(api_key=settings.openai_api_key)
    qdrant_client = QdrantClient(
        url=str(settings.qdrant_url),
        api_key=settings.qdrant_api_key,
        timeout=60,  # Increase timeout for cloud connections
        prefer_grpc=False,  # Use HTTP instead of gRPC for better Windows compatibility
    )
    print("  ✓ OpenAI client initialized")
    print("  ✓ Qdrant client initialized")

    # Test connection to Qdrant
    print("\n[1.5/4] Testing Qdrant connection...")
    try:
        collections = qdrant_client.get_collections()
        print(f"  ✓ Connected to Qdrant ({len(collections.collections)} collections found)")

        # Check if our collection exists
        collection_exists = any(
            c.name == settings.vector_collection_name for c in collections.collections
        )
        if not collection_exists:
            print(f"  ⚠ Collection '{settings.vector_collection_name}' not found!")
            print(f"  → Run: python scripts/setup_qdrant_collection.py")
            sys.exit(1)
        else:
            print(f"  ✓ Collection '{settings.vector_collection_name}' exists")
    except Exception as e:
        print(f"  ✗ Connection failed: {e}")
        print("\n  Troubleshooting:")
        print("  1. Check your QDRANT_URL in .env (should start with https://)")
        print("  2. Check your QDRANT_API_KEY in .env")
        print("  3. Verify your Qdrant Cloud cluster is running in the dashboard")
        print("  4. Check if your firewall/antivirus is blocking the connection")
        sys.exit(1)

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
        response = openai_client.embeddings.create(
            model=settings.embedding_model, input=chunk["content"]
        )
        embedding = response.data[0].embedding

        # Create Qdrant point
        point = PointStruct(
            id=i,  # Simple sequential IDs for test data
            vector=embedding,
            payload=chunk,
        )
        points.append(point)

    print(f"  ✓ Generated {len(points)} embeddings")

    # Upload to Qdrant
    print(f"\n[3/4] Uploading to Qdrant collection '{settings.vector_collection_name}'...")
    try:
        # Upload in smaller batches for better reliability
        batch_size = 2
        for i in range(0, len(points), batch_size):
            batch = points[i : i + batch_size]
            qdrant_client.upsert(
                collection_name=settings.vector_collection_name,
                points=batch,
                wait=True,  # Wait for indexing to complete
            )
            print(f"  → Uploaded batch {i//batch_size + 1}/{(len(points)-1)//batch_size + 1}")

        print(f"  ✓ Uploaded {len(points)} points successfully")
    except Exception as e:
        print(f"  ✗ Upload failed: {e}")
        print("\n  Troubleshooting:")
        print("  1. Connection may have timed out - try running the script again")
        print("  2. Check if your Qdrant cluster has enough storage (free tier: 1GB)")
        print("  3. Verify the collection exists: python scripts/setup_qdrant_collection.py")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    # Verify upload
    print("\n[4/4] Verifying upload...")
    try:
        collection_info = qdrant_client.get_collection(settings.vector_collection_name)
        print(f"  ✓ Collection now has {collection_info.points_count} points")
    except Exception as e:
        print(f"  ⚠ Could not verify: {e}")

    # Print next steps
    print("\n" + "=" * 80)
    print("Test Data Added Successfully!")
    print("=" * 80)
    print("\nYou can now test the query endpoint:")
    print("\n  curl -X POST http://localhost:8000/v1/query \\")
    print('    -H "Content-Type: application/json" \\')
    print("    -d '{")
    print('      "query_text": "What are ROS 2 nodes?",')
    print('      "chapter_id": "ch-ros2-fundamentals",')
    print('      "user_id": "550e8400-e29b-41d4-a716-446655440000"')
    print("    }'")
    print("\nOr visit the interactive docs: http://localhost:8000/v1/docs")
    print("=" * 80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCanceled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
