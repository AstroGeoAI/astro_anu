#!/usr/bin/env python
import sys
import warnings
import os
from datetime import datetime

from crew import AstroGeoCrew

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

os.makedirs('output', exist_ok=True)

def run():
    """Run the AstroGeo crew with Hugging Face model."""
    
    print("🚀 AstroGeo AI Multi-Agent System (Hugging Face)")
    print("="*50)
    print("🌌 Space Intelligence | 🌍 Environmental Analysis | 🌤️ Weather Intelligence")
    print("💰 Using YOUR Hugging Face model - No OpenAI charges!")
    print("="*50)
    
    query = input("Enter your query: ")
    
    inputs = {'query': query}
    
    print(f"\n🔄 Processing: {query}")
    print("⏳ Agents analyzing...")
    
    try:
        result = AstroGeoCrew().crew().kickoff(inputs=inputs)
        
        print("\n" + "="*60)
        print("🎯 ASTROGEO INTELLIGENCE REPORT")
        print("="*60)
        print(f"Query: {query}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
        print("-"*60)
        print(result.raw)
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("Make sure config files exist and HF token is set")

if __name__ == "__main__":
    run()
