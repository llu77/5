# Strapi AI Integration - Usage Examples

## Practical Use Cases

### 1. Auto-Generate Restaurant Descriptions

Automatically generate engaging descriptions for restaurants in your database.

```javascript
// In your Strapi controller or service
async createRestaurantWithAI(ctx) {
  const { name, cuisine, location } = ctx.request.body;

  // Generate description using AI
  const aiResult = await strapi
    .service('api::ai-assistant.ai-assistant')
    .generateResponse(
      `Write an engaging 2-paragraph description for a ${cuisine} restaurant called "${name}" located in ${location}. Make it warm and inviting.`,
      { temperature: 0.8, max_tokens: 300 }
    );

  if (aiResult.success) {
    // Create restaurant with AI-generated description
    const restaurant = await strapi.entityService.create('api::restaurant.restaurant', {
      data: {
        name,
        cuisine,
        location,
        description: aiResult.data.response,
      },
    });

    return restaurant;
  }
}
```

### 2. Content Enhancement

Enhance existing content with AI-powered suggestions.

```javascript
// Enhance product descriptions
async enhanceProductDescription(productId) {
  // Get existing product
  const product = await strapi.entityService.findOne(
    'api::product.product',
    productId
  );

  // Generate enhanced description
  const aiResult = await strapi
    .service('api::ai-assistant.ai-assistant')
    .generateContent('product-description', {
      name: product.name,
      category: product.category,
      features: product.features,
      targetAudience: 'tech-savvy consumers',
    });

  if (aiResult.success) {
    // Update product with enhanced description
    await strapi.entityService.update('api::product.product', productId, {
      data: {
        enhancedDescription: aiResult.data.content,
      },
    });
  }
}
```

### 3. Content Moderation

Automatically analyze and moderate user-generated content.

```javascript
// Moderate user reviews
async moderateReview(ctx) {
  const { text, restaurantId } = ctx.request.body;

  // Analyze sentiment and content
  const analysisResult = await strapi
    .service('api::ai-assistant.ai-assistant')
    .analyzeText(text, 'sentiment');

  if (analysisResult.success) {
    const sentiment = analysisResult.data.sentiment;
    const isApproved = sentiment !== 'extremely_negative';

    // Create review with moderation data
    const review = await strapi.entityService.create('api::review.review', {
      data: {
        text,
        restaurant: restaurantId,
        sentiment: sentiment,
        approved: isApproved,
        needsReview: sentiment === 'negative',
      },
    });

    return review;
  }
}
```

### 4. SEO Meta Generation

Automatically generate SEO-optimized meta tags.

```javascript
// Generate SEO meta tags for articles
async generateSEOMeta(articleId) {
  const article = await strapi.entityService.findOne(
    'api::article.article',
    articleId
  );

  // Generate meta title
  const titleResult = await strapi
    .service('api::ai-assistant.ai-assistant')
    .generateResponse(
      `Create an SEO-optimized meta title (max 60 characters) for an article about: ${article.title}`,
      { max_tokens: 100 }
    );

  // Generate meta description
  const descResult = await strapi
    .service('api::ai-assistant.ai-assistant')
    .generateResponse(
      `Create an SEO-optimized meta description (max 160 characters) for: ${article.content.substring(0, 200)}`,
      { max_tokens: 200 }
    );

  if (titleResult.success && descResult.success) {
    await strapi.entityService.update('api::article.article', articleId, {
      data: {
        metaTitle: titleResult.data.response,
        metaDescription: descResult.data.response,
      },
    });
  }
}
```

### 5. Multi-language Content Translation

Generate content in multiple languages.

```javascript
// Generate multilingual content
async createMultilingualContent(ctx) {
  const { title, content, targetLanguages } = ctx.request.body;

  const translations = {};

  for (const lang of targetLanguages) {
    const result = await strapi
      .service('api::ai-assistant.ai-assistant')
      .generateResponse(
        `Translate the following to ${lang}, maintaining the tone and style:\n\nTitle: ${title}\n\nContent: ${content}`,
        { temperature: 0.3 }
      );

    if (result.success) {
      translations[lang] = result.data.response;
    }
  }

  return translations;
}
```

### 6. Smart Search and Recommendations

Enhance search with AI-powered understanding.

```javascript
// AI-powered search
async intelligentSearch(ctx) {
  const { query } = ctx.request.query;

  // Analyze user intent
  const intentResult = await strapi
    .service('api::ai-assistant.ai-assistant')
    .analyzeText(query, 'intent');

  if (intentResult.success) {
    const intent = intentResult.data.intent;

    // Perform targeted search based on intent
    let results;
    if (intent === 'restaurant_search') {
      results = await strapi.entityService.findMany('api::restaurant.restaurant', {
        filters: {
          // Smart filters based on query
        },
      });
    }

    return results;
  }
}
```

### 7. Automated Content Categorization

Automatically categorize and tag content.

```javascript
// Auto-categorize blog posts
async categorizePost(postId) {
  const post = await strapi.entityService.findOne('api::post.post', postId);

  const analysisResult = await strapi
    .service('api::ai-assistant.ai-assistant')
    .analyzeText(
      `${post.title}\n\n${post.content}`,
      'categorization'
    );

  if (analysisResult.success) {
    const { categories, tags, topics } = analysisResult.data;

    await strapi.entityService.update('api::post.post', postId, {
      data: {
        categories,
        tags,
        topics,
      },
    });
  }
}
```

### 8. Chatbot Integration

Create an AI-powered chatbot for your website.

```javascript
// Chatbot endpoint
async chat(ctx) {
  const { message, conversationHistory } = ctx.request.body;

  // Build context from conversation history
  const context = conversationHistory
    .map(msg => `${msg.role}: ${msg.content}`)
    .join('\n');

  const prompt = `${context}\nUser: ${message}\nAssistant:`;

  const result = await strapi
    .service('api::ai-assistant.ai-assistant')
    .generateResponse(prompt, {
      temperature: 0.7,
      max_tokens: 500,
    });

  if (result.success) {
    return {
      response: result.data.response,
      timestamp: new Date(),
    };
  }
}
```

### 9. Content Quality Checker

Check and improve content quality.

```javascript
// Check content quality
async checkContentQuality(ctx) {
  const { content } = ctx.request.body;

  const qualityCheck = await strapi
    .service('api::ai-assistant.ai-assistant')
    .analyzeText(content, 'quality');

  if (qualityCheck.success) {
    const suggestions = await strapi
      .service('api::ai-assistant.ai-assistant')
      .generateResponse(
        `Improve the following content while maintaining its core message:\n\n${content}`,
        { temperature: 0.5 }
      );

    return {
      quality: qualityCheck.data,
      suggestions: suggestions.data.response,
    };
  }
}
```

### 10. Personalized Email Generation

Generate personalized emails for users.

```javascript
// Generate personalized welcome email
async generateWelcomeEmail(userId) {
  const user = await strapi.entityService.findOne(
    'plugin::users-permissions.user',
    userId,
    { populate: ['preferences', 'interests'] }
  );

  const emailResult = await strapi
    .service('api::ai-assistant.ai-assistant')
    .generateContent('email', {
      type: 'welcome',
      userName: user.username,
      userInterests: user.interests.map(i => i.name).join(', '),
      tone: 'friendly',
    });

  if (emailResult.success) {
    // Send email
    await strapi.plugins['email'].services.email.send({
      to: user.email,
      subject: 'Welcome to Our Platform!',
      html: emailResult.data.content,
    });
  }
}
```

## Frontend Integration Examples

### React Component

```jsx
import React, { useState } from 'react';
import axios from 'axios';

function AIContentGenerator() {
  const [prompt, setPrompt] = useState('');
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);

  const generateContent = async () => {
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:1337/api/ai-assistant/generate', {
        prompt,
        options: { temperature: 0.7 }
      });
      setResult(response.data.data.response);
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to generate content');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>AI Content Generator</h2>
      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Enter your prompt..."
        rows={5}
        style={{ width: '100%' }}
      />
      <button onClick={generateContent} disabled={loading}>
        {loading ? 'Generating...' : 'Generate Content'}
      </button>
      {result && (
        <div style={{ marginTop: '20px', padding: '15px', background: '#f5f5f5' }}>
          <h3>Result:</h3>
          <p>{result}</p>
        </div>
      )}
    </div>
  );
}

export default AIContentGenerator;
```

### Vue.js Component

```vue
<template>
  <div class="ai-assistant">
    <h2>AI Assistant</h2>
    <textarea
      v-model="prompt"
      placeholder="Ask me anything..."
      rows="5"
    ></textarea>
    <button @click="generateResponse" :disabled="loading">
      {{ loading ? 'Thinking...' : 'Ask AI' }}
    </button>
    <div v-if="response" class="response">
      <h3>Response:</h3>
      <p>{{ response }}</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      prompt: '',
      response: '',
      loading: false,
    };
  },
  methods: {
    async generateResponse() {
      this.loading = true;
      try {
        const { data } = await axios.post(
          'http://localhost:1337/api/ai-assistant/generate',
          { prompt: this.prompt }
        );
        this.response = data.data.response;
      } catch (error) {
        console.error('Error:', error);
        alert('Failed to get response');
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>

<style scoped>
textarea {
  width: 100%;
  margin-bottom: 10px;
}
.response {
  margin-top: 20px;
  padding: 15px;
  background: #f5f5f5;
  border-radius: 5px;
}
</style>
```

## Best Practices

1. **Error Handling**: Always check the `success` property in AI responses
2. **Rate Limiting**: Implement rate limiting to prevent API abuse
3. **Caching**: Cache frequently requested AI responses
4. **Validation**: Validate and sanitize AI-generated content before saving
5. **User Feedback**: Allow users to provide feedback on AI-generated content
6. **Fallbacks**: Have fallback content when AI generation fails
7. **Monitoring**: Monitor AI usage and costs
8. **Privacy**: Don't send sensitive user data to AI services

## Performance Optimization

```javascript
// Cache AI responses
const cachedAIResponse = async (key, generator) => {
  const cached = await strapi.cache.get(key);
  if (cached) return cached;

  const result = await generator();
  await strapi.cache.set(key, result, { ttl: 3600 }); // 1 hour
  return result;
};

// Usage
const response = await cachedAIResponse(
  `ai_description_${restaurantId}`,
  () => strapi.service('api::ai-assistant.ai-assistant')
    .generateResponse(prompt)
);
```

## Troubleshooting

- **Slow Responses**: Consider implementing background jobs for AI operations
- **API Limits**: Monitor your API usage and implement request queuing
- **Quality Issues**: Adjust temperature and max_tokens parameters
- **Context Length**: Break long content into smaller chunks

For more examples and documentation, visit the [AI Integration README](./AI_INTEGRATION_README.md).
