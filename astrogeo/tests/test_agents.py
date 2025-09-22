import pytest
import yaml
from pathlib import Path
import sys

# Add src to path for testing
sys.path.append(str(Path(__file__).parent.parent / "src"))

from astrogeo.agents.data_harvester import create_data_harvester_agent
from astrogeo.agents.multi_api_manager import create_multi_api_manager_agent
from astrogeo.agents.astro_intel import create_astro_intel_agent

class TestAgents:
    """Test agent initialization and configuration"""
    
    def test_agents_yaml_exists(self):
        """Test that agents.yaml configuration file exists"""
        config_path = Path("config/agents.yaml")
        assert config_path.exists(), "agents.yaml configuration file not found"
    
    def test_agents_yaml_valid(self):
        """Test that agents.yaml is valid YAML"""
        config_path = Path("config/agents.yaml")
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        
        assert config is not None, "agents.yaml is empty or invalid"
        assert isinstance(config, dict), "agents.yaml should contain a dictionary"
    
    def test_data_harvesting_agent_initialization(self):
        """Test DataHarvestingAgent can be initialized from agents.yaml"""
        try:
            agent = create_data_harvester_agent()
            assert agent is not None, "Data harvesting agent not created"
            assert hasattr(agent, 'role'), "Agent missing role attribute"
            assert hasattr(agent, 'goal'), "Agent missing goal attribute"
            assert hasattr(agent, 'backstory'), "Agent missing backstory attribute"
        except Exception as e:
            pytest.fail(f"Data harvesting agent initialization failed: {e}")
    
    def test_multi_api_manager_initialization(self):
        """Test MultiApiManagerAgent can be initialized"""
        try:
            agent = create_multi_api_manager_agent()
            assert agent is not None, "Multi API manager agent not created"
        except Exception as e:
            pytest.fail(f"Multi API manager agent initialization failed: {e}")
    
    def test_astro_intel_initialization(self):
        """Test AstroIntelAgent can be initialized"""
        try:
            agent = create_astro_intel_agent()
            assert agent is not None, "Astro intel agent not created"
        except Exception as e:
            pytest.fail(f"Astro intel agent initialization failed: {e}")
    
    def test_agent_configuration_completeness(self):
        """Test that all agents have complete configuration"""
        config_path = Path("config/agents.yaml")
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        
        required_agents = [
            'data_harvesting_agent',
            'multi_api_management_agent', 
            'astronomical_intelligence_agent',
            'geospatial_analytics_agent'
        ]
        
        for agent_name in required_agents:
            assert agent_name in config, f"Missing agent configuration: {agent_name}"
            
            agent_config = config[agent_name]
            assert 'role' in agent_config, f"Missing role for {agent_name}"
            assert 'goal' in agent_config, f"Missing goal for {agent_name}"
            assert 'backstory' in agent_config, f"Missing backstory for {agent_name}"
