"""
Qdrant Collection Setup for RAG Pipeline Query Endpoint.

This script creates and configures the Qdrant vector database collection
for storing textbook chapter embeddings.

Requirements:
- Qdrant Cloud instance (or local Qdrant server)
- QDRANT_URL and QDRANT_API_KEY environment variables set
- qdrant-client Python package installed

Usage:
    python scripts/setup_qdrant_collection.py

Environment Variables:
    QDRANT_URL: Qdrant instance URL (e.g., https://xyz.cloud.qdrant.io)
    QDRANT_API_KEY: Qdrant API key for authentication
    QDRANT_COLLECTION_NAME: Collection name (default: textbook-chapters)
    EMBEDDING_DIMENSIONS: Embedding vector dimensions (default: 1536)

Design Decisions:
    - Collection: "textbook-chapters"
    - Vector dimensions: 1536 (OpenAI text-embedding-3-small)
    - Distance metric: COSINE (standard for semantic similarity)
    - HNSW config: M=16, ef_construction=100 (balance speed vs quality)
    - Payload schema: chapter_id, chunk_id, text, metadata

Constitution Compliance:
    - Rule I: 100% type hints, formatted with Black
    - Rule V: Credentials from environment variables only
"""

import os
import sys
from typing import Any

from dotenv import load_dotenv
from qdrant_client import QdrantClient

# Load environment variables from .env file
load_dotenv()
from qdrant_client.models import (
    Distance,
    HnswConfigDiff,
    OptimizersConfigDiff,
    PointStruct,
    VectorParams,
)


def get_env_var(key: str, default: str | None = None) -> str:
    """
    Get environment variable or raise error if not set.

    Args:
        key: Environment variable name
        default: Default value if env var not set (None means required)

    Returns:
        Environment variable value

    Raises:
        ValueError: If required environment variable not set
    """
    value = os.getenv(key, default)
    if value is None:
        raise ValueError(
            f"Environment variable {key} is required. "
            f"Set it in .env file or export it in your shell."
        )
    return value


def create_qdrant_collection() -> None:
    """
    Create and configure Qdrant collection for textbook chapter embeddings.

    Raises:
        Exception: If collection creation fails
    """
    print("=" * 80)
    print("Qdrant Collection Setup for RAG Pipeline")
    print("=" * 80)

    # Load environment variables
    print("\n[1/5] Loading environment variables...")
    qdrant_url = get_env_var("QDRANT_URL")
    qdrant_api_key = get_env_var("QDRANT_API_KEY")
    collection_name = get_env_var("VECTOR_COLLECTION_NAME", "textbook-chapters")
    embedding_dimensions = int(get_env_var("EMBEDDING_DIMENSIONS", "1536"))

    print(f"  ✓ QDRANT_URL: {qdrant_url}")
    print(f"  ✓ Collection name: {collection_name}")
    print(f"  ✓ Embedding dimensions: {embedding_dimensions}")

    # Initialize Qdrant client
    print("\n[2/5] Connecting to Qdrant instance...")
    client = QdrantClient(
        url=qdrant_url,
        api_key=qdrant_api_key,
        timeout=60,
        prefer_grpc=False,  # Use HTTP instead of gRPC for better Windows compatibility
    )

    try:
        # Test connection
        collections = client.get_collections()
        print(f"  ✓ Connected successfully ({len(collections.collections)} collections exist)")
    except Exception as e:
        print(f"  ✗ Connection failed: {e}")
        sys.exit(1)

    # Check if collection already exists
    print(f"\n[3/5] Checking if collection '{collection_name}' exists...")
    collection_exists = False
    try:
        client.get_collection(collection_name)
        collection_exists = True
        print(f"  ⚠ Collection '{collection_name}' already exists")
    except Exception:
        print(f"  ✓ Collection '{collection_name}' does not exist (ready to create)")

    # Create collection if it doesn't exist
    if collection_exists:
        print("\n[4/5] Skipping collection creation (already exists)")
        print("\nOptions:")
        print("  1. Delete existing collection: client.delete_collection(collection_name)")
        print("  2. Use existing collection as-is")
        print("  3. Rename VECTOR_COLLECTION_NAME in .env to create a new collection")
    else:
        print(f"\n[4/5] Creating collection '{collection_name}'...")

        # Collection configuration (per FR-003 and implementation plan)
        vector_config = VectorParams(
            size=embedding_dimensions,
            distance=Distance.COSINE,  # COSINE distance for semantic similarity
        )

        # HNSW (Hierarchical Navigable Small World) index configuration
        # - M=16: Number of bi-directional links (higher = better quality, more memory)
        # - ef_construction=100: Search depth during construction (higher = better quality, slower)
        # These values balance search speed vs quality for RAG use case
        hnsw_config = HnswConfigDiff(
            m=16,  # Number of edges per node (default: 16, range: 4-64)
            ef_construct=100,  # Construction-time search depth (default: 100, range: 4-512)
        )

        # Optimizer configuration for write performance
        optimizers_config = OptimizersConfigDiff(
            indexing_threshold=20000,  # Start indexing after 20k vectors
            memmap_threshold=50000,  # Use memory-mapped storage after 50k vectors
        )

        try:
            client.create_collection(
                collection_name=collection_name,
                vectors_config=vector_config,
                hnsw_config=hnsw_config,
                optimizers_config=optimizers_config,
            )
            print(f"  ✓ Collection '{collection_name}' created successfully")
            print("    - Distance metric: COSINE")
            print(f"    - Vector dimensions: {embedding_dimensions}")
            print("    - HNSW config: M=16, ef_construct=100")
        except Exception as e:
            print(f"  ✗ Collection creation failed: {e}")
            sys.exit(1)

    # Create payload indexes for fast filtering (FR-002: filter by chapter_id)
    print("\n[5/5] Creating payload indexes...")
    try:
        # Index on chapter_id for fast filtering by chapter
        # Supports queries like: filter={"chapter_id": "chapter-01"}
        client.create_payload_index(
            collection_name=collection_name,
            field_name="chapter_id",
            field_schema="keyword",  # Exact match index for string IDs
        )
        print("  ✓ Created index on 'chapter_id' (keyword)")

        # Index on chunk_id for deduplication checks
        client.create_payload_index(
            collection_name=collection_name,
            field_name="chunk_id",
            field_schema="keyword",
        )
        print("  ✓ Created index on 'chunk_id' (keyword)")

        print("\nPayload indexes created successfully!")
    except Exception as e:
        # Index creation might fail if indexes already exist (non-fatal)
        print(f"  ⚠ Index creation warning: {e}")
        print("    (Indexes may already exist)")

    # Get collection info
    print("\n" + "=" * 80)
    print("Collection Setup Summary")
    print("=" * 80)
    collection_info = client.get_collection(collection_name)
    print(f"Collection: {collection_name}")
    print(f"Status: {collection_info.status}")
    print(f"Vectors: {collection_info.points_count:,}")
    print(f"Indexed vectors: {collection_info.indexed_vectors_count:,}")
    print(f"Vector size: {collection_info.config.params.vectors.size}")
    print(f"Distance: {collection_info.config.params.vectors.distance}")

    # Print next steps
    print("\n" + "=" * 80)
    print("Next Steps")
    print("=" * 80)
    print("1. Ingest textbook chapter embeddings:")
    print("   - Chunk textbook chapters into ~500-token segments")
    print("   - Generate embeddings using OpenAI text-embedding-3-small")
    print("   - Upload to Qdrant using client.upsert()")
    print("\n2. Example payload schema:")
    print("   {")
    print('     "chapter_id": "chapter-01",')
    print('     "chunk_id": "chapter-01-chunk-0001",')
    print('     "text": "Introduction to Physical AI...",')
    print('     "metadata": {')
    print('       "chapter_title": "Introduction to Physical AI",')
    print('       "section": "1.1 What is Physical AI?",')
    print('       "page_number": 15')
    print("     }")
    print("   }")
    print("\n3. Test vector search:")
    print("   python scripts/test_qdrant_search.py")
    print("\n" + "=" * 80)
    print("Setup Complete!")
    print("=" * 80)


def main() -> None:
    """Main entry point."""
    # Set UTF-8 encoding for Windows console
    if sys.platform == "win32":
        import io

        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

    try:
        create_qdrant_collection()
    except ValueError as e:
        print(f"\n[ERROR] Configuration Error: {e}")
        print("\nMake sure .env file exists with required variables:")
        print("  QDRANT_URL=https://your-instance.cloud.qdrant.io")
        print("  QDRANT_API_KEY=your-api-key-here")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
