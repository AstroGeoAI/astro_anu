from crewai_tools import BaseTool
import requests
import os
from typing import Dict, Any, Optional
from loguru import logger

class IsroApiTool(BaseTool):
    name: str = "ISRO API Tool"
    description: str = "Access ISRO's Bhuvan platform and satellite data services"
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv('ISRO_API_KEY', '')
        self.base_url = "https://bhuvan.nrsc.gov.in/api"
        
    def _run(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Execute ISRO/Bhuvan API call"""
        if params is None:
            params = {}
            
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            headers = {'Authorization': f'Bearer {self.api_key}'} if self.api_key else {}
            
            response = requests.get(url, params=params, headers=headers, timeout=45)
            response.raise_for_status()
            
            # Handle different response types
            if 'application/json' in response.headers.get('content-type', ''):
                data = response.json()
                return str(data)
            else:
                return response.text
                
        except requests.exceptions.RequestException as e:
            error_msg = f"ISRO API request failed for {endpoint}: {str(e)}"
            logger.error(error_msg)
            return error_msg

isro_api_tool = IsroApiTool()
