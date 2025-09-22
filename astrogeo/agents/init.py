from .data_harvester import create_data_harvester_agent
from .multi_api_manager import create_multi_api_manager_agent
from .astro_intel import create_astro_intel_agent
from .geo_analytics import create_geo_analytics_agent

# Create similar imports for all 12 agents
from .visual_intel import create_visual_intel_agent
from .daily_insights import create_daily_insights_agent
from .research_assistant import create_research_assistant_agent
from .qa_agent import create_qa_agent
from .predictive import create_predictive_agent
from .visualization3d import create_visualization3d_agent
from .collaborative_research import create_collaborative_research_agent
from .anomaly_detection import create_anomaly_detection_agent

__all__ = [
    'create_data_harvester_agent',
    'create_multi_api_manager_agent',
    'create_astro_intel_agent',
    'create_geo_analytics_agent',
    'create_visual_intel_agent',
    'create_daily_insights_agent',
    'create_research_assistant_agent',
    'create_qa_agent',
    'create_predictive_agent',
    'create_visualization3d_agent',
    'create_collaborative_research_agent',
    'create_anomaly_detection_agent'
]
