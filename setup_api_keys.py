#!/usr/bin/env python3
"""
Interactive API Key Setup Script
Helps users configure their API keys for the MCP Agent system
"""

import os
import sys
from pathlib import Path

def print_banner():
    """Print setup banner"""
    print("🔑 MCP Agent - API Key Setup")
    print("=" * 40)
    print("This script will help you configure your API keys.")
    print()

def check_env_file():
    """Check if .env file exists and load current values"""
    env_file = Path('.env')
    current_keys = {}
    
    if env_file.exists():
        print("📁 Found existing .env file")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    current_keys[key] = value
        
        print("Current configuration:")
        openai_key = current_keys.get('OPENAI_API_KEY', 'Not set')
        weather_key = current_keys.get('WEATHER_API_KEY', 'Not set')
        
        if openai_key and openai_key != 'your_openai_api_key_here':
            print(f"  ✅ OpenAI API Key: {openai_key[:10]}...")
        else:
            print(f"  ❌ OpenAI API Key: {openai_key}")
            
        if weather_key and weather_key != 'your_openweathermap_api_key_here':
            print(f"  ✅ Weather API Key: {weather_key[:10]}...")
        else:
            print(f"  ⚠️  Weather API Key: {weather_key}")
    else:
        print("📁 No .env file found. Creating new one...")
    
    return current_keys

def get_openai_key(current_key):
    """Get OpenAI API key from user"""
    print("\n🔑 OpenAI API Key Setup")
    print("-" * 30)
    print("The OpenAI API key is REQUIRED for the system to work.")
    print("It powers the LLM agent that interprets user queries.")
    print()
    print("To get your API key:")
    print("1. Go to https://platform.openai.com/")
    print("2. Sign up or log in")
    print("3. Go to 'View API keys'")
    print("4. Click 'Create new secret key'")
    print("5. Copy the key (starts with 'sk-')")
    print()
    print("⚠️  IMPORTANT: You need to add a payment method to your OpenAI account!")
    print("   The system uses GPT-3.5-turbo which costs ~$0.0002-0.0004 per query.")
    print()
    
    if current_key and current_key != 'your_openai_api_key_here':
        use_current = input(f"Use existing key ({current_key[:10]}...)? (y/n): ").lower().strip()
        if use_current == 'y':
            return current_key
    
    while True:
        api_key = input("Enter your OpenAI API key (starts with 'sk-'): ").strip()
        
        if not api_key:
            print("❌ API key cannot be empty!")
            continue
            
        if not api_key.startswith('sk-'):
            print("❌ OpenAI API key should start with 'sk-'")
            continue
            
        if len(api_key) < 20:
            print("❌ API key seems too short")
            continue
            
        # Test the API key
        print("🧪 Testing API key...")
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            
            response = client.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=[{'role': 'user', 'content': 'Hello'}],
                max_tokens=5
            )
            print("✅ API key is valid!")
            return api_key
            
        except Exception as e:
            error_msg = str(e).lower()
            if 'invalid' in error_msg or 'authentication' in error_msg:
                print("❌ Invalid API key. Please check and try again.")
            elif 'quota' in error_msg or 'billing' in error_msg:
                print("❌ Billing issue. Please add a payment method to your OpenAI account.")
            else:
                print(f"❌ API test failed: {e}")
            
            retry = input("Try again? (y/n): ").lower().strip()
            if retry != 'y':
                return None

def get_weather_key(current_key):
    """Get OpenWeatherMap API key from user"""
    print("\n🌤️ OpenWeatherMap API Key Setup (Optional)")
    print("-" * 40)
    print("This API key is used for weather queries.")
    print("The system will work without it, but weather queries will show errors.")
    print()
    print("To get your API key:")
    print("1. Go to https://openweathermap.org/api")
    print("2. Sign up for free")
    print("3. Go to 'My API keys'")
    print("4. Copy your default API key")
    print()
    print("✅ Free tier: 1,000 calls/day (no credit card required)")
    print()
    
    if current_key and current_key != 'your_openweathermap_api_key_here':
        use_current = input(f"Use existing key ({current_key[:10]}...)? (y/n): ").lower().strip()
        if use_current == 'y':
            return current_key
    
    skip = input("Skip weather API setup? (y/n): ").lower().strip()
    if skip == 'y':
        return 'your_openweathermap_api_key_here'
    
    while True:
        api_key = input("Enter your OpenWeatherMap API key: ").strip()
        
        if not api_key:
            print("❌ API key cannot be empty!")
            continue
            
        if len(api_key) < 10:
            print("❌ API key seems too short")
            continue
            
        # Test the API key
        print("🧪 Testing API key...")
        try:
            import requests
            
            response = requests.get(
                'http://api.openweathermap.org/data/2.5/weather',
                params={'q': 'London', 'appid': api_key, 'units': 'metric'},
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ API key is valid!")
                return api_key
            elif response.status_code == 401:
                print("❌ Invalid API key")
            else:
                print(f"❌ API error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ API test failed: {e}")
        
        retry = input("Try again? (y/n): ").lower().strip()
        if retry != 'y':
            return 'your_openweathermap_api_key_here'

def save_env_file(openai_key, weather_key):
    """Save API keys to .env file"""
    print("\n💾 Saving configuration...")
    
    env_content = f"""# MCP Agent API Configuration
# Generated by setup_api_keys.py

# Required: OpenAI API Key for LLM agent
OPENAI_API_KEY={openai_key}

# Optional: OpenWeatherMap API Key for weather data
WEATHER_API_KEY={weather_key}
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Configuration saved to .env file")
    print("🔒 Remember: Never commit this file to version control!")

def test_system():
    """Test the system with the new configuration"""
    print("\n🧪 Testing system with new configuration...")
    
    try:
        # Test database
        print("Testing database...")
        import sqlite3
        conn = sqlite3.connect('db/test.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        count = cursor.fetchone()[0]
        print(f"✅ Database: {count} users found")
        conn.close()
        
        # Test tool executor
        print("Testing tool executor...")
        import sys
        sys.path.append('.')
        from app.tools import ToolExecutor
        executor = ToolExecutor()
        result = executor.sql_tool("SELECT COUNT(*) FROM users")
        print(f"✅ Tool executor: {result}")
        
        print("\n🎉 System test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ System test failed: {e}")
        return False

def main():
    """Main setup function"""
    print_banner()
    
    # Check current configuration
    current_keys = check_env_file()
    
    # Get OpenAI API key
    openai_key = get_openai_key(current_keys.get('OPENAI_API_KEY'))
    if not openai_key:
        print("\n❌ OpenAI API key is required. Setup cancelled.")
        return False
    
    # Get Weather API key
    weather_key = get_weather_key(current_keys.get('WEATHER_API_KEY'))
    
    # Save configuration
    save_env_file(openai_key, weather_key)
    
    # Test system
    if test_system():
        print("\n" + "=" * 40)
        print("🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Start the server: python3 start.py")
        print("3. Open frontend.html in your browser")
        print("\nHappy coding! 🚀")
    else:
        print("\n⚠️  Setup completed but system test failed.")
        print("Please check the errors above and try again.")

if __name__ == "__main__":
    main() 