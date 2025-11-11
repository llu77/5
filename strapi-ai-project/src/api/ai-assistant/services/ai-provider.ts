/**
 * AI Provider Factory
 * Manages different AI service providers (Strapi AI, Cloudflare Gateway, etc.)
 */

import type { Core } from '@strapi/strapi';

type AIProvider = 'strapi-ai' | 'cloudflare-gateway' | 'anthropic-direct';

interface AIServiceInterface {
  generateResponse(prompt: string, options?: any): Promise<any>;
  generateContent(contentType: string, context?: any): Promise<any>;
  analyzeText(text: string, analysisType?: string): Promise<any>;
}

export default ({ strapi }: { strapi: Core.Strapi }) => ({
  /**
   * Get the configured AI provider
   */
  getProvider(): AIProvider {
    const provider = (process.env.AI_PROVIDER || 'strapi-ai') as AIProvider;

    const validProviders: AIProvider[] = ['strapi-ai', 'cloudflare-gateway', 'anthropic-direct'];

    if (!validProviders.includes(provider)) {
      strapi.log.warn(`Invalid AI_PROVIDER: ${provider}. Falling back to strapi-ai`);
      return 'strapi-ai';
    }

    return provider;
  },

  /**
   * Get the AI service instance based on configured provider
   */
  getService(): AIServiceInterface {
    const provider = this.getProvider();

    switch (provider) {
      case 'cloudflare-gateway':
        return strapi.service('api::ai-assistant.cloudflare-gateway');

      case 'strapi-ai':
      default:
        return strapi.service('api::ai-assistant.ai-assistant');
    }
  },

  /**
   * Generate AI response using configured provider
   */
  async generateResponse(prompt: string, options: any = {}) {
    const service = this.getService();
    return service.generateResponse(prompt, options);
  },

  /**
   * Generate content using configured provider
   */
  async generateContent(contentType: string, context: any = {}) {
    const service = this.getService();
    return service.generateContent(contentType, context);
  },

  /**
   * Analyze text using configured provider
   */
  async analyzeText(text: string, analysisType: string = 'general') {
    const service = this.getService();
    return service.analyzeText(text, analysisType);
  },

  /**
   * Get provider information and status
   */
  async getProviderInfo() {
    const provider = this.getProvider();

    const info: any = {
      provider,
      configured: false,
      available: false,
    };

    switch (provider) {
      case 'cloudflare-gateway':
        info.configured = !!(
          process.env.ANTHROPIC_API_KEY &&
          process.env.CLOUDFLARE_ACCOUNT_ID &&
          process.env.CLOUDFLARE_GATEWAY_ID
        );
        info.requiredEnvVars = [
          'ANTHROPIC_API_KEY',
          'CLOUDFLARE_ACCOUNT_ID',
          'CLOUDFLARE_GATEWAY_ID',
        ];
        info.features = ['caching', 'rate-limiting', 'analytics', 'streaming'];
        break;

      case 'strapi-ai':
      default:
        info.configured = !!process.env.STRAPI_AI_API_KEY;
        info.requiredEnvVars = ['STRAPI_AI_API_KEY'];
        info.features = ['content-generation', 'analysis'];
        break;
    }

    info.available = info.configured;

    return info;
  },
});
