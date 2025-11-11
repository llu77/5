# Cloudflare Worker for Strapi AI

Edge API for private Strapi instances using Cloudflare VPC Services.

## Features

- 🔒 Secure VPC connectivity to private Strapi
- ⚡ Edge caching for AI responses
- 🌍 Global distribution (300+ locations)
- 📊 Built-in analytics and monitoring
- 🛡️ DDoS protection and WAF

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure VPC

Edit `wrangler.toml`:

```toml
vpc_services = [
  {
    binding = "STRAPI_VPC",
    service_id = "YOUR_VPC_SERVICE_ID",
    remote = true
  }
]

vars = {
  STRAPI_URL = "http://your-private-strapi:1337"
}
```

### 3. Set Secrets

```bash
# Create .dev.vars for local development
cp .dev.vars.example .dev.vars

# Add your Strapi API token to .dev.vars
# For production:
wrangler secret put STRAPI_API_TOKEN
```

### 4. Deploy

```bash
# Deploy to production
npm run deploy:production

# Or staging
npm run deploy:staging
```

## Available Scripts

```bash
npm run dev              # Local development
npm run deploy           # Deploy to production
npm run deploy:staging   # Deploy to staging
npm run tail            # View logs (production)
npm test                # Run tests
```

## API Endpoints

### Health Check
```bash
GET /health
```

### AI Generation
```bash
POST /api/ai/generate
Body: { "prompt": "...", "options": {} }
```

### Content Generation
```bash
POST /api/ai/content
Body: { "contentType": "blog-post", "context": {} }
```

### Text Analysis
```bash
POST /api/ai/analyze
Body: { "text": "...", "analysisType": "sentiment" }
```

### Proxy Strapi API
```bash
GET/POST /api/*
# Proxies to Strapi via VPC
```

## Documentation

See [CLOUDFLARE_WORKER_VPC.md](../CLOUDFLARE_WORKER_VPC.md) for complete documentation including:

- VPC Services setup
- Security best practices
- Performance optimization
- Monitoring and debugging
- Cost analysis
- Troubleshooting

## Architecture

```
Client → Cloudflare Worker → VPC Service → Private Strapi
         (Edge, Caching)      (Secure)     (Not Public)
```

## Configuration

### Environment Variables

**wrangler.toml** (public config):
- `STRAPI_URL`: Internal Strapi URL
- `ENVIRONMENT`: production/staging/dev

**Secrets** (via `wrangler secret`):
- `STRAPI_API_TOKEN`: Strapi API token

### VPC Service

Required for production connectivity:

1. Create VPC endpoint (AWS/GCP/Azure)
2. Configure in Cloudflare Dashboard
3. Get Service ID
4. Update `wrangler.toml`

## Development

Local development proxies directly (VPC not used):

```bash
npm run dev
# Visit http://localhost:8787/health
```

## Testing

```bash
# Run tests
npm test

# Watch mode
npm run test:watch
```

## Monitoring

View logs in real-time:

```bash
npm run tail
```

Or in Cloudflare Dashboard:
- Workers & Pages → Your Worker → Logs

## Deployment

### Automatic (GitHub Actions)

Push to main branch auto-deploys.

### Manual

```bash
# Production
npm run deploy:production

# Staging
npm run deploy:staging
```

### Rollback

```bash
wrangler rollback --env production
```

## Cost

**Workers**: $5/month (10M requests included)
**VPC Services**: Enterprise feature (contact sales)
**Savings**: ~80% reduction in AI API costs via caching

## Support

- [Cloudflare Workers Docs](https://developers.cloudflare.com/workers/)
- [VPC Services Docs](https://developers.cloudflare.com/cloudflare-one/connections/connect-private-networks/)
- [Complete Guide](../CLOUDFLARE_WORKER_VPC.md)

## License

MIT
