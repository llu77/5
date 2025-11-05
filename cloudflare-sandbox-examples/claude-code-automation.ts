/**
 * Claude Code Automation with Sandboxes
 *
 * Automatically clone repositories, run Claude Code to implement features/fix bugs,
 * and return git diffs. Based on cloudflare/sandbox-sdk claude-code example.
 */

import { getSandbox } from '@cloudflare/sandbox';

export { Sandbox } from '@cloudflare/sandbox';

interface Env {
  Sandbox: DurableObjectNamespace;
  ANTHROPIC_API_KEY: string;
}

interface CmdOutput {
  success: boolean;
  stdout: string;
  stderr: string;
  exitCode: number;
}

interface AutomationRequest {
  repo: string;
  task: string;
  branch?: string;
  appendSystemPrompt?: string;
}

interface AutomationResult {
  success: boolean;
  logs: string;
  diff: string;
  filesChanged: string[];
  error?: string;
}

/**
 * Helper to read outputs from exec results
 */
const getOutput = (res: CmdOutput): string =>
  res.success ? res.stdout : res.stderr;

/**
 * Default system prompt for Claude Code automation
 */
const DEFAULT_SYSTEM_PROMPT =
  'You are an automatic feature-implementer/bug-fixer. ' +
  'You apply all necessary changes to achieve the user request. ' +
  'You must ensure you DO NOT commit the changes, ' +
  'so the pipeline can read the local `git diff` and apply the change upstream.';

/**
 * Parse git diff to extract changed files
 */
function extractChangedFiles(diff: string): string[] {
  const files: Set<string> = new Set();
  const lines = diff.split('\n');

  for (const line of lines) {
    if (line.startsWith('diff --git')) {
      // Extract filename from "diff --git a/file.ts b/file.ts"
      const match = line.match(/b\/(.+)$/);
      if (match) {
        files.add(match[1]);
      }
    }
  }

  return Array.from(files);
}

/**
 * Run Claude Code automation in isolated sandbox
 */
async function runAutomation(
  env: Env,
  request: AutomationRequest
): Promise<AutomationResult> {
  try {
    // Extract repo name
    const repoName = request.repo.split('/').pop() || 'repo';

    // Create unique sandbox for this automation
    const sandboxId = crypto.randomUUID().slice(0, 8);
    const sandbox = getSandbox(env.Sandbox, sandboxId);

    // Clone repository
    console.log(`Cloning ${request.repo} to ${repoName}...`);
    await sandbox.gitCheckout(request.repo, {
      targetDir: repoName,
      ...(request.branch && { branch: request.branch })
    });

    // Set environment variables for Claude Code
    await sandbox.setEnvVars({
      ANTHROPIC_API_KEY: env.ANTHROPIC_API_KEY
    });

    // Build Claude Code command
    const systemPrompt = request.appendSystemPrompt || DEFAULT_SYSTEM_PROMPT;
    const cmd = [
      `cd ${repoName}`,
      '&&',
      'claude',
      '--append-system-prompt',
      `"${systemPrompt}"`,
      '-p',
      `"${request.task.replaceAll('"', '\\"')}"`,
      '--permission-mode acceptEdits'
    ].join(' ');

    console.log(`Running Claude Code with task: ${request.task}`);

    // Execute Claude Code
    const claudeResult = await sandbox.exec(cmd);
    const logs = getOutput(claudeResult);

    // Get git diff
    const diffResult = await sandbox.exec('git diff');
    const diff = getOutput(diffResult);

    // Extract changed files
    const filesChanged = extractChangedFiles(diff);

    return {
      success: claudeResult.success,
      logs,
      diff,
      filesChanged
    };

  } catch (error) {
    console.error('Automation failed:', error);
    return {
      success: false,
      logs: '',
      diff: '',
      filesChanged: [],
      error: error instanceof Error ? error.message : String(error)
    };
  }
}

/**
 * Validate repository URL
 */
function isValidRepoUrl(url: string): boolean {
  try {
    const patterns = [
      /^https:\/\/github\.com\/[\w-]+\/[\w.-]+$/,
      /^git@github\.com:[\w-]+\/[\w.-]+\.git$/
    ];
    return patterns.some(pattern => pattern.test(url));
  } catch {
    return false;
  }
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    if (request.method !== 'POST') {
      return new Response(
        JSON.stringify({
          error: 'Method not allowed',
          usage: {
            endpoint: 'POST /',
            body: {
              repo: 'https://github.com/user/repo',
              task: 'Add feature X or fix bug Y',
              branch: 'optional-branch-name',
              appendSystemPrompt: 'optional-custom-system-prompt'
            }
          }
        }),
        {
          status: 405,
          headers: { 'Content-Type': 'application/json' }
        }
      );
    }

    try {
      const body = await request.json<AutomationRequest>();

      // Validate required fields
      if (!body.repo || !body.task) {
        return Response.json(
          { error: 'Missing required fields: repo and task' },
          { status: 400 }
        );
      }

      // Validate repo URL
      if (!isValidRepoUrl(body.repo)) {
        return Response.json(
          { error: 'Invalid repository URL. Use format: https://github.com/user/repo' },
          { status: 400 }
        );
      }

      // Run automation
      const result = await runAutomation(env, body);

      return Response.json(result);

    } catch (error) {
      console.error('Request failed:', error);
      return Response.json(
        { error: error instanceof Error ? error.message : 'Internal error' },
        { status: 500 }
      );
    }
  }
} satisfies ExportedHandler<Env>;
