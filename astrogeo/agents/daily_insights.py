from crewai import Agent
import yaml
from loguru import logger

class DailyInsightsAgent:
    def __init__(self, config_path: str = "config/agents.yaml"):
        self.config = self._load_agent_config(config_path)
        self.agent = self._create_agent()
        
    def _load_agent_config(self, config_path: str):
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
                return config.get('daily_insights_agent', {})
        except Exception as e:
            return {
                'role': 'Space Events Monitoring and Daily Intelligence Reporter',
                'goal': 'Monitor real-time space events and compile daily summaries',
                'backstory': 'Space intelligence analyst maintaining constant vigilance over the cosmos.'
            }
    
    def _create_agent(self) -> Agent:
        return Agent(
            role=self.config.get('role', 'Daily Insights Agent'),
            goal=self.config.get('goal', 'Monitor space events'),
            backstory=self.config.get('backstory', 'Expert in space monitoring'),
            verbose=True,
            allow_delegation=False,
            max_iter=3,
            memory=True
        )

def create_daily_insights_agent() -> Agent:
    insights = DailyInsightsAgent()
    return insights.agent
