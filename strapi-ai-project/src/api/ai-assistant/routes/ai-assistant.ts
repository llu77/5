/**
 * ai-assistant router
 */

export default {
  routes: [
    {
      method: 'POST',
      path: '/ai-assistant/generate',
      handler: 'ai-assistant.generate',
      config: {
        policies: [],
        middlewares: [],
      },
    },
    {
      method: 'POST',
      path: '/ai-assistant/content',
      handler: 'ai-assistant.generateContent',
      config: {
        policies: [],
        middlewares: [],
      },
    },
    {
      method: 'POST',
      path: '/ai-assistant/analyze',
      handler: 'ai-assistant.analyze',
      config: {
        policies: [],
        middlewares: [],
      },
    },
    {
      method: 'GET',
      path: '/ai-assistant/health',
      handler: 'ai-assistant.healthCheck',
      config: {
        policies: [],
        middlewares: [],
      },
    },
  ],
};
