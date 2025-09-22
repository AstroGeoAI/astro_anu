from crewai_tools import BaseTool
import requests
import os
from typing import Dict, Any, Optional
from loguru import logger

class EsaApiTool(BaseTool):
    name: str = "ESA API Tool"
    description: str = "Access ESA's Copernicus and Earth observation data services"
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv('ESA_API_KEY', '')
        self.base_url = "https://scihub.copernicus.eu/apihub"
        
    def _run(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Execute ESA API call"""
        if params is None:
            params = {}
            
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            auth = (self.api_key, self.api_key) if self.api_key else None
            
            response = requests.get(url, params=params, auth=auth, timeout=60)
            response.raise_for_status()
            
            logger.info(f"Successfully fetched data from ESA API: {endpoint}")
            return response.text
            
        except requests.exceptions.RequestException as e:
            error_msg = f"ESA API request failed for {endpoint}: {str(e)}"
            logger.error(error_msg)
            return error_msg

esa_api_tool = EsaApiTool()
