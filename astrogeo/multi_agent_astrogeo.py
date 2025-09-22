import gradio as gr
import os
import sys
from pathlib import Path
from datetime import datetime
import requests
import chromadb
from sentence_transformers import SentenceTransformer
import json

# Add src to path
sys.path.append('src')

# NASA API Key
NASA_API_KEY = os.getenv('NASA_API_KEY', 'DEMO_KEY')

class BaseAgent:
    """Base agent class for all specialized agents"""
    def __init__(self, name, role, capabilities):
        self.name = name
        self.role = role
        self.capabilities = capabilities
    
    def can_handle(self, query):
        """Check if this agent can handle the query"""
        return False
    
    def process(self, query):
        """Process the query and return response"""
        return "Agent not implemented"

class ISROGeospatialAgent(BaseAgent):
    """ISRO and Bhuvan geospatial specialist agent"""
    def __init__(self, vector_store):
        super().__init__(
            name="ISRO Geospatial Expert",
            role="Specialist in ISRO missions, Bhuvan platform, and Indian space technology",
            capabilities=["ISRO missions", "Bhuvan platform", "SAPHIR instrument", "OCM data", "Indian satellites"]
        )
        self.vector_store = vector_store
    
    def can_handle(self, query):
        query_lower = query.lower()
        keywords = ['isro', 'bhuvan', 'saphir', 'ocm', 'chandrayaan', 'mangalyaan', 'indian space', 'aryabhatta']
        return any(keyword in query_lower for keyword in keywords)
    
    def process(self, query):
        # Search vector database for ISRO-specific content
        results = self.vector_store.search_vector_db(query, k=5)
        
        if results and any(keyword in result['content'].lower() for result in results for keyword in ['isro', 'bhuvan', 'saphir', 'ocm']):
            response = f"🇮🇳 **{self.name} Analysis**:\n\n"
            
            for i, result in enumerate(results[:3], 1):
                content = result['content'][:250] + "..." if len(result['content']) > 250 else result['content']
                response += f"**{i}.** {content}\n\n"
            
            # Add contextual information
            if 'bhuvan' in query.lower():
                response += """**About Bhuvan**: India's geoportal developed by ISRO for satellite imagery and geospatial services, supporting applications in agriculture, disaster management, and urban planning."""
            
            return response
        else:
            # Fallback knowledge
            return self._get_fallback_knowledge(query)
    
    def _get_fallback_knowledge(self, query):
        query_lower = query.lower()
        
        if 'bhuvan' in query_lower:
            return """🇮🇳 **ISRO Bhuvan Platform**:

**Bhuvan** is India's comprehensive geospatial platform providing:
• High-resolution satellite imagery of India and global locations
• Thematic mapping for agriculture, forestry, and urban planning
• Disaster management and emergency response capabilities
• APIs for developers and government services
• Mobile applications for citizen services

**Key Instruments**:
• **SAPHIR**: Atmospheric humidity profiling
• **OCM**: Ocean color monitoring for marine studies
• **Cartosat series**: High-resolution Earth imaging
• **ResourceSat**: Natural resource monitoring"""
        
        elif 'isro' in query_lower:
            return """🇮🇳 **ISRO - Indian Space Research Organisation**:

**Established**: 1969, Headquarters: Bengaluru

**Major Achievements**:
• **Chandrayaan-3**: First successful lunar south pole landing (2023)
• **Mangalyaan**: Mars orbit mission for just $74 million
• **Record Launch**: 104 satellites in single mission (2017)
• **Aryabhatta**: India's first satellite (1975)

**Current Programs**:
• **Gaganyaan**: Human spaceflight mission
• **Aditya-L1**: Solar observation mission
• **Shukrayaan**: Planned Venus mission"""
        
        else:
            return "Please specify which aspect of ISRO or Bhuvan you'd like to know about."

class NASALiveDataAgent(BaseAgent):
    """NASA live data specialist agent"""
    def __init__(self):
        super().__init__(
            name="NASA Live Data Specialist",
            role="Real-time NASA data access and analysis",
            capabilities=["APOD", "Solar activity", "Mars rover data", "Asteroid tracking"]
        )
    
    def can_handle(self, query):
        query_lower = query.lower()
        live_keywords = ['today', 'current', 'now', 'recent', 'live', 'latest']
        nasa_keywords = ['nasa', 'apod', 'picture', 'mars rover', 'solar', 'asteroid']
        return any(live in query_lower for live in live_keywords) and any(nasa in query_lower for nasa in nasa_keywords)
    
    def process(self, query):
        query_lower = query.lower()
        response = f"📡 **{self.name} Report**:\n\n"
        
        try:
            # Solar activity
            if any(term in query_lower for term in ['solar', 'space weather', 'flare', 'sun']):
                solar_data = self._get_solar_activity()
                response += solar_data
            
            # APOD
            elif any(term in query_lower for term in ['apod', 'picture', 'image']) and 'mars' not in query_lower:
                apod_data = self._get_apod()
                response += apod_data
            
            # Mars rover
            elif 'mars' in query_lower and any(term in query_lower for term in ['rover', 'photo', 'image']):
                mars_data = self._get_mars_photos()
                response += mars_data
            
            # Asteroids
            elif any(term in query_lower for term in ['asteroid', 'space rock']):
                asteroid_data = self._get_asteroid_data()
                response += asteroid_data
            
            else:
                response += "I can provide live data on: Solar activity, NASA's daily space picture, Mars rover photos, or asteroid tracking. Please specify!"
            
            return response
            
        except Exception as e:
            return f"❌ Unable to fetch live NASA data: {str(e)}"
    
    def _get_solar_activity(self):
        response = requests.get("https://api.nasa.gov/DONKI/FLR", params={"api_key": NASA_API_KEY}, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data:
            return "☀️ **Solar Status**: The Sun is currently calm with no major flare activity - completely normal!"
        
        flare = data[0]
        flare_class = flare.get('classType', 'Unknown')
        peak_time = flare.get('peakTime', 'Unknown')
        
        intensity_map = {
            'X': ("🔥 **Major Solar Flare**", "Can affect satellites and create spectacular auroras!"),
            'M': ("⚡ **Moderate Solar Flare**", "May cause minor radio disruptions and enhance auroras."),
            'C': ("✨ **Minor Solar Flare**", "Minimal Earth impact but scientifically interesting!")
        }
        
        intensity, impact = intensity_map.get(flare_class[0] if flare_class else 'C', ("🌟 **Solar Activity**", "Energy release detected."))
        
        return f"""☀️ **Live Solar Weather**:
{intensity} (Class {flare_class})
**Peak Time**: {peak_time}
**Impact**: {impact}
**Status**: Continuously monitored by NASA for space weather alerts."""
    
    def _get_apod(self):
        response = requests.get("https://api.nasa.gov/planetary/apod", params={"api_key": NASA_API_KEY}, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        title = data.get('title', 'Unknown')
        explanation = data.get('explanation', '')[:200] + "..." if len(data.get('explanation', '')) > 200 else data.get('explanation', '')
        url = data.get('url', '')
        
        return f"""🌟 **Today's Space Highlight**: {title}
**About**: {explanation}
**View**: {url}"""
    
    def _get_mars_photos(self):
        response = requests.get(
            "https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos",
            params={"sol": 1000, "api_key": NASA_API_KEY},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        photos = data.get('photos', [])
        if not photos:
            return "🔴 **Mars Update**: Curiosity is busy with science - no photos from this sol!"
        
        result = "🔴 **Live from Mars**:\n"
        for i, photo in enumerate(photos[:2], 1):
            result += f"**Photo {i}**: {photo.get('earth_date')} - {photo.get('camera', {}).get('full_name', 'Unknown')}\n{photo.get('img_src', '')}\n\n"
        
        return result
    
    def _get_asteroid_data(self):
        response = requests.get("https://api.nasa.gov/neo/rest/v1/feed", params={"api_key": NASA_API_KEY}, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        total = sum(len(asteroids) for asteroids in data.get('near_earth_objects', {}).values())
        hazardous = sum(1 for asteroids in data.get('near_earth_objects', {}).values() 
                       for asteroid in asteroids if asteroid.get('is_potentially_hazardous_asteroid'))
        
        return f"""🌌 **Asteroid Watch**: Tracking {total} near-Earth objects
{'⚠️' if hazardous > 0 else '✅'} **Hazardous**: {hazardous} (closely monitored)
🛡️ **Defense**: NASA's planetary defense systems active"""

class SpaceWeatherAgent(BaseAgent):
    """Space weather monitoring agent"""
    def __init__(self):
        super().__init__(
            name="Space Weather Monitor",
            role="Space weather analysis and Earth impact assessment",
            capabilities=["Solar activity", "Geomagnetic storms", "Radiation levels", "Satellite safety"]
        )
    
    def can_handle(self, query):
        query_lower = query.lower()
        return any(term in query_lower for term in ['space weather', 'solar wind', 'geomagnetic', 'aurora', 'solar storm'])
    
    def process(self, query):
        return f"☀️ **{self.name}**: Space weather analysis with solar activity monitoring, geomagnetic storm tracking, and satellite impact assessment."

class GeospatialAgent(BaseAgent):
    """Geospatial and Earth observation agent"""
    def __init__(self, vector_store):
        super().__init__(
            name="Geospatial Intelligence Expert",
            role="Satellite imagery and Earth observation analysis",
            capabilities=["Satellite imagery", "Remote sensing", "GIS analysis", "Environmental monitoring"]
        )
        self.vector_store = vector_store
    
    def can_handle(self, query):
        query_lower = query.lower()
        return any(term in query_lower for term in ['satellite', 'imagery', 'remote sensing', 'gis', 'earth observation', 'landsat', 'sentinel'])
    
    def process(self, query):
        return f"🛰️ **{self.name}**: Satellite imagery analysis, remote sensing data processing, and environmental monitoring using advanced GIS techniques."

class QueryRouter:
    """Intelligent query router that decides which agent should handle the query"""
    def __init__(self):
        self.space_keywords = [
            'space', 'astronomy', 'planet', 'star', 'galaxy', 'nasa', 'isro', 'esa', 
            'satellite', 'rocket', 'mars', 'moon', 'sun', 'solar', 'asteroid', 
            'comet', 'telescope', 'rover', 'spacecraft', 'orbit', 'mission', 
            'apollo', 'chandrayaan', 'bhuvan', 'saphir', 'ocm', 'cosmic', 
            'universe', 'celestial', 'nebula', 'meteor', 'spacex', 'apod'
        ]
    
    def is_space_query(self, query):
        """Check if query is space-related"""
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in self.space_keywords)
    
    def identify_non_space_domain(self, query):
        """Identify what domain a non-space query belongs to"""
        query_lower = query.lower()
        
        if any(term in query_lower for term in ['weather in', 'temperature in', 'climate in']):
            return "weather/climate"
        elif any(term in query_lower for term in ['news', 'current events']):
            return "news"
        elif any(term in query_lower for term in ['movie', 'film', 'entertainment']):
            return "entertainment"
        elif any(term in query_lower for term in ['food', 'restaurant', 'recipe']):
            return "food/dining"
        elif any(term in query_lower for term in ['travel', 'hotel', 'flight']):
            return "travel"
        else:
            return "general information"
    
    def route_query(self, query, agents):
        """Route query to appropriate agent"""
        if not self.is_space_query(query):
            domain = self.identify_non_space_domain(query)
            return {
                'agent': None,
                'message': f"🤖 I'm AstroGeo, specialized in space and astronomy topics. Your query appears to be about {domain}. Please ask me about space agencies, planets, satellites, missions, or astronomical phenomena!",
                'suggestions': [
                    "What's today's NASA picture?",
                    "Tell me about ISRO missions",
                    "Current solar activity",
                    "Mars exploration updates"
                ]
            }
        
        # Find the best agent for space queries
        for agent in agents:
            if agent.can_handle(query):
                return {
                    'agent': agent,
                    'message': None,
                    'suggestions': []
                }
        
        # Default space knowledge
        return {
            'agent': None,
            'message': "🌌 I can help with space topics! Try asking about specific space agencies (NASA, ISRO), planets, missions, or current space events.",
            'suggestions': [
                "What is the International Space Station?",
                "Tell me about Mars rovers",
                "ISRO's recent achievements",
                "Current space missions"
            ]
        }

class IntelligentAstroGeoSystem:
    """Main system that coordinates all agents"""
    def __init__(self):
        print("🚀 AstroGeo Intelligent Multi-Agent System")
        print(f"NASA API: {'✅ Configured' if NASA_API_KEY != 'DEMO_KEY' else '⚠️ Using DEMO'}")
        
        # Initialize vector database
        self.vector_store = self._initialize_vector_db()
        
        # Initialize query router
        self.router = QueryRouter()
        
        # Initialize all agents
        self.agents = [
            ISROGeospatialAgent(self),
            NASALiveDataAgent(),
            SpaceWeatherAgent(),
            GeospatialAgent(self)
        ]
        
        print(f"✅ Initialized {len(self.agents)} specialized agents")
    
    def _initialize_vector_db(self):
        """Initialize vector database"""
        try:
            vector_db_path = "data/vector_store/vector_db"
            chroma_client = chromadb.PersistentClient(path=vector_db_path)
            collections = chroma_client.list_collections()
            
            if collections:
                collection = collections[0]
                embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
                print(f"✅ Vector DB connected: {collection.name}")
                
                class VectorStore:
                    def __init__(self, client, collection, model):
                        self.client = client
                        self.collection = collection
                        self.embedding_model = model
                    
                    def search_vector_db(self, query, k=3):
                        query_embedding = self.embedding_model.encode([query])
                        results = self.collection.query(
                            query_embeddings=query_embedding.tolist(),
                            n_results=k,
                            include=['documents', 'distances']
                        )
                        
                        documents = []
                        if results and results['documents'] and results['documents'][0]:
                            for i, doc in enumerate(results['documents'][0]):
                                score = 1 - results['distances'][0][i] if results['distances'][0] else 0
                                if score > 0.3:
                                    documents.append({'content': doc, 'score': score})
                        return documents
                
                return VectorStore(chroma_client, collection, embedding_model)
            
        except Exception as e:
            print(f"⚠️ Vector DB not available: {e}")
            return None
    
    def search_vector_db(self, query, k=3):
        """Wrapper for vector database search"""
        if self.vector_store:
            return self.vector_store.search_vector_db(query, k)
        return []
    
    def process_query(self, query, use_nasa_api, progress=gr.Progress()):
        """Main query processing with intelligent agent routing"""
        if not query.strip():
            return """🤖 **Welcome to AstroGeo!**

I'm your intelligent space assistant with specialized agents for:
• 🇮🇳 **ISRO & Bhuvan**: Indian space missions and geospatial data
• 📡 **NASA Live Data**: Real-time space information
• ☀️ **Space Weather**: Solar activity and space environment
• 🛰️ **Geospatial Intelligence**: Satellite imagery and Earth observation

Ask me anything about space, astronomy, or space agencies!"""
        
        try:
            progress(0.1, desc="Analyzing query...")
            
            # Route the query
            routing_result = self.router.route_query(query, self.agents)
            
            response = f"🧠 **AstroGeo Multi-Agent Analysis**\n\n"
            response += f"**Your Query**: {query}\n\n"
            
            if routing_result['agent'] is None:
                # Non-space query or needs clarification
                response += routing_result['message']
                
                if routing_result['suggestions']:
                    response += "\n\n**🎯 Try these space topics instead:**\n"
                    for suggestion in routing_result['suggestions']:
                        response += f"• {suggestion}\n"
                
                return response
            
            # Process with selected agent
            agent = routing_result['agent']
            progress(0.5, desc=f"Consulting {agent.name}...")
            
            response += f"**Assigned Agent**: {agent.name}\n"
            response += f"**Agent Role**: {agent.role}\n\n"
            
            # Agent processes the query
            agent_response = agent.process(query)
            response += agent_response
            
            progress(1.0, desc="Analysis complete!")
            return response
            
        except Exception as e:
            return f"❌ System Error: {str(e)}\n\nPlease try rephrasing your space-related query!"

def create_agent_interface():
    system = IntelligentAstroGeoSystem()
    
    with gr.Blocks(title="AstroGeo - Multi-Agent Space Intelligence", theme=gr.themes.Soft()) as demo:
        
        gr.Markdown("""
        # 🤖 AstroGeo - Multi-Agent Space Intelligence System
        **Intelligent Query Routing | Specialized AI Agents | Real-time Space Data**
        
        I automatically route your queries to the most appropriate specialist agent!
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                query_input = gr.Textbox(
                    label="🔍 Ask me about space (I'll route to the right expert)",
                    placeholder="Try: 'What is Bhuvan?', 'Today's solar activity', 'Weather in Mumbai', 'Mars rover status'",
                    lines=2
                )
                
                use_nasa_api = gr.Checkbox(
                    label="📡 Enable live NASA data",
                    value=True
                )
                
                ask_btn = gr.Button("🤖 Multi-Agent Analysis", variant="primary", size="lg")
            
            with gr.Column(scale=1):
                status = gr.Textbox(
                    label="🤖 Agent System Status",
                    value=f"""🧠 Smart Query Routing Active
🇮🇳 ISRO/Bhuvan Expert Ready
📡 NASA Live Data Agent Ready
☀️ Space Weather Monitor Ready
🛰️ Geospatial Expert Ready
✅ All {len(system.agents)} Agents Online""",
                    lines=8,
                    interactive=False
                )
        
        with gr.Row():
            output = gr.Textbox(
                label="🤖 Multi-Agent Analysis Results",
                lines=25,
                interactive=False
            )
        
        gr.Markdown("### 🎯 Test Different Agent Routing")
        with gr.Row():
            examples = [
                gr.Button("🇮🇳 What is Bhuvan?", size="sm"),
                gr.Button("📡 Today's NASA picture", size="sm"),
                gr.Button("☀️ Current solar activity", size="sm"),
                gr.Button("🌤️ Weather in Mumbai", size="sm")
            ]
        
        ask_btn.click(
            fn=system.process_query,
            inputs=[query_input, use_nasa_api],
            outputs=[output]
        )
        
        example_queries = [
            "What is Bhuvan platform?",
            "What's today's NASA astronomy picture?", 
            "What's the current solar activity?",
            "What's the weather in Mumbai?"
        ]
        
        for btn, query in zip(examples, example_queries):
            btn.click(lambda q=query: q, outputs=[query_input])
        
        gr.Markdown("""
        ---
        **🤖 Multi-Agent Intelligence**: Automatic routing to specialized experts | **🧠 Smart**: Handles both space and non-space queries appropriately
        """)
    
    return demo

if __name__ == "__main__":
    demo = create_agent_interface()
    print("🤖 Launching Multi-Agent AstroGeo System...")
    demo.launch(server_port=7863, share=False)
