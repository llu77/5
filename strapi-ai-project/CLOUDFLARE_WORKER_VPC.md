# Cloudflare Worker with VPC Services for Strapi

## Overview

This Cloudflare Worker provides a secure, globally-distributed edge API for your private Strapi instance using **Cloudflare VPC Services**. It enables:

- ✅ **Private Connectivity**: Connect to Strapi without exposing it to the internet
- ✅ **Edge Caching**: Cache AI responses at Cloudflare's edge for better performance
- ✅ **Global Distribution**: Serve from 300+ cities worldwide
- ✅ **Zero Cold Starts**: Instant response times
- ✅ **Built-in Security**: DDoS protection, WAF, bot mitigation
- ✅ **Cost Optimization**: Reduce Strapi load and AI API costs

## Architecture

```
┌─────────────┐         ┌──────────────────┐         ┌─────────────────┐
│   Client    │────────▶│ Cloudflare       │────────▶│ Private Strapi  │
│ (Browser/   │         │ Worker + VPC     │ (VPC)   │ Instance        │
│  Mobile)    │         │ Services         │         │ (Not Public)    │
└─────────────┘         └──────────────────┘         └─────────────────┘
                               │                              │
                               │                              ▼
                               │                      ┌──────────────┐
                               │                      │ Cloudflare   │
                               └─────────────────────▶│ AI Gateway   │
                                                      │ + Anthropic  │
                                                      └──────────────┘
```

**Benefits**:
1. Strapi stays private (no public IP needed)
2. VPC Services provide secure tunnel between Worker and Strapi
3. Edge caching reduces backend load
4. AI Gateway provides analytics and cost optimization

## Setup Guide

### Prerequisites

1. **Cloudflare Account** with Workers Paid plan ($5/month)
2. **VPC Services** enabled (contact Cloudflare Enterprise sales)
3. **Private Strapi Instance** (on AWS VPC, GCP, Azure, or on-prem)
4. **Node.js** 18+ and npm

### Step 1: Install Wrangler CLI

```bash
npm install -g wrangler

# Login to Cloudflare
wrangler login
```

### Step 2: Set Up VPC Service

**Option A: AWS VPC (Most Common)**

1. **Create VPC Endpoint**:
   - AWS Console → VPC → Endpoints
   - Service: com.amazonaws.vpce.{region}.vpce-svc-{id}
   - VPC: Your Strapi's VPC
   - Subnets: Private subnets where Strapi runs

2. **Note the VPC Endpoint ID** (e.g., `vpce-0abc123def456...`)

3. **Configure in Cloudflare**:
   - Dashboard → Workers & Pages → VPC Services
   - Create VPC Service
   - Provider: AWS PrivateLink
   - Endpoint ID: Your VPC Endpoint ID
   - Note the Service ID generated

**Option B: GCP Private Service Connect**

1. Create Private Service Connect endpoint
2. Configure in Cloudflare Dashboard
3. Note the Service ID

**Option C: Azure Private Link**

1. Create Azure Private Endpoint
2. Configure in Cloudflare Dashboard
3. Note the Service ID

### Step 3: Configure Worker

Navigate to the worker directory:

```bash
cd cloudflare-worker
```

Edit `wrangler.toml` and update:

```toml
vpc_services = [
  {
    binding = "STRAPI_VPC",
    service_id = "YOUR_VPC_SERVICE_ID_HERE",  # From Step 2
    remote = true
  }
]

vars = {
  STRAPI_URL = "http://your-private-strapi-ip:1337",  # Internal IP
  ENVIRONMENT = "production"
}
```

### Step 4: Set Up Secrets

Create `.dev.vars` for local development:

```bash
cp .dev.vars.example .dev.vars
```

Edit `.dev.vars`:

```bash
STRAPI_API_TOKEN=your-strapi-api-token
```

For production, set secrets:

```bash
# Production secret
wrangler secret put STRAPI_API_TOKEN
# Enter your Strapi API token when prompted

# Staging secret
wrangler secret put STRAPI_API_TOKEN --env staging
```

### Step 5: Generate Strapi API Token

In your Strapi instance:

1. Go to **Settings → API Tokens**
2. Click **Create new API Token**
3. Name: `Cloudflare Worker`
4. Type: **Full Access** or **Custom** (with AI endpoints access)
5. Copy the token (you'll only see it once!)

### Step 6: Install Dependencies

```bash
npm install
```

### Step 7: Test Locally

```bash
npm run dev
```

Visit: `http://localhost:8787/health`

**Note**: Local development won't connect via VPC - it proxies directly. VPC is only used in production.

### Step 8: Deploy to Cloudflare

```bash
# Deploy to production
npm run deploy:production

# Or staging
npm run deploy:staging
```

Your worker will be available at:
`https://strapi-ai-worker-production.YOUR-SUBDOMAIN.workers.dev`

### Step 9: Add Custom Domain (Optional)

1. **Cloudflare Dashboard** → Workers & Pages → Your Worker
2. **Triggers** → **Custom Domains** → **Add Custom Domain**
3. Enter: `api.yourdomain.com`
4. Cloudflare automatically creates DNS records

Now accessible at: `https://api.yourdomain.com`

## API Endpoints

### Health Check

Check worker and Strapi status:

```bash
curl https://your-worker.workers.dev/health
```

Response:
```json
{
  "worker": "ok",
  "environment": "production",
  "strapi": {
    "status": "ok",
    "provider": "cloudflare-gateway",
    "configured": true
  },
  "timestamp": "2025-02-04T12:00:00.000Z"
}
```

### AI Generate

Generate AI responses with edge caching:

```bash
curl -X POST https://your-worker.workers.dev/api/ai/generate \
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

**Features**:
- ✅ Automatic caching (1 hour TTL)
- ✅ Cache key based on prompt hash
- ✅ `X-Cache` header (`HIT` or `MISS`)

### AI Content Generation

```bash
curl -X POST https://your-worker.workers.dev/api/ai/content \
  -H "Content-Type: application/json" \
  -d '{
    "contentType": "blog-post",
    "context": {
      "topic": "Cloudflare Workers",
      "tone": "technical",
      "length": "medium"
    }
  }'
```

### Text Analysis

```bash
curl -X POST https://your-worker.workers.dev/api/ai/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This product is amazing!",
    "analysisType": "sentiment"
  }'
```

### Proxy Other Strapi Endpoints

Any `/api/*` request is proxied to Strapi:

```bash
# Get pages
curl https://your-worker.workers.dev/api/pages

# Get single page
curl https://your-worker.workers.dev/api/pages/1

# Create entry (requires authentication)
curl -X POST https://your-worker.workers.dev/api/articles \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-strapi-user-token" \
  -d '{"data": {"title": "Hello World"}}'
```

## Features

### 1. Edge Caching

The worker implements intelligent caching for AI responses:

```typescript
// Cache configuration
const CACHE_TTL = 3600; // 1 hour
const CACHE_CONTROL = 'public, max-age=3600';
```

**How it works**:
1. Request comes in with prompt
2. Worker generates cache key from prompt hash
3. Checks Cloudflare cache
4. If hit: Returns cached response (faster + cheaper)
5. If miss: Calls Strapi via VPC, caches response

**Cache Headers**:
- `X-Cache: HIT` - Served from cache
- `X-Cache: MISS` - Fresh from Strapi

**Benefits**:
- 50-90% reduction in AI API calls
- < 50ms response time for cached requests
- Automatic cache invalidation after TTL

### 2. VPC Security

**Private Communication**:
- Strapi never exposed to public internet
- VPC tunnel encrypted by Cloudflare
- No need for VPN or bastion hosts
- Automatic failover and load balancing

**Security Layers**:
```
Internet → Cloudflare WAF → Worker (Edge) → VPC Tunnel → Private Strapi
         ↑                                    ↑
    DDoS Protection                    Encrypted
```

### 3. Global Distribution

Worker runs in 300+ Cloudflare data centers:

- Request routes to nearest edge location
- < 50ms latency worldwide
- Automatic failover if edge unavailable
- 99.99% uptime SLA

### 4. CORS Handling

Built-in CORS support:

```typescript
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
};
```

**Features**:
- Preflight (OPTIONS) handling
- Configurable origins
- Credential support
- Custom headers

### 5. Error Handling

Comprehensive error handling:

```typescript
try {
  // VPC request
} catch (error) {
  return new Response(JSON.stringify({
    error: error.message,
    timestamp: new Date().toISOString()
  }), {
    status: 500,
    headers: { 'Content-Type': 'application/json' }
  });
}
```

**Error Types**:
- Network errors (VPC connection issues)
- Strapi errors (API errors)
- Validation errors (missing fields)
- Authentication errors

## Development

### Local Development

```bash
# Start dev server
npm run dev
```

**Features**:
- Hot reload on file changes
- Local binding simulation
- Request logging
- Source maps

**Limitations**:
- VPC Services don't work locally (proxies directly)
- Some Cloudflare features unavailable (KV, Durable Objects with local mode)

### Testing

Create `src/index.test.ts`:

```typescript
import { expect, test } from 'vitest';
import worker from './index';

test('health endpoint returns ok', async () => {
  const request = new Request('http://example.com/health');
  const env = {
    STRAPI_URL: 'http://localhost:1337',
    ENVIRONMENT: 'test',
  };

  const response = await worker.fetch(request, env, {});

  expect(response.status).toBe(200);

  const data = await response.json();
  expect(data.worker).toBe('ok');
});
```

Run tests:

```bash
npm test
```

### Debugging

**View Logs (Real-time)**:

```bash
# Production logs
npm run tail:production

# Staging logs
wrangler tail --env staging
```

**Dashboard Logs**:
- Cloudflare Dashboard → Workers & Pages → Your Worker → Logs
- Real-time log streaming
- Filter by status, method, etc.
- Export logs (CSV/JSON)

### Deployment

**Environments**:

```bash
# Development (auto-deployed on push)
npm run dev

# Staging
npm run deploy:staging

# Production
npm run deploy:production
```

**CI/CD with GitHub Actions**:

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy Worker

on:
  push:
    branches: [main]
    paths:
      - 'cloudflare-worker/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-node@v3
        with:
          node-version: '20'

      - name: Install dependencies
        working-directory: cloudflare-worker
        run: npm ci

      - name: Deploy to Cloudflare Workers
        working-directory: cloudflare-worker
        run: npx wrangler deploy --env production
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
```

**Deployment Strategies**:

1. **Blue-Green**: Deploy new version, test, route traffic
2. **Canary**: Gradual rollout (10% → 50% → 100%)
3. **Rollback**: Instant rollback to previous version

```bash
# Deploy new version
wrangler deploy --env production

# Rollback if issues
wrangler rollback --env production
```

## Monitoring

### Metrics Dashboard

Access at: `https://dash.cloudflare.com` → Workers → Your Worker

**Key Metrics**:
- **Requests**: Total requests per time period
- **Success Rate**: % of successful requests (2xx)
- **Errors**: 4xx and 5xx error rates
- **CPU Time**: Average execution time
- **Duration**: P50, P95, P99 latency
- **Bandwidth**: Data transferred

### Analytics

**Built-in Analytics**:
- Request volume by country
- Cache hit rate
- Error breakdown
- Status code distribution
- Top endpoints

**Custom Analytics**:

```typescript
// Add custom metrics
ctx.waitUntil(
  fetch('https://analytics.example.com/track', {
    method: 'POST',
    body: JSON.stringify({
      endpoint: '/api/ai/generate',
      duration: Date.now() - startTime,
      cacheHit: cacheHit,
    })
  })
);
```

### Alerts

Set up alerts for:

1. **High Error Rate**: > 5% errors
2. **Slow Responses**: P95 latency > 1000ms
3. **High Traffic**: Unusual spike in requests
4. **VPC Connectivity**: Connection failures

**Configure**:
- Dashboard → Workers → Your Worker → Alerts
- Choose metric, threshold, notification channel
- Supports: Email, Slack, PagerDuty, webhooks

### Logging

**Structured Logging**:

```typescript
console.log(JSON.stringify({
  level: 'info',
  message: 'AI request processed',
  endpoint: '/api/ai/generate',
  cacheHit: true,
  duration: 150,
  timestamp: new Date().toISOString(),
}));
```

**Log Aggregation**:
- Export to Cloudflare Logpush
- Send to Datadog, New Relic, Splunk
- Store in R2 buckets
- Query with LogQL

## Performance Optimization

### 1. Caching Strategy

```typescript
// Smart cache key generation
function getCacheKey(prompt: string, options: any): string {
  const hash = hashPrompt(prompt);
  const model = options.model || 'default';
  return `ai-cache:${model}:${hash}`;
}

// Vary cache by important parameters only
// Don't include timestamp, user ID, etc.
```

### 2. Request Deduplication

```typescript
// Prevent duplicate requests
const pendingRequests = new Map();

async function generateWithDedup(prompt: string) {
  const key = hashPrompt(prompt);

  if (pendingRequests.has(key)) {
    return await pendingRequests.get(key);
  }

  const promise = actuallyGenerate(prompt);
  pendingRequests.set(key, promise);

  try {
    return await promise;
  } finally {
    pendingRequests.delete(key);
  }
}
```

### 3. Parallel Requests

```typescript
// Process multiple prompts in parallel
const results = await Promise.all([
  generateAI(prompt1),
  generateAI(prompt2),
  generateAI(prompt3),
]);
```

### 4. Compression

```typescript
// Enable compression for responses
const compressed = await compressResponse(response);

return new Response(compressed, {
  headers: {
    'Content-Encoding': 'gzip',
    'Content-Type': 'application/json',
  }
});
```

## Cost Analysis

### Worker Costs

**Cloudflare Workers Pricing** (Paid Plan):
- $5/month base
- Includes: 10 million requests
- Additional: $0.50 per million requests
- CPU time: 50ms free per request

**Example Monthly Cost** (1M requests):
- Base: $5
- Requests: Included
- **Total: $5/month**

### VPC Services Costs

**Pricing**:
- Enterprise feature (contact sales)
- Typical: $200-500/month
- Depends on: Bandwidth, connections, region

### Savings from Caching

**Without Caching** (1M AI requests):
- AI API calls: 1,000,000
- Cost at $0.003/request: $3,000

**With Caching** (80% cache hit rate):
- AI API calls: 200,000 (20% miss)
- Cost: $600
- **Savings: $2,400/month (80%)**

**ROI**:
- Worker + VPC: ~$500/month
- Savings: $2,400/month
- **Net savings: $1,900/month**

## Security Best Practices

### 1. Authentication

```typescript
// Verify request authentication
function verifyAuth(request: Request): boolean {
  const authHeader = request.headers.get('Authorization');
  if (!authHeader?.startsWith('Bearer ')) {
    return false;
  }
  const token = authHeader.slice(7);
  return token === env.STRAPI_API_TOKEN;
}
```

### 2. Rate Limiting

```typescript
// Implement rate limiting
const limiter = {
  async check(ip: string): Promise<boolean> {
    const key = `ratelimit:${ip}`;
    const count = await env.RATE_LIMIT_KV.get(key);

    if (count && parseInt(count) > 100) {
      return false; // Rate limit exceeded
    }

    await env.RATE_LIMIT_KV.put(key, (parseInt(count || '0') + 1).toString(), {
      expirationTtl: 60 // 1 minute
    });

    return true;
  }
};
```

### 3. Input Validation

```typescript
// Validate and sanitize inputs
function validatePrompt(prompt: string): boolean {
  if (!prompt || typeof prompt !== 'string') {
    return false;
  }
  if (prompt.length > 10000) {
    return false; // Too long
  }
  if (prompt.includes('<script>')) {
    return false; // XSS attempt
  }
  return true;
}
```

### 4. Secrets Management

```bash
# Never commit secrets
# Use Wrangler secrets

# Set secret
wrangler secret put STRAPI_API_TOKEN

# Update secret
wrangler secret put STRAPI_API_TOKEN --env production

# List secrets (doesn't show values)
wrangler secret list
```

## Troubleshooting

### Issue: VPC Connection Fails

**Symptoms**:
- `ECONNREFUSED` errors
- Timeout after 30 seconds
- "Unable to reach private service" error

**Solutions**:
1. **Verify VPC Service ID** in `wrangler.toml`
2. **Check Strapi is running** on private IP
3. **Verify Security Groups** allow traffic from Cloudflare
4. **Check VPC Endpoint** status in AWS/GCP/Azure
5. **Test connectivity** from another instance in same VPC

### Issue: High Latency

**Symptoms**:
- P95 latency > 1000ms
- Slow response times

**Solutions**:
1. **Enable caching** if not already
2. **Optimize Strapi** queries (add indexes)
3. **Use faster models** (Haiku vs Sonnet)
4. **Reduce max_tokens** in AI requests
5. **Check VPC latency** (should be < 100ms)

### Issue: Cache Not Working

**Symptoms**:
- Always `X-Cache: MISS`
- High AI API costs

**Solutions**:
1. **Check cache key generation** (ensure consistent)
2. **Verify response is cacheable** (status 200)
3. **Check TTL** is not too short
4. **Review vary headers** (don't cache user-specific data)

### Issue: 401 Unauthorized

**Symptoms**:
- 401 errors from Strapi
- "Invalid token" messages

**Solutions**:
1. **Regenerate API token** in Strapi
2. **Update secret** in Wrangler: `wrangler secret put STRAPI_API_TOKEN`
3. **Check token permissions** (needs AI endpoints access)
4. **Verify header format**: `Authorization: Bearer token`

### Issue: CORS Errors

**Symptoms**:
- Browser console: "CORS policy" error
- Preflight requests fail

**Solutions**:
1. **Check CORS headers** in worker code
2. **Handle OPTIONS** requests properly
3. **Allow origin**: Update `Access-Control-Allow-Origin`
4. **Allow credentials** if needed

## Advanced Features

### 1. Streaming Responses

```typescript
// Stream AI responses to client
async function handleStream(request: Request, env: Env) {
  const { prompt } = await request.json();

  const strapiRequest = new Request(
    `${env.STRAPI_URL}/api/ai-assistant/stream`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${env.STRAPI_API_TOKEN}`,
      },
      body: JSON.stringify({ prompt }),
    }
  );

  const strapiResponse = await env.STRAPI_VPC.fetch(strapiRequest);

  // Pass through the stream
  return new Response(strapiResponse.body, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    },
  });
}
```

### 2. Durable Objects for State

```typescript
// Maintain conversation state
export class ConversationState {
  constructor(private state: DurableObjectState) {}

  async fetch(request: Request) {
    const history = await this.state.storage.get('messages') || [];
    const { message } = await request.json();

    history.push(message);
    await this.state.storage.put('messages', history);

    // Generate AI response with full context
    const response = await generateWithHistory(history);

    return new Response(JSON.stringify(response));
  }
}
```

### 3. R2 for Large Responses

```typescript
// Store large AI responses in R2
async function handleLargeGeneration(request: Request, env: Env) {
  const result = await generateAI(longPrompt);

  // Store in R2
  const key = `ai-responses/${Date.now()}.json`;
  await env.R2_BUCKET.put(key, JSON.stringify(result));

  // Return signed URL
  const url = await env.R2_BUCKET.createSignedUrl(key, {
    expiresIn: 3600
  });

  return new Response(JSON.stringify({ url }));
}
```

### 4. WebSockets for Real-time

```typescript
// Real-time AI streaming via WebSocket
async function handleWebSocket(request: Request, env: Env) {
  const upgradeHeader = request.headers.get('Upgrade');
  if (upgradeHeader !== 'websocket') {
    return new Response('Expected websocket', { status: 400 });
  }

  const [client, server] = Object.values(new WebSocketPair());

  server.addEventListener('message', async (event) => {
    const { prompt } = JSON.parse(event.data);

    // Stream AI response back
    const stream = await generateAIStream(prompt, env);
    for await (const chunk of stream) {
      server.send(JSON.stringify(chunk));
    }
  });

  server.accept();

  return new Response(null, {
    status: 101,
    webSocket: client,
  });
}
```

## Migration from Public Strapi

If you're migrating from public Strapi to VPC:

### Step 1: Set Up VPC

1. Create VPC in AWS/GCP/Azure
2. Move Strapi to private subnet
3. Remove public IP/load balancer
4. Create VPC endpoint

### Step 2: Deploy Worker

1. Configure VPC Services in Cloudflare
2. Deploy worker with VPC binding
3. Test connectivity

### Step 3: Update DNS

1. Point API domain to Worker
2. Monitor traffic
3. Verify no errors

### Step 4: Decommission Public Access

1. Remove security group rules
2. Delete load balancer
3. Confirm all traffic via Worker

## Best Practices Summary

✅ **DO**:
- Use VPC for private Strapi instances
- Enable edge caching for AI responses
- Implement rate limiting
- Monitor performance and errors
- Use secrets for API tokens
- Test thoroughly before production
- Set up alerts

❌ **DON'T**:
- Expose Strapi publicly if using VPC
- Commit secrets to Git
- Skip error handling
- Forget to set cache headers
- Ignore security best practices
- Deploy without testing

## Resources

### Documentation
- [Cloudflare Workers](https://developers.cloudflare.com/workers/)
- [VPC Services](https://developers.cloudflare.com/cloudflare-one/connections/connect-private-networks/)
- [Wrangler CLI](https://developers.cloudflare.com/workers/wrangler/)
- [Workers AI](https://developers.cloudflare.com/workers-ai/)

### Examples
- [Worker Templates](https://github.com/cloudflare/workers-sdk/tree/main/templates)
- [Community Projects](https://github.com/cloudflare/workers-sdk#community)

### Support
- [Cloudflare Community](https://community.cloudflare.com/c/developers/workers/40)
- [Discord](https://discord.gg/cloudflaredev)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/cloudflare-workers)

## Summary

This Cloudflare Worker + VPC setup provides:

- 🔒 **Secure**: Private Strapi, encrypted tunnel
- 🚀 **Fast**: Edge caching, global distribution
- 💰 **Cost-effective**: Reduce AI API costs by 80%
- 📊 **Observable**: Built-in metrics and logging
- 🌍 **Scalable**: 300+ edge locations
- 🛡️ **Protected**: DDoS, WAF, bot protection

Start by configuring VPC Services, then deploy the worker to secure your Strapi instance!

```bash
cd cloudflare-worker
npm install
npm run deploy:production
```

Your edge API is now live! 🎉
