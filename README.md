# MCP Agent Orchestration System

A production-quality AI Agent orchestration platform that simulates the MCP (Modular Control Point) architecture. This system demonstrates intelligent tool selection, natural language processing, and seamless API integration.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5--Turbo-purple.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Overview

This system showcases a complete AI Agent orchestration platform that:

- Understands natural language queries using OpenAI GPT-3.5
- Intelligently selects tools from a modular registry
- Executes real-time API calls to external services
- Manages local databases with SQL operations
- Provides a beautiful web interface for interaction

### Architecture

```
User Query → MCP Client (AI Agent) → MCP Registry → MCP Server → Response
```

- MCP Client: LLM-based agent that interprets user intent
- MCP Registry: Tool manifest describing available capabilities
- MCP Server: Tool executor that runs selected operations

## Features

### New in This Version

- **Multi-step Prompt Orchestration:** Supports prompts with multiple instructions (e.g., "Add a user and show the weather"), executing each step in sequence and returning step-by-step results.
- **Frontend UI Enhancements:**
  - Collapsible input/examples section with a slider for maximizing chat area.
  - Chat area auto-expands and auto-scrolls to always show the latest message.
  - Step-by-step results are clearly displayed, including tool and parameter info for each step.
- **Improved Error Handling:**
  - Database locking is handled with retries.
  - Clean display of only relevant tool info in multi-step results.

### Integrated Tools

| Tool | Type | Description | Example Queries |
|------|------|-------------|-----------------|
| SQL Database | Local SQLite | User management and data queries | "Show me all users", "Find user Alice" |
| Weather API | OpenWeatherMap | Real-time weather data | "Weather in Tokyo", "Temperature in London" |
| SpaceX API | REST API | Launch and mission information | "Recent SpaceX launches", "Crew-1 mission" |

### AI Capabilities

- Natural Language Understanding: Converts human queries to technical operations
- Dynamic Tool Selection: Automatically chooses the right tool for each request
- Parameter Extraction: Intelligently extracts relevant parameters from queries
- Error Handling: Graceful failure management and user feedback

### Access Methods

- Web Interface: Beautiful, interactive frontend (frontend.html)
- REST API: Programmatic access with Swagger documentation
- Command Line: Direct API calls for testing and automation

## Prerequisites

- Python 3.8+ (tested with Python 3.13)
- OpenAI API Key (required for AI functionality)
- OpenWeatherMap API Key (optional, for weather features)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd MCpilot-Agent
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Keys

Create a `.env` file in the project root:

```bash
# Required: OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Weather API Key
WEATHER_API_KEY=your_openweathermap_api_key_here
```

#### Getting API Keys

OpenAI API Key:
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Go to "View API keys"
4. Create a new secret key
5. Add payment method (required for API usage)

OpenWeatherMap API Key:
1. Visit [OpenWeatherMap](https://openweathermap.org/api)
2. Sign up for free account
3. Get your API key from the dashboard

### 4. Initialize the System

```bash
python3 start.py
```

The system will:
- ✅ Check Python version and dependencies
- ✅ Validate API key configuration
- ✅ Initialize SQLite database with sample data
- ✅ Start the FastAPI server

## Usage

### Multi-step Prompts (NEW)

You can now enter prompts with multiple instructions, separated by ".", ";", or "and". The system will process each step in order and return a step-by-step result.

**Example Prompt:**

```
Add a new user named Priya Sharma with email priya.sharma@gmail.com. What is the weather in Paris? Show all users in the database.
```

**What happens:**
- Step 1: Adds the user
- Step 2: Gets the weather in Paris
- Step 3: Shows all users (including Priya)

Each step’s result is shown in the chat UI, with tool and parameter info for transparency.

### Web Interface (Recommended)

1. **Start the server:**
   ```bash
   python3 start.py
   ```

2. **Open the frontend:**
   - Navigate to `frontend.html` in your browser
   - Or visit: `http://localhost:8000` (API docs)

3. **Start querying:**
   - Type natural language queries
   - Watch the AI automatically select and execute tools
   - View real-time responses

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `POST /query` | POST | Process natural language queries |
| `GET /health` | GET | System health check |
| `GET /tools` | GET | List available tools |
| `GET /docs` | GET | Interactive API documentation |

### Example API Calls

```bash
# Database query
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me all users"}'

# Weather query
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the weather in Paris?"}'

# SpaceX query
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Recent SpaceX launches"}'
```

## Demo Script

Perfect for showcasing to stakeholders or managers:

### 1. Introduction
"This is an AI Agent system that understands natural language and automatically chooses the right tool to answer questions."

### 2. Database Demo
Query: "Show me all users in the database"
"Notice how the AI automatically detected this was a database query and executed the appropriate SQL command."

### 3. Weather Demo
Query: "What's the weather in New York right now?"
"The AI recognized this as a weather request and called the OpenWeatherMap API for real-time data."

### 4. SpaceX Demo
Query: "Show me recent SpaceX launches"
"The AI identified this as a SpaceX request and fetched the latest launch data from their official API."

### 5. Complex Query Demo
Query: "Tell me about the weather in Tokyo and then show me recent SpaceX missions"
"This demonstrates multi-tool orchestration and complex query handling."

### 6. Multi-step Orchestration Demo (NEW)
Query: "Add a new user named John Doe with email john@example.com. What is the weather in Paris? Show all users in the database."
"The system splits the prompt into three steps, executes each in order, and displays step-by-step results in the chat UI."

## System Architecture

### Core Components

```
app/
├── main.py          # FastAPI application and endpoints
├── agent.py         # MCP Client (AI agent with OpenAI)
├── tools.py         # MCP Server (tool executor)
└── manifest.json    # MCP Registry (tool definitions)

db/
├── init_db.py       # Database initialization
└── test.db          # SQLite database

frontend.html        # Web interface
start.py             # System startup script
```

### Data Flow

1. **User Input**: Natural language query via web interface or API
2. **AI Processing**: GPT-3.5 analyzes intent and selects appropriate tool
3. **Tool Execution**: Selected tool executes with extracted parameters
4. **Response**: Formatted result returned to user

### Tool Selection Logic

The AI agent uses a structured prompt to:
- Analyze user intent
- Match against available tools in the registry
- Extract relevant parameters
- Generate appropriate API calls or database queries

## Configuration

### Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for AI functionality | None |
| `WEATHER_API_KEY` | No | OpenWeatherMap API key | None |

### Database Schema

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Testing

### Automated Tests

```bash
python3 test_system.py
```

### Manual Testing

```bash
# Test all tools
curl -X POST "http://localhost:8000/query" -H "Content-Type: application/json" -d '{"query": "Show me all users"}'
curl -X POST "http://localhost:8000/query" -H "Content-Type: application/json" -d '{"query": "Weather in London"}'
curl -X POST "http://localhost:8000/query" -H "Content-Type: application/json" -d '{"query": "Recent SpaceX launches"}'
```

## Deployment

### Local Development

```bash
python3 start.py
```

### Production Deployment

1. **Set up environment variables**
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Run with production server**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

### Docker (Optional)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| "OpenAI API key not configured" | Add OPENAI_API_KEY to .env file |
| "Weather API key not configured" | Add WEATHER_API_KEY to .env file (optional) |
| "Address already in use" | Kill existing process: pkill -f "python3 start.py" |
| "Import errors" | Install dependencies: pip install -r requirements.txt |

### Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "agent_initialized": true,
  "openai_key_configured": true,
  "weather_key_configured": true
}
```

## Performance

- **Response Time**: 1-3 seconds per query
- **Concurrent Users**: Supports multiple simultaneous requests
- **API Rate Limits**: Respects OpenAI and OpenWeatherMap limits
- **Database**: SQLite for simplicity, easily upgradeable to PostgreSQL

## Future Enhancements

- [ ] Add more tools (news API, translation, etc.)
- [ ] Implement conversation memory
- [ ] Add authentication and user management
- [ ] Support for custom tool definitions
- [ ] Real-time streaming responses
- [ ] Docker containerization
- [ ] Kubernetes deployment manifests

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **OpenAI** for GPT-3.5 Turbo API
- **OpenWeatherMap** for weather data
- **SpaceX** for launch information
- **FastAPI** for the web framework
- **SQLite** for database functionality

---

Built with love for demonstrating AI Agent orchestration and MCP architecture patterns.
