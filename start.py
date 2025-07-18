#!/usr/bin/env python3
"""
MCP Agent Orchestration System - Startup Script
Initializes the database and starts the FastAPI server
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import openai
        import requests
        import gql
        import dotenv
        print("✅ All dependencies are installed")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        sys.exit(1)

def check_env_file():
    """Check if .env file exists and has required keys"""
    env_file = Path('.env')
    if not env_file.exists():
        print("⚠️  .env file not found. Creating template...")
        with open('.env', 'w') as f:
            f.write("OPENAI_API_KEY=your_openai_api_key_here\n")
            f.write("WEATHER_API_KEY=your_openweathermap_api_key_here\n")
        print("📝 Created .env template. Please add your API keys.")
        return False
    
    # Check if API keys are configured
    from dotenv import load_dotenv
    load_dotenv()
    
    openai_key = os.getenv('OPENAI_API_KEY')
    weather_key = os.getenv('WEATHER_API_KEY')
    
    if not openai_key or openai_key == 'your_openai_api_key_here':
        print("⚠️  OpenAI API key not configured in .env file")
        return False
    
    if not weather_key or weather_key == 'your_openweathermap_api_key_here':
        print("⚠️  Weather API key not configured (optional, weather tool will show errors)")
    
    print("✅ Environment variables configured")
    return True

def init_database():
    """Initialize the SQLite database"""
    try:
        print("🗄️  Initializing database...")
        from db.init_db import init_database
        init_database()
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting MCP Agent server...")
    print("📡 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🌐 Frontend: Open frontend.html in your browser")
    print("\nPress Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")

def main():
    """Main startup function"""
    print("🤖 MCP Agent Orchestration System")
    print("=" * 40)
    
    # Check prerequisites
    check_python_version()
    check_dependencies()
    
    # Check environment
    env_ok = check_env_file()
    
    # Initialize database
    if not init_database():
        print("❌ Failed to initialize database")
        sys.exit(1)
    
    # Start server
    if env_ok:
        start_server()
    else:
        print("\n⚠️  Please configure your API keys in the .env file before starting the server")
        print("You can still start the server manually with: uvicorn app.main:app --reload")

if __name__ == "__main__":
    main() 