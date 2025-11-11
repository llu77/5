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
        .service('api::ai-assistant.ai-assistant')
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
        .service('api::ai-assistant.ai-assistant')
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
        .service('api::ai-assistant.ai-assistant')
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
      const apiKey = process.env.STRAPI_AI_API_KEY;

      ctx.body = {
        status: 'ok',
        configured: !!apiKey,
        message: apiKey ? 'Strapi AI is configured and ready' : 'Strapi AI API key not configured',
      };
    } catch (error: any) {
      ctx.throw(500, error.message);
    }
  },
});
