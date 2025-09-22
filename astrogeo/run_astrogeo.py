import gradio as gr
import os
import sys
from pathlib import Path
from datetime import datetime
import requests
import chromadb
from sentence_transformers import SentenceTransformer

# Add src to path
sys.path.append('src')

# NASA API Key
NASA_API_KEY = os.getenv('NASA_API_KEY', 'DEMO_KEY')

class IntelligentAstroGeo:
    def __init__(self):
        print("🚀 AstroGeo Intelligent System")
        print(f"NASA API: {'✅ Configured' if NASA_API_KEY != 'DEMO_KEY' else '⚠️ Using DEMO'}")
        
        # Initialize vector database
        self.vector_db_path = "data/vector_store/vector_db"
        self.chroma_client = None
        self.collection = None
        self.embedding_model = None
        self.initialize_vector_db()
    
    def initialize_vector_db(self):
        """Initialize vector database connection"""
        try:
            self.chroma_client = chromadb.PersistentClient(path=self.vector_db_path)
            collections = self.chroma_client.list_collections()
            if collections:
                self.collection = collections[0]
                print(f"✅ Vector DB connected: {self.collection.name}")
            
            self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            print("✅ Embedding model loaded")
        except Exception as e:
            print(f"⚠️ Vector DB not available: {e}")
    
    def search_vector_db(self, query, k=3):
        """Search vector database for specific knowledge"""
        try:
            if not self.collection or not self.embedding_model:
                return []
            
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
                    if score > 0.3:  # Only high relevance
                        documents.append({'content': doc, 'score': score})
            
            return documents
        except Exception as e:
            return []
    
    def analyze_query_intent(self, query):
        """INTELLIGENT query analysis to decide which agent/data source to use"""
        query_lower = query.lower()
        
        # ISRO/Bhuvan specific queries
        if any(term in query_lower for term in ['bhuvan', 'isro', 'saphir', 'ocm', 'indian space', 'chandrayaan', 'mangalyaan']):
            return {
                'agent': 'isro_geospatial',
                'data_source': 'vector_db',
                'reason': 'ISRO/Indian space query - checking specialized knowledge base'
            }
        
        # NASA live data queries
        elif any(term in query_lower for term in ['nasa picture', 'apod', 'today', 'current nasa']) and not any(term in query_lower for term in ['solar', 'mars']):
            return {
                'agent': 'nasa_live',
                'data_source': 'nasa_api',
                'reason': 'Live NASA APOD request'
            }
        
        # Space weather/solar activity
        elif any(term in query_lower for term in ['solar', 'space weather', 'flare', 'sun activity', 'today', 'current']) and 'solar' in query_lower:
            return {
                'agent': 'space_weather',
                'data_source': 'nasa_api',
                'reason': 'Space weather monitoring query'
            }
        
        # Asteroid tracking
        elif any(term in query_lower for term in ['asteroid', 'space rock', 'dangerous', 'near earth']):
            return {
                'agent': 'asteroid_tracker',
                'data_source': 'nasa_api',
                'reason': 'Asteroid monitoring query'
            }
        
        # Mars exploration
        elif any(term in query_lower for term in ['mars', 'red planet', 'rover', 'perseverance', 'curiosity']):
            return {
                'agent': 'mars_expert',
                'data_source': 'mixed',  # Both NASA API and knowledge
                'reason': 'Mars exploration query'
            }
        
        # General space agencies
        elif any(term in query_lower for term in ['nasa', 'esa', 'spacex']) and not any(term in query_lower for term in ['picture', 'today', 'current']):
            return {
                'agent': 'space_agency_expert',
                'data_source': 'knowledge_base',
                'reason': 'General space agency information'
            }
        
        # Satellite/geospatial technology
        elif any(term in query_lower for term in ['satellite', 'geospatial', 'remote sensing', 'earth observation']):
            return {
                'agent': 'geospatial_expert',
                'data_source': 'vector_db',
                'reason': 'Geospatial/satellite technology query'
            }
        
        # Default
        else:
            return {
                'agent': 'general_space',
                'data_source': 'knowledge_base',
                'reason': 'General space knowledge query'
            }
    
    def get_nasa_live_data(self, query_lower):
        """Get live NASA data based on query analysis"""
        try:
            # Solar activity / space weather
            if any(term in query_lower for term in ['solar', 'space weather', 'flare', 'sun']):
                response = requests.get(
                    "https://api.nasa.gov/DONKI/FLR",
                    params={"api_key": NASA_API_KEY},
                    timeout=10
                )
                response.raise_for_status()
                data = response.json()
                
                if not data:
                    return "☀️ **Solar Weather Report**: The Sun is currently in a calm phase with no significant solar flare activity detected. This is completely normal - our star has quiet periods between active cycles!"
                
                flare = data[0]
                flare_class = flare.get('classType', 'Unknown')
                peak_time = flare.get('peakTime', 'Unknown')
                source = flare.get('sourceLocation', 'Unknown')
                
                # Make it conversational
                if flare_class.startswith('X'):
                    intensity_desc = "🔥 **Major Solar Flare**"
                    impact = "This is a powerful flare that can affect satellite communications and create spectacular auroras!"
                elif flare_class.startswith('M'):
                    intensity_desc = "⚡ **Moderate Solar Flare**"
                    impact = "This medium-strength flare might cause minor radio disruptions and enhance aurora displays."
                elif flare_class.startswith('C'):
                    intensity_desc = "✨ **Minor Solar Flare**"
                    impact = "This is a small flare with minimal Earth impact, but scientifically interesting!"
                else:
                    intensity_desc = "🌟 **Solar Activity Detected**"
                    impact = "The Sun released energy in our direction."
                
                return f"""☀️ **Live Solar Activity Report**:

{intensity_desc} (Class {flare_class})
**When**: {peak_time}
**Location**: {source} on the Sun's surface

**What this means**: {impact}

**Space Weather Impact**: NASA continuously monitors solar activity to protect astronauts, satellites, and power grids on Earth. Solar flares are a natural part of our Sun's 11-year activity cycle."""
            
            # APOD - Astronomy Picture of the Day
            elif any(term in query_lower for term in ['apod', 'picture', 'image', 'photo']) and 'mars' not in query_lower:
                response = requests.get(
                    "https://api.nasa.gov/planetary/apod",
                    params={"api_key": NASA_API_KEY},
                    timeout=10
                )
                response.raise_for_status()
                data = response.json()
                
                title = data.get('title', 'Unknown')
                explanation = data.get('explanation', 'No description available')
                url = data.get('url', '')
                media_type = data.get('media_type', 'image')
                
                result = f"🌟 **Today's NASA Space Highlight**: {title}\n\n"
                
                if explanation and len(explanation) > 200:
                    sentences = explanation.split('. ')
                    result += f"**What you're seeing**: {sentences[0]}.\n\n"
                    if len(sentences) > 1:
                        result += f"**Fascinating details**: {'. '.join(sentences[1:2])}.\n\n"
                else:
                    result += f"**About this cosmic wonder**: {explanation}\n\n"
                
                if media_type == 'video':
                    result += f"🎥 **Watch the video**: {url}"
                else:
                    result += f"🖼️ **View full resolution image**: {url}"
                
                return result
            
            # Mars rover photos
            elif any(term in query_lower for term in ['mars']) and any(term in query_lower for term in ['photo', 'image', 'rover', 'picture']):
                response = requests.get(
                    "https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos",
                    params={"sol": 1000, "api_key": NASA_API_KEY},
                    timeout=10
                )
                response.raise_for_status()
                data = response.json()
                
                photos = data.get('photos', [])
                if not photos:
                    return "🔴 **Mars Rover Update**: Curiosity hasn't taken photos on this Martian day. Mars rovers are busy with science experiments and don't photograph every day!"
                
                result = "🔴 **Live from Mars - Curiosity Rover Photos**:\n\n"
                
                for i, photo in enumerate(photos[:3], 1):
                    earth_date = photo.get('earth_date', 'Unknown')
                    camera = photo.get('camera', {}).get('full_name', 'Unknown camera')
                    img_url = photo.get('img_src', '')
                    
                    result += f"**Photo {i}**: {earth_date}\n"
                    result += f"**Camera**: {camera}\n"
                    result += f"**Image**: {img_url}\n\n"
                
                result += "🤖 **Rover Status**: Curiosity continues exploring Mars, analyzing rocks and soil to understand the Red Planet's history!"
                return result
            
            # Near-Earth asteroids
            elif any(term in query_lower for term in ['asteroid', 'space rock', 'dangerous', 'near earth']):
                response = requests.get(
                    "https://api.nasa.gov/neo/rest/v1/feed",
                    params={"api_key": NASA_API_KEY},
                    timeout=10
                )
                response.raise_for_status()
                data = response.json()
                
                neo_objects = data.get('near_earth_objects', {})
                total_count = sum(len(asteroids) for asteroids in neo_objects.values())
                hazardous_count = 0
                
                for asteroids in neo_objects.values():
                    for asteroid in asteroids:
                        if asteroid.get('is_potentially_hazardous_asteroid', False):
                            hazardous_count += 1
                
                result = f"🌌 **Live Asteroid Tracking**: NASA is currently monitoring **{total_count} near-Earth asteroids**.\n\n"
                
                if hazardous_count > 0:
                    result += f"⚠️ **{hazardous_count} are classified as potentially hazardous** - but don't worry! This just means they're large enough and close enough that we monitor them carefully.\n\n"
                else:
                    result += "✅ **Good news!** None of the currently tracked asteroids pose any threat to Earth.\n\n"
                
                result += "🛡️ **Earth's Defense**: NASA's Planetary Defense team continuously scans the skies to protect our planet!"
                return result
            
            else:
                return "Live NASA data is available! Please specify what you'd like: today's space picture, solar activity, Mars rover photos, or asteroid tracking."
                
        except Exception as e:
            return f"❌ Unable to fetch live NASA data: {str(e)}"
    
    def process_isro_bhuvan_query(self, query):
        """Specialized processing for ISRO/Bhuvan queries"""
        # First check vector database
        vector_results = self.search_vector_db(query, k=5)
        
        if vector_results and any('bhuvan' in result['content'].lower() or 'saphir' in result['content'].lower() or 'ocm' in result['content'].lower() for result in vector_results):
            response = "🇮🇳 **ISRO/Bhuvan Intelligence** (from specialized knowledge base):\n\n"
            
            for i, result in enumerate(vector_results[:3], 1):
                content = result['content'].strip()
                if len(content) > 200:
                    content = content[:200] + "..."
                response += f"**{i}.** {content}\n\n"
            
            # Add context about what Bhuvan is
            if 'bhuvan' in query.lower():
                response += "**About Bhuvan**: Bhuvan is ISRO's geoportal providing satellite imagery and geospatial services. "
                response += "It includes various instruments like SAPHIR for atmospheric profiling and OCM for ocean color monitoring."
            
            return response
        else:
            # Fallback knowledge
            if 'bhuvan' in query.lower():
                return """🇮🇳 **Bhuvan - ISRO's Geospatial Platform**

**Bhuvan** is India's geoportal developed by ISRO (Indian Space Research Organisation) that provides satellite imagery and geospatial services.

**Key Features**:
• **Satellite Imagery**: High-resolution images of India and the world
• **Thematic Services**: Land use, urban planning, disaster management
• **APIs**: For developers to integrate geospatial data
• **Mobile Apps**: Bhuvan for citizen services

**Instruments & Data**:
• **SAPHIR**: Atmospheric humidity profiling instrument
• **OCM (Ocean Colour Monitor)**: Marine and coastal monitoring
• **Cartosat**: High-resolution earth imaging
• **ResourceSat**: Natural resource monitoring

**Applications**: Agriculture, water resources, forestry, urban planning, and disaster management.

*Your vector database contains technical details about specific SAPHIR and OCM data processing methods.*"""
            else:
                return "Please specify what aspect of ISRO or Bhuvan you'd like to know about."
    
    def get_general_space_knowledge(self, query_lower):
        """Provide general space knowledge"""
        if 'nasa' in query_lower:
            return """🚀 **NASA - America's Space Agency**

NASA has been exploring space since 1958! Current major projects include:
• **Artemis Program**: Taking humans back to the Moon by 2026
• **Mars Exploration**: Multiple rovers studying the Red Planet  
• **James Webb Telescope**: Revolutionary deep space observations
• **International Space Station**: Continuous human presence in orbit

**Recent Achievements**: Successfully landed Perseverance rover on Mars, launched James Webb telescope, and preparing for human lunar missions.

NASA's missions help us understand our universe and develop technologies that benefit life on Earth!"""

        elif 'mars' in query_lower:
            return """🔴 **Mars - The Red Planet**

Mars fascinates scientists because it's the most Earth-like planet in our solar system!

**Key Facts**:
• About half the size of Earth
• Day is 24 hours 37 minutes (similar to Earth!)
• Has seasons like Earth due to tilted axis
• Evidence of ancient rivers and lakes
• Two small moons: Phobos and Deimos

**Current Exploration**: NASA's Perseverance and Curiosity rovers are actively exploring, searching for signs of ancient microbial life and studying Martian geology."""

        else:
            return """🌌 **The Amazing Universe**

Space is full of incredible wonders:
• **Our Solar System**: 8 planets, over 200 moons, and countless asteroids
• **The Sun**: A middle-aged star that powers all life on Earth
• **Exoplanets**: Over 5,000 confirmed planets orbiting other stars
• **Galaxies**: Billions of galaxies, each with billions of stars

**Current Discoveries**: We're finding potentially habitable worlds, studying black holes, and even detecting gravitational waves from cosmic collisions!

Ask me about specific topics like NASA missions, Mars exploration, or space agencies!"""
    
    def process_query(self, query, use_nasa_api, progress=gr.Progress()):
        """INTELLIGENT query processing with proper routing"""
        if not query.strip():
            return "Hi! I'm AstroGeo, your intelligent space assistant. I can access live NASA data, search specialized knowledge bases, and provide expert analysis on space topics!"
        
        try:
            progress(0.1, desc="Analyzing your query...")
            
            # STEP 1: Intelligent query analysis
            intent = self.analyze_query_intent(query)
            
            response = f"🧠 **AstroGeo Intelligent Analysis**\n\n"
            response += f"**Query**: {query}\n"
            response += f"**Detected Intent**: {intent['reason']}\n"
            response += f"**Agent**: {intent['agent']}\n"
            response += f"**Data Source**: {intent['data_source']}\n\n"
            
            # STEP 2: Route to appropriate processing
            if intent['agent'] == 'isro_geospatial':
                progress(0.5, desc="Consulting ISRO knowledge base...")
                analysis = self.process_isro_bhuvan_query(query)
                response += analysis
            
            elif intent['agent'] in ['nasa_live', 'space_weather', 'asteroid_tracker'] and use_nasa_api:
                progress(0.5, desc="Getting live NASA data...")
                nasa_data = self.get_nasa_live_data(query.lower())
                response += f"📡 **Live NASA Data**:\n\n{nasa_data}"
            
            elif intent['agent'] == 'mars_expert':
                progress(0.5, desc="Consulting Mars exploration experts...")
                if use_nasa_api and any(term in query.lower() for term in ['photo', 'image', 'picture']):
                    nasa_data = self.get_nasa_live_data(query.lower())
                    response += f"📡 **Live Mars Data**:\n\n{nasa_data}"
                else:
                    mars_knowledge = self.get_general_space_knowledge(query.lower())
                    response += f"🔴 **Mars Expert Analysis**:\n\n{mars_knowledge}"
            
            elif intent['data_source'] == 'vector_db':
                progress(0.5, desc="Searching specialized knowledge base...")
                vector_results = self.search_vector_db(query)
                if vector_results:
                    response += "📚 **From Specialized Knowledge Base**:\n\n"
                    for i, result in enumerate(vector_results[:2], 1):
                        content = result['content'][:300] + "..." if len(result['content']) > 300 else result['content']
                        response += f"**{i}.** {content}\n\n"
                else:
                    response += "No specific information found in knowledge base. Providing general knowledge:\n\n"
                    response += self.get_general_space_knowledge(query.lower())
            
            else:
                progress(0.5, desc="Providing general space knowledge...")
                general_knowledge = self.get_general_space_knowledge(query.lower())
                response += f"📖 **Space Knowledge**:\n\n{general_knowledge}"
            
            progress(1.0, desc="Analysis complete!")
            return response
            
        except Exception as e:
            return f"❌ Error processing query: {str(e)}"

def create_intelligent_interface():
    app = IntelligentAstroGeo()
    
    with gr.Blocks(title="AstroGeo - Intelligent Space Assistant", theme=gr.themes.Soft()) as demo:
        
        gr.Markdown("""
        # 🧠 AstroGeo - Intelligent Space Analysis System
        **Smart Query Routing | Specialized Agents | Multiple Data Sources**
        
        I intelligently decide whether to use NASA APIs, search your knowledge base, or provide expert analysis!
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                query_input = gr.Textbox(
                    label="🔍 Ask me anything about space (I'll route intelligently)",
                    placeholder="Try: 'What is Bhuvan?', 'Today's solar activity', 'ISRO SAPHIR instrument', 'Mars rover photos'",
                    lines=2
                )
                
                use_nasa_api = gr.Checkbox(
                    label="📡 Enable live NASA data (when relevant)",
                    value=True
                )
                
                ask_btn = gr.Button("🧠 Intelligent Analysis", variant="primary", size="lg")
            
            with gr.Column(scale=1):
                status = gr.Textbox(
                    label="🧠 Intelligent System",
                    value=f"""🧠 Smart Query Routing
📚 Vector Knowledge Base
🛰️ NASA API: {'Ready' if NASA_API_KEY != 'DEMO_KEY' else 'Demo'}
🇮🇳 ISRO/Bhuvan Expert
🔴 Mars Specialist
☀️ Solar Weather Monitor
✅ Multi-Agent Intelligence""",
                    lines=8,
                    interactive=False
                )
        
        with gr.Row():
            output = gr.Textbox(
                label="🧠 Intelligent Analysis Results",
                lines=25,
                interactive=False
            )
        
        # Smart examples showing different routing
        gr.Markdown("### 🎯 Smart Examples (Different Agents)")
        with gr.Row():
            examples = [
                gr.Button("🇮🇳 What is Bhuvan?", size="sm"),
                gr.Button("☀️ Today's solar activity", size="sm"),
                gr.Button("🖼️ NASA's picture today", size="sm"),
                gr.Button("🔴 Mars rover photos", size="sm")
            ]
        
        # Event handlers
        ask_btn.click(
            fn=app.process_query,
            inputs=[query_input, use_nasa_api],
            outputs=[output]
        )
        
        # Smart example handlers
        example_queries = [
            "What is Bhuvan and how does it work?",
            "What's today's solar activity and space weather?",
            "What's today's NASA astronomy picture?",
            "Show me recent Mars rover photos"
        ]
        
        for btn, query in zip(examples, example_queries):
            btn.click(lambda q=query: q, outputs=[query_input])
        
        gr.Markdown("""
        ---
        **🧠 Intelligence**: Smart routing to specialized agents | **📚 Sources**: Vector DB + NASA APIs + Expert Knowledge
        """)
    
    return demo

if __name__ == "__main__":
    demo = create_intelligent_interface()
    print("🧠 Launching Intelligent AstroGeo...")
    demo.launch(server_port=7862, share=False)
