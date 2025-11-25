/**
 * Authentication API Endpoint
 * Handles login, logout, session management
 */

interface Env {
  CACHE: KVNamespace;
  JWT_SECRET: string;
}

interface LoginRequest {
  email: string;
  password: string;
}

interface RegisterRequest {
  email: string;
  password: string;
  name: string;
}

/**
 * Simple JWT-like token generator
 * In production, use proper JWT library
 */
async function generateToken(payload: any): Promise<string> {
  const data = JSON.stringify(payload);
  const encoder = new TextEncoder();
  const dataBuffer = encoder.encode(data);

  // Generate hash
  const hashBuffer = await crypto.subtle.digest('SHA-256', dataBuffer);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');

  // Combine payload and signature
  const token = btoa(data) + '.' + hashHex.slice(0, 32);

  return token;
}

/**
 * Hash password
 */
async function hashPassword(password: string): Promise<string> {
  const encoder = new TextEncoder();
  const data = encoder.encode(password);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

/**
 * Verify password
 */
async function verifyPassword(password: string, hash: string): Promise<boolean> {
  const passwordHash = await hashPassword(password);
  return passwordHash === hash;
}

/**
 * POST /api/auth/login
 * User login
 */
export const onRequestPost: PagesFunction<Env> = async (context) => {
  const { request, env } = context;
  const url = new URL(request.url);

  try {
    // Handle different auth endpoints
    if (url.pathname.endsWith('/login')) {
      return await handleLogin(request, env);
    } else if (url.pathname.endsWith('/register')) {
      return await handleRegister(request, env);
    } else if (url.pathname.endsWith('/logout')) {
      return await handleLogout(request, env);
    } else if (url.pathname.endsWith('/refresh')) {
      return await handleRefresh(request, env);
    }

    return new Response(
      JSON.stringify({ error: 'Not found' }),
      {
        status: 404,
        headers: { 'Content-Type': 'application/json' },
      }
    );
  } catch (error) {
    console.error('Auth endpoint error:', error);

    return new Response(
      JSON.stringify({
        error: error instanceof Error ? error.message : 'Internal server error',
      }),
      {
        status: 500,
        headers: { 'Content-Type': 'application/json' },
      }
    );
  }
};

/**
 * Handle login request
 */
async function handleLogin(request: Request, env: Env): Promise<Response> {
  const body: LoginRequest = await request.json();

  if (!body.email || !body.password) {
    return new Response(
      JSON.stringify({ error: 'Email and password required' }),
      {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      }
    );
  }

  // Get user from KV
  const user = await env.CACHE.get(`user:${body.email}`, { type: 'json' }) as any;

  if (!user) {
    return new Response(
      JSON.stringify({ error: 'Invalid credentials' }),
      {
        status: 401,
        headers: { 'Content-Type': 'application/json' },
      }
    );
  }

  // Verify password
  const passwordValid = await verifyPassword(body.password, user.passwordHash);

  if (!passwordValid) {
    return new Response(
      JSON.stringify({ error: 'Invalid credentials' }),
      {
        status: 401,
        headers: { 'Content-Type': 'application/json' },
      }
    );
  }

  // Generate session token
  const sessionToken = await generateToken({
    userId: user.id,
    email: user.email,
    timestamp: Date.now(),
  });

  // Store session in KV
  await env.CACHE.put(
    `session:${sessionToken}`,
    JSON.stringify({
      userId: user.id,
      email: user.email,
      name: user.name,
      createdAt: Date.now(),
    }),
    { expirationTtl: 86400 * 7 } // 7 days
  );

  return new Response(
    JSON.stringify({
      success: true,
      token: sessionToken,
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
      },
    }),
    {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    }
  );
}

/**
 * Handle register request
 */
async function handleRegister(request: Request, env: Env): Promise<Response> {
  const body: RegisterRequest = await request.json();

  if (!body.email || !body.password || !body.name) {
    return new Response(
      JSON.stringify({ error: 'Email, password, and name required' }),
      {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      }
    );
  }

  // Check if user already exists
  const existingUser = await env.CACHE.get(`user:${body.email}`);

  if (existingUser) {
    return new Response(
      JSON.stringify({ error: 'User already exists' }),
      {
        status: 409,
        headers: { 'Content-Type': 'application/json' },
      }
    );
  }

  // Hash password
  const passwordHash = await hashPassword(body.password);

  // Create user
  const userId = crypto.randomUUID();
  const user = {
    id: userId,
    email: body.email,
    name: body.name,
    passwordHash,
    createdAt: Date.now(),
  };

  // Store user in KV
  await env.CACHE.put(
    `user:${body.email}`,
    JSON.stringify(user),
    { expirationTtl: 86400 * 365 } // 1 year
  );

  // Also store by ID for easy lookup
  await env.CACHE.put(
    `user:id:${userId}`,
    body.email,
    { expirationTtl: 86400 * 365 }
  );

  // Generate session token
  const sessionToken = await generateToken({
    userId: user.id,
    email: user.email,
    timestamp: Date.now(),
  });

  // Store session
  await env.CACHE.put(
    `session:${sessionToken}`,
    JSON.stringify({
      userId: user.id,
      email: user.email,
      name: user.name,
      createdAt: Date.now(),
    }),
    { expirationTtl: 86400 * 7 }
  );

  return new Response(
    JSON.stringify({
      success: true,
      token: sessionToken,
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
      },
    }),
    {
      status: 201,
      headers: { 'Content-Type': 'application/json' },
    }
  );
}

/**
 * Handle logout request
 */
async function handleLogout(request: Request, env: Env): Promise<Response> {
  const authHeader = request.headers.get('Authorization');

  if (!authHeader) {
    return new Response(
      JSON.stringify({ error: 'No authorization header' }),
      {
        status: 401,
        headers: { 'Content-Type': 'application/json' },
      }
    );
  }

  const token = authHeader.replace('Bearer ', '');

  // Delete session from KV
  await env.CACHE.delete(`session:${token}`);

  return new Response(
    JSON.stringify({ success: true }),
    {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    }
  );
}

/**
 * Handle refresh token request
 */
async function handleRefresh(request: Request, env: Env): Promise<Response> {
  const authHeader = request.headers.get('Authorization');

  if (!authHeader) {
    return new Response(
      JSON.stringify({ error: 'No authorization header' }),
      {
        status: 401,
        headers: { 'Content-Type': 'application/json' },
      }
    );
  }

  const oldToken = authHeader.replace('Bearer ', '');

  // Get old session
  const session = await env.CACHE.get(`session:${oldToken}`, { type: 'json' }) as any;

  if (!session) {
    return new Response(
      JSON.stringify({ error: 'Invalid session' }),
      {
        status: 401,
        headers: { 'Content-Type': 'application/json' },
      }
    );
  }

  // Generate new token
  const newToken = await generateToken({
    userId: session.userId,
    email: session.email,
    timestamp: Date.now(),
  });

  // Store new session
  await env.CACHE.put(
    `session:${newToken}`,
    JSON.stringify({
      ...session,
      refreshedAt: Date.now(),
    }),
    { expirationTtl: 86400 * 7 }
  );

  // Delete old session
  await env.CACHE.delete(`session:${oldToken}`);

  return new Response(
    JSON.stringify({
      success: true,
      token: newToken,
    }),
    {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    }
  );
}

/**
 * GET /api/auth/me
 * Get current user info
 */
export const onRequestGet: PagesFunction<Env> = async (context) => {
  const { request, env } = context;

  try {
    const authHeader = request.headers.get('Authorization');

    if (!authHeader) {
      return new Response(
        JSON.stringify({ error: 'No authorization header' }),
        {
          status: 401,
          headers: { 'Content-Type': 'application/json' },
        }
      );
    }

    const token = authHeader.replace('Bearer ', '');

    // Get session
    const session = await env.CACHE.get(`session:${token}`, { type: 'json' }) as any;

    if (!session) {
      return new Response(
        JSON.stringify({ error: 'Invalid session' }),
        {
          status: 401,
          headers: { 'Content-Type': 'application/json' },
        }
      );
    }

    // Get full user info
    const user = await env.CACHE.get(`user:${session.email}`, { type: 'json' }) as any;

    if (!user) {
      return new Response(
        JSON.stringify({ error: 'User not found' }),
        {
          status: 404,
          headers: { 'Content-Type': 'application/json' },
        }
      );
    }

    return new Response(
      JSON.stringify({
        user: {
          id: user.id,
          email: user.email,
          name: user.name,
          createdAt: user.createdAt,
        },
      }),
      {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }
    );
  } catch (error) {
    console.error('Get user error:', error);

    return new Response(
      JSON.stringify({
        error: error instanceof Error ? error.message : 'Internal server error',
      }),
      {
        status: 500,
        headers: { 'Content-Type': 'application/json' },
      }
    );
  }
};
