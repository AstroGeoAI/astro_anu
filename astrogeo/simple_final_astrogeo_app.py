import gradio as gr
import os
import sys
from pathlib import Path
from datetime import datetime
import requests

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

# NASA API Configuration
NASA_API_KEY = os.getenv('NASA_API_KEY', 'DEMO_KEY')

class SimpleFinalAstroGeoApp:
    def __init__(self):
        print("✅ AstroGeo Simple System Initialized")
        print(f"✅ NASA API: {'Configured' if NASA_API_KEY != 'DEMO_KEY' else 'Using DEMO_KEY'}")
    
    def nasa_apod_tool(self):
        """Get NASA APOD"""
        try:
            r = requests.get(
                "https://api.nasa.gov/planetary/apod",
                params={"api_key": NASA_API_KEY},
                timeout=10
            )
            r.raise_for_status()
            d = r.json()
            return f"🌟 **Today's NASA APOD**: '{d.get('title')}' ({d.get('date')})\n\n{d.get('explanation')}\n\n📸 **Image**: {d.get('url')}"
        except Exception as e:
            return f"❌ Error fetching APOD: {e}"

    def nasa_mars_tool(self, sol=1000):
        """Get Mars rover photos"""
        try:
            r = requests.get(
                "https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos",
                params={"sol": sol, "api_key": NASA_API_KEY},
                timeout=10
            )
            r.raise_for_status()
            photos = r.json().get("photos", [])
            if not photos:
                return "No Mars photos found for that sol."
            
            items = photos[:3]
            text = "🔴 **Recent Mars Rover Images from Curiosity**:\n\n"
            for i, p in enumerate(items, 1):
                text += f"**{i}.** {p['earth_date']} - {p['camera']['full_name']}\n"
                text += f"📸 Image: {p['img_src']}\n\n"
            
            return text
        except Exception as e:
            return f"❌ Error fetching Mars photos: {e}"

    def nasa_asteroids_tool(self):
        """Get near-Earth asteroid data"""
        try:
            r = requests.get(
                "https://api.nasa.gov/neo/rest/v1/feed",
                params={"api_key": NASA_API_KEY},
                timeout=10
            )
            r.raise_for_status()
            data = r.json().get("near_earth_objects", {})
            
            items = []
            total_count = 0
            for date, arr in list(data.items())[:3]:
                total_count += len(arr)
                for a in arr[:2]:
                    hazardous = "⚠️ YES" if a['is_potentially_hazardous_asteroid'] else "✅ No"
                    items.append(f"• **{a['name']}** - Potentially Hazardous: {hazardous}")
            
            return f"🌌 **Near-Earth Asteroids** (Total tracked: {total_count}):\n\n" + "\n".join(items)
        except Exception as e:
            return f"❌ Error fetching asteroid data: {e}"

    def nasa_solar_activity_tool(self):
        """Get solar flare activity"""
        try:
            url = "https://api.nasa.gov/DONKI/FLR"
            r = requests.get(url, params={"api_key": NASA_API_KEY}, timeout=10)
            r.raise_for_status()
            arr = r.json()
            
            if not arr:
                return "☀️ **Solar Activity**: No recent solar flare data found. Solar activity is currently calm."
            
            flare = arr[0]
            text = f"☀️ **Recent Solar Activity**:\n\n"
            text += f"**Solar Flare Class**: {flare.get('classType', 'Unknown')}\n"
            text += f"**Peak Time**: {flare.get('peakTime', 'Unknown')}\n"
            text += f"**Source Location**: {flare.get('sourceLocation', 'Unknown')}\n"
            
            return text
        except Exception as e:
            return f"❌ Error fetching solar activity: {e}"
    
    def get_space_knowledge(self, query_lower):
        """Comprehensive space knowledge base"""
        knowledge = {}
        
        # NASA Knowledge
        if 'nasa' in query_lower:
            knowledge['nasa'] = {
                'overview': 'NASA (National Aeronautics and Space Administration) - Leading space agency since 1958',
                'current_missions': [
                    'Artemis Program - Return humans to Moon by 2026',
                    'Mars Sample Return - Bringing Mars rocks to Earth',
                    'James Webb Space Telescope - Revolutionary space observations',
                    'Parker Solar Probe - Touching the Sun\'s corona'
                ],
                'achievements': 'Apollo Moon landings, Space Shuttle, ISS, Mars rovers, Hubble telescope'
            }
        
        # ISRO Knowledge  
        if 'isro' in query_lower:
            knowledge['isro'] = {
                'overview': 'ISRO - Indian Space Research Organisation, cost-effective space missions since 1969',
                'achievements': [
                    'Chandrayaan-3 - Successful lunar south pole landing (2023)',
                    'Mangalyaan - Mars mission for just $74 million',
                    'Record 104 satellites in single launch',
                    'Aryabhatta - First Indian satellite (1975)'
                ],
                'upcoming': 'Gaganyaan human spaceflight, Shukrayaan Venus mission'
            }
        
        # Mars Knowledge
        if 'mars' in query_lower:
            knowledge['mars'] = {
                'facts': [
                    'Fourth planet from Sun, known as Red Planet',
                    'Day: 24h 37m, Year: 687 Earth days',  
                    'Two moons: Phobos and Deimos',
                    'Evidence of ancient water and possible life'
                ],
                'exploration': 'Multiple rovers active: Perseverance, Curiosity, plus orbiters'
            }
        
        return knowledge
    
    def analyze_space_query(self, query: str, query_type: str, use_nasa_api: bool, progress=gr.Progress()):
        """Main analysis function with NASA API integration"""
        if not query.strip():
            return "Please enter a query about space or astronomy."
        
        try:
            query_lower = query.lower()
            
            progress(0.1, desc="Starting analysis...")
            
            response = f"🚀 **AstroGeo Live NASA Analysis**\n\n"
            response += f"**Query**: {query}\n"
            response += f"**Type**: {query_type.title()}\n"
            response += f"**NASA API**: {'Active' if use_nasa_api else 'Disabled'}\n"
            response += f"**Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            # NASA API Data
            if use_nasa_api:
                progress(0.3, desc="Fetching live NASA data...")
                
                # Check what NASA data to fetch based on query
                if any(term in query_lower for term in ['apod', 'picture', 'image', 'photo', 'today']):
                    response += "## 🌟 **Live NASA Data**\n\n"
                    nasa_data = self.nasa_apod_tool()
                    response += f"{nasa_data}\n\n"
                
                elif any(term in query_lower for term in ['mars', 'rover', 'curiosity', 'red planet']):
                    response += "## 🔴 **Live Mars Data**\n\n"
                    mars_data = self.nasa_mars_tool()
                    response += f"{mars_data}\n\n"
                
                elif any(term in query_lower for term in ['asteroid', 'neo', 'near earth']):
                    response += "## 🌌 **Live Asteroid Data**\n\n"
                    asteroid_data = self.nasa_asteroids_tool()
                    response += f"{asteroid_data}\n\n"
                
                elif any(term in query_lower for term in ['solar', 'flare', 'sun', 'space weather']):
                    response += "## ☀️ **Live Solar Data**\n\n"
                    solar_data = self.nasa_solar_activity_tool()
                    response += f"{solar_data}\n\n"
                
                # For general NASA queries, get APOD
                elif 'nasa' in query_lower and len([t for t in ['apod', 'mars', 'asteroid', 'solar'] if t in query_lower]) == 0:
                    response += "## 🌟 **Live NASA Data**\n\n"
                    nasa_data = self.nasa_apod_tool()
                    response += f"{nasa_data}\n\n"
            
            # Comprehensive Knowledge
            progress(0.6, desc="Adding comprehensive knowledge...")
            space_knowledge = self.get_space_knowledge(query_lower)
            
            if space_knowledge:
                response += "## 📚 **Space Knowledge Database**\n\n"
                for topic, info in space_knowledge.items():
                    response += f"### {topic.upper()}\n\n"
                    
                    if 'overview' in info:
                        response += f"**Overview**: {info['overview']}\n\n"
                    
                    if 'achievements' in info:
                        response += "**Key Achievements**:\n"
                        if isinstance(info['achievements'], list):
                            for achievement in info['achievements']:
                                response += f"• {achievement}\n"
                        else:
                            response += f"• {info['achievements']}\n"
                        response += "\n"
                    
                    if 'current_missions' in info:
                        response += "**Current Missions**:\n"
                        for mission in info['current_missions']:
                            response += f"• {mission}\n"
                        response += "\n"
                    
                    if 'facts' in info:
                        response += "**Key Facts**:\n"
                        for fact in info['facts']:
                            response += f"• {fact}\n"
                        response += "\n"
            
            progress(0.9, desc="Finalizing...")
            response += "## ✅ **Analysis Complete**\n\n"
            response += f"**NASA Integration**: {'Live API data included' if use_nasa_api else 'Knowledge base only'}\n"
            response += f"**Data Sources**: NASA APIs + Comprehensive knowledge base\n"
            
            progress(1.0, desc="Done!")
            return response
            
        except Exception as e:
            return f"❌ Analysis Error: {str(e)}"

def create_simple_final_interface():
    """Create simplified final interface"""
    app = SimpleFinalAstroGeoApp()
    
    with gr.Blocks(title="AstroGeo - Live NASA System", theme=gr.themes.Soft()) as demo:
        
        gr.Markdown("""
        # 🚀 AstroGeo - Live NASA Data System
        **Real NASA APIs + Comprehensive Knowledge Base**
        
        Get live NASA data including APOD, Mars photos, asteroids, and solar activity!
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                query_input = gr.Textbox(
                    label="🔍 Ask about space with live NASA data",
                    placeholder="Try: 'Today's NASA picture', 'Mars rover photos', 'Solar activity', 'Near Earth asteroids'",
                    lines=2
                )
                
                with gr.Row():
                    query_type = gr.Dropdown(
                        choices=[
                            "nasa_apod", 
                            "mars_data", 
                            "solar_activity", 
                            "asteroids",
                            "general_space",
                            "space_agencies"
                        ],
                        label="🎯 Query Type",
                        value="nasa_apod",
                        scale=2
                    )
                    
                    use_nasa_api = gr.Checkbox(
                        label="🛰️ Live NASA APIs",
                        value=True,
                        scale=1
                    )
                
                analyze_btn = gr.Button("🚀 Get Live NASA Data", variant="primary", size="lg")
            
            with gr.Column(scale=1):
                system_status = gr.Textbox(
                    label="📡 NASA System Status",
                    value=f"""🛰️ NASA API: {'Connected' if NASA_API_KEY != 'DEMO_KEY' else 'DEMO Mode'}
🌟 APOD: Available
🔴 Mars Photos: Available  
☀️ Solar Data: Available
🌌 Asteroid Data: Available
✅ Ready for Live Queries!""",
                    interactive=False,
                    lines=8
                )
        
        with gr.Row():
            analysis_output = gr.Textbox(
                label="🛰️ Live NASA Analysis Results",
                lines=25,
                interactive=False
            )
        
        # NASA-specific examples
        gr.Markdown("### 🛰️ Live NASA Data Examples")
        with gr.Row():
            examples = [
                gr.Button("🌟 Today's NASA APOD", size="sm"),
                gr.Button("🔴 Mars rover photos", size="sm"), 
                gr.Button("☀️ Current solar activity", size="sm"),
                gr.Button("🌌 Near-Earth asteroids", size="sm"),
                gr.Button("🚀 What's NASA doing?", size="sm")
            ]
        
        # Event handlers
        analyze_btn.click(
            fn=app.analyze_space_query,
            inputs=[query_input, query_type, use_nasa_api],
            outputs=[analysis_output]
        )
        
        # NASA example handlers
        nasa_queries = [
            "What is today's NASA Astronomy Picture of the Day?",
            "Show me recent Mars rover photos from Curiosity",
            "What is the current solar activity?", 
            "What near-Earth asteroids are being tracked right now?",
            "What are NASA's current missions and latest updates?"
        ]
        
        for btn, query in zip(examples, nasa_queries):
            btn.click(
                fn=lambda q=query: q,
                outputs=[query_input]
            )
        
        gr.Markdown("""
        ---
        **🛰️ Live NASA Data**: APOD, Mars, Solar, Asteroids | **📡 Status**: Connected | **🚀 Ready**: For Real-Time Queries!
        """)
    
    return demo

if __name__ == "__main__":
    demo = create_simple_final_interface()
    demo.launch(server_port=7865, share=False)
