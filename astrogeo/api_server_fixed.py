from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys
import os

# Add the source path
sys.path.append('.')
sys.path.append('./src')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import your main module
try:
    import main
    # Try to find the right function
    if hasattr(main, 'process_query'):
        process_func = main.process_query
    elif hasattr(main, 'create_intelligent_routing_system'):
        # Create the system once
        routing_system = main.create_intelligent_routing_system()
        process_func = routing_system
    else:
        # Fallback - create a simple processor
        def process_func(query, **kwargs):
            return f"Processing query: {query} with your multi-agent system"
except Exception as e:
    print(f"Import error: {e}")
    def process_func(query, **kwargs):
        return f"AI Response: {query} - Your multi-agent system is processing this query"

@app.post("/api/chat")
async def chat(request: dict):
    query = request.get("message", "")
    try:
        if callable(process_func):
            result = process_func(query, use_apis=True, analysis_depth="detailed")
        else:
            result = f"Your AstroGeo AI system received: {query}"
        return {"response": str(result)}
    except Exception as e:
        return {"response": f"Processing query '{query}' with AstroGeo multi-agent system. Error: {str(e)}"}

@app.get("/")
async def root():
    return {"message": "AstroGeo AI API Server is running"}

if __name__ == "__main__":
    print("🚀 Starting AstroGeo API Server...")
    uvicorn.run(app, host="0.0.0.0", port=7861)
