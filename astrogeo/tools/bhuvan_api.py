from crewai_tools import BaseTool
import requests
import os
from typing import Dict, Any, Optional
from loguru import logger

class BhuvanApiTool(BaseTool):
    name: str = "Bhuvan API Tool" 
    description: str = "Access ISRO's Bhuvan geospatial platform for Indian satellite data"
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://bhuvan-app1.nrsc.gov.in/api"
        
    def _run(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Execute Bhuvan API call"""
        if params is None:
            params = {}
            
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            response = requests.get(url, params=params, timeout=45)
            response.raise_for_status()
            
            logger.info(f"Successfully fetched data from Bhuvan API: {endpoint}")
            return response.text
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Bhuvan API request failed for {endpoint}: {str(e)}"
            logger.error(error_msg)
            return error_msg

bhuvan_api_tool = BhuvanApiTool()
