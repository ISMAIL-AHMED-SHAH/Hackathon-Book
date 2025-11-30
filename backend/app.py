"""
Hugging Face Spaces entry point with Gradio wrapper for FastAPI backend.
This allows the backend to run on HF Spaces while maintaining API endpoints.
"""
import gradio as gr
import uvicorn
from threading import Thread
from src.api.main import app as fastapi_app
import httpx
import os

# Get the base URL for API calls
API_BASE_URL = os.getenv("SPACE_HOST", "http://localhost:7860")


def query_rag(question: str, chapter_id: str = "") -> dict:
    """Query the RAG backend via internal API call."""
    try:
        url = f"{API_BASE_URL}/v1/query"
        payload = {
            "query_text": question,
            "chapter_id": chapter_id if chapter_id else None,
            "user_id": "hf-spaces-demo-user",
        }

        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()

            # Format the response nicely
            answer = result.get("answer", "No answer generated")
            sources = result.get("sources", [])
            confidence = result.get("confidence_score", 0)

            sources_text = "\n\n**Sources:**\n"
            for i, source in enumerate(sources[:3], 1):
                excerpt = source.get("content_excerpt", "")
                score = source.get("similarity_score", 0)
                sources_text += f"{i}. (Score: {score:.2f}) {excerpt[:200]}...\n\n"

            return {
                "answer": answer,
                "metadata": f"**Confidence:** {confidence:.2f}\n{sources_text}",
            }
    except Exception as e:
        return {
            "answer": f"Error querying backend: {str(e)}",
            "metadata": "Please check if the backend is running properly.",
        }


def gradio_interface(question: str, chapter_filter: str = "") -> tuple:
    """Gradio interface wrapper."""
    result = query_rag(question, chapter_filter)
    return result["answer"], result["metadata"]


# Start FastAPI in background thread
def start_fastapi():
    uvicorn.run(fastapi_app, host="0.0.0.0", port=7860, log_level="info")


# Create Gradio interface
with gr.Blocks(title="Physical AI Textbook RAG Query") as demo:
    gr.Markdown(
        """
    # 🤖 Physical AI Textbook - RAG Query Interface

    Ask questions about Physical AI, Humanoid Robotics, ROS 2, and Isaac Sim!

    **API Endpoint:** Access the raw API at `/v1/query` for programmatic queries.
    """
    )

    with gr.Row():
        with gr.Column():
            question_input = gr.Textbox(
                label="Your Question", placeholder="e.g., What are ROS 2 nodes?", lines=3
            )
            chapter_input = gr.Textbox(
                label="Chapter Filter (optional)", placeholder="e.g., ch-ros2-nodes", lines=1
            )
            submit_btn = gr.Button("Ask Question", variant="primary")

        with gr.Column():
            answer_output = gr.Textbox(label="Answer", lines=10, interactive=False)
            metadata_output = gr.Textbox(label="Sources & Metadata", lines=8, interactive=False)

    gr.Examples(
        examples=[
            ["What are ROS 2 nodes?", ""],
            ["Explain humanoid robot kinematics", ""],
            ["How does Isaac Sim work?", "ch-isaac-sim"],
        ],
        inputs=[question_input, chapter_input],
    )

    submit_btn.click(
        fn=gradio_interface,
        inputs=[question_input, chapter_input],
        outputs=[answer_output, metadata_output],
    )

if __name__ == "__main__":
    # Start FastAPI in background
    api_thread = Thread(target=start_fastapi, daemon=True)
    api_thread.start()

    # Launch Gradio interface (shares same port with FastAPI)
    demo.queue().launch(server_name="0.0.0.0", server_port=7860, share=False)
