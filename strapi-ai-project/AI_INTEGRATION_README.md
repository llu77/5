# Strapi AI Integration Guide

## Overview
This project integrates Strapi AI capabilities to provide intelligent features including content generation, text analysis, and AI-powered responses.

## Configuration

### Environment Variables
The Strapi AI API key is configured in the `.env` file:

```env
STRAPI_AI_API_KEY=70e3f5cf898a87c6f7334d3f98bee3461e4d4d1fe79dd542c12d80f14dceba389914a818de394e7c7a39aafb8e2eeb10e8222bd12b2b391b7c1f789f4977ff29031e60ae30070ef22d18cc47720c255cc24ace2e38f6c9a16ea97977348c4161b292e25645fe4ed77852265ccbf430a01b40cf6214c8e6720ecfcaceee698369
```

## API Endpoints

### 1. Health Check
Check if the AI integration is configured correctly.

**Endpoint:** `GET /api/ai-assistant/health`

**Response:**
```json
{
  "status": "ok",
  "configured": true,
  "message": "Strapi AI is configured and ready"
}
```

### 2. Generate AI Response
Generate AI responses based on a prompt.

**Endpoint:** `POST /api/ai-assistant/generate`

**Request Body:**
```json
{
  "prompt": "Write a welcome message for a restaurant",
  "options": {
    "temperature": 0.7,
    "max_tokens": 500
  }
}
```

**Response:**
```json
{
  "data": {
    "response": "Generated AI content..."
  }
}
```

### 3. Generate Content
Generate specific types of content using AI.

**Endpoint:** `POST /api/ai-assistant/content`

**Request Body:**
```json
{
  "contentType": "blog-post",
  "context": {
    "topic": "Strapi CMS",
    "tone": "professional",
    "length": "medium"
  }
}
```

**Response:**
```json
{
  "data": {
    "content": "Generated content..."
  }
}
```

### 4. Analyze Text
Analyze text for various purposes (sentiment, keywords, summary, etc.).

**Endpoint:** `POST /api/ai-assistant/analyze`

**Request Body:**
```json
{
  "text": "Text to analyze...",
  "analysisType": "sentiment"
}
```

**Response:**
```json
{
  "data": {
    "analysis": {
      "sentiment": "positive",
      "score": 0.85
    }
  }
}
```

## Usage Examples

### JavaScript/TypeScript
```javascript
// Health Check
const healthCheck = async () => {
  const response = await fetch('http://localhost:1337/api/ai-assistant/health');
  const data = await response.json();
  console.log(data);
};

// Generate AI Response
const generateResponse = async () => {
  const response = await fetch('http://localhost:1337/api/ai-assistant/generate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      prompt: 'Write a creative product description for a smartphone',
      options: {
        temperature: 0.8,
        max_tokens: 300
      }
    })
  });
  const data = await response.json();
  console.log(data);
};

// Generate Content
const generateContent = async () => {
  const response = await fetch('http://localhost:1337/api/ai-assistant/content', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      contentType: 'article',
      context: {
        topic: 'AI and Future of Web Development',
        tone: 'informative',
        targetAudience: 'developers'
      }
    })
  });
  const data = await response.json();
  console.log(data);
};

// Analyze Text
const analyzeText = async () => {
  const response = await fetch('http://localhost:1337/api/ai-assistant/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      text: 'This is an amazing product! I love it so much.',
      analysisType: 'sentiment'
    })
  });
  const data = await response.json();
  console.log(data);
};
```

### cURL Examples

```bash
# Health Check
curl http://localhost:1337/api/ai-assistant/health

# Generate AI Response
curl -X POST http://localhost:1337/api/ai-assistant/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a tagline for a coffee shop",
    "options": {
      "temperature": 0.7
    }
  }'

# Generate Content
curl -X POST http://localhost:1337/api/ai-assistant/content \
  -H "Content-Type: application/json" \
  -d '{
    "contentType": "social-media-post",
    "context": {
      "platform": "twitter",
      "topic": "new feature launch"
    }
  }'

# Analyze Text
curl -X POST http://localhost:1337/api/ai-assistant/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your text to analyze here",
    "analysisType": "keywords"
  }'
```

## Development

### Start Development Server
```bash
npm run develop
```

The server will start on `http://localhost:1337`

### Build for Production
```bash
npm run build
npm run start
```

## File Structure

```
src/
└── api/
    └── ai-assistant/
        ├── controllers/
        │   └── ai-assistant.ts    # Request handlers
        ├── routes/
        │   └── ai-assistant.ts    # API routes definition
        └── services/
            └── ai-assistant.ts    # AI service logic
```

## Features

- **AI Response Generation**: Generate intelligent responses based on prompts
- **Content Creation**: Create various types of content (articles, social posts, descriptions)
- **Text Analysis**: Analyze text for sentiment, keywords, summaries, etc.
- **Health Monitoring**: Check AI integration status

## Security Notes

- The API key is stored securely in environment variables
- Never commit the `.env` file to version control
- Consider adding authentication middleware for production use
- Implement rate limiting to prevent abuse

## Troubleshooting

### API Key Not Configured
If you see "STRAPI_AI_API_KEY is not configured", ensure:
1. The `.env` file exists in the project root
2. The `STRAPI_AI_API_KEY` variable is set
3. The server has been restarted after adding the key

### Connection Errors
If you encounter connection errors:
1. Verify your internet connection
2. Check that the Strapi AI service is operational
3. Validate that your API key is correct

## Next Steps

1. Add authentication to protect AI endpoints
2. Implement rate limiting
3. Create custom content types that utilize AI
4. Build admin panel extensions for AI features
5. Add caching for frequently used AI responses

## Support

For issues or questions:
- Strapi Documentation: https://docs.strapi.io
- Strapi AI Documentation: https://strapi.io/ai
- Community: https://forum.strapi.io
