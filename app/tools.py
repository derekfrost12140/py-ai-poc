import requests
import sqlite3
import os
from typing import Dict, Any, List, Tuple
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ToolExecutor:
    """MCP Server simulation - executes different types of tools"""
    
    def __init__(self):
        self.weather_api_key = os.getenv('WEATHER_API_KEY')
        self.db_path = 'db/test.db'
        
        # Initialize GraphQL client for SpaceX API
        transport = RequestsHTTPTransport(
            url='https://spacex-production.up.railway.app/',
            verify=True,
            retries=3,
        )
        self.graphql_client = Client(transport=transport, fetch_schema_from_transport=True)
    
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
                'units': 'metric'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            temp = data['main']['temp']
            description = data['weather'][0]['description']
            humidity = data['main']['humidity']
            
            return f"{location}: {temp}°C, {description}, humidity: {humidity}%"
            
        except requests.exceptions.RequestException as e:
            return f"Error fetching weather for {location}: {str(e)}"
        except KeyError as e:
            return f"Error parsing weather data for {location}: {str(e)}"
    
    def sql_tool(self, sql_query: str) -> str:
        """
        SQL Tool - MCP Server simulation
        Executes SQL queries on local SQLite database
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(sql_query)
            
            if sql_query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                conn.close()
                return str(results)
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
            # Use the official SpaceX REST API v3 for recent launches
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
                    formatted_result = "🚀 Recent SpaceX Launches:\n"
                    count = 0
                    
                    for launch in launches:
                        # Only show completed launches (not upcoming)
                        if launch.get('upcoming', False):
                            continue
                            
                        # Limit to 5 most recent completed launches
                        if count >= 5:
                            break
                            
                        mission_name = launch.get('mission_name', 'Unknown')
                        launch_date = launch.get('launch_date_utc', 'Unknown')
                        success = "✅" if launch.get('launch_success') else "❌"
                        flight_number = launch.get('flight_number', 'Unknown')
                        
                        # Format date nicely
                        try:
                            from datetime import datetime
                            date_obj = datetime.fromisoformat(launch_date.replace('Z', '+00:00'))
                            formatted_date = date_obj.strftime('%Y-%m-%d %H:%M UTC')
                        except:
                            formatted_date = launch_date
                        
                        status = "✅ Success" if success else "❌ Failed"
                        
                        formatted_result += f"• {mission_name} (Flight #{flight_number})\n"
                        formatted_result += f"  📅 {formatted_date}\n"
                        formatted_result += f"  {status}\n\n"
                        
                        count += 1
                    
                    if count == 0:
                        return "No recent completed launches found"
                    
                    return formatted_result
                else:
                    return "No launch data found"
            else:
                return f"API Error: {response.status_code}"
            
        except Exception as e:
            return f"SpaceX API Error: {str(e)}\n\nDebug: This might be due to network issues."
    
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
            if not sql_query:
                return "Error: sql_query parameter required for sql_tool"
            return self.sql_tool(sql_query)
            
        elif tool_name == "graphql_tool":
            query = parameters.get('query', '')
            return self.graphql_tool(query)
            
        else:
            return f"Error: Unknown tool '{tool_name}'" 