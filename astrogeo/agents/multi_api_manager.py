from crewai import Agent
import yaml
from pathlib import Path
from loguru import logger

class MultiApiManagerAgent:
    def __init__(self, config_path: str = "config/agents.yaml"):
        self.config = self._load_agent_config(config_path)
        self.agent = self._create_agent()
        
    def _load_agent_config(self, config_path: str):
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
                return config['multi_api_management_agent']
        except Exception as e:
            logger.error(f"Failed to load agent config: {e}")
            return {
                'role': 'API Orchestration and Integration Manager',
                'goal': 'Coordinate and optimize API calls across multiple space agencies',
                'backstory': 'Seasoned API integration specialist managing complex multi-vendor ecosystems.'
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

def create_multi_api_manager_agent() -> Agent:
    manager = MultiApiManagerAgent()
    return manager.agent
