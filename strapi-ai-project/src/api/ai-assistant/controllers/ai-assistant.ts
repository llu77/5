/**
 * ai-assistant controller
 */

import type { Core } from '@strapi/strapi';

export default ({ strapi }: { strapi: Core.Strapi }) => ({
  /**
   * Generate AI response endpoint
   */
  async generate(ctx) {
    try {
      const { prompt, options } = ctx.request.body;

      if (!prompt) {
        return ctx.badRequest('Prompt is required');
      }

      const result = await strapi
        .service('api::ai-assistant.ai-provider')
        .generateResponse(prompt, options);

      if (!result.success) {
        return ctx.badRequest(result.error);
      }

      ctx.body = {
        data: result.data,
      };
    } catch (error: any) {
      ctx.throw(500, error.message);
    }
  },

  /**
   * Generate content suggestions endpoint
   */
  async generateContent(ctx) {
    try {
      const { contentType, context } = ctx.request.body;

      if (!contentType) {
        return ctx.badRequest('Content type is required');
      }

      const result = await strapi
        .service('api::ai-assistant.ai-provider')
        .generateContent(contentType, context);

      if (!result.success) {
        return ctx.badRequest(result.error);
      }

      ctx.body = {
        data: result.data,
      };
    } catch (error: any) {
      ctx.throw(500, error.message);
    }
  },

  /**
   * Analyze text endpoint
   */
  async analyze(ctx) {
    try {
      const { text, analysisType } = ctx.request.body;

      if (!text) {
        return ctx.badRequest('Text is required');
      }

      const result = await strapi
        .service('api::ai-assistant.ai-provider')
        .analyzeText(text, analysisType);

      if (!result.success) {
        return ctx.badRequest(result.error);
      }

      ctx.body = {
        data: result.data,
      };
    } catch (error: any) {
      ctx.throw(500, error.message);
    }
  },

  /**
   * Health check endpoint for AI integration
   */
  async healthCheck(ctx) {
    try {
      const providerInfo = await strapi
        .service('api::ai-assistant.ai-provider')
        .getProviderInfo();

      ctx.body = {
        status: 'ok',
        provider: providerInfo.provider,
        configured: providerInfo.configured,
        available: providerInfo.available,
        features: providerInfo.features,
        message: providerInfo.configured
          ? `${providerInfo.provider} is configured and ready`
          : `${providerInfo.provider} is not configured. Required env vars: ${providerInfo.requiredEnvVars.join(', ')}`,
      };
    } catch (error: any) {
      ctx.throw(500, error.message);
    }
  },
});
