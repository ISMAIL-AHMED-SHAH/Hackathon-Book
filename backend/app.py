"""
Hugging Face Spaces entry point for FastAPI RAG backend.

This file runs the FastAPI application directly on Hugging Face Spaces.
No Gradio wrapper - pure FastAPI for API endpoints.
"""

import os
import uvicorn
from src.api.main import app

if __name__ == "__main__":
    # Get port from environment (HF Spaces uses 7860)
    port = int(os.getenv("PORT", "7860"))
    host = os.getenv("HOST", "0.0.0.0")

    # Run FastAPI with uvicorn
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True,
    )
