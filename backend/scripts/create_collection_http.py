"""
Create Qdrant collection using HTTP API directly.

This bypasses any gRPC/client library issues on Windows.
"""

import json
import os
import sys

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def main() -> None:
    """Create collection using HTTP API."""
    # Set UTF-8 encoding for Windows console
    if sys.platform == "win32":
        import io

        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    collection_name = os.getenv("VECTOR_COLLECTION_NAME", "textbook-chapters")
    embedding_dim = int(os.getenv("EMBEDDING_DIMENSIONS", "1536"))

    print(f"Creating collection '{collection_name}'...")
    print(f"Qdrant URL: {qdrant_url}")

    # Collection configuration
    payload = {
        "vectors": {
            "size": embedding_dim,
            "distance": "Cosine",
        },
        "hnsw_config": {"m": 16, "ef_construct": 100},
        "optimizers_config": {
            "indexing_threshold": 20000,
            "memmap_threshold": 50000,
        },
    }

    # Create collection via HTTP PUT
    url = f"{qdrant_url}/collections/{collection_name}"
    headers = {"api-key": qdrant_api_key, "Content-Type": "application/json"}

    try:
        response = requests.put(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        print(f"✓ Collection '{collection_name}' created successfully!")
        print(json.dumps(response.json(), indent=2))
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 409:
            print(f"⚠ Collection '{collection_name}' already exists")
        else:
            print(f"✗ HTTP Error: {e}")
            print(f"Response: {e.response.text}")
            sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)

    # Create payload indexes
    print("\nCreating payload indexes...")

    # Index on chapter_id
    index_url = f"{qdrant_url}/collections/{collection_name}/index"
    index_payload = {"field_name": "chapter_id", "field_schema": "keyword"}

    try:
        response = requests.put(index_url, headers=headers, json=index_payload, timeout=30)
        response.raise_for_status()
        print("✓ Created index on 'chapter_id'")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 409:
            print("⚠ Index on 'chapter_id' already exists")
        else:
            print(f"⚠ Index creation failed: {e.response.text}")

    # Index on chunk_id
    index_payload = {"field_name": "chunk_id", "field_schema": "keyword"}

    try:
        response = requests.put(index_url, headers=headers, json=index_payload, timeout=30)
        response.raise_for_status()
        print("✓ Created index on 'chunk_id'")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 409:
            print("⚠ Index on 'chunk_id' already exists")
        else:
            print(f"⚠ Index creation failed: {e.response.text}")

    print("\n✓ Collection setup complete!")


if __name__ == "__main__":
    main()
