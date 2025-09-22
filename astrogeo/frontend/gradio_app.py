import gradio as gr
import asyncio
from typing import List, Dict, Any
import os
from datetime import datetime
from loguru import logger
import sys
import re
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from astrogeo.crew import AstroGeoCrew
from astrogeo.utils.vector_store import VectorStoreManager
from astrogeo.utils.config_loader import ConfigLoader

class AstroGeoGradioApp:
    def __init__(self):
        self.config_loader = ConfigLoader()
        self.configs = self.config_loader.get_all_configs()
        self.vector_store = None
        self.crew = None
        self.initialize_components()
        
    def initialize_components(self):
        """Initialize enhanced components with weather intelligence"""
        try:
            # Initialize vector store
            rag_config = self.configs.get('rag', {})
            self.vector_store = VectorStoreManager(rag_config)
            self.vector_store.initialize_vector_store()
            
            # Initialize enhanced crew with geospatial agent
            self.crew = AstroGeoCrew()
            
            logger.info("AstroGeo enhanced components with weather intelligence initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize enhanced components: {e}")
    
    def analyze_query_intent(self, query: str):
        """Analyze query to determine appropriate task routing"""
        query_lower = query.lower()
        
        # Weather and geospatial queries
        if any(term in query_lower for term in ['weather', 'temperature', 'rain', 'rainfall', 'climate', 'humidity', 'precipitation']):
            return 'geospatial_analysis'
        
        # NASA and space queries
        elif any(term in query_lower for term in ['nasa', 'apod', 'mars rover', 'solar activity', 'asteroid', 'space picture']):
            return 'astronomical_analysis'
        
        # ISRO and Indian space queries
        elif any(term in query_lower for term in ['isro', 'bhuvan', 'chandrayaan', 'mangalyaan', 'indian space']):
            return 'data_harvesting'
        
        # Default to astronomical analysis
        else:
            return 'astronomical_analysis'
    
    def extract_location_from_query(self, query: str):
        """Extract location from weather-related queries"""
        query_lower = query.lower()
        
        # Common location extraction patterns
        location_patterns = [
            r'weather in ([a-zA-Z\s]+)',
            r'rainfall in ([a-zA-Z\s]+)', 
            r'temperature in ([a-zA-Z\s]+)',
            r'climate in ([a-zA-Z\s]+)'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, query_lower)
            if match:
                return match.group(1).strip().title()
        
        return "Delhi"  # Default location
    
    def process_query(self, query: str, query_type: str, use_live_apis: bool, progress=gr.Progress()) -> str:
        """Enhanced query processing with intelligent task routing"""
        if not query.strip():
            return """🌍🚀 **Welcome to Enhanced AstroGeo!**

I'm your intelligent assistant for:
• **🌤️ Weather Intelligence**: Current weather, rainfall forecasts, climate data
• **🛰️ Geospatial Analysis**: Satellite imagery, remote sensing, environmental monitoring  
• **🇮🇳 ISRO Missions**: Bhuvan platform, Chandrayaan, Mangalyaan, Indian satellites
• **📡 NASA Live Data**: Space pictures, Mars rovers, solar activity, asteroids
• **🌌 Space Intelligence**: Astronomical events, space missions, cosmic phenomena

Ask me about weather, space missions, satellite data, or astronomical events!"""
        
        try:
            progress(0.1, desc="Analyzing query intent...")
            
            # Determine query intent and appropriate task
            intent = self.analyze_query_intent(query)
            location = self.extract_location_from_query(query) if 'weather' in query.lower() or 'rain' in query.lower() else None
            
            response = f"🧠 **Enhanced AstroGeo Analysis**\n\n"
            response += f"**Query**: {query}\n"
            response += f"**Intent**: {intent.replace('_', ' ').title()}\n"
            if location:
                response += f"**Location**: {location}\n"
            response += f"**Live APIs**: {'Enabled' if use_live_apis else 'Disabled'}\n\n"
            
            progress(0.4, desc="Activating specialized agents...")
            
            if self.crew:
                # Prepare inputs for CrewAI with enhanced parameters
                inputs = {
                    'topic': query,
                    'query_type': query_type,
                    'intent': intent,
                    'location': location or 'global',
                    'use_live_apis': use_live_apis,
                    'data_categories': intent,
                    'time_range': 'current',
                    'analysis_depth': 'comprehensive'
                }
                
                progress(0.7, desc="Multi-agent analysis in progress...")
                
                # Execute CrewAI crew with enhanced capabilities
                result = self.crew.crew().kickoff(inputs=inputs)
                result_text = str(result)
                
                response += f"## 🤖 **Multi-Agent Analysis Results**:\n\n{result_text}\n\n"
            
            # Add vector database context if relevant
            progress(0.8, desc="Searching knowledge base...")
            if self.vector_store:
                context_results = self.vector_store.similarity_search(query, k=3)
                if context_results:
                    response += "## 📚 **Knowledge Base Context**:\n\n"
                    for i, result in enumerate(context_results[:2], 1):
                        clean_doc = result['document'][:200] + "..." if len(result['document']) > 200 else result['document']
                        response += f"**{i}.** {clean_doc}\n\n"
            
            progress(1.0, desc="Analysis complete!")
            return response
            
        except Exception as e:
            logger.error(f"Error in enhanced query processing: {e}")
            return f"❌ **Analysis Error**: {str(e)}\n\nPlease try rephrasing your query or check system configuration."
    
    def create_interface(self):
        """Create enhanced Gradio interface with weather and space intelligence"""
        with gr.Blocks(title="AstroGeo - Enhanced Space & Weather Intelligence", theme=gr.themes.Soft()) as interface:
            
            gr.Markdown("""
            # 🌍🚀 AstroGeo - Enhanced Space & Weather Intelligence
            **Multi-Agent System | Weather APIs | NASA Data | ISRO Integration | Geospatial Analysis**
            
            Your comprehensive assistant for weather, space missions, and geospatial intelligence!
            """)
            
            with gr.Row():
                with gr.Column(scale=2):
                    query_input = gr.Textbox(
                        label="🔍 Ask about weather, space, or geospatial topics",
                        placeholder="Try: 'Weather in Mumbai', 'Today's NASA picture', 'What is Bhuvan?', 'Rainfall forecast for Delhi'",
                        lines=3
                    )
                    
                    with gr.Row():
                        query_type = gr.Dropdown(
                            choices=[
                                "weather_geospatial", 
                                "space_astronomy", 
                                "nasa_missions", 
                                "isro_missions",
                                "satellite_imagery",
                                "environmental_monitoring",
                                "general_inquiry"
                            ],
                            label="🎯 Query Category",
                            value="weather_geospatial"
                        )
                        
                        use_live_apis = gr.Checkbox(
                            label="📡 Use Live APIs",
                            value=True
                        )
                    
                    analyze_btn = gr.Button("🌍🚀 Enhanced Analysis", variant="primary", size="lg")
                
                with gr.Column(scale=1):
                    system_info = gr.Textbox(
                        label="🖥️ Enhanced System Status",
                        value="""🌤️ Weather Intelligence Agent
🛰️ Geospatial Expert Agent
🇮🇳 ISRO Mission Specialist
📡 NASA Live Data Agent
🌌 Astronomical Intelligence
📚 Vector Knowledge Base
✅ Multi-Agent System Ready""",
                        interactive=False,
                        lines=9
                    )
            
            with gr.Row():
                response_output = gr.Textbox(
                    label="🧠 Enhanced Multi-Agent Analysis",
                    lines=25,
                    interactive=False
                )
            
            # Enhanced examples showing different capabilities
            gr.Markdown("### 🎯 Test Enhanced Capabilities")
            with gr.Row():
                example_btns = [
                    gr.Button("🌤️ Weather in Mumbai", size="sm"),
                    gr.Button("🌧️ Rainfall in Delhi", size="sm"),
                    gr.Button("📡 Today's NASA picture", size="sm"),
                    gr.Button("🇮🇳 ISRO Bhuvan platform", size="sm")
                ]
            
            # Event handlers
            analyze_btn.click(
                fn=self.process_query,
                inputs=[query_input, query_type, use_live_apis],
                outputs=[response_output]
            )
            
            # Enhanced example handlers
            example_queries = [
                "What's the current weather in Mumbai?",
                "What's the rainfall forecast for Delhi?",
                "What's today's NASA astronomy picture of the day?",
                "Tell me about ISRO's Bhuvan geospatial platform"
            ]
            
            for btn, query in zip(example_btns, example_queries):
                btn.click(
                    fn=lambda q=query: q,
                    outputs=[query_input]
                )
            
            gr.Markdown("""
            ---
            **🌍 Earth Intelligence**: Weather, Climate, Geospatial Analysis | **🚀 Space Intelligence**: NASA, ISRO, Missions, Astronomy | **🤖 Enhanced AI**: Multi-agent coordination with live data
            """)
        
        return interface

def create_astrogeo_app():
    """Factory function to create enhanced AstroGeo app"""
    app = AstroGeoGradioApp()
    return app.create_interface()
