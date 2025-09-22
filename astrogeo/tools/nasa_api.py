from crewai_tools import BaseTool
import requests
import os
from typing import Dict, Any, Optional
from loguru import logger

class NasaApodTool(BaseTool):
    name: str = "NASA APOD Tool"
    description: str = "Get NASA's Astronomy Picture of the Day with title, explanation and image URL"
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv('NASA_API_KEY', 'DEMO_KEY')
        
    def _run(self) -> str:
        """Get today's NASA APOD"""
        try:
            r = requests.get(
                "https://api.nasa.gov/planetary/apod",
                params={"api_key": self.api_key},
                timeout=10
            )
            r.raise_for_status()
            d = r.json()
            return f"Today's NASA APOD is titled '{d.get('title')}' ({d.get('date')}). {d.get('explanation')} Image URL: {d.get('url')}"
        except Exception as e:
            return f"Error fetching APOD: {e}"

class NasaMarsRoverTool(BaseTool):
    name: str = "NASA Mars Rover Tool"
    description: str = "Get Mars rover photos from Curiosity rover with camera details and image URLs"
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv('NASA_API_KEY', 'DEMO_KEY')
        
    def _run(self, sol: int = 1000) -> str:
        """Get Mars rover photos for specified sol (Mars day)"""
        try:
            r = requests.get(
                "https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos",
                params={"sol": sol, "api_key": self.api_key},
                timeout=10
            )
            r.raise_for_status()
            photos = r.json().get("photos", [])
            if not photos:
                return "No Mars photos found for that sol."
            items = photos[:3]
            text = "Here are some recent Mars rover images:\n"
            for p in items:
                text += f"- {p['earth_date']} {p['camera']['full_name']}: {p['img_src']}\n"
            return text
        except Exception as e:
            return f"Error fetching Mars photos: {e}"

class NasaAsteroidTool(BaseTool):
    name: str = "NASA Near-Earth Asteroid Tool"
    description: str = "Get information about near-Earth asteroids and potentially hazardous objects"
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv('NASA_API_KEY', 'DEMO_KEY')
        
    def _run(self) -> str:
        """Get near-Earth asteroid data"""
        try:
            r = requests.get(
                "https://api.nasa.gov/neo/rest/v1/feed",
                params={"api_key": self.api_key},
                timeout=10
            )
            r.raise_for_status()
            data = r.json().get("near_earth_objects", {})
            items = []
            for date, arr in list(data.items())[:2]:
                for a in arr[:2]:
                    items.append(f"{a['name']} (Potentially Hazardous: {a['is_potentially_hazardous_asteroid']})")
            return "The recent near-Earth asteroids are:\n" + "\n".join(items)
        except Exception as e:
            return f"Error fetching asteroid data: {e}"

class NasaSolarActivityTool(BaseTool):
    name: str = "NASA Solar Activity Tool"  
    description: str = "Get recent solar flare activity and space weather information"
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv('NASA_API_KEY', 'DEMO_KEY')
        
    def _run(self) -> str:
        """Get solar activity data"""
        try:
            url = "https://api.nasa.gov/DONKI/FLR"
            r = requests.get(url, params={"api_key": self.api_key}, timeout=10)
            r.raise_for_status()
            arr = r.json()
            if not arr:
                return "No recent solar flare data found."
            flare = arr[0]
            return f"Recent solar activity: Solar flare of class {flare.get('classType')} peaked at {flare.get('peakTime')}."
        except Exception as e:
            return f"Error fetching solar activity: {e}"

# Create tool instances
nasa_apod_tool = NasaApodTool()
nasa_mars_rover_tool = NasaMarsRoverTool()
nasa_asteroid_tool = NasaAsteroidTool()
nasa_solar_activity_tool = NasaSolarActivityTool()
