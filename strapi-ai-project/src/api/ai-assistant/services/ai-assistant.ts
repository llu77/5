/**
 * ai-assistant service
 */

import axios from 'axios';
import type { Core } from '@strapi/strapi';

const STRAPI_AI_API_URL = 'https://api.strapi.io/ai';

export default ({ strapi }: { strapi: Core.Strapi }) => ({
  /**
   * Generate AI response using Strapi AI
   * @param prompt - The prompt to send to AI
   * @param options - Additional options for the AI request
   */
  async generateResponse(prompt: string, options: any = {}) {
    try {
      const apiKey = process.env.STRAPI_AI_API_KEY;

      if (!apiKey) {
        throw new Error('STRAPI_AI_API_KEY is not configured');
      }

      const response = await axios.post(
        `${STRAPI_AI_API_URL}/generate`,
        {
          prompt,
          ...options,
        },
        {
          headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json',
          },
        }
      );

      return {
        success: true,
        data: response.data,
      };
    } catch (error: any) {
      strapi.log.error('Strapi AI Error:', error.response?.data || error.message);

      return {
        success: false,
        error: error.response?.data?.message || error.message || 'Failed to generate AI response',
      };
    }
  },

  /**
   * Generate content suggestions using AI
   * @param contentType - The type of content to generate
   * @param context - Context for generating content
   */
  async generateContent(contentType: string, context: any = {}) {
    try {
      const apiKey = process.env.STRAPI_AI_API_KEY;

      if (!apiKey) {
        throw new Error('STRAPI_AI_API_KEY is not configured');
      }

      const response = await axios.post(
        `${STRAPI_AI_API_URL}/content`,
        {
          type: contentType,
          context,
        },
        {
          headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json',
          },
        }
      );

      return {
        success: true,
        data: response.data,
      };
    } catch (error: any) {
      strapi.log.error('Strapi AI Content Generation Error:', error.response?.data || error.message);

      return {
        success: false,
        error: error.response?.data?.message || error.message || 'Failed to generate content',
      };
    }
  },

  /**
   * Analyze text using Strapi AI
   * @param text - The text to analyze
   * @param analysisType - Type of analysis to perform
   */
  async analyzeText(text: string, analysisType: string = 'general') {
    try {
      const apiKey = process.env.STRAPI_AI_API_KEY;

      if (!apiKey) {
        throw new Error('STRAPI_AI_API_KEY is not configured');
      }

      const response = await axios.post(
        `${STRAPI_AI_API_URL}/analyze`,
        {
          text,
          type: analysisType,
        },
        {
          headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json',
          },
        }
      );

      return {
        success: true,
        data: response.data,
      };
    } catch (error: any) {
      strapi.log.error('Strapi AI Analysis Error:', error.response?.data || error.message);

      return {
        success: false,
        error: error.response?.data?.message || error.message || 'Failed to analyze text',
      };
    }
  },
});
