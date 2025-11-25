/**
 * Global Middleware for Cloudflare Pages Functions
 * Handles authentication, CORS, rate limiting, logging
 */

interface Env {
  CACHE: KVNamespace;
  ANTHROPIC_API_KEY_1: string;
  ANTHROPIC_API_KEY_2: string;
  ENVIRONMENT: string;
}

interface RequestContext {
  request: Request;
  env: Env;
  next: () => Promise<Response>;
  data: Record<string, any>;
}

// CORS configuration
const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-API-Key',
  'Access-Control-Max-Age': '86400',
};

// Security headers
const SECURITY_HEADERS = {
  'X-Content-Type-Options': 'nosniff',
  'X-Frame-Options': 'DENY',
  'X-XSS-Protection': '1; mode=block',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
};

/**
 * Rate Limiting using KV
 */
async function checkRateLimit(
  request: Request,
  env: Env
): Promise<{ allowed: boolean; remaining: number }> {
  const ip = request.headers.get('CF-Connecting-IP') || 'unknown';
  const key = `ratelimit:${ip}`;

  try {
    const current = await env.CACHE.get(key);
    const count = current ? parseInt(current) : 0;

    const limit = 100; // 100 requests per minute
    const ttl = 60; // 1 minute

    if (count >= limit) {
      return { allowed: false, remaining: 0 };
    }

    // Increment counter
    await env.CACHE.put(key, String(count + 1), { expirationTtl: ttl });

    return { allowed: true, remaining: limit - count - 1 };
  } catch (error) {
    console.error('Rate limit check failed:', error);
    // Allow request on error
    return { allowed: true, remaining: -1 };
  }
}

/**
 * Authentication middleware
 */
async function authenticate(request: Request, env: Env): Promise<{
  authenticated: boolean;
  user?: any;
  error?: string;
}> {
  // Check for Authorization header
  const authHeader = request.headers.get('Authorization');

  if (!authHeader) {
    return { authenticated: false, error: 'No authorization header' };
  }

  // Extract token
  const token = authHeader.replace('Bearer ', '');

  if (!token) {
    return { authenticated: false, error: 'Invalid token format' };
  }

  try {
    // Validate token against KV store
    const sessionData = await env.CACHE.get(`session:${token}`, { type: 'json' });

    if (!sessionData) {
      return { authenticated: false, error: 'Invalid or expired token' };
    }

    return { authenticated: true, user: sessionData };
  } catch (error) {
    console.error('Authentication failed:', error);
    return { authenticated: false, error: 'Authentication error' };
  }
}

/**
 * Request logging
 */
async function logRequest(request: Request, response: Response, startTime: number) {
  const duration = Date.now() - startTime;

  const logEntry = {
    timestamp: new Date().toISOString(),
    method: request.method,
    url: request.url,
    status: response.status,
    duration: `${duration}ms`,
    userAgent: request.headers.get('User-Agent') || 'unknown',
    ip: request.headers.get('CF-Connecting-IP') || 'unknown',
    country: request.headers.get('CF-IPCountry') || 'unknown',
  };

  console.log(JSON.stringify(logEntry));
}

/**
 * Error handler
 */
function handleError(error: Error, status: number = 500): Response {
  console.error('Request error:', error);

  return new Response(
    JSON.stringify({
      error: error.message,
      status,
      timestamp: new Date().toISOString(),
    }),
    {
      status,
      headers: {
        'Content-Type': 'application/json',
        ...CORS_HEADERS,
        ...SECURITY_HEADERS,
      },
    }
  );
}

/**
 * Main middleware handler
 */
export const onRequest: PagesFunction<Env> = async (context) => {
  const startTime = Date.now();
  const { request, env, next } = context;

  try {
    // Handle OPTIONS requests (CORS preflight)
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        status: 204,
        headers: CORS_HEADERS,
      });
    }

    // Rate limiting (skip for authenticated requests)
    const rateLimit = await checkRateLimit(request, env);

    if (!rateLimit.allowed) {
      return new Response(
        JSON.stringify({
          error: 'Rate limit exceeded',
          retryAfter: 60,
        }),
        {
          status: 429,
          headers: {
            'Content-Type': 'application/json',
            'X-RateLimit-Remaining': '0',
            'Retry-After': '60',
            ...CORS_HEADERS,
          },
        }
      );
    }

    // Authentication for protected routes
    const url = new URL(request.url);
    const protectedPaths = ['/api/users', '/api/admin', '/api/chat'];

    if (protectedPaths.some(path => url.pathname.startsWith(path))) {
      const auth = await authenticate(request, env);

      if (!auth.authenticated) {
        return new Response(
          JSON.stringify({
            error: auth.error || 'Unauthorized',
          }),
          {
            status: 401,
            headers: {
              'Content-Type': 'application/json',
              ...CORS_HEADERS,
            },
          }
        );
      }

      // Attach user to context
      context.data.user = auth.user;
    }

    // Process request
    const response = await next();

    // Add headers to response
    const newResponse = new Response(response.body, response);

    // Add CORS headers
    Object.entries(CORS_HEADERS).forEach(([key, value]) => {
      newResponse.headers.set(key, value);
    });

    // Add security headers
    Object.entries(SECURITY_HEADERS).forEach(([key, value]) => {
      newResponse.headers.set(key, value);
    });

    // Add rate limit headers
    newResponse.headers.set('X-RateLimit-Remaining', String(rateLimit.remaining));

    // Log request
    await logRequest(request, newResponse, startTime);

    return newResponse;
  } catch (error) {
    return handleError(error as Error);
  }
};
