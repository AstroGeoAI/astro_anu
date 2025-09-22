from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys
sys.path.append('.')
from main import process_query

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/chat")
async def chat(request: dict):
    query = request.get("message", "")
    try:
        # Use your actual multi-agent system
        result = process_query(query, use_apis=True, analysis_depth="detailed")
        return {"response": result}
    except Exception as e:
        return {"response": f"Error processing query: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7861)
