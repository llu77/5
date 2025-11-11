# Cloudflare AI Gateway Integration

## Overview

This Strapi project now supports **Cloudflare AI Gateway** as an AI provider, which offers:

- ✅ **Caching**: Reduce costs and latency with intelligent caching
- ✅ **Rate Limiting**: Control API usage and costs
- ✅ **Analytics**: Track usage, costs, and performance
- ✅ **Logging**: Monitor all AI requests and responses
- ✅ **Multiple Providers**: Support for Anthropic, OpenAI, Workers AI, and more
- ✅ **Cost Control**: Real-time cost tracking and alerts

## What is Cloudflare AI Gateway?

Cloudflare AI Gateway sits between your application and AI providers (like Anthropic, OpenAI), providing:

1. **Unified Interface**: One API for multiple AI providers
2. **Observability**: Detailed logs and analytics
3. **Control**: Rate limiting, caching, and access controls
4. **Savings**: Reduce costs through intelligent caching

## Setup Guide

### 1. Create Cloudflare AI Gateway

1. Log in to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Navigate to **AI** → **AI Gateway**
3. Click **Create Gateway**
4. Configure your gateway:
   - **Gateway Name**: `my-strapi-ai-gateway`
   - **Rate Limiting**: Optional (e.g., 100 requests/minute)
   - **Caching**: Enable (recommended)
5. Copy your **Account ID** and **Gateway ID**

### 2. Get Anthropic API Key

1. Visit [Anthropic Console](https://console.anthropic.com)
2. Create an account or sign in
3. Navigate to **API Keys**
4. Create a new API key
5. Copy the API key (starts with `sk-ant-...`)

### 3. Configure Strapi Project

Add to your `.env` file:

```env
# Set provider to cloudflare-gateway
AI_PROVIDER=cloudflare-gateway

# Anthropic API Key
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# Cloudflare Configuration
CLOUDFLARE_ACCOUNT_ID=your-account-id-here
CLOUDFLARE_GATEWAY_ID=my-strapi-ai-gateway
```

### 4. Restart Strapi

```bash
npm run develop
```

## Usage

### Health Check

Test the integration:

```bash
curl http://localhost:1337/api/ai-assistant/health
```

Expected response:

```json
{
  "status": "ok",
  "provider": "cloudflare-gateway",
  "configured": true,
  "available": true,
  "features": ["caching", "rate-limiting", "analytics", "streaming"],
  "message": "cloudflare-gateway is configured and ready"
}
```

### Generate AI Response

```bash
curl -X POST http://localhost:1337/api/ai-assistant/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a product description for a smartwatch",
    "options": {
      "model": "claude-sonnet-4-20250514",
      "temperature": 0.7,
      "max_tokens": 500
    }
  }'
```

### Generate Content

```bash
curl -X POST http://localhost:1337/api/ai-assistant/content \
  -H "Content-Type: application/json" \
  -d '{
    "contentType": "blog-post",
    "context": {
      "topic": "Benefits of AI in content management",
      "tone": "professional",
      "keywords": ["AI", "CMS", "automation"]
    }
  }'
```

### Analyze Text

```bash
curl -X POST http://localhost:1337/api/ai-assistant/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This product exceeded all my expectations! Highly recommended.",
    "analysisType": "sentiment"
  }'
```

## Available Models

Cloudflare AI Gateway supports all Anthropic models:

- `claude-sonnet-4-20250514` (Recommended) - Latest Sonnet 4.5
- `claude-opus-4-20250514` - Most capable
- `claude-3-5-sonnet-20241022` - Previous Sonnet
- `claude-3-opus-20240229` - Previous Opus
- `claude-3-haiku-20240307` - Fast and economical

## Features

### 1. Caching

Cloudflare automatically caches responses to reduce costs:

```javascript
// Same prompt within cache TTL = cached response (faster + cheaper)
const result1 = await aiProvider.generateResponse("What is Strapi?");
const result2 = await aiProvider.generateResponse("What is Strapi?"); // Cached!
```

**Cache Configuration** (in Cloudflare Dashboard):
- TTL: 1 hour (default)
- Cache key: Includes provider, model, and request params
- Bypass cache: Add `cf-aig-skip-cache: true` header (advanced)

### 2. Rate Limiting

Control API usage:

**Dashboard Settings**:
- Requests per minute: 100
- Requests per hour: 5,000
- Requests per day: 50,000

**When limit exceeded**:
- Response: `429 Too Many Requests`
- Retry after: Specified in response headers

### 3. Analytics

View in Cloudflare Dashboard:

- **Request Volume**: Requests over time
- **Token Usage**: Input/output tokens
- **Cost Tracking**: Estimated costs
- **Latency**: P50, P95, P99 response times
- **Error Rates**: 4xx and 5xx errors
- **Cache Hit Rate**: Percentage of cached responses

### 4. Logging

All requests are logged with:

- Timestamp
- Request/response bodies
- Model and provider
- Token usage
- Latency
- Cache status
- Errors (if any)

**Access logs**:
- Cloudflare Dashboard → AI Gateway → Logs
- Retention: 30 days (configurable)
- Export: CSV or JSON

## Cost Optimization

### Caching Strategy

```javascript
// High cache value prompts
const faqs = [
  "What is Strapi?",
  "How do I install Strapi?",
  "What databases does Strapi support?"
];

// Process all (most will be cached after first run)
for (const question of faqs) {
  await aiProvider.generateResponse(question);
}
```

### Smart Model Selection

```javascript
// Use Haiku for simple tasks (cheaper)
const summary = await aiProvider.generateResponse(text, {
  model: "claude-3-haiku-20240307"
});

// Use Sonnet for complex tasks
const analysis = await aiProvider.generateResponse(text, {
  model: "claude-sonnet-4-20250514"
});
```

### Token Management

```javascript
// Limit tokens for cost control
const result = await aiProvider.generateResponse(prompt, {
  max_tokens: 500 // Reduce from default 4096
});
```

## Integration with Strapi Services

### In Content Types

```typescript
// src/api/article/controllers/article.ts
async create(ctx) {
  const { title, outline } = ctx.request.body.data;

  // Generate article content via Cloudflare AI Gateway
  const aiProvider = strapi.service('api::ai-assistant.ai-provider');
  const content = await aiProvider.generateContent('article', {
    topic: title,
    outline: outline,
    tone: 'professional',
    length: 'medium'
  });

  if (content.success) {
    ctx.request.body.data.content = content.data.content;
  }

  return super.create(ctx);
}
```

### In Lifecycle Hooks

```typescript
// src/api/article/content-types/article/lifecycles.ts
module.exports = {
  async beforeCreate(event) {
    const { data } = event.params;

    // Auto-generate SEO meta description
    if (!data.metaDescription && data.title) {
      const aiProvider = strapi.service('api::ai-assistant.ai-provider');
      const result = await aiProvider.generateResponse(
        `Write a 150-character SEO meta description for an article titled: ${data.title}`
      );

      if (result.success) {
        data.metaDescription = result.data.response;
      }
    }
  }
};
```

## Advanced Features

### Streaming Responses

```typescript
// Enable streaming for long responses
const stream = await strapi
  .service('api::ai-assistant.cloudflare-gateway')
  .streamResponse('Write a detailed article about Strapi');

if (stream.success) {
  for await (const chunk of stream.stream) {
    if (chunk.type === 'content_block_delta') {
      console.log(chunk.delta.text);
    }
  }
}
```

### Custom System Prompts

```typescript
const result = await aiProvider.generateContent('custom', {
  systemPrompt: 'You are a technical documentation writer for Strapi CMS.',
  userPrompt: 'Explain how to create custom controllers',
  model: 'claude-sonnet-4-20250514',
  max_tokens: 2000
});
```

### Batch Processing

```typescript
// Process multiple items efficiently
const articles = await strapi.entityService.findMany('api::article.article', {
  filters: { needsSummary: true },
  limit: 10
});

for (const article of articles) {
  const summary = await aiProvider.generateResponse(
    `Summarize this article in 2 sentences: ${article.content}`,
    { max_tokens: 100 }
  );

  if (summary.success) {
    await strapi.entityService.update('api::article.article', article.id, {
      data: { summary: summary.data.response }
    });
  }

  // Rate limiting handled by Cloudflare
  // Caching saves costs on similar content
}
```

## Monitoring

### Dashboard Metrics

Access at: `https://dash.cloudflare.com/[account_id]/ai/ai-gateway/[gateway_id]`

**Key Metrics**:
- **Total Requests**: Last 24h, 7d, 30d
- **Cache Hit Rate**: % of cached responses
- **Average Latency**: Response time trends
- **Token Usage**: Input/output tokens
- **Estimated Cost**: Based on provider pricing
- **Error Rate**: Failed requests percentage

### Alerts

Set up alerts for:
- High error rates (>5%)
- Rate limit approaches (>80% of limit)
- Unusual cost spikes
- Low cache hit rates (<30%)

### Logs Analysis

```bash
# Example: Find most common prompts
# Export logs from dashboard, then analyze

cat gateway-logs.json | jq '.query.messages[0].content' | sort | uniq -c | sort -rn | head -10
```

## Switching Between Providers

### Back to Strapi AI

```env
AI_PROVIDER=strapi-ai
STRAPI_AI_API_KEY=your-strapi-ai-key
```

### Try Multiple Providers

```typescript
// Custom implementation for A/B testing
const providers = ['strapi-ai', 'cloudflare-gateway'];
const selectedProvider = providers[Math.floor(Math.random() * providers.length)];

process.env.AI_PROVIDER = selectedProvider;
const result = await aiProvider.generateResponse(prompt);
```

## Troubleshooting

### Error: "ANTHROPIC_API_KEY is not configured"

**Solution**: Add API key to `.env`:
```env
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

### Error: "CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_GATEWAY_ID must be configured"

**Solution**: Get from Cloudflare Dashboard and add to `.env`:
```env
CLOUDFLARE_ACCOUNT_ID=abc123def456
CLOUDFLARE_GATEWAY_ID=my-gateway
```

### Error: 429 Too Many Requests

**Cause**: Rate limit exceeded

**Solutions**:
1. Increase rate limits in Cloudflare Dashboard
2. Implement request queuing in your app
3. Use caching more effectively
4. Reduce request frequency

### Error: 401 Unauthorized

**Cause**: Invalid Anthropic API key

**Solutions**:
1. Verify API key in Anthropic Console
2. Check for extra spaces in `.env`
3. Regenerate API key if needed

### High Costs

**Solutions**:
1. Enable caching (if not already)
2. Reduce max_tokens in requests
3. Use cheaper models (Haiku) for simple tasks
4. Implement request deduplication
5. Set up cost alerts in Cloudflare

### Low Cache Hit Rate

**Causes**:
- Unique prompts every time
- Short cache TTL
- Varying parameters

**Solutions**:
1. Standardize common prompts
2. Increase cache TTL
3. Use template prompts with variables

## Best Practices

### 1. Prompt Design

```typescript
// ❌ Bad: Unique prompt every time (no caching)
const prompt = `Write about ${topic} on ${new Date()}`;

// ✅ Good: Standardized prompt (cacheable)
const prompt = `Write a professional blog post about ${topic}`;
```

### 2. Error Handling

```typescript
const result = await aiProvider.generateResponse(prompt);

if (!result.success) {
  // Log error
  strapi.log.error('AI generation failed:', result.error);

  // Fallback to default content
  return { content: defaultContent };
}
```

### 3. Token Budgets

```typescript
// Set appropriate token limits
const limits = {
  summary: 200,
  description: 500,
  article: 2000,
  analysis: 1000
};

const result = await aiProvider.generateContent(type, {
  ...context,
  max_tokens: limits[type]
});
```

### 4. Monitoring

```typescript
// Track AI usage
async function generateWithTracking(prompt, options) {
  const start = Date.now();

  const result = await aiProvider.generateResponse(prompt, options);

  const duration = Date.now() - start;

  await strapi.entityService.create('api::ai-log.ai-log', {
    data: {
      provider: 'cloudflare-gateway',
      duration,
      success: result.success,
      tokens: result.data?.usage?.output_tokens || 0
    }
  });

  return result;
}
```

## Resources

### Documentation
- [Cloudflare AI Gateway](https://developers.cloudflare.com/ai-gateway/)
- [Anthropic API](https://docs.anthropic.com/claude/reference/getting-started-with-the-api)
- [Anthropic SDK](https://github.com/anthropics/anthropic-sdk-typescript)

### Pricing
- [Anthropic Pricing](https://www.anthropic.com/pricing)
- [Cloudflare AI Gateway Pricing](https://www.cloudflare.com/products/ai-gateway/) (Free tier available)

### Support
- [Cloudflare Community](https://community.cloudflare.com/)
- [Anthropic Discord](https://discord.gg/anthropic)
- [Strapi Discord](https://discord.strapi.io)

## Migration Guide

### From Strapi AI to Cloudflare Gateway

1. **Sign up for Anthropic** and get API key
2. **Create Cloudflare AI Gateway**
3. **Update `.env`**:
   ```env
   AI_PROVIDER=cloudflare-gateway
   ANTHROPIC_API_KEY=your-key
   CLOUDFLARE_ACCOUNT_ID=your-account
   CLOUDFLARE_GATEWAY_ID=your-gateway
   ```
4. **Restart Strapi**: `npm run develop`
5. **Test**: `curl http://localhost:1337/api/ai-assistant/health`
6. **Monitor**: Check Cloudflare Dashboard

### No Code Changes Required!

The same API endpoints work with both providers:
- `/api/ai-assistant/generate`
- `/api/ai-assistant/content`
- `/api/ai-assistant/analyze`

Just switch `AI_PROVIDER` in `.env` and restart!

## Summary

Cloudflare AI Gateway provides:

- 🚀 **Performance**: Faster responses through caching
- 💰 **Cost Savings**: Reduced API costs
- 📊 **Visibility**: Comprehensive analytics
- 🛡️ **Control**: Rate limiting and access controls
- 🔧 **Flexibility**: Multiple AI providers
- 📈 **Scalability**: Enterprise-grade infrastructure

Start using it today by updating your `.env` file!

```env
AI_PROVIDER=cloudflare-gateway
ANTHROPIC_API_KEY=your-anthropic-key
CLOUDFLARE_ACCOUNT_ID=your-account-id
CLOUDFLARE_GATEWAY_ID=your-gateway-id
```

Then restart Strapi and you're ready to go! 🎉
