import os
import requests
import json

# Ford LLM integration for OpenAI-style chat/completions

def call_model(state):
    """
    Calls Ford's internal LLM using OpenAI-style chat/completions format.
    - Endpoint: from LLM_URL env var
    - Bearer token: from LLM_AUTH_TOKEN env var
    - Payload: {"model", "messages", "temperature"}
    - state.messages: list of HumanMessage, AIMessage, or FunctionMessage (dicts/objects)
    - Returns: { "messages": [AIMessage(...)] }
    - Handles tool_calls if present in AIMessage
    - Robust error handling
    """
    LLM_URL = os.getenv("LLM_URL", "https://api.pivpn.core.ford.com/fordllmapi/api/v1/chat/completions")
    LLM_AUTH_TOKEN = os.getenv("LLM_AUTH_TOKEN", "<YOUR_FORD_LLM_TOKEN>")
    MODEL = os.getenv("LLM_MODEL", "ford-llm-chat")
    TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))

    # Convert state.messages to OpenAI format
    def convert_message(msg):
        # If already dict, use as is; else, try to extract type/role/content
        if isinstance(msg, dict):
            role = msg.get("role") or msg.get("type")
            content = msg.get("content")
            message = {"role": role, "content": content}
            # Add tool_calls if present
            if role == "assistant" and "tool_calls" in msg:
                message["tool_calls"] = msg["tool_calls"]
            return message
        # If object, try to extract attributes
        role = getattr(msg, "role", None) or getattr(msg, "type", None)
        content = getattr(msg, "content", None)
        message = {"role": role, "content": content}
        if role == "assistant" and hasattr(msg, "tool_calls"):
            message["tool_calls"] = getattr(msg, "tool_calls")
        return message

    messages = [convert_message(m) for m in getattr(state, "messages", [])]

    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": TEMPERATURE
    }

    headers = {
        "Authorization": f"Bearer {LLM_AUTH_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(LLM_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        return {"messages": [{"type": "error", "content": f"Ford LLM request failed: {str(e)}"}]}
    except json.JSONDecodeError as e:
        return {"messages": [{"type": "error", "content": f"Ford LLM response not valid JSON: {str(e)}"}]}

    # Parse response: expect OpenAI-style { choices: [{ message: { content, ... } }] }
    try:
        choice = data["choices"][0]["message"]
        content = choice.get("content", "")
        tool_calls = choice.get("tool_calls")
        ai_message = {"type": "ai", "content": content}
        if tool_calls:
            ai_message["tool_calls"] = tool_calls
        return {"messages": [ai_message]}
    except Exception as e:
        return {"messages": [{"type": "error", "content": f"Ford LLM response parsing error: {str(e)}"}]} 