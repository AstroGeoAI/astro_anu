from crewai import Agent
import yaml
import requests
import os
from loguru import logger

class AstroIntelAgent:
    def __init__(self, config_path: str = "config/agents.yaml"):
        self.config = self._load_agent_config(config_path)
        self.nasa_api_key = os.getenv('NASA_API_KEY', 'DEMO_KEY')
        self.agent = self._create_agent()
        
    def _load_agent_config(self, config_path: str):
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
                return config.get('astronomical_intelligence_agent', {})
        except Exception as e:
            return {
                'role': 'Deep Space Analysis and Astronomical Research Expert with Live NASA Data Access',
                'goal': 'Analyze astronomical phenomena using live NASA APIs including APOD, solar activity, and asteroid data',
                'backstory': 'Expert astrophysicist with direct access to NASA\'s real-time space data, capable of translating complex astronomical information into understandable insights.'
            }
    
    def get_nasa_apod(self):
        """Get NASA's Astronomy Picture of the Day with intelligent processing"""
        try:
            r = requests.get(
                "https://api.nasa.gov/planetary/apod",
                params={"api_key": self.nasa_api_key},
                timeout=10
            )
            r.raise_for_status()
            data = r.json()
            
            # Process the data intelligently
            title = data.get('title', 'Unknown')
            explanation = data.get('explanation', 'No description available')
            url = data.get('url', '')
            media_type = data.get('media_type', 'image')
            
            # Create natural language response
            response = f"Today's space highlight is '{title}'. "
            
            if len(explanation) > 200:
                sentences = explanation.split('. ')
                response += f"What you're seeing: {sentences[0]}. "
                if len(sentences) > 1:
                    response += f"Key details: {'. '.join(sentences[1:2])}. "
            else:
                response += f"About this: {explanation} "
            
            response += f"View it at: {url}"
            
            return response
        except Exception as e:
            return f"Unable to access today's astronomy picture: {str(e)}"
    
    def get_solar_activity(self):
        """Get solar activity with intelligent interpretation"""
        try:
            r = requests.get(
                "https://api.nasa.gov/DONKI/FLR",
                params={"api_key": self.nasa_api_key},
                timeout=10
            )
            r.raise_for_status()
            data = r.json()
            
            if not data:
                return "The Sun is currently quiet with no major flare activity - this is normal solar behavior."
            
            flare = data[0]
            flare_class = flare.get('classType', 'Unknown')
            peak_time = flare.get('peakTime', 'Unknown')
            
            # Interpret flare intensity
            if flare_class.startswith('X'):
                intensity = "major solar flare that can affect satellites and create auroras"
            elif flare_class.startswith('M'):
                intensity = "moderate flare that might cause minor radio disruptions"
            elif flare_class.startswith('C'):
                intensity = "minor flare with minimal Earth impact"
            else:
                intensity = "solar activity detected"
            
            return f"Recent solar activity: {intensity} (Class {flare_class}) peaked at {peak_time}. This is normal solar behavior that NASA monitors for space weather."
            
        except Exception as e:
            return f"Solar activity data temporarily unavailable: {str(e)}"
    
    def get_asteroid_data(self):
        """Get asteroid data with risk assessment"""
        try:
            r = requests.get(
                "https://api.nasa.gov/neo/rest/v1/feed",
                params={"api_key": self.nasa_api_key},
                timeout=10
            )
            r.raise_for_status()
            data = r.json()
            
            neo_objects = data.get('near_earth_objects', {})
            total_count = sum(len(asteroids) for asteroids in neo_objects.values())
            
            hazardous_count = 0
            notable_asteroids = []
            
            for date, asteroids in list(neo_objects.items())[:2]:
                for asteroid in asteroids:
                    if asteroid.get('is_potentially_hazardous_asteroid', False):
                        hazardous_count += 1
                    
                    if len(notable_asteroids) < 3:
                        size_max = asteroid.get('estimated_diameter', {}).get('meters', {}).get('estimated_diameter_max', 0)
                        notable_asteroids.append({
                            'name': asteroid.get('name', 'Unknown'),
                            'hazardous': asteroid.get('is_potentially_hazardous_asteroid', False),
                            'size': size_max
                        })
            
            response = f"NASA is tracking {total_count} near-Earth asteroids. "
            
            if hazardous_count > 0:
                response += f"{hazardous_count} are classified as potentially hazardous (large and close enough to monitor carefully). "
            else:
                response += "None are currently considered potentially hazardous. "
            
            if notable_asteroids:
                response += "Notable objects: "
                for ast in notable_asteroids:
                    size_desc = "large" if ast['size'] > 500 else "medium" if ast['size'] > 50 else "small"
                    response += f"{ast['name']} ({size_desc}), "
                
            response += "All are being safely monitored by NASA's planetary defense systems."
            
            return response
            
        except Exception as e:
            return f"Asteroid tracking data temporarily unavailable: {str(e)}"
    
    def _create_agent(self) -> Agent:
        return Agent(
            role=self.config.get('role', 'Astronomical Intelligence Agent with NASA API Access'),
            goal=self.config.get('goal', 'Provide live astronomical analysis using NASA data'),
            backstory=self.config.get('backstory', 'Expert astrophysicist with NASA API access for real-time space data'),
            verbose=True,
            allow_delegation=False,
            max_iter=3,
            memory=True
        )
    
    def analyze_query(self, query: str) -> str:
        """Main analysis method that processes queries intelligently"""
        query_lower = query.lower()
        
        response_parts = []
        
        # Determine what data to fetch based on query
        if any(term in query_lower for term in ['apod', 'picture', 'image', 'today', 'daily']):
            response_parts.append(self.get_nasa_apod())
        
        if any(term in query_lower for term in ['solar', 'sun', 'flare', 'space weather']):
            response_parts.append(self.get_solar_activity())
        
        if any(term in query_lower for term in ['asteroid', 'space rock', 'near earth']):
            response_parts.append(self.get_asteroid_data())
        
        # If no specific data requested, provide APOD as default
        if not response_parts and any(term in query_lower for term in ['nasa', 'space', 'astronomy']):
            response_parts.append(self.get_nasa_apod())
        
        if response_parts:
            return f"Astronomical Intelligence Analysis: {' '.join(response_parts)}"
        else:
            return "Please specify what astronomical information you'd like - today's space picture, solar activity, or asteroid tracking."

def create_astro_intel_agent() -> Agent:
    intel = AstroIntelAgent()
    return intel.agent

# Export the agent's analysis function for direct use
def analyze_astronomical_query(query: str) -> str:
    agent = AstroIntelAgent()
    return agent.analyze_query(query)
