/**
 * Orchestrator-Workers Pattern with Cloudflare Sandboxes
 *
 * Distributes work across multiple isolated sandboxes.
 * Each worker runs in its own container for true isolation.
 */

import { getSandbox } from '@cloudflare/sandbox';
import Anthropic from '@anthropic-ai/sdk';

export { Sandbox } from '@cloudflare/sandbox';

interface Env {
  Sandbox: DurableObjectNamespace;
  ANTHROPIC_API_KEY: string;
}

interface WorkerTask {
  id: string;
  role: string;
  task: string;
  sandboxId: string;
}

interface OrchestratorRequest {
  task: string;
  context?: string;
  maxWorkers?: number;
}

interface WorkerResult {
  workerId: string;
  role: string;
  result: string;
  sandboxOutput?: string;
  error?: string;
}

interface OrchestratorResult {
  analysis: string;
  workers: WorkerResult[];
  synthesis: string;
}

const ORCHESTRATOR_PROMPT = `You are an orchestrator that analyzes tasks and delegates them to specialized workers.

Given a task, you should:
1. Break it down into subtasks
2. Determine what specialist roles are needed
3. Output the task assignments in XML format

Use this format:
<analysis>
Your analysis of the task and decomposition strategy
</analysis>

<workers>
<worker>
<role>Role name (e.g., "Data Analyst", "Security Researcher")</role>
<task>Specific task for this worker</task>
</worker>
<!-- More workers as needed -->
</workers>

Limit to 5 workers maximum for efficiency.`;

const WORKER_SYSTEM_TEMPLATE = `You are a {role}.

Your specific task:
{task}

Provide a focused response based on your expertise. If you need to run code or commands,
describe what should be executed - it will run in an isolated sandbox environment.`;

/**
 * Parse XML content between tags
 */
function extractXML(text: string, tag: string): string {
  const regex = new RegExp(`<${tag}>([\\s\\S]*?)</${tag}>`, 'i');
  const match = text.match(regex);
  return match ? match[1].trim() : '';
}

/**
 * Parse worker tasks from orchestrator response
 */
function parseWorkerTasks(orchestratorResponse: string): WorkerTask[] {
  const workersXML = extractXML(orchestratorResponse, 'workers');
  const workerBlocks = workersXML.match(/<worker>[\s\S]*?<\/worker>/gi) || [];

  return workerBlocks.map((block, index) => ({
    id: `worker-${index + 1}`,
    role: extractXML(block, 'role'),
    task: extractXML(block, 'task'),
    sandboxId: crypto.randomUUID().slice(0, 8)
  }));
}

/**
 * Execute worker task in isolated sandbox
 */
async function runWorker(
  env: Env,
  worker: WorkerTask,
  originalTask: string
): Promise<WorkerResult> {
  try {
    const anthropic = new Anthropic({ apiKey: env.ANTHROPIC_API_KEY });

    // Create dedicated sandbox for this worker
    const sandbox = getSandbox(env.Sandbox, worker.sandboxId);

    // Prepare system prompt
    const systemPrompt = WORKER_SYSTEM_TEMPLATE
      .replace('{role}', worker.role)
      .replace('{task}', worker.task);

    // Get worker's response
    const response = await anthropic.messages.create({
      model: 'claude-sonnet-4-5',
      max_tokens: 2000,
      system: systemPrompt,
      messages: [{
        role: 'user',
        content: `Original task: ${originalTask}\n\nYour specific assignment: ${worker.task}`
      }]
    });

    let result = '';
    for (const block of response.content) {
      if (block.type === 'text') {
        result = block.text;
      }
    }

    // Check if worker mentioned code/commands to execute
    let sandboxOutput: string | undefined;
    const codeBlocks = extractCodeBlocks(result);

    if (codeBlocks.length > 0) {
      // Execute first code block in sandbox
      const { code } = codeBlocks[0];
      const execResult = await sandbox.exec(`python3 -c "${code.replaceAll('"', '\\"')}"`);
      sandboxOutput = execResult.success ? execResult.stdout : execResult.stderr;
    }

    return {
      workerId: worker.id,
      role: worker.role,
      result,
      sandboxOutput
    };

  } catch (error) {
    return {
      workerId: worker.id,
      role: worker.role,
      result: '',
      error: error instanceof Error ? error.message : String(error)
    };
  }
}

/**
 * Extract code blocks from text
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

/**
 * Synthesize worker results
 */
async function synthesizeResults(
  env: Env,
  originalTask: string,
  analysis: string,
  workerResults: WorkerResult[]
): Promise<string> {
  const anthropic = new Anthropic({ apiKey: env.ANTHROPIC_API_KEY });

  // Build synthesis prompt
  let prompt = `Original task: ${originalTask}\n\n`;
  prompt += `Orchestrator analysis:\n${analysis}\n\n`;
  prompt += 'Worker results:\n\n';

  for (const worker of workerResults) {
    prompt += `## ${worker.role} (${worker.workerId})\n`;
    prompt += `${worker.result}\n`;
    if (worker.sandboxOutput) {
      prompt += `Sandbox execution output:\n${worker.sandboxOutput}\n`;
    }
    if (worker.error) {
      prompt += `Error: ${worker.error}\n`;
    }
    prompt += '\n';
  }

  prompt += 'Synthesize these results into a comprehensive answer to the original task.';

  const response = await anthropic.messages.create({
    model: 'claude-sonnet-4-5',
    max_tokens: 3000,
    messages: [{ role: 'user', content: prompt }]
  });

  for (const block of response.content) {
    if (block.type === 'text') {
      return block.text;
    }
  }

  return 'Failed to synthesize results';
}

/**
 * Main orchestrator-workers flow
 */
async function processWithOrchestrator(
  env: Env,
  request: OrchestratorRequest
): Promise<OrchestratorResult> {
  const anthropic = new Anthropic({ apiKey: env.ANTHROPIC_API_KEY });

  // Step 1: Orchestrator analyzes and delegates
  const orchestratorResponse = await anthropic.messages.create({
    model: 'claude-sonnet-4-5',
    max_tokens: 2000,
    system: ORCHESTRATOR_PROMPT,
    messages: [{
      role: 'user',
      content: request.context
        ? `Task: ${request.task}\n\nContext: ${request.context}`
        : request.task
    }]
  });

  let orchestratorOutput = '';
  for (const block of orchestratorResponse.content) {
    if (block.type === 'text') {
      orchestratorOutput = block.text;
    }
  }

  const analysis = extractXML(orchestratorOutput, 'analysis');
  let workerTasks = parseWorkerTasks(orchestratorOutput);

  // Limit workers if specified
  if (request.maxWorkers && workerTasks.length > request.maxWorkers) {
    workerTasks = workerTasks.slice(0, request.maxWorkers);
  }

  // Step 2: Run workers in parallel, each in own sandbox
  const workerPromises = workerTasks.map(task =>
    runWorker(env, task, request.task)
  );
  const workerResults = await Promise.all(workerPromises);

  // Step 3: Synthesize results
  const synthesis = await synthesizeResults(
    env,
    request.task,
    analysis,
    workerResults
  );

  return {
    analysis,
    workers: workerResults,
    synthesis
  };
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405 });
    }

    try {
      const body = await request.json<OrchestratorRequest>();

      if (!body.task) {
        return Response.json({ error: 'Missing task field' }, { status: 400 });
      }

      const result = await processWithOrchestrator(env, body);

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
