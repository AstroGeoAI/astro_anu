from crewai import Agent
import yaml
from loguru import logger

class GeoAnalyticsAgent:
    def __init__(self, config_path: str = "config/agents.yaml"):
        self.config = self._load_agent_config(config_path)
        self.agent = self._create_agent()
        
    def _load_agent_config(self, config_path: str):
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
                return config['geospatial_analytics_agent']
        except Exception as e:
            return {
                'role': 'Earth Observation and Geospatial Intelligence Analyst',
                'goal': 'Process satellite imagery and perform geospatial analysis',
                'backstory': 'Geospatial intelligence expert with extensive satellite imagery analysis experience.'
            }
    
    def _create_agent(self) -> Agent:
        return Agent(
            role=self.config['role'],
            goal=self.config['goal'],
            backstory=self.config['backstory'],
            verbose=True,
            allow_delegation=False,
            tools=[],
            max_iter=3,
            memory=True
        )

def create_geo_analytics_agent() -> Agent:
    geo = GeoAnalyticsAgent()
    return geo.agent
