# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Strapi v5.30.1 headless CMS server application built with TypeScript, featuring integrated AI capabilities through Strapi AI. It provides a backend API for content management with AI-powered content generation, analysis, and enhancement features.

## Architecture

### Core Structure

- **Config Layer** (`config/`): Database, middleware, admin, and server configuration
- **Application Layer** (`src/`): Main application entry point and lifecycle hooks
- **API Layer** (`src/api/`): Content types, controllers, routes, and services
  - **AI Assistant** (`src/api/ai-assistant/`): AI integration endpoints and services
- **Admin Layer** (`src/admin/`): Admin panel customizations
- **Extensions** (`src/extensions/`): Plugin extensions and customizations

### Key Configuration Files

- `config/database.ts`: Database configuration (currently SQLite with better-sqlite3)
- `config/server.ts`: Server configuration and port settings
- `config/middlewares.ts`: Middleware stack configuration
- `src/index.ts`: Application lifecycle hooks (register/bootstrap)
- `.env`: Environment variables including Strapi AI API key

## Development Commands

### Core Development

```bash
npm run develop       # Start development server with auto-reload
npm run dev          # Alias for develop
npm run start        # Start production server
npm run start:custom # Start with custom server.js entry point
npm run build        # Build admin panel
```

### AI Integration

```bash
npm run test:ai      # Test AI integration endpoints
```

### Strapi CLI

```bash
npm run strapi       # Access Strapi CLI directly
npm run console      # Open Strapi console
npm run deploy       # Deploy to Strapi Cloud
```

### Maintenance

```bash
npm run upgrade        # Upgrade to latest Strapi version
npm run upgrade:dry    # Preview upgrade changes
```

## Environment Configuration

The application uses environment variables defined in `.env`:

### Server Configuration
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 1337)

### Security Keys
- `APP_KEYS`: Application encryption keys
- `API_TOKEN_SALT`: API token salt
- `ADMIN_JWT_SECRET`: Admin JWT secret
- `TRANSFER_TOKEN_SALT`: Transfer token salt
- `ENCRYPTION_KEY`: Encryption key

### Database Configuration
- `DATABASE_CLIENT`: Database type (sqlite)
- `DATABASE_FILENAME`: SQLite database file path

### AI Configuration
- `STRAPI_AI_API_KEY`: Strapi AI API key (required for AI features)

Copy `.env.example` to `.env` and update values for local development.

## AI Integration

### AI Assistant API Endpoints

The application includes a complete AI integration located at `src/api/ai-assistant/`:

#### Available Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/ai-assistant/health` | GET | Check AI integration status |
| `/api/ai-assistant/generate` | POST | Generate AI responses from prompts |
| `/api/ai-assistant/content` | POST | Generate specific content types |
| `/api/ai-assistant/analyze` | POST | Analyze text (sentiment, keywords, etc.) |

#### Service Methods

The AI service (`src/api/ai-assistant/services/ai-assistant.ts`) provides:

- `generateResponse(prompt, options)`: Generate AI responses
- `generateContent(contentType, context)`: Generate specific content types
- `analyzeText(text, analysisType)`: Analyze text for various purposes

#### Usage Examples

```typescript
// In a controller or service
const aiService = strapi.service('api::ai-assistant.ai-assistant');

// Generate content
const result = await aiService.generateResponse(
  'Write a product description',
  { temperature: 0.7, max_tokens: 300 }
);

// Generate specific content
const content = await aiService.generateContent('blog-post', {
  topic: 'Strapi CMS',
  tone: 'professional'
});

// Analyze text
const analysis = await aiService.analyzeText(
  'Text to analyze',
  'sentiment'
);
```

### AI Integration Documentation

For detailed AI integration documentation, see:
- `AI_INTEGRATION_README.md`: Complete API documentation
- `USAGE_EXAMPLES.md`: 10+ practical use cases
- `QUICK_START.md`: Quick start guide
- `test-ai-integration.js`: Test suite

## TypeScript Configuration

- **Target**: ES2019 with CommonJS modules
- **Strict Mode**: Disabled (Strapi compatibility)
- **Output**: `dist/` directory
- **Excludes**: Admin files, tests, and plugins from server compilation

## Content Type Development

When creating new content types, they will be automatically scaffolded in:

- `src/api/[content-type]/controllers/`
- `src/api/[content-type]/routes/`
- `src/api/[content-type]/services/`
- `src/api/[content-type]/content-types/`

Use the Strapi admin panel or CLI to generate content types rather than creating them manually.

### Integrating AI with Content Types

You can integrate AI features into custom content types:

```typescript
// In a custom controller
async create(ctx) {
  const { title, description } = ctx.request.body;

  // Enhance description with AI
  const aiService = strapi.service('api::ai-assistant.ai-assistant');
  const enhanced = await aiService.generateContent('description', {
    original: description,
    style: 'engaging'
  });

  // Create entry with enhanced content
  const entry = await strapi.entityService.create('api::article.article', {
    data: {
      title,
      description: enhanced.data.content
    }
  });

  return entry;
}
```

## CRON Jobs

### Enabling CRON

Enable CRON in `config/server.ts`:

```typescript
export default ({ env }) => ({
  host: env('HOST', '0.0.0.0'),
  port: env.int('PORT', 1337),
  cron: {
    enabled: true,
  },
});
```

### Creating CRON Tasks

Create `config/cron-tasks.ts`:

```typescript
export default {
  // AI-powered daily content summary
  dailyAISummary: {
    task: async ({ strapi }) => {
      const aiService = strapi.service('api::ai-assistant.ai-assistant');
      const articles = await strapi.entityService.findMany('api::article.article', {
        limit: 10,
        sort: 'createdAt:desc'
      });

      // Generate summary with AI
      const summary = await aiService.generateContent('summary', {
        articles: articles.map(a => a.title)
      });

      console.log('Daily summary:', summary.data);
    },
    options: {
      rule: '0 9 * * *', // Every day at 9 AM
      tz: 'UTC',
    },
  },

  // Health check
  healthCheck: {
    task: ({ strapi }) => {
      console.log('Health check completed');
    },
    options: {
      rule: '*/30 * * * *', // Every 30 minutes
    },
  },
};
```

### CRON Schedule Format

```
* * * * *
│ │ │ │ │
│ │ │ │ └─── day of week (0-7)
│ │ │ └───── month (1-12)
│ │ └─────── day of month (1-31)
│ └───────── hour (0-23)
└─────────── minute (0-59)
```

## Admin Panel

Access the admin panel at `http://localhost:1337/admin` when running in development mode. Admin customizations go in `src/admin/`.

## Custom Server Entry Point

The project includes a custom server entry point (`server.js`) that provides:

- Enhanced logging and startup information
- AI integration status display
- Graceful shutdown handling
- Error handling

Use it with: `npm run start:custom`

## Testing

### AI Integration Tests

Run the AI integration test suite:

```bash
# Start the server first
npm run develop

# In another terminal
npm run test:ai
```

The test suite checks all AI endpoints and provides detailed output.

## Best Practices

### AI Integration

1. **Error Handling**: Always check the `success` property in AI responses
2. **Rate Limiting**: Implement rate limiting for AI endpoints
3. **Caching**: Cache frequently requested AI responses
4. **Validation**: Validate and sanitize AI-generated content
5. **Monitoring**: Monitor AI usage and API limits

### Content Development

1. Use the Strapi CLI or admin panel to generate content types
2. Keep business logic in services, not controllers
3. Use TypeScript types for better type safety
4. Document custom endpoints and services

### Security

1. Never commit `.env` file to version control
2. Add authentication middleware to sensitive endpoints
3. Implement proper RBAC for AI features
4. Validate all user inputs

## Project Structure

```
strapi-ai-project/
├── .env                              # Environment variables (not in git)
├── .env.example                      # Example environment file
├── config/                           # Configuration files
│   ├── admin.ts
│   ├── api.ts
│   ├── database.ts
│   ├── middlewares.ts
│   ├── plugins.ts
│   └── server.ts
├── src/
│   ├── admin/                        # Admin customizations
│   ├── api/
│   │   └── ai-assistant/             # AI integration
│   │       ├── controllers/
│   │       ├── routes/
│   │       └── services/
│   ├── extensions/                   # Plugin extensions
│   └── index.ts                      # App lifecycle hooks
├── server.js                         # Custom server entry point
├── test-ai-integration.js            # AI test suite
├── AI_INTEGRATION_README.md          # AI documentation
├── USAGE_EXAMPLES.md                 # AI usage examples
├── QUICK_START.md                    # Quick start guide
└── package.json
```

## Strapi Documentation Reference

When answering questions about Strapi features, architecture, or best practices, reference the official Strapi v5 documentation:

### Core Documentation Areas

- **Installation & Setup**: `https://docs.strapi.io/cms/installation`, `https://docs.strapi.io/cms/quick-start`
- **Project Structure**: `https://docs.strapi.io/cms/project-structure`
- **Configuration**: `https://docs.strapi.io/cms/configurations/database`, `https://docs.strapi.io/cms/configurations/server`, `https://docs.strapi.io/cms/configurations/environment`
- **Backend Customization**: `https://docs.strapi.io/cms/backend-customization/controllers`, `https://docs.strapi.io/cms/backend-customization/services`, `https://docs.strapi.io/cms/backend-customization/routes`, `https://docs.strapi.io/cms/backend-customization/policies`, `https://docs.strapi.io/cms/backend-customization/middlewares`
- **Content API**: `https://docs.strapi.io/cms/api/content-api`, `https://docs.strapi.io/cms/api/rest`, `https://docs.strapi.io/cms/api/document-service`
- **Admin Panel**: `https://docs.strapi.io/cms/admin-panel-customization`, `https://docs.strapi.io/cms/features/admin-panel`
- **Content Management**: `https://docs.strapi.io/cms/features/content-manager`, `https://docs.strapi.io/cms/features/content-type-builder`
- **Plugin Development**: `https://docs.strapi.io/cms/plugins-development/developing-plugins`, `https://docs.strapi.io/cms/plugins-development/create-a-plugin`

### Key Features Documentation

- **Draft & Publish**: `https://docs.strapi.io/cms/features/draft-and-publish`
- **Internationalization**: `https://docs.strapi.io/cms/features/internationalization`
- **Role-Based Access Control**: `https://docs.strapi.io/cms/features/rbac`
- **Users & Permissions**: `https://docs.strapi.io/cms/features/users-permissions`
- **API Tokens**: `https://docs.strapi.io/cms/features/api-tokens`
- **Media Library**: `https://docs.strapi.io/cms/features/media-library`
- **Custom Fields**: `https://docs.strapi.io/cms/features/custom-fields`
- **Review Workflows**: `https://docs.strapi.io/cms/features/review-workflows`
- **Releases**: `https://docs.strapi.io/cms/features/releases`
- **Content History**: `https://docs.strapi.io/cms/features/content-history`
- **Audit Logs**: `https://docs.strapi.io/cms/features/audit-logs`

### Cloud & Deployment

- **Strapi Cloud**: `https://docs.strapi.io/cloud/getting-started/intro`, `https://docs.strapi.io/cloud/projects/overview`
- **Deployment**: `https://docs.strapi.io/cms/deployment`, `https://docs.strapi.io/cloud/getting-started/deployment`
- **CLI**: `https://docs.strapi.io/cms/cli`, `https://docs.strapi.io/cloud/cli/cloud-cli`

### Development Topics

- **TypeScript**: `https://docs.strapi.io/cms/typescript`, `https://docs.strapi.io/cms/typescript/development`
- **Testing**: `https://docs.strapi.io/cms/testing`
- **Database**: `https://docs.strapi.io/cms/configurations/database`, `https://docs.strapi.io/cms/database-migrations`
- **Error Handling**: `https://docs.strapi.io/cms/error-handling`
- **Webhooks**: `https://docs.strapi.io/cms/backend-customization/webhooks`
- **CRON Jobs**: `https://docs.strapi.io/cms/configurations/cron`

Use WebFetch tool to access specific documentation pages when providing detailed answers about Strapi features or best practices.

## Additional Resources

- [Strapi Documentation](https://docs.strapi.io)
- [Strapi AI Features](https://strapi.io/ai)
- [Strapi Community](https://forum.strapi.io)
- Project documentation files for AI integration details
