from crewai import Agent
import yaml
from loguru import logger

class VisualIntelAgent:
    def __init__(self, config_path: str = "config/agents.yaml"):
        self.config = self._load_agent_config(config_path)
        self.agent = self._create_agent()
        
    def _load_agent_config(self, config_path: str):
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
                return config.get('visual_intelligence_agent', {})
        except Exception as e:
            return {
                'role': 'Space Imagery Analysis and Visual Processing Specialist',
                'goal': 'Process and analyze visual data from space missions including Mars rover images and astronomy pictures',
                'backstory': 'Computer vision expert specializing in space imagery with access to NASA Mars rover photos and APOD images.'
            }
    
    def _create_agent(self) -> Agent:
        # Import NASA visual tools
        from ..tools.nasa_api import nasa_mars_rover_tool, nasa_apod_tool
        from ..tools.dall_e_tool import dall_e_tool
        
        return Agent(
            role=self.config.get('role', 'Visual Intelligence Agent'),
            goal=self.config.get('goal', 'Analyze space imagery and visual data'),
            backstory=self.config.get('backstory', 'Expert in visual analysis with NASA imagery access'),
            verbose=True,
            allow_delegation=False,
            tools=[nasa_mars_rover_tool, nasa_apod_tool, dall_e_tool],
            max_iter=3,
            memory=True
        )

def create_visual_intel_agent() -> Agent:
    visual = VisualIntelAgent()
    return visual.agent
