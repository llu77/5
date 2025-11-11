# Quick Start Guide - Strapi AI Integration

## Setup (Already Completed ✓)

Your Strapi AI integration is ready to use! Here's what has been configured:

### ✓ Environment Configuration
- API key configured in `.env` file
- Axios installed for HTTP requests

### ✓ API Structure
```
src/api/ai-assistant/
├── controllers/ai-assistant.ts    # Request handlers
├── routes/ai-assistant.ts         # API routes
└── services/ai-assistant.ts       # AI service logic
```

## Usage in 3 Steps

### 1. Start the Server

```bash
npm run develop
```

The server will start on `http://localhost:1337`

### 2. Test the Integration

Open a new terminal and run:

```bash
npm run test:ai
```

This will test all AI endpoints automatically.

### 3. Make Your First AI Request

```bash
# Test AI generation
curl -X POST http://localhost:1337/api/ai-assistant/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a tagline for a coffee shop"
  }'
```

## Available Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/ai-assistant/health` | GET | Check AI status |
| `/api/ai-assistant/generate` | POST | Generate AI responses |
| `/api/ai-assistant/content` | POST | Generate specific content |
| `/api/ai-assistant/analyze` | POST | Analyze text |

## Quick Examples

### Check if AI is Working
```bash
curl http://localhost:1337/api/ai-assistant/health
```

### Generate Content
```bash
curl -X POST http://localhost:1337/api/ai-assistant/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Write a welcome message"}'
```

### Analyze Sentiment
```bash
curl -X POST http://localhost:1337/api/ai-assistant/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is amazing!",
    "analysisType": "sentiment"
  }'
```

## Next Steps

1. **Read Full Documentation**: Check [AI_INTEGRATION_README.md](./AI_INTEGRATION_README.md)
2. **See Examples**: Review [USAGE_EXAMPLES.md](./USAGE_EXAMPLES.md)
3. **Run Tests**: Execute `npm run test:ai` after starting the server
4. **Integrate**: Use the AI endpoints in your frontend application

## Project Structure

```
strapi-ai-project/
├── .env                          # Contains STRAPI_AI_API_KEY
├── src/
│   └── api/
│       └── ai-assistant/         # AI integration code
├── AI_INTEGRATION_README.md      # Detailed documentation
├── USAGE_EXAMPLES.md             # Practical examples
├── test-ai-integration.js        # Test script
└── package.json                  # Updated with test:ai script
```

## Troubleshooting

**Server won't start?**
- Make sure you're in the project directory
- Run `npm install` to ensure dependencies are installed

**AI requests failing?**
- Verify the API key is set in `.env`
- Check your internet connection
- Review server logs for errors

**Need help?**
- Check the documentation files
- Review the test script for usage examples
- Ensure Strapi is running before testing

## Resources

- [Strapi Documentation](https://docs.strapi.io)
- [Strapi AI Features](https://strapi.io/ai)
- Project README files for detailed guides

---

**You're all set! 🚀**

Start the server with `npm run develop` and begin using AI-powered features in your Strapi application.
