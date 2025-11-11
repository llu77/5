/**
 * Cloudflare Worker for Strapi AI Integration
 *
 * This worker provides a secure edge API for your private Strapi instance
 * using Cloudflare VPC Services for private connectivity.
 */

export interface Env {
  STRAPI_VPC: Fetcher;
  STRAPI_URL: string;
  STRAPI_API_TOKEN: string;
  ENVIRONMENT: string;
  AI_RATE_LIMITER: RateLimit;
}

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    // CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      'Access-Control-Max-Age': '86400',
    };

    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    try {
      const url = new URL(request.url);
      const path = url.pathname;

      // Route handling
      if (path === '/health') {
        return handleHealth(request, env, corsHeaders);
      }

      if (path === '/api/ai/generate') {
        return handleAIGenerate(request, env, corsHeaders);
      }

      if (path === '/api/ai/content') {
        return handleAIContent(request, env, corsHeaders);
      }

      if (path === '/api/ai/analyze') {
        return handleAIAnalyze(request, env, corsHeaders);
      }

      if (path.startsWith('/api/')) {
        return handleProxyRequest(request, env, corsHeaders);
      }

      return new Response('Not Found', {
        status: 404,
        headers: corsHeaders
      });

    } catch (error: any) {
      console.error('Worker error:', error);
      return new Response(JSON.stringify({
        error: error.message || 'Internal Server Error'
      }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }
  },
};

/**
 * Health check endpoint
 */
async function handleHealth(
  request: Request,
  env: Env,
  corsHeaders: Record<string, string>
): Promise<Response> {
  try {
    // Check Strapi health via VPC
    const strapiRequest = new Request(
      `${env.STRAPI_URL}/api/ai-assistant/health`,
      {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${env.STRAPI_API_TOKEN}`,
        },
      }
    );

    const strapiResponse = await env.STRAPI_VPC.fetch(strapiRequest);
    const strapiHealth = await strapiResponse.json() as any;

    return new Response(JSON.stringify({
      worker: 'ok',
      environment: env.ENVIRONMENT,
      strapi: strapiHealth,
      timestamp: new Date().toISOString(),
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });

  } catch (error: any) {
    return new Response(JSON.stringify({
      worker: 'ok',
      strapi: 'error',
      error: error.message,
      timestamp: new Date().toISOString(),
    }), {
      status: 503,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }
}

/**
 * AI Generate endpoint with caching
 */
async function handleAIGenerate(
  request: Request,
  env: Env,
  corsHeaders: Record<string, string>
): Promise<Response> {
  if (request.method !== 'POST') {
    return new Response('Method Not Allowed', {
      status: 405,
      headers: corsHeaders
    });
  }

  try {
    const body = await request.json() as any;
    const { prompt, options } = body;

    if (!prompt) {
      return new Response(JSON.stringify({
        error: 'Prompt is required'
      }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }

    // Create cache key for identical requests
    const cacheKey = new Request(
      `https://cache.strapi-ai.com/generate/${hashPrompt(prompt)}`,
      { method: 'GET' }
    );

    // Check cache first
    const cache = caches.default;
    let response = await cache.match(cacheKey);

    if (response) {
      // Cache hit!
      return new Response(response.body, {
        headers: {
          ...corsHeaders,
          'Content-Type': 'application/json',
          'X-Cache': 'HIT',
        },
      });
    }

    // Cache miss - call Strapi via VPC
    const strapiRequest = new Request(
      `${env.STRAPI_URL}/api/ai-assistant/generate`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${env.STRAPI_API_TOKEN}`,
        },
        body: JSON.stringify({ prompt, options }),
      }
    );

    const strapiResponse = await env.STRAPI_VPC.fetch(strapiRequest);
    const data = await strapiResponse.json();

    // Create response
    response = new Response(JSON.stringify(data), {
      headers: {
        ...corsHeaders,
        'Content-Type': 'application/json',
        'X-Cache': 'MISS',
      },
    });

    // Cache successful responses for 1 hour
    if (strapiResponse.ok) {
      const cacheResponse = response.clone();
      const cacheHeaders = new Headers(cacheResponse.headers);
      cacheHeaders.set('Cache-Control', 'public, max-age=3600');

      await cache.put(
        cacheKey,
        new Response(cacheResponse.body, {
          headers: cacheHeaders,
        })
      );
    }

    return response;

  } catch (error: any) {
    return new Response(JSON.stringify({
      error: error.message || 'Failed to generate AI response'
    }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }
}

/**
 * AI Content Generation endpoint
 */
async function handleAIContent(
  request: Request,
  env: Env,
  corsHeaders: Record<string, string>
): Promise<Response> {
  if (request.method !== 'POST') {
    return new Response('Method Not Allowed', {
      status: 405,
      headers: corsHeaders
    });
  }

  try {
    const body = await request.json() as any;
    const { contentType, context } = body;

    if (!contentType) {
      return new Response(JSON.stringify({
        error: 'Content type is required'
      }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }

    const strapiRequest = new Request(
      `${env.STRAPI_URL}/api/ai-assistant/content`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${env.STRAPI_API_TOKEN}`,
        },
        body: JSON.stringify({ contentType, context }),
      }
    );

    const strapiResponse = await env.STRAPI_VPC.fetch(strapiRequest);
    const data = await strapiResponse.json();

    return new Response(JSON.stringify(data), {
      status: strapiResponse.status,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });

  } catch (error: any) {
    return new Response(JSON.stringify({
      error: error.message || 'Failed to generate content'
    }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }
}

/**
 * Text Analysis endpoint
 */
async function handleAIAnalyze(
  request: Request,
  env: Env,
  corsHeaders: Record<string, string>
): Promise<Response> {
  if (request.method !== 'POST') {
    return new Response('Method Not Allowed', {
      status: 405,
      headers: corsHeaders
    });
  }

  try {
    const body = await request.json() as any;
    const { text, analysisType } = body;

    if (!text) {
      return new Response(JSON.stringify({
        error: 'Text is required'
      }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }

    const strapiRequest = new Request(
      `${env.STRAPI_URL}/api/ai-assistant/analyze`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${env.STRAPI_API_TOKEN}`,
        },
        body: JSON.stringify({ text, analysisType }),
      }
    );

    const strapiResponse = await env.STRAPI_VPC.fetch(strapiRequest);
    const data = await strapiResponse.json();

    return new Response(JSON.stringify(data), {
      status: strapiResponse.status,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });

  } catch (error: any) {
    return new Response(JSON.stringify({
      error: error.message || 'Failed to analyze text'
    }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }
}

/**
 * Generic proxy for other Strapi API endpoints
 */
async function handleProxyRequest(
  request: Request,
  env: Env,
  corsHeaders: Record<string, string>
): Promise<Response> {
  try {
    const url = new URL(request.url);
    const strapiUrl = `${env.STRAPI_URL}${url.pathname}${url.search}`;

    // Clone request and update URL
    const strapiRequest = new Request(strapiUrl, {
      method: request.method,
      headers: {
        ...Object.fromEntries(request.headers),
        'Authorization': `Bearer ${env.STRAPI_API_TOKEN}`,
      },
      body: request.body,
    });

    const strapiResponse = await env.STRAPI_VPC.fetch(strapiRequest);

    // Clone response with CORS headers
    return new Response(strapiResponse.body, {
      status: strapiResponse.status,
      statusText: strapiResponse.statusText,
      headers: {
        ...corsHeaders,
        ...Object.fromEntries(strapiResponse.headers),
      },
    });

  } catch (error: any) {
    return new Response(JSON.stringify({
      error: error.message || 'Proxy request failed'
    }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }
}

/**
 * Simple hash function for cache keys
 */
function hashPrompt(prompt: string): string {
  let hash = 0;
  for (let i = 0; i < prompt.length; i++) {
    const char = prompt.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32bit integer
  }
  return Math.abs(hash).toString(36);
}
