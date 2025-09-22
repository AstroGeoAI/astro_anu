from crewai import Agent
from crewai_tools import BaseTool
from typing import Dict, Any
import yaml
from pathlib import Path
from loguru import logger

class DataHarvesterAgent:
    """Data Harvesting Agent for multi-source space data collection"""
    
    def __init__(self, config_path: str = "config/agents.yaml"):
        self.config = self._load_agent_config(config_path)
        self.agent = self._create_agent()
        
    def _load_agent_config(self, config_path: str) -> Dict[str, Any]:
        """Load agent configuration from YAML"""
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
                return config['data_harvesting_agent']
        except Exception as e:
            logger.error(f"Failed to load agent config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Fallback configuration if YAML loading fails"""
        return {
            'role': 'Multi-Source Space Data Harvesting Specialist',
            'goal': 'Efficiently collect, validate, and structure astronomical and geospatial datasets from NASA, ISRO, ESA, and other space agencies APIs',
            'backstory': 'Expert data engineer specializing in space agency APIs with extensive experience in satellite data acquisition and quality validation.'
        }
    
    def _create_agent(self) -> Agent:
        """Create CrewAI Agent with loaded configuration"""
        return Agent(
            role=self.config['role'],
            goal=self.config['goal'],
            backstory=self.config['backstory'],
            verbose=True,
            allow_delegation=False,
            tools=[],  # Tools will be added when available
            max_iter=3,
            memory=True
        )

# Factory function for easy import
def create_data_harvester_agent() -> Agent:
    """Factory function to create data harvester agent"""
    harvester = DataHarvesterAgent()
    return harvester.agent
