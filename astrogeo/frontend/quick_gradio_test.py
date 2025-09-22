import gradio as gr
import os
from pathlib import Path

def test_astrogeo(query):
    # Simple response for now
    vector_db_path = Path("data/vector_store/vector_db")
    
    if vector_db_path.exists():
        files = len(list(vector_db_path.glob("*")))
        return f"🚀 AstroGeo Response: {query}\n\n✅ Vector DB connected ({files} files found)\n\n[This is a test response - full system loading...]"
    else:
        return f"❌ Vector DB not found at {vector_db_path}"

# Create interface
demo = gr.Interface(
    fn=test_astrogeo,
    inputs=gr.Textbox(placeholder="Ask about space or astronomy..."),
    outputs=gr.Textbox(),
    title="🚀 AstroGeo - Quick Test",
    description="Testing AstroGeo with your existing vector database"
)

if __name__ == "__main__":
    demo.launch(server_port=7860)
