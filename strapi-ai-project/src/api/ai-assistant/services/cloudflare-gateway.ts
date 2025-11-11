/**
 * Cloudflare AI Gateway service with Anthropic SDK
 */

import Anthropic from '@anthropic-ai/sdk';
import type { Core } from '@strapi/strapi';

const DEFAULT_MODEL = 'claude-sonnet-4-20250514';
const DEFAULT_MAX_TOKENS = 4096;

export default ({ strapi }: { strapi: Core.Strapi }) => ({
  /**
   * Initialize Anthropic client with Cloudflare AI Gateway
   */
  getClient() {
    const apiKey = process.env.ANTHROPIC_API_KEY;
    const accountId = process.env.CLOUDFLARE_ACCOUNT_ID;
    const gatewayId = process.env.CLOUDFLARE_GATEWAY_ID;

    if (!apiKey) {
      throw new Error('ANTHROPIC_API_KEY is not configured');
    }

    if (!accountId || !gatewayId) {
      throw new Error('CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_GATEWAY_ID must be configured');
    }

    const baseURL = `https://gateway.ai.cloudflare.com/v1/${accountId}/${gatewayId}/anthropic`;

    return new Anthropic({
      apiKey,
      baseURL,
    });
  },

  /**
   * Generate AI response using Cloudflare AI Gateway + Anthropic
   * @param prompt - The prompt to send to Claude
   * @param options - Additional options for the AI request
   */
  async generateResponse(prompt: string, options: any = {}) {
    try {
      const client = this.getClient();

      const model = options.model || DEFAULT_MODEL;
      const maxTokens = options.max_tokens || options.maxTokens || DEFAULT_MAX_TOKENS;
      const temperature = options.temperature || 0.7;

      const message = await client.messages.create({
        model,
        max_tokens: maxTokens,
        temperature,
        messages: [
          {
            role: 'user',
            content: prompt,
          },
        ],
      });

      // Extract text content from response
      const textContent = message.content
        .filter((block: any) => block.type === 'text')
        .map((block: any) => block.text)
        .join('\n');

      return {
        success: true,
        data: {
          response: textContent,
          model: message.model,
          usage: {
            input_tokens: message.usage.input_tokens,
            output_tokens: message.usage.output_tokens,
          },
          id: message.id,
        },
      };
    } catch (error: any) {
      strapi.log.error('Cloudflare AI Gateway Error:', error.message);

      return {
        success: false,
        error: error.message || 'Failed to generate AI response',
      };
    }
  },

  /**
   * Generate content with system prompt
   * @param contentType - The type of content to generate
   * @param context - Context for generating content
   */
  async generateContent(contentType: string, context: any = {}) {
    try {
      const client = this.getClient();

      // Build system prompt based on content type
      const systemPrompt = this.buildSystemPrompt(contentType, context);
      const userPrompt = this.buildUserPrompt(contentType, context);

      const message = await client.messages.create({
        model: context.model || DEFAULT_MODEL,
        max_tokens: context.max_tokens || DEFAULT_MAX_TOKENS,
        temperature: context.temperature || 0.7,
        system: systemPrompt,
        messages: [
          {
            role: 'user',
            content: userPrompt,
          },
        ],
      });

      const textContent = message.content
        .filter((block: any) => block.type === 'text')
        .map((block: any) => block.text)
        .join('\n');

      return {
        success: true,
        data: {
          content: textContent,
          model: message.model,
          usage: message.usage,
        },
      };
    } catch (error: any) {
      strapi.log.error('Cloudflare AI Gateway Content Generation Error:', error.message);

      return {
        success: false,
        error: error.message || 'Failed to generate content',
      };
    }
  },

  /**
   * Analyze text using Claude via Cloudflare Gateway
   * @param text - The text to analyze
   * @param analysisType - Type of analysis to perform
   */
  async analyzeText(text: string, analysisType: string = 'general') {
    try {
      const client = this.getClient();

      const systemPrompt = this.buildAnalysisSystemPrompt(analysisType);
      const userPrompt = `Analyze the following text:\n\n${text}`;

      const message = await client.messages.create({
        model: DEFAULT_MODEL,
        max_tokens: 2048,
        temperature: 0.3, // Lower temperature for analysis
        system: systemPrompt,
        messages: [
          {
            role: 'user',
            content: userPrompt,
          },
        ],
      });

      const textContent = message.content
        .filter((block: any) => block.type === 'text')
        .map((block: any) => block.text)
        .join('\n');

      // Try to parse as JSON if analysis type expects it
      let analysisData;
      try {
        analysisData = JSON.parse(textContent);
      } catch {
        analysisData = { analysis: textContent };
      }

      return {
        success: true,
        data: analysisData,
      };
    } catch (error: any) {
      strapi.log.error('Cloudflare AI Gateway Analysis Error:', error.message);

      return {
        success: false,
        error: error.message || 'Failed to analyze text',
      };
    }
  },

  /**
   * Build system prompt based on content type
   */
  buildSystemPrompt(contentType: string, context: any): string {
    const prompts: Record<string, string> = {
      'blog-post': `You are a professional blog post writer. Create engaging, informative blog posts based on the topic and context provided. Write in a ${context.tone || 'professional'} tone.`,
      'product-description': `You are an expert product copywriter. Create compelling product descriptions that highlight features and benefits. Write in a ${context.tone || 'persuasive'} tone.`,
      'social-media-post': `You are a social media content creator. Create engaging social media posts optimized for ${context.platform || 'general social media'}. Keep it concise and engaging.`,
      'email': `You are an email copywriter. Create ${context.type || 'professional'} emails that are clear, concise, and effective.`,
      'article': `You are a professional article writer. Create well-researched, informative articles on the given topic. Write for ${context.targetAudience || 'general audience'}.`,
      'description': `You are a content writer specializing in descriptions. Create ${context.style || 'clear and engaging'} descriptions based on the provided information.`,
      'summary': `You are a professional summarizer. Create concise, accurate summaries that capture the key points of the content.`,
    };

    return prompts[contentType] || 'You are a helpful AI assistant. Create high-quality content based on the user\'s request.';
  },

  /**
   * Build user prompt based on content type and context
   */
  buildUserPrompt(contentType: string, context: any): string {
    const parts: string[] = [];

    if (context.topic) {
      parts.push(`Topic: ${context.topic}`);
    }

    if (context.keywords) {
      parts.push(`Keywords: ${Array.isArray(context.keywords) ? context.keywords.join(', ') : context.keywords}`);
    }

    if (context.length) {
      parts.push(`Length: ${context.length}`);
    }

    if (context.additional) {
      parts.push(`Additional context: ${context.additional}`);
    }

    if (parts.length === 0) {
      return `Create a ${contentType} based on the following context: ${JSON.stringify(context)}`;
    }

    return parts.join('\n\n');
  },

  /**
   * Build analysis system prompt based on analysis type
   */
  buildAnalysisSystemPrompt(analysisType: string): string {
    const prompts: Record<string, string> = {
      sentiment: 'You are a sentiment analysis expert. Analyze the text and return a JSON object with: { "sentiment": "positive|negative|neutral", "score": 0-1, "reasoning": "brief explanation" }',
      keywords: 'You are a keyword extraction expert. Extract the most important keywords and return a JSON object with: { "keywords": ["keyword1", "keyword2", ...], "categories": ["category1", ...] }',
      summary: 'You are a text summarization expert. Create a concise summary of the main points.',
      topics: 'You are a topic modeling expert. Identify the main topics and return a JSON object with: { "topics": [{"topic": "name", "relevance": 0-1}] }',
      quality: 'You are a content quality analyst. Evaluate the text quality and return a JSON object with: { "score": 0-100, "strengths": [], "improvements": [], "readability": "easy|medium|hard" }',
      general: 'You are a text analysis expert. Provide a comprehensive analysis of the text including sentiment, key themes, and overall quality.',
    };

    return prompts[analysisType] || prompts.general;
  },

  /**
   * Stream response (for future implementation)
   * Cloudflare AI Gateway supports streaming
   */
  async streamResponse(prompt: string, options: any = {}) {
    try {
      const client = this.getClient();

      const stream = await client.messages.create({
        model: options.model || DEFAULT_MODEL,
        max_tokens: options.max_tokens || DEFAULT_MAX_TOKENS,
        temperature: options.temperature || 0.7,
        messages: [
          {
            role: 'user',
            content: prompt,
          },
        ],
        stream: true,
      });

      return {
        success: true,
        stream,
      };
    } catch (error: any) {
      strapi.log.error('Cloudflare AI Gateway Streaming Error:', error.message);

      return {
        success: false,
        error: error.message || 'Failed to create stream',
      };
    }
  },
});
