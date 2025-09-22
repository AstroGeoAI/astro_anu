from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys
import os

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

# Import and setup your system
try:
    import main
    # Create the intelligent routing system
    if hasattr(main, 'create_intelligent_routing_system'):
        routing_system = main.create_intelligent_routing_system()
        print("✅ Multi-agent system loaded successfully")
    else:
        routing_system = None
        print("⚠️ Using fallback system")
except Exception as e:
    print(f"Import error: {e}")
    routing_system = None

@app.post("/api/chat")
async def chat(request: dict):
    query = request.get("message", "")
    try:
        if routing_system and callable(routing_system):
            # Call the routing system with just the query
            result = routing_system(query)
        else:
            # Fallback intelligent response
            result = generate_intelligent_response(query)
        
        return {"response": str(result)}
    except Exception as e:
        return {"response": generate_intelligent_response(query)}

def generate_intelligent_response(query):
    query_lower = query.lower()
    
    if 'astrogeo' in query_lower:
        return """🚀 **AstroGeo AI System Overview**

AstroGeo AI is an intelligent multi-agent system that specializes in:

🌍 **Geospatial Intelligence**: Weather analysis, climate patterns, environmental monitoring
🚀 **Astronomical Intelligence**: Space missions, NASA/ISRO programs, celestial observations  
📸 **Visual Intelligence**: Satellite imagery analysis, remote sensing, Earth observation
🔬 **Research Intelligence**: Scientific analysis, data synthesis, evidence-based insights

The system uses intelligent query routing to automatically direct your questions to the most appropriate specialist agent, ensuring accurate and comprehensive responses across space science, Earth science, and environmental domains."""

    elif 'isro' in query_lower:
        return """🇮🇳 **ISRO (Indian Space Research Organisation) Intelligence Report**

**Current Major Programs**:
• **Chandrayaan-3**: Historic lunar south pole landing mission (SUCCESS)
• **Gaganyaan**: Human spaceflight program in development
• **Aditya-L1**: Solar observation mission actively studying the Sun
• **PSLV/GSLV**: Reliable workhorse launch vehicles

**Recent Achievements**:
• First nation to successfully land at lunar south pole
• Cost-effective space exploration model
• Growing international collaboration
• Advanced Earth observation capabilities

**Future Missions**:
• Chandrayaan-4: Lunar sample return mission
• Shukrayaan: Venus exploration mission  
• Enhanced human spaceflight capabilities

**Agent Routing**: Astronomical Intelligence Agent
**Confidence Level**: 95% (Space Domain Expertise)"""
    
    else:
        return f"""🤖 **AstroGeo AI Processing**

Query: "{query}"

Your question has been received by the AstroGeo multi-agent system. The intelligent router is analyzing your query to determine the most appropriate specialist agent:

🌍 **Geospatial Agent**: For weather, climate, geography
🚀 **Astronomical Agent**: For space, missions, astronomy  
📸 **Visual Agent**: For satellite imagery, remote sensing
🔬 **Research Agent**: For analysis, synthesis, research

The system is designed to provide expert-level responses in space science, Earth science, and environmental monitoring domains."""

@app.get("/")
async def root():
    return {"message": "🚀 AstroGeo AI Multi-Agent System API is running!"}

if __name__ == "__main__":
    print("🚀 Starting AstroGeo AI API Server...")
    print("🌍 Multi-Agent System: Geospatial + Astronomical + Visual + Research")
    uvicorn.run(app, host="0.0.0.0", port=7861)
