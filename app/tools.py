import requests
import sqlite3
import os
from typing import Dict, Any, List, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ToolExecutor:
    """MCP Server simulation - executes different types of tools"""
    
    def __init__(self):
        self.weather_api_key = os.getenv('WEATHER_API_KEY')
        self.db_path = 'db/test.db'
    
    def weather_tool(self, location: str) -> str:
        """
        Weather Tool (REST API) - MCP Server simulation
        Calls OpenWeatherMap API to get current weather for a location
        """
        if not self.weather_api_key:
            return "Error: Weather API key not configured"
        
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': location,
                'appid': self.weather_api_key,
                'units': 'imperial'  # Use Fahrenheit
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            temp = data['main']['temp']
            description = data['weather'][0]['description']
            humidity = data['main']['humidity']
            
            return f"{location}: {temp}°F, {description}, humidity: {humidity}%"
            
        except requests.exceptions.RequestException as e:
            return f"Error fetching weather for {location}: {str(e)}"
        except KeyError as e:
            return f"Error parsing weather data for {location}: {str(e)}"
    
    def sql_tool(self, sql_query: str, security_password: str = None) -> str:
        """
        SQL Tool - MCP Server simulation
        Executes SQL queries on local SQLite database
        """
        try:
            # Remove password check for DELETE
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(sql_query)
            if sql_query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                conn.close()
                if not results:
                    return "No results found."
                # Format as a user-friendly list
                formatted = []
                for row in results:
                    user_info = (
                        f"ID: {row[0]} Name: {row[1]} Email: {row[2]} Created At: {row[3]}"
                    )
                    formatted.append(user_info)
                return "User List:\n" + "\n\n".join(formatted)
            else:
                conn.commit()
                conn.close()
                return f"Query executed successfully: {sql_query}"
        except sqlite3.Error as e:
            return f"SQL Error: {str(e)}"
        except Exception as e:
            return f"Error executing SQL query: {str(e)}"
    
    def graphql_tool(self, query: str) -> str:
        """
        SpaceX Tool - MCP Server simulation
        Queries SpaceX REST API for mission and launch information
        """
        try:
            query_lower = query.lower()
            
            # Different endpoints based on query type
            if 'rocket' in query_lower or 'rockets' in query_lower:
                # Get rocket information
                response = requests.get(
                    'https://api.spacexdata.com/v3/rockets',
                    timeout=10
                )
                
                if response.status_code == 200:
                    rockets = response.json()
                    if rockets:
                        formatted_result = "🚀 SpaceX Rockets:\n"
                        for rocket in rockets[:5]:  # Show top 5 rockets
                            name = rocket.get('rocket_name', 'Unknown')
                            type = rocket.get('rocket_type', 'Unknown')
                            cost = rocket.get('cost_per_launch', 'Unknown')
                            success_rate = rocket.get('success_rate_pct', 'Unknown')
                            description = rocket.get('description', '')[:100] + '...' if rocket.get('description') else 'No description available'
                            
                            formatted_result += f"• {name} ({type})\n"
                            formatted_result += f"  💰 Cost per launch: ${cost:,}\n"
                            formatted_result += f"  📊 Success rate: {success_rate}%\n"
                            formatted_result += f"  📝 {description}\n\n"
                        
                        return formatted_result
                    else:
                        return "No rocket data found"
                else:
                    return f"API Error: {response.status_code}"
            
            elif 'mission' in query_lower or 'missions' in query_lower:
                # Get mission information with more details
                response = requests.get(
                    'https://api.spacexdata.com/v3/launches',
                    params={
                        'limit': 8,
                        'order': 'desc'
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    launches = response.json()
                    
                    if launches:
                        formatted_result = "🚀 SpaceX Missions:\n"
                        count = 0
                        
                        for launch in launches:
                            if launch.get('upcoming', False):
                                continue
                                
                            if count >= 5:
                                break
                                
                            mission_name = launch.get('mission_name', 'Unknown')
                            launch_date = launch.get('launch_date_utc', 'Unknown')
                            success = launch.get('launch_success')
                            flight_number = launch.get('flight_number', 'Unknown')
                            rocket_name = launch.get('rocket', {}).get('rocket_name', 'Unknown')
                            launch_site = launch.get('launch_site', {}).get('site_name', 'Unknown')
                            details = launch.get('details', '')[:150] + '...' if launch.get('details') else 'No details available'
                            
                            # Format date
                            try:
                                from datetime import datetime
                                date_obj = datetime.fromisoformat(launch_date.replace('Z', '+00:00'))
                                formatted_date = date_obj.strftime('%Y-%m-%d %H:%M UTC')
                            except:
                                formatted_date = launch_date
                            
                            status = "✅ Success" if success else "❌ Failed"
                            
                            formatted_result += f"• {mission_name} (Flight #{flight_number})\n"
                            formatted_result += f"  🚀 Rocket: {rocket_name}\n"
                            formatted_result += f"  📍 Launch Site: {launch_site}\n"
                            formatted_result += f"  📅 {formatted_date}\n"
                            formatted_result += f"  {status}\n"
                            formatted_result += f"  📝 {details}\n\n"
                            
                            count += 1
                        
                        if count == 0:
                            return "No recent completed missions found"
                        
                        return formatted_result
                    else:
                        return "No mission data found"
                else:
                    return f"API Error: {response.status_code}"
            
            else:
                # Default: recent launches
                response = requests.get(
                    'https://api.spacexdata.com/v3/launches',
                    params={
                        'limit': 10,
                        'order': 'desc'
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    launches = response.json()
                    
                    if launches:
                        formatted_result = "🚀 Recent SpaceX Launches:\n\n"
                        count = 0
                        for launch in launches:
                            if launch.get('upcoming', False):
                                continue
                            if count >= 5:
                                break
                            mission_name = launch.get('mission_name', 'Unknown')
                            launch_date = launch.get('launch_date_utc', 'Unknown')
                            success = launch.get('launch_success')
                            flight_number = launch.get('flight_number', 'Unknown')
                            # Format date
                            try:
                                from datetime import datetime
                                date_obj = datetime.fromisoformat(launch_date.replace('Z', '+00:00'))
                                formatted_date = date_obj.strftime('%Y-%m-%d %H:%M UTC')
                            except:
                                formatted_date = launch_date
                            status = "✅ Success" if success else "❌ Failed"
                            formatted_result += f"\n{mission_name} (Flight #{flight_number})\n  📅 {formatted_date}\n  {status}\n"
                            count += 1
                        if count == 0:
                            return "No recent completed launches found"
                        return formatted_result.strip()
                    else:
                        return "No launch data found"
                else:
                    return f"API Error: {response.status_code}"
            
        except Exception as e:
            return f"SpaceX API Error: {str(e)}\n\nDebug: This might be due to network issues."
    
    def system_info_tool(self, query: str) -> str:
        """
        System Information Tool - MCP Server simulation
        Provides information about the system architecture, tools, and capabilities
        """
        query_lower = query.lower()
        
        if 'tool' in query_lower or 'function' in query_lower or 'available' in query_lower:
            return """🔧 Available Tools in MCP Agent System

1. **Weather Tool** (weather_tool)
   - Purpose: Get current weather information for any location
   - Parameters: location (city name, coordinates, etc.)
   - Example: "What's the weather in New York?"
   - API: OpenWeatherMap REST API

2. **SQL Tool** (sql_tool)
   - Purpose: Query local SQLite database
   - Parameters: sql_query (SQL statement)
   - Example: "Show me all users in the database"
   - Database: Local SQLite with users table

3. **SpaceX Tool** (graphql_tool)
   - Purpose: Get SpaceX launch and rocket information
   - Parameters: query (rocket/mission/launch keywords)
   - Example: "Get details about SpaceX rockets"
   - API: SpaceX REST API v3

4. **System Info Tool** (system_info_tool)
   - Purpose: Get information about the system itself
   - Parameters: query (system-related questions)
   - Example: "What tools are available?"

Each tool simulates an MCP Server that the AI agent can call based on user intent."""

        elif 'architecture' in query_lower or 'how' in query_lower or 'work' in query_lower:
            return """🏗️ MCP Agent System Architecture

**MCP (Modular Control Point) Architecture Simulation**

1. **Frontend Layer**
   - Simple HTML/JS interface for user queries
   - Communicates with FastAPI backend via REST

2. **API Gateway (FastAPI)**
   - `/query` endpoint receives natural language queries
   - `/tools` endpoint lists available tools
   - `/health` endpoint for system status
   - CORS enabled for frontend communication

3. **AI Agent (MCP Client Simulation)**
   - Uses OpenAI GPT-3.5 Turbo for intent recognition
   - Analyzes user queries to select appropriate tools
   - Extracts parameters for tool execution
   - Manages tool orchestration

4. **Tool Registry (manifest.json)**
   - JSON manifest listing all available tools
   - Defines tool names, descriptions, and parameters
   - Acts as MCP Registry for tool discovery

5. **Tool Executors (MCP Server Simulation)**
   - Weather Tool: REST API calls to OpenWeatherMap
   - SQL Tool: Local SQLite database operations
   - SpaceX Tool: REST API calls to SpaceX API
   - System Info Tool: Provides system documentation

**Data Flow**
User Query → Frontend → FastAPI → AI Agent → Tool Selection → Tool Execution → Response → Frontend

**Key Features**
- Modular tool architecture
- Natural language processing
- Dynamic tool selection
- Error handling and fallbacks
- Real-time API integration"""

        elif 'agent' in query_lower or 'ai' in query_lower or 'can' in query_lower:
            return """🤖 AI Agent Capabilities

**What the AI Agent Can Do**

1. **Natural Language Understanding**
   - Interprets user queries in plain English
   - Understands context and intent
   - Extracts relevant parameters

2. **Intelligent Tool Selection**
   - Chooses the most appropriate tool for each query
   - Handles ambiguous requests
   - Provides fallback responses

3. **Multi-Tool Orchestration**
   - Manages multiple tool types (REST, SQL, GraphQL)
   - Handles tool execution and error recovery
   - Formats responses for user consumption

4. **Dynamic Query Processing**
   - Weather queries: "What's the weather in Tokyo?"
   - Database queries: "Show me all users"
   - SpaceX queries: "Get rocket information"
   - System queries: "What tools are available?"

5. **Error Handling**
   - Graceful handling of API failures
   - User-friendly error messages
   - Fallback responses when tools are unavailable

**Example Capabilities**
- "Get weather for New York" → Weather Tool
- "Show me database users" → SQL Tool  
- "SpaceX rocket details" → SpaceX Tool
- "What can you do?" → System Info Tool

The agent acts as an intelligent coordinator between user requests and specialized tools."""

        else:
            return """📋 MCP Agent System Overview

**System Purpose**
This is a production-quality AI Agent orchestration system that simulates MCP (Modular Control Point) architecture. It demonstrates how AI agents can intelligently route user queries to specialized tools.

**Core Components**
- FastAPI backend with REST endpoints
- OpenAI-powered AI agent for intent recognition
- Modular tool system with 4 specialized tools
- SQLite database for local data storage
- Web frontend for user interaction

**Key Technologies**
- Python 3.13, FastAPI, SQLite
- OpenAI GPT-3.5 Turbo API
- OpenWeatherMap API, SpaceX API
- HTML/JavaScript frontend

**Use Cases**
- Weather information retrieval
- Database querying and management
- Space mission and rocket data
- System documentation and help

Ask me about specific tools, architecture, or capabilities for more detailed information!"""

    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """
        Main tool execution router - MCP Server simulation
        Routes tool calls to appropriate handlers based on tool name
        """
        if tool_name == "weather_tool":
            location = parameters.get('location')
            if not location:
                return "Error: location parameter required for weather_tool"
            return self.weather_tool(location)
            
        elif tool_name == "sql_tool":
            sql_query = parameters.get('sql_query')
            security_password = parameters.get('security_password')
            if not sql_query:
                return "Error: sql_query parameter required for sql_tool"
            return self.sql_tool(sql_query, security_password)
            
        elif tool_name == "graphql_tool":
            query = parameters.get('query', '')
            return self.graphql_tool(query)
            
        elif tool_name == "system_info_tool":
            query = parameters.get('query', '')
            return self.system_info_tool(query)
            
        else:
            return f"Error: Unknown tool '{tool_name}'" 