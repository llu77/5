# Cloudflare Pages KV Namespace Error - Complete Fix Guide

## 🎯 Problem Summary

Your Cloudflare Pages deployment is failing with:
```
Error: Failed to publish your Function. Got error: KV namespace '606e2671e250401bbc01f097797f1f66' not found.
```

This happens when your `wrangler.toml` references a KV namespace that doesn't exist in your Cloudflare account.

## 🚀 Quick Fix (3 Steps)

### Step 1: Create KV Namespaces
```bash
cd cloudflare-deployment-fix
./setup-kv-namespaces.sh
```

This will:
- Create the required KV namespace
- Generate both production and preview namespace IDs
- Show you the configuration to add to `wrangler.toml`

### Step 2: Store API Keys Securely
```bash
./setup-api-keys.sh
```

This will:
- Store your two API keys as encrypted Cloudflare secrets
- Set up environment-specific keys (dev, staging, production)
- Never expose keys in your code or git repository

### Step 3: Update Your Repository
Copy the generated `wrangler.toml` to your repository and deploy:
```bash
# In your Fgfg repository
cp cloudflare-deployment-fix/wrangler.toml ./wrangler.toml
git add wrangler.toml
git commit -m "fix: update wrangler.toml with correct KV namespace configuration"
git push origin main
```

---

## 📚 Detailed Guide

### Understanding the Error

The error occurs because your `functions/` directory or Pages Functions are trying to use a KV namespace binding, but the namespace with ID `606e2671e250401bbc01f097797f1f66` doesn't exist in your Cloudflare account.

**Why this happens:**
1. The namespace was created in a different Cloudflare account
2. The namespace was deleted but still referenced in config
3. You're using a template/example config that references someone else's namespace
4. The wrangler.toml was copied without updating the IDs

### KV Namespace Architecture

```
┌─────────────────────────────────────────┐
│         Your Application                │
├─────────────────────────────────────────┤
│  Pages Functions / Workers              │
│  ↓                                      │
│  KV Binding (e.g., "CACHE")            │
│  ↓                                      │
│  Namespace ID: 606e...                 │
├─────────────────────────────────────────┤
│         Cloudflare KV Store             │
│                                         │
│  ┌─────────────────────────────────┐  │
│  │  Namespace: cache                │  │
│  │  Production ID: 606e...          │  │
│  │  Preview ID: abc123...           │  │
│  │                                  │  │
│  │  Key-Value Pairs:                │  │
│  │  ├─ user:123 → {data}           │  │
│  │  ├─ cache:api → {response}      │  │
│  │  └─ config:app → {settings}     │  │
│  └─────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

### Best Practices for KV Namespaces

#### 1. **Namespace Naming Convention**
```
project-purpose-environment
```

Examples:
- `lmm-finance-cache-prod`
- `lmm-finance-sessions-dev`
- `api-gateway-config-staging`

#### 2. **Separate Namespaces by Purpose**

| Namespace | Purpose | TTL Strategy |
|-----------|---------|--------------|
| `CACHE` | API response caching | Short (1-24 hours) |
| `SESSIONS` | User session storage | Medium (7-30 days) |
| `CONFIG` | Application configuration | Long/No expiration |
| `API_KEYS` | Encrypted API key storage | No expiration |
| `RATE_LIMIT` | Rate limiting counters | Very short (1-60 minutes) |

#### 3. **Environment Separation**

**Option A: Separate Namespaces (Recommended)**
```toml
[env.production]
[[env.production.kv_namespaces]]
binding = "CACHE"
id = "production-namespace-id"

[env.dev]
[[env.dev.kv_namespaces]]
binding = "CACHE"
id = "dev-namespace-id"
```

**Option B: Preview IDs (Good for Pages)**
```toml
[[kv_namespaces]]
binding = "CACHE"
id = "production-id"
preview_id = "preview-id"  # Used for preview deployments
```

#### 4. **KV Data Patterns**

**Cache Pattern:**
```javascript
// In your Pages Function
export async function onRequest(context) {
  const { CACHE } = context.env;
  const cacheKey = `api:${userId}:${endpoint}`;

  // Try to get from cache
  let data = await CACHE.get(cacheKey, { type: 'json' });

  if (!data) {
    // Fetch fresh data
    data = await fetchFromAPI();

    // Store in cache with TTL (1 hour)
    await CACHE.put(
      cacheKey,
      JSON.stringify(data),
      { expirationTtl: 3600 }
    );
  }

  return Response.json(data);
}
```

**Configuration Pattern:**
```javascript
// Store config once
await CONFIG.put('app:settings', JSON.stringify({
  apiVersion: '2.0',
  features: { ai: true, analytics: true }
}));

// Read config (cached by KV)
const settings = await CONFIG.get('app:settings', { type: 'json' });
```

**Session Pattern:**
```javascript
// Create session
const sessionId = crypto.randomUUID();
await SESSIONS.put(`session:${sessionId}`, JSON.stringify({
  userId: user.id,
  createdAt: Date.now()
}), { expirationTtl: 86400 * 7 });  // 7 days

// Validate session
const session = await SESSIONS.get(`session:${sessionId}`, { type: 'json' });
if (!session) {
  return new Response('Unauthorized', { status: 401 });
}
```

### API Keys Security Best Practices

#### ✅ DO:

1. **Use Cloudflare Secrets for API Keys**
   ```bash
   wrangler secret put ANTHROPIC_API_KEY_1
   ```

2. **Rotate Keys Regularly**
   - Every 90 days minimum
   - Immediately if compromised
   - Keep old key active during rotation period

3. **Separate Keys by Environment**
   ```bash
   # Production
   wrangler secret put API_KEY --env production

   # Development (use test keys)
   wrangler secret put API_KEY --env dev
   ```

4. **Use Key Prefixes for Tracking**
   - `sk-prod-*` for production
   - `sk-dev-*` for development
   - `sk-test-*` for testing

5. **Monitor Key Usage**
   ```javascript
   // Add logging and monitoring
   const startTime = Date.now();
   const response = await fetch(API_ENDPOINT, {
     headers: { 'Authorization': `Bearer ${API_KEY}` }
   });

   await logKeyUsage({
     key: 'API_KEY_1',
     duration: Date.now() - startTime,
     status: response.status,
     timestamp: new Date().toISOString()
   });
   ```

#### ❌ DON'T:

1. **Never Commit Keys to Git**
   ```bash
   # Add to .gitignore
   .env
   .env.local
   .dev.vars
   wrangler.toml.local
   ```

2. **Never Store Keys in KV Without Encryption**
   ```javascript
   // BAD
   await KV.put('api_key', 'sk-RbQ0xi...');

   // GOOD - Use secrets instead
   const apiKey = context.env.ANTHROPIC_API_KEY_1;
   ```

3. **Never Log Keys**
   ```javascript
   // BAD
   console.log('API Key:', apiKey);

   // GOOD
   console.log('API Key:', apiKey.slice(0, 10) + '...');
   ```

4. **Never Expose Keys in Client-Side Code**
   ```javascript
   // BAD - Keys in frontend
   const response = await fetch('/api', {
     headers: { 'X-API-Key': 'sk-...' }  // Exposed!
   });

   // GOOD - Keys stay server-side
   // In /functions/api.js
   export async function onRequest(context) {
     const apiKey = context.env.ANTHROPIC_API_KEY_1;
     // Use key server-side only
   }
   ```

### Deployment Troubleshooting

#### Error: "KV namespace not found"

**Solution:**
```bash
# 1. List existing namespaces
wrangler kv:namespace list

# 2. Create new namespace
wrangler kv:namespace create "cache"

# 3. Update wrangler.toml with the ID shown
[[kv_namespaces]]
binding = "CACHE"
id = "new-namespace-id"
```

#### Error: "Invalid redirect rules"

The warning about infinite loop in redirect rules:
```
#6: /*  /index.html  200
```

**Solution - Update `_redirects` file:**
```
# Remove or fix this line:
# /*  /index.html  200  ❌ Causes infinite loop

# Use this instead:
/*  /index.html  404  ✅ Only redirect on 404
```

#### Error: "Secrets not found"

**Solution:**
```bash
# Check existing secrets
wrangler secret list

# Add missing secrets
wrangler secret put ANTHROPIC_API_KEY_1
wrangler secret put ANTHROPIC_API_KEY_2
```

### Performance Optimization

#### 1. **KV Read Performance**

```javascript
// SLOW - Sequential reads
const user = await KV.get(`user:${id}`);
const prefs = await KV.get(`prefs:${id}`);
const stats = await KV.get(`stats:${id}`);

// FAST - Parallel reads
const [user, prefs, stats] = await Promise.all([
  KV.get(`user:${id}`),
  KV.get(`prefs:${id}`),
  KV.get(`stats:${id}`)
]);
```

#### 2. **Cache Warming**

```javascript
// Pre-populate cache for hot data
async function warmCache() {
  const hotKeys = await getPopularItems();

  await Promise.all(
    hotKeys.map(async key => {
      const data = await fetchFromOrigin(key);
      await CACHE.put(key, JSON.stringify(data), {
        expirationTtl: 3600
      });
    })
  );
}
```

#### 3. **Stale-While-Revalidate Pattern**

```javascript
async function getCachedData(key, fetcher, ttl = 3600) {
  const cached = await CACHE.get(key, {
    type: 'json',
    cacheTtl: ttl
  });

  if (cached) {
    // Return cached data immediately
    // Optionally refresh in background
    if (shouldRefresh(cached)) {
      context.waitUntil(
        fetcher().then(data =>
          CACHE.put(key, JSON.stringify(data), { expirationTtl: ttl })
        )
      );
    }
    return cached;
  }

  // Cache miss - fetch and store
  const fresh = await fetcher();
  await CACHE.put(key, JSON.stringify(fresh), { expirationTtl: ttl });
  return fresh;
}
```

### Monitoring & Observability

#### 1. **KV Usage Analytics**

```javascript
// Track KV operations
export async function onRequest(context) {
  const { CACHE } = context.env;
  const startTime = Date.now();

  try {
    const result = await CACHE.get(key);

    // Log metrics
    context.waitUntil(
      logMetric({
        operation: 'kv.get',
        key,
        hit: result !== null,
        latency: Date.now() - startTime,
        timestamp: Date.now()
      })
    );

    return Response.json({ data: result });
  } catch (error) {
    // Log errors
    context.waitUntil(
      logError({
        operation: 'kv.get',
        key,
        error: error.message,
        timestamp: Date.now()
      })
    );
    throw error;
  }
}
```

#### 2. **Cache Hit Rate Monitoring**

```javascript
let hits = 0;
let misses = 0;

async function getCached(key) {
  const value = await CACHE.get(key);

  if (value) {
    hits++;
  } else {
    misses++;
  }

  const hitRate = hits / (hits + misses);

  // Alert if hit rate drops below threshold
  if (hitRate < 0.7) {
    await sendAlert('Low cache hit rate: ' + hitRate);
  }

  return value;
}
```

### Cost Optimization

#### KV Pricing (as of 2024)
- **Storage:** $0.50 per GB per month
- **Reads:** $0.50 per million reads
- **Writes:** $5.00 per million writes
- **Deletes:** $5.00 per million deletes
- **Lists:** $5.00 per million list operations

#### Cost Optimization Strategies

1. **Batch Operations**
   ```javascript
   // EXPENSIVE - Many small writes
   for (const item of items) {
     await KV.put(`item:${item.id}`, JSON.stringify(item));
   }

   // CHEAPER - Batch with scheduled worker
   await scheduleKVBatchWrite(items);
   ```

2. **Use Appropriate TTLs**
   ```javascript
   // Short TTL for frequently changing data
   await CACHE.put('stock:AAPL', price, { expirationTtl: 60 });

   // Long TTL for static data
   await CACHE.put('config:theme', theme, { expirationTtl: 86400 * 30 });
   ```

3. **Avoid Unnecessary Writes**
   ```javascript
   // Check before writing
   const existing = await KV.get(key);
   if (existing !== newValue) {
     await KV.put(key, newValue);
   }
   ```

## 🔍 Testing Your Setup

### 1. Test KV Namespace
```bash
# Write test data
wrangler kv:key put --namespace-id=YOUR_NAMESPACE_ID "test:key" "test value"

# Read test data
wrangler kv:key get --namespace-id=YOUR_NAMESPACE_ID "test:key"

# Delete test data
wrangler kv:key delete --namespace-id=YOUR_NAMESPACE_ID "test:key"
```

### 2. Test Secrets
```bash
# List secrets
wrangler secret list

# Test in local development
wrangler dev
```

### 3. Test Deployment
```bash
# Deploy to preview
wrangler pages deploy

# Check deployment logs
wrangler pages deployment tail
```

## 📋 Checklist

Before deploying, ensure:

- [ ] KV namespaces created with `setup-kv-namespaces.sh`
- [ ] Namespace IDs updated in `wrangler.toml`
- [ ] API keys stored as secrets with `setup-api-keys.sh`
- [ ] No secrets committed to git
- [ ] `.gitignore` includes `.env`, `.dev.vars`
- [ ] Preview namespace IDs configured
- [ ] Environment-specific configs set up
- [ ] Testing completed in dev environment
- [ ] Monitoring/logging implemented
- [ ] Error handling added
- [ ] Documentation updated

## 🚨 Emergency Procedures

### Key Compromise
```bash
# 1. Immediately delete old secret
wrangler secret delete COMPROMISED_KEY

# 2. Generate new key at provider

# 3. Update secret with new key
wrangler secret put COMPROMISED_KEY

# 4. Monitor for unauthorized usage
wrangler tail
```

### KV Corruption
```bash
# 1. List all keys
wrangler kv:key list --namespace-id=YOUR_ID

# 2. Backup data
wrangler kv:bulk get --namespace-id=YOUR_ID > backup.json

# 3. Clear namespace
wrangler kv:bulk delete --namespace-id=YOUR_ID

# 4. Restore from backup if needed
```

## 📞 Support

- **Cloudflare Docs:** https://developers.cloudflare.com/kv
- **Wrangler Docs:** https://developers.cloudflare.com/workers/wrangler
- **Community:** https://discord.gg/cloudflaredev

---

## 🎓 Additional Resources

### Example Code Repository
Check the `examples/` directory for:
- Complete Pages Function with KV
- API key rotation system
- Monitoring dashboard
- Load testing scripts

### Related Documentation
- [Cloudflare KV Best Practices](cloudflare-kv-best-practices.md)
- [API Key Management Guide](api-key-management.md)
- [Deployment Automation](deployment-automation.md)

---

**Created:** 2024-11-25
**Updated:** 2024-11-25
**Version:** 1.0.0
