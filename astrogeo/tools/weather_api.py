from crewai_tools import BaseTool
import requests
import os
import re
from typing import Dict, Any, Optional
from datetime import datetime
import json
from loguru import logger

class IntelligentWeatherTool(BaseTool):
    name: str = "Intelligent Weather Analysis Tool"
    description: str = "Professional weather analysis with intelligent location detection and validation for ANY city worldwide using OpenWeatherMap API"
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv('OPENWEATHERMAP_KEY', 'DEMO_KEY')
        
    def _run(self, query: str) -> str:
        """
        Intelligent weather analysis for any location mentioned in natural language query
        Args:
            query: Natural language query mentioning location and weather requirements
        """
        try:
            # STEP 1: Extract and validate location intelligently
            location = self._extract_and_validate_location(query)
            
            if not location:
                return f"""❌ **INTELLIGENT WEATHER ANALYSIS FAILED**
                
**Query**: {query}
**Issue**: Could not identify or validate any location
**Solutions**:
• Specify clear city name: "Weather in Mumbai" or "Delhi climate"
• Check spelling of city name
• Try adding country: "CityName, Country"
• Use major nearby city if small town not found

**Supported**: Any of 200,000+ cities worldwide in OpenWeatherMap database"""
            
            # STEP 2: Get comprehensive weather data
            weather_data = self._get_comprehensive_weather_data(location)
            
            return weather_data
            
        except Exception as e:
            logger.error(f"Intelligent Weather Tool error: {e}")
            return f"Weather analysis system error: {str(e)}"
    
    def _extract_and_validate_location(self, query: str) -> Optional[str]:
        """Extract location from query and validate with OpenWeatherMap API"""
        
        # Extract potential locations using multiple patterns
        potential_locations = []
        
        # Pattern 1: "for [location]"
        for_match = re.search(r'\bfor\s+([a-zA-Z][a-zA-Z\s,-]+?)(?:\s+including|\s+with|\?|$)', query, re.IGNORECASE)
        if for_match:
            potential_locations.append(for_match.group(1).strip())
        
        # Pattern 2: "in [location]"
        in_match = re.search(r'\bin\s+([a-zA-Z][a-zA-Z\s,-]+?)(?:\s+including|\s+with|\?|$)', query, re.IGNORECASE)
        if in_match:
            potential_locations.append(in_match.group(1).strip())
        
        # Pattern 3: "[location] weather/analysis"
        start_match = re.search(r'^([a-zA-Z][a-zA-Z\s,-]+?)\s+(?:weather|climate|analysis|temperature)', query, re.IGNORECASE)
        if start_match:
            potential_locations.append(start_match.group(1).strip())
        
        # Pattern 4: Capitalized words (proper nouns)
        caps_words = re.findall(r'\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*\b', query)
        for word in caps_words:
            if word.lower() not in ['weather', 'analysis', 'environmental', 'air', 'quality', 'temperature', 'climate']:
                potential_locations.append(word)
        
        # Validate each potential location with API
        if self.api_key == 'DEMO_KEY':
            return potential_locations[0] if potential_locations else None
        
        for location_candidate in potential_locations:
            validated = self._validate_location_with_geocoding_api(location_candidate)
            if validated:
                return validated
        
        return None
    
    def _validate_location_with_geocoding_api(self, location_candidate: str) -> Optional[str]:
        """Validate location using OpenWeatherMap Geocoding API"""
        try:
            # Clean location
            location_clean = re.sub(r'\s+', ' ', location_candidate.strip())
            
            # Try geocoding API
            geo_url = "https://api.openweathermap.org/geo/1.0/direct"
            params = {"q": location_clean, "limit": 3, "appid": self.api_key}
            
            response = requests.get(geo_url, params=params, timeout=8)
            response.raise_for_status()
            locations = response.json()
            
            if locations:
                best_match = locations[0]
                city_name = best_match["name"]
                country = best_match["country"]
                
                # Format for weather API
                if country == "IN":
                    return f"{city_name},IN"
                else:
                    return f"{city_name},{country}"
            
            # Try with ", India" suffix for Indian context
            if not locations and not "," in location_clean:
                params_india = {"q": f"{location_clean}, India", "limit": 2, "appid": self.api_key}
                response_india = requests.get(geo_url, params=params_india, timeout=8)
                
                if response_india.status_code == 200:
                    locations_india = response_india.json()
                    if locations_india:
                        city_name = locations_india[0]["name"]
                        return f"{city_name},IN"
            
            return None
            
        except Exception as e:
            logger.warning(f"Location validation failed for '{location_candidate}': {e}")
            return None
    
    def _get_comprehensive_weather_data(self, location: str) -> str:
        """Get comprehensive weather analysis for validated location"""
        try:
            # Current weather
            current_url = "https://api.openweathermap.org/data/2.5/weather"
            current_params = {"q": location, "appid": self.api_key, "units": "metric"}
            current_response = requests.get(current_url, params=current_params, timeout=10)
            current_response.raise_for_status()
            current_data = current_response.json()
            
            # Forecast
            forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
            forecast_params = {"q": location, "appid": self.api_key, "units": "metric"}
            forecast_response = requests.get(forecast_url, params=forecast_params, timeout=10)
            forecast_response.raise_for_status()
            forecast_data = forecast_response.json()
            
            # Extract data
            city_name = current_data["name"]
            country = current_data["sys"]["country"]
            temp = current_data["main"]["temp"]
            feels_like = current_data["main"]["feels_like"]
            humidity = current_data["main"]["humidity"]
            pressure = current_data["main"]["pressure"]
            description = current_data["weather"][0]["description"]
            wind_speed = current_data["wind"]["speed"]
            
            # Calculate rainfall
            total_rainfall = sum(item.get("rain", {}).get("3h", 0) for item in forecast_data["list"][:16])
            
            # Professional analysis
            analysis = self._generate_weather_analysis(temp, humidity, wind_speed, total_rainfall, country)
            
            return f"""🌍 **INTELLIGENT WEATHER ANALYSIS**

📍 **Location Confirmed**: {city_name}, {country}
🌡️ **Current Conditions**: {temp}°C (feels like {feels_like}°C), {description.title()}
💧 **Atmospheric Data**: Humidity {humidity}%, Pressure {pressure} hPa
💨 **Wind Conditions**: {wind_speed} m/s
🌧️ **48h Rainfall Forecast**: {total_rainfall:.1f}mm

📊 **PROFESSIONAL ANALYSIS**:
{analysis}

✅ **Intelligence Confidence**: Location validated and confirmed
📡 **Data Source**: OpenWeatherMap API - Real-time meteorological data"""
            
        except Exception as e:
            return f"Weather data retrieval failed for {location}: {str(e)}"
    
    def _generate_weather_analysis(self, temp: float, humidity: int, wind_speed: float, rainfall: float, country: str) -> str:
        """Generate professional weather impact analysis"""
        analysis_points = []
        
        # Temperature analysis
        if temp > 40:
            analysis_points.append("🔥 Extreme heat conditions - Heat emergency protocols recommended")
        elif temp > 35:
            analysis_points.append("🌡️ High temperature stress - Infrastructure cooling demands increased")
        elif temp < 0:
            analysis_points.append("❄️ Freezing conditions - Infrastructure protection required")
        elif temp < 5:
            analysis_points.append("🧥 Cold weather impacts - Heating systems under load")
        else:
            analysis_points.append("✅ Temperature within normal operational range")
        
        # Humidity analysis
        if humidity > 85:
            analysis_points.append("💧 Very high humidity - Mold risk, comfort degradation")
        elif humidity < 30:
            analysis_points.append("🏜️ Low humidity - Fire risk, respiratory issues possible")
        
        # Wind analysis
        if wind_speed > 15:
            analysis_points.append("💨 High wind conditions - Transport disruption likely")
        elif wind_speed > 10:
            analysis_points.append("🌬️ Moderate winds - Outdoor activity caution advised")
        
        # Rainfall analysis
        if rainfall > 75:
            analysis_points.append("🌊 Heavy rainfall forecast - Flood risk assessment required")
        elif rainfall > 25:
            analysis_points.append("🌧️ Significant precipitation - Monitor drainage systems")
        elif rainfall > 5:
            analysis_points.append("☔ Light to moderate rain - Normal precautions sufficient")
        
        return "\n".join(f"• {point}" for point in analysis_points)

class IntelligentAirQualityTool(BaseTool):
    name: str = "Intelligent Air Quality Analysis Tool"
    description: str = "Advanced air quality monitoring with intelligent location detection for any city worldwide"
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv('OPENWEATHERMAP_KEY', 'DEMO_KEY')
    
    def _run(self, query: str) -> str:
        """
        Intelligent air quality analysis for any location in natural language query
        Args:
            query: Natural language query mentioning location and air quality requirements
        """
        try:
            # Extract and validate location
            location = self._extract_location_from_query(query)
            
            if not location:
                return f"""❌ **AIR QUALITY ANALYSIS FAILED**
                
**Query**: {query}
**Issue**: Could not identify valid location for air quality monitoring
**Required**: Clear city name in query
**Examples**: "Air quality in Delhi", "Mumbai pollution levels", "AQI for Tokyo"
**Coverage**: Global air quality monitoring for any major city"""
            
            # Get air quality data
            aqi_data = self._get_air_quality_data(location)
            return aqi_data
            
        except Exception as e:
            logger.error(f"Air Quality Tool error: {e}")
            return f"Air quality analysis error: {str(e)}"
    
    def _extract_location_from_query(self, query: str) -> Optional[str]:
        """Extract and validate location for air quality analysis"""
        # Use same intelligent extraction as weather tool
        weather_tool = IntelligentWeatherTool()
        return weather_tool._extract_and_validate_location(query)
    
    def _get_air_quality_data(self, location: str) -> str:
        """Get comprehensive air quality analysis"""
        try:
            # Get coordinates
            geo_url = "https://api.openweathermap.org/geo/1.0/direct"
            geo_params = {"q": location, "limit": 1, "appid": self.api_key}
            geo_response = requests.get(geo_url, params=geo_params, timeout=10)
            geo_response.raise_for_status()
            geo_data = geo_response.json()
            
            if not geo_data:
                return f"Air quality coordinates not found for {location}"
            
            lat, lon = geo_data[0]["lat"], geo_data[0]["lon"]
            city_name = geo_data[0]["name"]
            country = geo_data[0].get("country", "Unknown")
            
            # Air pollution API
            air_url = "https://api.openweathermap.org/data/2.5/air_pollution"
            air_params = {"lat": lat, "lon": lon, "appid": self.api_key}
            air_response = requests.get(air_url, params=air_params, timeout=10)
            air_response.raise_for_status()
            air_data = air_response.json()
            
            # Process data
            aqi = air_data["list"][0]["main"]["aqi"]
            components = air_data["list"][0]["components"]
            
            aqi_levels = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
            aqi_description = aqi_levels.get(aqi, "Unknown")
            
            # Health impact analysis
            health_analysis = self._analyze_health_impacts(aqi, components)
            
            return f"""🌬️ **INTELLIGENT AIR QUALITY ANALYSIS**

📍 **Location Confirmed**: {city_name}, {country}
📊 **Overall AQI**: {aqi}/5 ({aqi_description})

🔬 **Pollutant Breakdown**:
• PM2.5: {components.get('pm2_5', 'N/A')} μg/m³
• PM10: {components.get('pm10', 'N/A')} μg/m³
• NO2: {components.get('no2', 'N/A')} μg/m³
• SO2: {components.get('so2', 'N/A')} μg/m³
• CO: {components.get('co', 'N/A')} μg/m³
• O3: {components.get('o3', 'N/A')} μg/m³

⚕️ **HEALTH IMPACT ANALYSIS**:
{health_analysis}

✅ **Data Verification**: Real-time air pollution monitoring
📡 **Source**: OpenWeatherMap Air Pollution API"""
            
        except Exception as e:
            return f"Air quality data retrieval failed for {location}: {str(e)}"
    
    def _analyze_health_impacts(self, aqi: int, components: dict) -> str:
        """Analyze health impacts based on AQI and pollutant levels"""
        impacts = []
        
        if aqi >= 5:
            impacts.append("🔴 HAZARDOUS - Avoid all outdoor activities, use air purifiers indoors")
        elif aqi >= 4:
            impacts.append("🟠 UNHEALTHY - Limit outdoor exposure, masks recommended")
        elif aqi >= 3:
            impacts.append("🟡 MODERATE - Sensitive individuals should limit prolonged outdoor exertion")
        elif aqi >= 2:
            impacts.append("🟢 FAIR - Acceptable for most people, minor sensitivity possible")
        else:
            impacts.append("✅ GOOD - Air quality satisfactory for all population groups")
        
        # PM2.5 specific analysis
        pm25 = components.get('pm2_5', 0)
        if pm25 > 55:
            impacts.append("⚠️ PM2.5 at hazardous levels - Respiratory protection essential")
        elif pm25 > 35:
            impacts.append("⚠️ PM2.5 elevated - Consider indoor activities")
        
        return "\n".join(f"• {impact}" for impact in impacts)

# Tool instances for CrewAI integration
intelligent_weather_tool = IntelligentWeatherTool()
intelligent_air_quality_tool = IntelligentAirQualityTool()
