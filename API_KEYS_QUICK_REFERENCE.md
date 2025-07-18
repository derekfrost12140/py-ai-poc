# API Keys Quick Reference

## Required API Keys for MCP Agent System

### 1. OpenAI API Key (REQUIRED)
- Purpose: Powers the LLM agent for tool selection
- Cost: ~$0.0002-0.0004 per query
- Get it: https://platform.openai.com/
- Format: Starts with sk- (e.g., sk-1234567890abcdef...)
- Setup: 
  1. Sign up/login at OpenAI
  2. Go to "View API keys"
  3. Create new secret key
  4. Add payment method (required!)

### 2. OpenWeatherMap API Key (OPTIONAL)
- Purpose: Weather data queries
- Cost: FREE (1,000 calls/day)
- Get it: https://openweathermap.org/api
- Format: Alphanumeric string
- Setup:
  1. Sign up at OpenWeatherMap
  2. Go to "My API keys"
  3. Copy default key

---

## Quick Setup

### Option 1: Interactive Setup (Recommended)
```bash
python3 setup_api_keys.py
```

### Option 2: Manual Setup
1. Create `.env` file:
```bash
touch .env
```

2. Add your API keys:
```env
OPENAI_API_KEY=sk-your_openai_api_key_here
WEATHER_API_KEY=your_openweathermap_api_key_here
```

---

## Cost Breakdown

| Service | Cost per Query | Daily Cost (100 queries) | Monthly Cost |
|---------|----------------|--------------------------|--------------|
| OpenAI | $0.0002-0.0004 | $0.02-0.04 | $0.60-1.20 |
| Weather | FREE | FREE | FREE |

---

## Verification

Test your setup:
```bash
python3 test_system.py
```

Check API keys:
```bash
python3 -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('OpenAI:', 'OK' if os.getenv('OPENAI_API_KEY') else 'MISSING')
print('Weather:', 'OK' if os.getenv('WEATHER_API_KEY') else 'MISSING')
"
```

---

## Security Notes

- Never commit `.env` file to git
- Keep API keys private
- Monitor usage in OpenAI dashboard
- Rotate keys periodically

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Invalid API key" | Check key format and validity |
| "Insufficient credits" | Add payment method to OpenAI |
| "Rate limit exceeded" | Wait and try again |
| Weather queries fail | Get free OpenWeatherMap key |

---

## Next Steps

1. Get API keys
2. Run `python3 setup_api_keys.py`
3. Install dependencies: `pip install -r requirements.txt`
4. Start server: `python3 start.py`
5. Open `frontend.html` in browser

Happy coding! 