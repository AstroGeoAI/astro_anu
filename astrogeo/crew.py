from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
import os

# Hugging Face model configuration
hf_llm = LLM(
    model="microsoft/DialoGPT-large",
    api_key=os.getenv("HF_API_TOKEN", "hf_your_token_here"),
    base_url="https://api-inference.huggingface.co/models/microsoft/DialoGPT-large"
)

@CrewBase
class AstroGeoCrew():
    """AstroGeo AI crew using Hugging Face"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def astronomical_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['astronomical_agent'],
            verbose=True,
            llm=hf_llm,  # YOUR MODEL!
            max_execution_time=60,
            max_retry_limit=3
        )

    @agent
    def geospatial_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['geospatial_agent'],
            verbose=True,
            llm=hf_llm,  # YOUR MODEL!
            max_execution_time=60,
            max_retry_limit=3
        )

    @agent
    def weather_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['weather_agent'],
            verbose=True,
            llm=hf_llm,  # YOUR MODEL!
            max_execution_time=60,
            max_retry_limit=3
        )

    @task
    def astrogeo_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['astrogeo_analysis_task'],
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
