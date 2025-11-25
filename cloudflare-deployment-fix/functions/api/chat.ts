/**
 * AI Chat API Endpoint
 * Uses Anthropic API with your stored secrets
 */

interface Env {
  CACHE: KVNamespace;
  ANTHROPIC_API_KEY_1: string;
  ANTHROPIC_API_KEY_2: string;
  AI_GATEWAY_ACCOUNT_ID: string;
  AI_GATEWAY_NAME: string;
}

interface ChatRequest {
  message: string;
  conversationId?: string;
  model?: string;
  maxTokens?: number;
  temperature?: number;
}

interface ChatResponse {
  response: string;
  conversationId: string;
  model: string;
  usage: {
    inputTokens: number;
    outputTokens: number;
  };
  cached: boolean;
}

/**
 * Generate cache key for requests
 */
function getCacheKey(message: string, model: string): string {
  const hash = Array.from(message + model)
    .reduce((hash, char) => ((hash << 5) - hash) + char.charCodeAt(0), 0)
    .toString(36);

  return `chat:${hash}`;
}

/**
 * Call Anthropic API through Cloudflare AI Gateway
 */
async function callAnthropicAPI(
  env: Env,
  request: ChatRequest
): Promise<any> {
  const {
    message,
    model = 'claude-sonnet-4-5-20250929',
    maxTokens = 1024,
    temperature = 1.0,
  } = request;

  // Use AI Gateway for monitoring and caching
  const gatewayUrl = `https://gateway.ai.cloudflare.com/v1/${env.AI_GATEWAY_ACCOUNT_ID}/${env.AI_GATEWAY_NAME}/anthropic`;

  const response = await fetch(`${gatewayUrl}/v1/messages`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': env.ANTHROPIC_API_KEY_1,
      'anthropic-version': '2023-06-01',
    },
    body: JSON.stringify({
      model,
      max_tokens: maxTokens,
      temperature,
      messages: [
        {
          role: 'user',
          content: message,
        },
      ],
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Anthropic API error: ${error}`);
  }

  return await response.json();
}

/**
 * Load conversation history from KV
 */
async function loadConversation(
  env: Env,
  conversationId: string
): Promise<any[] | null> {
  try {
    const history = await env.CACHE.get(
      `conversation:${conversationId}`,
      { type: 'json' }
    );
    return history as any[] | null;
  } catch (error) {
    console.error('Failed to load conversation:', error);
    return null;
  }
}

/**
 * Save conversation history to KV
 */
async function saveConversation(
  env: Env,
  conversationId: string,
  messages: any[]
): Promise<void> {
  try {
    await env.CACHE.put(
      `conversation:${conversationId}`,
      JSON.stringify(messages),
      { expirationTtl: 86400 * 7 } // 7 days
    );
  } catch (error) {
    console.error('Failed to save conversation:', error);
  }
}

/**
 * POST /api/chat
 * Main chat endpoint
 */
export const onRequestPost: PagesFunction<Env> = async (context) => {
  const { request, env } = context;

  try {
    // Parse request body
    const body: ChatRequest = await request.json();

    if (!body.message || typeof body.message !== 'string') {
      return new Response(
        JSON.stringify({ error: 'Invalid message' }),
        {
          status: 400,
          headers: { 'Content-Type': 'application/json' },
        }
      );
    }

    // Generate or use existing conversation ID
    const conversationId = body.conversationId || crypto.randomUUID();

    // Check cache for exact same query
    const cacheKey = getCacheKey(body.message, body.model || 'default');
    const cachedResponse = await env.CACHE.get(cacheKey, { type: 'json' });

    if (cachedResponse) {
      console.log('Cache hit for message:', body.message.slice(0, 50));

      return new Response(
        JSON.stringify({
          ...cachedResponse,
          cached: true,
          conversationId,
        }),
        {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        }
      );
    }

    // Load conversation history if exists
    let conversationHistory = await loadConversation(env, conversationId) || [];

    // Call Anthropic API
    const apiResponse = await callAnthropicAPI(env, body);

    // Extract response text
    const responseText = apiResponse.content[0].text;

    // Update conversation history
    conversationHistory.push(
      { role: 'user', content: body.message },
      { role: 'assistant', content: responseText }
    );

    // Save conversation history
    await saveConversation(env, conversationId, conversationHistory);

    // Prepare response
    const chatResponse: ChatResponse = {
      response: responseText,
      conversationId,
      model: apiResponse.model,
      usage: {
        inputTokens: apiResponse.usage.input_tokens,
        outputTokens: apiResponse.usage.output_tokens,
      },
      cached: false,
    };

    // Cache the response (1 hour TTL for identical queries)
    await env.CACHE.put(
      cacheKey,
      JSON.stringify(chatResponse),
      { expirationTtl: 3600 }
    );

    return new Response(JSON.stringify(chatResponse), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (error) {
    console.error('Chat endpoint error:', error);

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
 * GET /api/chat?conversationId=xxx
 * Get conversation history
 */
export const onRequestGet: PagesFunction<Env> = async (context) => {
  const { request, env } = context;

  try {
    const url = new URL(request.url);
    const conversationId = url.searchParams.get('conversationId');

    if (!conversationId) {
      return new Response(
        JSON.stringify({ error: 'conversationId required' }),
        {
          status: 400,
          headers: { 'Content-Type': 'application/json' },
        }
      );
    }

    const history = await loadConversation(env, conversationId);

    if (!history) {
      return new Response(
        JSON.stringify({ error: 'Conversation not found' }),
        {
          status: 404,
          headers: { 'Content-Type': 'application/json' },
        }
      );
    }

    return new Response(
      JSON.stringify({
        conversationId,
        messages: history,
      }),
      {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }
    );
  } catch (error) {
    console.error('Get conversation error:', error);

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
 * DELETE /api/chat?conversationId=xxx
 * Delete conversation history
 */
export const onRequestDelete: PagesFunction<Env> = async (context) => {
  const { request, env } = context;

  try {
    const url = new URL(request.url);
    const conversationId = url.searchParams.get('conversationId');

    if (!conversationId) {
      return new Response(
        JSON.stringify({ error: 'conversationId required' }),
        {
          status: 400,
          headers: { 'Content-Type': 'application/json' },
        }
      );
    }

    await env.CACHE.delete(`conversation:${conversationId}`);

    return new Response(
      JSON.stringify({ success: true }),
      {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }
    );
  } catch (error) {
    console.error('Delete conversation error:', error);

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
