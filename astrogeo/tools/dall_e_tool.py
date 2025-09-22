from crewai_tools import BaseTool
import openai
import os
from typing import Optional
from loguru import logger

class DallETool(BaseTool):
    name: str = "DALL-E Image Generation Tool"
    description: str = "Generate space-themed images using OpenAI's DALL-E for visualization"
    
    def __init__(self):
        super().__init__()
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
    def _run(self, prompt: str, size: Optional[str] = "1024x1024") -> str:
        """Generate image using DALL-E"""
        try:
            # Enhance prompt for space/astronomy theme
            space_prompt = f"Space astronomy visualization: {prompt}. High quality, scientific, detailed."
            
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=space_prompt,
                size=size,
                quality="standard",
                n=1,
            )
            
            image_url = response.data[0].url
            logger.info(f"Generated space image for prompt: {prompt}")
            
            return f"Generated image URL: {image_url}"
            
        except Exception as e:
            error_msg = f"DALL-E image generation failed: {str(e)}"
            logger.error(error_msg)
            return error_msg

dall_e_tool = DallETool()
