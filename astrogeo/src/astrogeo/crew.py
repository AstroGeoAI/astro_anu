from crewai import Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
import yaml
from pathlib import Path
from loguru import logger

from .agents import *
from .agents.geospatial_expert import create_geospatial_expert_agent  # NEW
from .tools.nasa_api import nasa_api_tool
from .tools.weather_api import weather_tool, rainfall_tool  # NEW
from .tools.isro_api import isro_api_tool
from .tools.esa_api import esa_api_tool
from .tools.bhuvan_api import bhuvan_api_tool

@CrewBase
class AstroGeoCrew():
    """Enhanced AstroGeo Multi-Agent Space Data Analysis Crew with Weather Intelligence"""
    
    def __init__(self):
        self.agents_config = self._load_config('agents')
        self.tasks_config = self._load_config('tasks')
        
    def _load_config(self, config_type: str):
        """Load configuration from YAML files"""
        try:
            config_path = Path(f"config/{config_type}.yaml")
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            logger.error(f"Failed to load {config_type} config: {e}")
            return {}
    
    @agent
    def data_harvester(self) -> Agent:
        return create_data_harvester_agent()
    
    @agent
    def multi_api_manager(self) -> Agent:
        agent = create_multi_api_manager_agent()
        agent.tools = [nasa_api_tool, isro_api_tool, esa_api_tool, bhuvan_api_tool]
        return agent
    
    @agent
    def astro_intel(self) -> Agent:
        agent = create_astro_intel_agent()
        agent.tools = [nasa_api_tool]
        return agent
    
    @agent
    def geo_analytics(self) -> Agent:
        agent = create_geo_analytics_agent()
        agent.tools = [esa_api_tool, bhuvan_api_tool, isro_api_tool]
        return agent
    
    @agent
    def geospatial_expert(self) -> Agent:
        """NEW: Geospatial expert with weather and Earth observation capabilities"""
        return create_geospatial_expert_agent()
    
    @agent
    def visual_intel(self) -> Agent:
        return create_visual_intel_agent()
    
    @agent
    def daily_insights(self) -> Agent:
        return create_daily_insights_agent()
    
    @agent
    def research_assistant(self) -> Agent:
        return create_research_assistant_agent()
    
    @agent
    def qa_agent(self) -> Agent:
        return create_qa_agent()
    
    @task
    def data_harvesting_task(self) -> Task:
        return Task(
            description=self.tasks_config.get('data_harvesting_task', {}).get('description', 'Collect space and geospatial data'),
            expected_output=self.tasks_config.get('data_harvesting_task', {}).get('expected_output', 'Data collection report'),
            agent=self.data_harvester()
        )
    
    @task
    def geospatial_analysis_task(self) -> Task:
        return Task(
            description="Analyze geospatial queries including weather data, rainfall forecasts, satellite imagery, and environmental monitoring using live APIs and remote sensing data.",
            expected_output="Comprehensive geospatial analysis report with weather data, satellite information, and environmental insights based on the specific query.",
            agent=self.geospatial_expert()
        )
    
    @task
    def astronomical_analysis_task(self) -> Task:
        return Task(
            description=self.tasks_config.get('astronomical_analysis_task', {}).get('description', 'Analyze astronomical data'),
            expected_output=self.tasks_config.get('astronomical_analysis_task', {}).get('expected_output', 'Astronomical analysis report'),
            agent=self.astro_intel()
        )
    
    @crew
    def crew(self) -> Crew:
        """Enhanced AstroGeo crew with geospatial intelligence"""
        return Crew(
            agents=[
                self.data_harvester(),
                self.multi_api_manager(),
                self.astro_intel(),
                self.geo_analytics(),
                self.geospatial_expert(),  # NEW AGENT
                self.visual_intel(),
                self.daily_insights(),
                self.research_assistant(),
                self.qa_agent()
            ],
            tasks=[
                self.data_harvesting_task(),
                self.geospatial_analysis_task(),  # NEW TASK
                self.astronomical_analysis_task()
            ],
            process=Process.sequential,
            verbose=True,
            memory=True
        )
