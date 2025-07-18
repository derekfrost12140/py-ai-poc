# API Setup Guide

Complete guide for configuring API keys and external services for the MCP Agent Orchestration System.

## Overview

This system integrates with multiple external APIs to provide comprehensive functionality:

- OpenAI GPT-3.5 Turbo - AI-powered natural language understanding
- OpenWeatherMap - Real-time weather data
- SpaceX API - Launch and mission information

## Required APIs

### 1. OpenAI API (Required)

Purpose: Powers the AI agent that interprets natural language queries and selects appropriate tools.

#### Setup Steps

1. Create OpenAI Account
   - Visit [OpenAI Platform](https://platform.openai.com/)
   - Sign up with email or Google/Microsoft account
   - Verify your email address

2. Add Payment Method
   - Go to "Billing" in your account
   - Add a credit card or payment method
   - Important: OpenAI requires payment info even for free tier

3. Generate API Key
   - Navigate to "API Keys" section
   - Click "Create new secret key"
   - Copy the key (starts with sk-)
   - Store securely: You won't see it again

4. Configure in System
   ```bash
   # Add to .env file
   OPENAI_API_KEY=sk-your-api-key-here
   ```

#### Usage & Costs

- Model: GPT-3.5-turbo
- Cost: ~$0.0002-0.0004 per query
- Rate Limits: 3,500 requests per minute
- Free Tier: $5 credit for new accounts

#### Troubleshooting

| Issue | Solution |
|-------|----------|
| "Invalid API key" | Verify key format starts with sk- |
| "Insufficient credits" | Add payment method and credits |
| "Rate limit exceeded" | Wait 1 minute between requests |
| "Model not found" | Ensure using gpt-3.5-turbo |

## Optional APIs

### 2. OpenWeatherMap API (Optional)

Purpose: Provides real-time weather data for any location worldwide.

#### Setup Steps

1. Create Account
   - Visit [OpenWeatherMap](https://openweathermap.org/api)
   - Click "Sign Up" and create free account
   - Verify email address

2. Get API Key
   - Log into your account
   - Go to "My API Keys" section
   - Copy your default API key
   - Note: New keys may take 2 hours to activate

3. Configure in System
   ```bash
   # Add to .env file
   WEATHER_API_KEY=your-openweathermap-key-here
   ```

#### API Features

- Free Tier: 1,000 calls/day
- Data: Current weather, temperature, humidity, conditions
- Locations: Worldwide coverage
- Units: Metric (Celsius) or Imperial (Fahrenheit)

#### Example Usage

```bash
# Test API directly
curl "http://api.openweathermap.org/data/2.5/weather?q=London&appid=YOUR_KEY&units=metric"
```

#### Troubleshooting

| Issue | Solution |
|-------|----------|
| "API key not valid" | Wait 2 hours for new keys to activate |
| "City not found" | Check city name spelling |
| "Daily limit exceeded" | Upgrade to paid plan or wait 24 hours |

### 3. SpaceX API (No Setup Required)

Purpose: Provides SpaceX launch and mission information.

#### Features

- No API Key Required: Public API
- Data: Launch history, mission details, rocket information
- Rate Limits: Generous limits for public use
- Real-time: Updated with latest launch information

#### Available Data

- Recent launches (2020 onwards)
- Mission names and flight numbers
- Launch dates and success status
- Rocket and payload information

## Configuration

### Environment File Setup

Create a `.env` file in your project root:

```bash
# Required: OpenAI API Key
OPENAI_API_KEY=sk-your-openai-api-key-here

# Optional: Weather API Key
WEATHER_API_KEY=your-openweathermap-api-key-here
```

### Validation

Test your configuration:

```bash
# Check if keys are loaded
python3 -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('OpenAI Key:', '✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Missing')
print('Weather Key:', '✅ Set' if os.getenv('WEATHER_API_KEY') else '❌ Missing')
"
```

### Health Check

Verify system status:

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

## Testing APIs

### Test OpenAI Integration

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Hello, how are you?"}'
```

### Test Weather Integration

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the weather in Tokyo?"}'
```

### Test SpaceX Integration

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me recent SpaceX launches"}'
```

## Security Best Practices

### API Key Management

1. **Never commit API keys to version control**
   - Add `.env` to `.gitignore`
   - Use environment variables in production

2. **Rotate keys regularly**
   - Generate new keys periodically
   - Revoke old keys when not needed

3. **Monitor usage**
   - Check OpenAI usage dashboard
   - Monitor OpenWeatherMap call counts

4. **Use least privilege**
   - Only grant necessary permissions
   - Use read-only keys when possible

### Production Deployment

```bash
# Set environment variables securely
export OPENAI_API_KEY="sk-your-key"
export WEATHER_API_KEY="your-weather-key"

# Start application
python3 start.py
```

## Cost Management

### OpenAI Costs

- **GPT-3.5-turbo**: ~$0.002 per 1K tokens
- **Typical query**: 100-200 tokens
- **Cost per query**: ~$0.0002-0.0004
- **Monthly budget**: Set spending limits in OpenAI dashboard

### OpenWeatherMap Costs

- **Free tier**: 1,000 calls/day
- **Paid plans**: Starting at $40/month for 100K calls
- **Cost per call**: Free tier sufficient for testing

### Budget Recommendations

| Use Case | Monthly Budget | Plan |
|----------|----------------|------|
| **Development/Testing** | $5-10 | OpenAI free tier + OpenWeatherMap free |
| **Small Production** | $20-50 | OpenAI pay-as-you-go + OpenWeatherMap free |
| **Large Production** | $100+ | OpenAI pay-as-you-go + OpenWeatherMap paid |

## 🚨 Troubleshooting

### Common Issues

#### OpenAI Issues

```bash
# Check API key format
echo $OPENAI_API_KEY | grep -E "^sk-[a-zA-Z0-9]{32,}$"

# Test API directly
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models
```

#### Weather API Issues

```bash
# Test weather API
curl "http://api.openweathermap.org/data/2.5/weather?q=London&appid=$WEATHER_API_KEY&units=metric"
```

#### System Issues

```bash
# Check if server is running
curl http://localhost:8000/health

# Check environment variables
python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print('Keys loaded:', bool(os.getenv('OPENAI_API_KEY')))"
```

### Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `"OpenAI API key not configured"` | Missing or invalid key | Add valid key to `.env` |
| `"Weather API key not configured"` | Missing weather key | Add key or skip weather features |
| `"Rate limit exceeded"` | Too many requests | Wait and retry |
| `"Invalid API key"` | Wrong key format | Check key format and validity |

## 📞 Support

### OpenAI Support

- **Documentation**: [OpenAI API Docs](https://platform.openai.com/docs)
- **Community**: [OpenAI Community](https://community.openai.com/)
- **Billing**: [OpenAI Billing](https://platform.openai.com/account/billing)

### OpenWeatherMap Support

- **Documentation**: [OpenWeatherMap API Docs](https://openweathermap.org/api)
- **Support**: [OpenWeatherMap Support](https://openweathermap.org/support)
- **Pricing**: [OpenWeatherMap Pricing](https://openweathermap.org/price)

### System Support

- **Issues**: Check the main README troubleshooting section
- **Health Check**: Use `/health` endpoint
- **Logs**: Check server logs for detailed error information

---

**Need help?** Check the main README or create an issue in the repository. 