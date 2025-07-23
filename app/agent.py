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
        
        tool_descriptions_str = chr(10).join(tool_descriptions)
        prompt = f"""
You are an AI agent that needs to select the appropriate tool to handle a user's request.

Available tools:
{tool_descriptions_str}

User query: \"{user_query}\"

Based on the user's request, determine which tool to use and extract the necessary parameters.

Note: For system-related questions like \"What tools are available?\", \"Show me the architecture\", \"How does this work?\", \"What can you do?\", use the system_info_tool.

Important: For any DELETE operation on the database, you must require a security_password parameter. Do not allow DELETE queries without this password.

Respond ONLY with a JSON object in this exact format:
{{
    "tool": "tool_name",
    "parameters": {{
        "param_name": "param_value"
    }}
}}

Examples:
- For weather queries: {{"tool": "weather_tool", "parameters": {{"location": "Paris"}}}}
- For database SELECT queries: {{"tool": "sql_tool", "parameters": {{"sql_query": "SELECT * FROM users"}}}}
- For user count queries: {{"tool": "sql_tool", "parameters": {{"sql_query": "SELECT COUNT(*) FROM users"}}}}
- For prompts like "How many users are in the system?", "User count", "Number of users": {{"tool": "sql_tool", "parameters": {{"sql_query": "SELECT COUNT(*) FROM users"}}}}
- For prompts like "show all users", "list all users", "display all users", "who are the users", "get all users", "show me everyone in the database", "give me a list of users": {{"tool": "sql_tool", "parameters": {{"sql_query": "SELECT * FROM users"}}}}
- For database INSERT queries: {{"tool": "sql_tool", "parameters": {{"sql_query": "INSERT INTO users (name, email) VALUES ('John Doe', 'john@example.com')"}}}}
- For database UPDATE queries: {{"tool": "sql_tool", "parameters": {{"sql_query": "UPDATE users SET email = 'alice@newdomain.com' WHERE name = 'Alice'"}}}}
- For deleting a user: {{"tool": "sql_tool", "parameters": {{"sql_query": "DELETE FROM users WHERE name = 'Michael Scott'", "security_password": "your_password"}}}}
- For prompts like "remove user Michael Scott", "delete user Michael Scott", "delete Michael Scott from the users", "remove Michael Scott from the database", "delete the user named Michael Scott": {{"tool": "sql_tool", "parameters": {{"sql_query": "DELETE FROM users WHERE name = 'Michael Scott'", "security_password": "your_password"}}}}
- For prompts like "delete a user", "remove a user", "delete someone from the users": {{"tool": "sql_tool", "parameters": {{"sql_query": "DELETE FROM users WHERE name = '<user_name>'", "security_password": "your_password"}}}}
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
    
    def _split_instructions(self, user_query: str) -> list:
        """Split a user query into multiple instructions based on delimiters."""
        import re
        # Split on '.', ';', ' and ', or newlines, but keep delimiters for context
        # Avoid splitting inside email addresses or numbers
        # This is a simple heuristic and can be improved
        parts = re.split(r'(?<=[.!?])\s+|\band\b|;|\n', user_query)
        # Remove empty and whitespace-only parts
        return [p.strip() for p in parts if p.strip()]

    def process_query(self, user_query: str, security_password: str = None) -> Dict[str, Any]:
        """
        Main method to process a user query through the MCP-style orchestration system
        Now supports multi-step prompts with step-by-step results.
        """
        try:
            instructions = self._split_instructions(user_query)
            if len(instructions) > 1:
                step_results = []
                for idx, instr in enumerate(instructions, 1):
                    single_result = self._process_single_query(instr, security_password)
                    step_results.append({
                        "step": idx,
                        **single_result
                    })
                return {
                    "success": all(r.get("success", False) for r in step_results),
                    "user_query": user_query,
                    "tool_selected": None,
                    "parameters": None,
                    "result": step_results,
                    "error": None if all(r.get("success", False) for r in step_results) else "One or more steps failed. See results."
                }
            else:
                return self._process_single_query(user_query, security_password)
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "user_query": user_query,
                "tool_selected": None,
                "parameters": None,
                "result": None
            }

    def _process_single_query(self, user_query: str, security_password: str = None) -> Dict[str, Any]:
        """Process a single instruction (existing logic)."""
        try:
            prompt = self._create_tool_selection_prompt(user_query)
            llm_response = self._call_openai(prompt)
            tool_name, parameters = self._parse_llm_response(llm_response)
            if tool_name == "none":
                lowered = user_query.lower()
                if "delete" in lowered and "user" in lowered:
                    import re
                    match = re.search(
                        r"user(?: named)? ([A-Za-z .'-]+?)(?:\\.|,| with| The security password| Security password| password|$)",
                        user_query,
                        re.IGNORECASE
                    )
                    if match:
                        user_name = match.group(1).strip().replace("'", "''")
                        user_name = user_name.rstrip('. ,')
                    else:
                        match2 = re.search(
                            r"delete(?: the)? user(?: named)? ([A-Za-z .'-]+?)(?:\\.|,| with| The security password| Security password| password|$)",
                            user_query,
                            re.IGNORECASE
                        )
                        user_name = match2.group(1).strip().replace("'", "''") if match2 else None
                        if user_name:
                            user_name = user_name.rstrip('. ,')
                    if user_name:
                        sql_query = f"DELETE FROM users WHERE name = '{user_name}'"
                        result = self.tool_executor.sql_tool(sql_query)
                        return {
                            "success": True,
                            "user_query": user_query,
                            "tool_selected": "sql_tool (fallback)",
                            "parameters": {"sql_query": sql_query},
                            "result": result
                        }
                    else:
                        return {
                            "success": False,
                            "error": "Could not extract user name from prompt.",
                            "user_query": user_query,
                            "tool_selected": None,
                            "parameters": None,
                            "result": None
                        }
                return {
                    "success": False,
                    "error": "No suitable tool found for this request",
                    "user_query": user_query,
                    "tool_selected": None,
                    "parameters": None,
                    "result": None
                }
            result = self.tool_executor.execute_tool(tool_name, parameters)
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