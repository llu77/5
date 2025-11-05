/**
 * Extended Thinking Agent with Cloudflare Sandbox
 *
 * Combines extended thinking pattern with isolated sandbox execution.
 * Run complex reasoning tasks with code execution in secure containers.
 */

import { getSandbox } from '@cloudflare/sandbox';
import Anthropic from '@anthropic-ai/sdk';

export { Sandbox } from '@cloudflare/sandbox';

interface Env {
  Sandbox: DurableObjectNamespace;
  ANTHROPIC_API_KEY: string;
}

interface ThinkingRequest {
  task: string;
  context?: string;
  thinkingBudget?: number;
  requiresCodeExecution?: boolean;
}

interface ThinkingResult {
  thinking: string;
  answer: string;
  codeExecutionResults?: Array<{
    code: string;
    output: string;
    success: boolean;
  }>;
}

/**
 * Execute code in sandbox and return results
 */
async function executeInSandbox(
  sandbox: any,
  code: string,
  language: 'python' | 'node' = 'python'
): Promise<{ output: string; success: boolean }> {
  try {
    const cmd = language === 'python'
      ? `python3 -c "${code.replaceAll('"', '\\"')}"`
      : `node -e "${code.replaceAll('"', '\\"')}"`;

    const result = await sandbox.exec(cmd);

    return {
      output: result.success ? result.stdout : result.stderr,
      success: result.success
    };
  } catch (error) {
    return {
      output: error instanceof Error ? error.message : String(error),
      success: false
    };
  }
}

/**
 * Process task with extended thinking and optional code execution
 */
async function processWithThinking(
  env: Env,
  request: ThinkingRequest
): Promise<ThinkingResult> {
  const anthropic = new Anthropic({ apiKey: env.ANTHROPIC_API_KEY });

  // Build system prompt
  let systemPrompt = 'You are an expert problem solver with deep analytical capabilities.';

  if (request.requiresCodeExecution) {
    systemPrompt += '\n\nWhen you need to perform calculations or data analysis, ' +
      'write Python code. The code will be executed in a secure sandbox.';
  }

  if (request.context) {
    systemPrompt += `\n\nContext: ${request.context}`;
  }

  // Create message with extended thinking
  const response = await anthropic.messages.create({
    model: 'claude-sonnet-4-5',
    max_tokens: 4000,
    thinking: {
      type: 'enabled',
      budget_tokens: request.thinkingBudget || 2000
    },
    system: systemPrompt,
    messages: [{ role: 'user', content: request.task }]
  });

  // Extract thinking and answer
  let thinking = '';
  let answer = '';
  const codeExecutionResults: Array<{ code: string; output: string; success: boolean }> = [];

  for (const block of response.content) {
    if (block.type === 'thinking') {
      thinking = block.thinking;
    } else if (block.type === 'text') {
      answer = block.text;

      // If code execution is enabled, extract and run code blocks
      if (request.requiresCodeExecution) {
        const codeBlocks = extractCodeBlocks(block.text);

        if (codeBlocks.length > 0) {
          // Create sandbox for code execution
          const sandbox = getSandbox(env.Sandbox, crypto.randomUUID().slice(0, 8));

          for (const { language, code } of codeBlocks) {
            const result = await executeInSandbox(sandbox, code, language as any);
            codeExecutionResults.push({ code, ...result });
          }
        }
      }
    }
  }

  return {
    thinking,
    answer,
    codeExecutionResults: codeExecutionResults.length > 0 ? codeExecutionResults : undefined
  };
}

/**
 * Extract code blocks from markdown
 */
function extractCodeBlocks(text: string): Array<{ language: string; code: string }> {
  const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g;
  const blocks: Array<{ language: string; code: string }> = [];
  let match;

  while ((match = codeBlockRegex.exec(text)) !== null) {
    blocks.push({
      language: match[1] || 'python',
      code: match[2].trim()
    });
  }

  return blocks;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405 });
    }

    try {
      const body = await request.json<ThinkingRequest>();

      if (!body.task) {
        return Response.json({ error: 'Missing task field' }, { status: 400 });
      }

      const result = await processWithThinking(env, body);

      return Response.json(result);

    } catch (error) {
      console.error('Error processing request:', error);
      return Response.json(
        { error: error instanceof Error ? error.message : 'Internal error' },
        { status: 500 }
      );
    }
  }
} satisfies ExportedHandler<Env>;
