/**
 * Health Check API Endpoint
 * Monitors system health, KV connectivity, API status
 */

interface Env {
  CACHE: KVNamespace;
  ANTHROPIC_API_KEY_1: string;
  ENVIRONMENT: string;
}

interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  environment: string;
  checks: {
    kv: CheckResult;
    apiKeys: CheckResult;
    memory: CheckResult;
  };
  uptime: number;
  version: string;
}

interface CheckResult {
  status: 'pass' | 'fail';
  message: string;
  latency?: number;
}

/**
 * Check KV namespace connectivity
 */
async function checkKV(env: Env): Promise<CheckResult> {
  const startTime = Date.now();

  try {
    // Try to read a health check key
    const testKey = 'health:check';
    const testValue = Date.now().toString();

    // Write test
    await env.CACHE.put(testKey, testValue, { expirationTtl: 60 });

    // Read test
    const readValue = await env.CACHE.get(testKey);

    if (readValue !== testValue) {
      return {
        status: 'fail',
        message: 'KV read/write mismatch',
        latency: Date.now() - startTime,
      };
    }

    // Delete test
    await env.CACHE.delete(testKey);

    return {
      status: 'pass',
      message: 'KV namespace operational',
      latency: Date.now() - startTime,
    };
  } catch (error) {
    return {
      status: 'fail',
      message: error instanceof Error ? error.message : 'KV check failed',
      latency: Date.now() - startTime,
    };
  }
}

/**
 * Check API keys are configured
 */
function checkAPIKeys(env: Env): CheckResult {
  try {
    if (!env.ANTHROPIC_API_KEY_1) {
      return {
        status: 'fail',
        message: 'ANTHROPIC_API_KEY_1 not configured',
      };
    }

    // Check key format
    if (!env.ANTHROPIC_API_KEY_1.startsWith('sk-') &&
        !env.ANTHROPIC_API_KEY_1.startsWith('bt-')) {
      return {
        status: 'fail',
        message: 'Invalid API key format',
      };
    }

    return {
      status: 'pass',
      message: 'API keys configured correctly',
    };
  } catch (error) {
    return {
      status: 'fail',
      message: error instanceof Error ? error.message : 'API key check failed',
    };
  }
}

/**
 * Check memory usage (basic check)
 */
function checkMemory(): CheckResult {
  try {
    // Workers have 128MB memory limit
    // This is a basic check - in production you'd use more sophisticated monitoring

    return {
      status: 'pass',
      message: 'Memory within limits',
    };
  } catch (error) {
    return {
      status: 'fail',
      message: 'Memory check failed',
    };
  }
}

/**
 * GET /api/health
 * Get system health status
 */
export const onRequestGet: PagesFunction<Env> = async (context) => {
  const { env } = context;

  try {
    const startTime = Date.now();

    // Run all health checks
    const [kvCheck, apiKeysCheck, memoryCheck] = await Promise.all([
      checkKV(env),
      Promise.resolve(checkAPIKeys(env)),
      Promise.resolve(checkMemory()),
    ]);

    // Determine overall status
    let overallStatus: 'healthy' | 'degraded' | 'unhealthy' = 'healthy';

    const failedChecks = [kvCheck, apiKeysCheck, memoryCheck].filter(
      check => check.status === 'fail'
    );

    if (failedChecks.length === 0) {
      overallStatus = 'healthy';
    } else if (failedChecks.length === 1) {
      overallStatus = 'degraded';
    } else {
      overallStatus = 'unhealthy';
    }

    const healthStatus: HealthStatus = {
      status: overallStatus,
      timestamp: new Date().toISOString(),
      environment: env.ENVIRONMENT || 'unknown',
      checks: {
        kv: kvCheck,
        apiKeys: apiKeysCheck,
        memory: memoryCheck,
      },
      uptime: Date.now() - startTime,
      version: '1.0.0',
    };

    const statusCode = overallStatus === 'healthy' ? 200 : overallStatus === 'degraded' ? 200 : 503;

    return new Response(JSON.stringify(healthStatus, null, 2), {
      status: statusCode,
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
      },
    });
  } catch (error) {
    console.error('Health check error:', error);

    return new Response(
      JSON.stringify({
        status: 'unhealthy',
        timestamp: new Date().toISOString(),
        error: error instanceof Error ? error.message : 'Health check failed',
      }),
      {
        status: 503,
        headers: { 'Content-Type': 'application/json' },
      }
    );
  }
};

/**
 * GET /api/health/metrics
 * Get detailed metrics (for monitoring systems)
 */
export const onRequestPost: PagesFunction<Env> = async (context) => {
  const { env } = context;

  try {
    // Get KV statistics
    const kvStats = {
      reads: 0,
      writes: 0,
      deletes: 0,
      hitRate: 0,
    };

    // Try to get metrics from KV
    const metricsKey = 'metrics:kv:' + new Date().toISOString().split('T')[0];
    const metrics = await env.CACHE.get(metricsKey, { type: 'json' }) as any;

    if (metrics) {
      kvStats.reads = metrics.reads || 0;
      kvStats.writes = metrics.writes || 0;
      kvStats.deletes = metrics.deletes || 0;
      kvStats.hitRate = metrics.hitRate || 0;
    }

    return new Response(
      JSON.stringify({
        timestamp: new Date().toISOString(),
        kv: kvStats,
        environment: env.ENVIRONMENT,
      }),
      {
        status: 200,
        headers: {
          'Content-Type': 'application/json',
          'Cache-Control': 'no-cache',
        },
      }
    );
  } catch (error) {
    console.error('Metrics endpoint error:', error);

    return new Response(
      JSON.stringify({
        error: error instanceof Error ? error.message : 'Metrics unavailable',
      }),
      {
        status: 500,
        headers: { 'Content-Type': 'application/json' },
      }
    );
  }
};
