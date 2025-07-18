import json
import os
import openai
from typing import Dict, Any, Tuple
from .tools import ToolExecutor

class MCPAgent:
    """
    MCP Client simulation - LLM-based agent that interprets user intent
    and orchestrates tool selection and execution
    """
    
    def __init__(self):
        # Load OpenAI API key
        openai.api_key = os.getenv('OPENAI_API_KEY')
        if not openai.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        # Load tool manifest (MCP Registry)
        self.manifest = self._load_manifest()
        
        # Initialize tool executor (MCP Server simulation)
        self.tool_executor = ToolExecutor()
    
    def _load_manifest(self) -> Dict[str, Any]:
        """Load the MCP-style tool manifest from JSON file"""
        try:
            with open('app/manifest.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError("manifest.json not found in app directory")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in manifest.json: {e}")
    
    def _create_tool_selection_prompt(self, user_query: str) -> str:
        """Create a structured prompt for the LLM to select the appropriate tool"""
        
        # Build tool descriptions from manifest
        tool_descriptions = []
        for tool in self.manifest['tools']:
            desc = f"- {tool['name']}: {tool['description']}"
            if 'parameters' in tool:
                params = []
                for param_name, param_info in tool['parameters'].items():
                    params.append(f"{param_name} ({param_info['type']})")
                desc += f" [Parameters: {', '.join(params)}]"
            tool_descriptions.append(desc)
        
        prompt = f"""
You are an AI agent that needs to select the appropriate tool to handle a user's request.

Available tools:
{chr(10).join(tool_descriptions)}

User query: "{user_query}"

Based on the user's request, determine which tool to use and extract the necessary parameters.

Note: For system-related questions like "What tools are available?", "Show me the architecture", "How does this work?", "What can you do?", use the system_info_tool.

Respond ONLY with a JSON object in this exact format:
{{
    "tool": "tool_name",
    "parameters": {{
        "param_name": "param_value"
    }}
}}

Examples:
- For weather queries: {{"tool": "weather_tool", "parameters": {{"location": "Paris"}}}}
- For database queries: {{"tool": "sql_tool", "parameters": {{"sql_query": "SELECT * FROM users"}}}}
- For SpaceX queries: {{"tool": "graphql_tool", "parameters": {{"query": "recent launches"}}}}
- For system info queries: {{"tool": "system_info_tool", "parameters": {{"query": "architecture"}}}}

If no tool matches the request, respond with:
{{"tool": "none", "parameters": {{}}}}

JSON response:
"""
        return prompt
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI GPT-3.5 to get tool selection and parameters"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai.api_key)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant that selects tools based on user requests. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip() if response.choices[0].message.content else ""
            
        except Exception as e:
            raise Exception(f"OpenAI API call failed: {str(e)}")
    
    def _parse_llm_response(self, llm_response: str) -> Tuple[str, Dict[str, Any]]:
        """Parse the LLM response to extract tool name and parameters"""
        try:
            # Clean up the response and parse JSON
            response_text = llm_response.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            parsed = json.loads(response_text)
            
            tool_name = parsed.get('tool', 'none')
            parameters = parsed.get('parameters', {})
            
            return tool_name, parameters
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {e}")
        except Exception as e:
            raise ValueError(f"Error parsing LLM response: {e}")
    
    def process_query(self, user_query: str) -> Dict[str, Any]:
        """
        Main method to process a user query through the MCP-style orchestration system
        
        This simulates the complete MCP Client -> MCP Registry -> MCP Server flow
        """
        try:
            # Step 1: MCP Client - Create prompt for tool selection
            prompt = self._create_tool_selection_prompt(user_query)
            
            # Step 2: MCP Client - Call LLM to determine tool and parameters
            llm_response = self._call_openai(prompt)
            
            # Step 3: MCP Client - Parse LLM response
            tool_name, parameters = self._parse_llm_response(llm_response)
            
            # Step 4: Check if a valid tool was selected
            if tool_name == "none":
                return {
                    "success": False,
                    "error": "No suitable tool found for this request",
                    "user_query": user_query,
                    "tool_selected": None,
                    "parameters": None,
                    "result": None
                }
            
            # Step 5: MCP Server - Execute the selected tool
            result = self.tool_executor.execute_tool(tool_name, parameters)
            
            # Step 6: Return formatted response
            return {
                "success": True,
                "user_query": user_query,
                "tool_selected": tool_name,
                "parameters": parameters,
                "result": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "user_query": user_query,
                "tool_selected": None,
                "parameters": None,
                "result": None
            } 