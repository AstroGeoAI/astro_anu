from crewai import Agent
import yaml
from loguru import logger

class AnomalyDetectionAgent:
    def __init__(self, config_path: str = "config/agents.yaml"):
        self.config = self._load_agent_config(config_path)
        self.agent = self._create_agent()
        
    def _load_agent_config(self, config_path: str):
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
                return config.get('anomaly_detection_agent', {})
        except Exception as e:
            return {
                'role': 'Anomaly Detection and Alert System Specialist',
                'goal': 'Identify unusual patterns in space data, detect anomalies, and monitor space weather threats',
                'backstory': 'Expert in pattern recognition and space weather monitoring with access to NASA solar activity and asteroid data.'
            }
    
    def _create_agent(self) -> Agent:
        # Import NASA monitoring tools
        from ..tools.nasa_api import nasa_solar_activity_tool, nasa_asteroid_tool
        
        return Agent(
            role=self.config.get('role', 'Anomaly Detection Agent'),
            goal=self.config.get('goal', 'Detect space anomalies and threats'),
            backstory=self.config.get('backstory', 'Expert in anomaly detection with NASA monitoring tools'),
            verbose=True,
            allow_delegation=False,
            tools=[nasa_solar_activity_tool, nasa_asteroid_tool],
            max_iter=3,
            memory=True
        )

def create_anomaly_detection_agent() -> Agent:
    anomaly = AnomalyDetectionAgent()
    return anomaly.agent
