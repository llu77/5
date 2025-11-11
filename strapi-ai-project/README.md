# Strapi AI Project 🚀

> A complete Strapi v5 CMS with AI integration, flexible component system, and cloud transfer capabilities.

[![Strapi Version](https://img.shields.io/badge/Strapi-v5.30.1-blue.svg)](https://strapi.io)
[![Node Version](https://img.shields.io/badge/Node-18%20%7C%2020%20%7C%2022-green.svg)](https://nodejs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue.svg)](https://www.typescriptlang.org)

## ✨ Features

- 🤖 **AI Integration**: Strapi AI for content generation, analysis, and enhancement
- 🧩 **Component System**: 10 pre-built components (global, shared, sections)
- 📄 **Page Builder**: Dynamic zones for flexible page construction
- 🗂️ **Hierarchical Categories**: Nested navigation with parent/child relationships
- ☁️ **Cloud Transfer**: Easy data migration to Strapi Cloud
- 🎨 **Responsive Design**: Mobile-first, accessibility-compliant components
- 🔒 **TypeScript**: Full TypeScript support
- 📦 **Draft & Publish**: Content workflow management

## 🚀 Quick Start

### Prerequisites

- Node.js (v18, v20, or v22)
- npm or yarn

### Installation

```bash
# Navigate to project
cd strapi-ai-project

# Install dependencies (if not already installed)
npm install

# Copy environment variables
cp .env.example .env

# Edit .env and add your Strapi AI API key
# STRAPI_AI_API_KEY=your-key-here

# Build the project
npm run build

# Start development server
npm run develop
```

### First Run

1. Open http://localhost:1337/admin
2. Create your first admin user
3. Start building content!

## 📚 Documentation

- **[Quick Start Guide](./QUICK_START.md)** - Get up and running in 5 minutes
- **[Project Summary](./PROJECT_SUMMARY.md)** - Complete feature overview
- **[AI Integration](./AI_INTEGRATION_README.md)** - AI API documentation
- **[Usage Examples](./USAGE_EXAMPLES.md)** - 10+ practical AI examples
- **[Component System](./COMPONENT_SYSTEM_DOCS.md)** - Component specifications
- **[Cloud Transfer](./STRAPI_CLOUD_TRANSFER.md)** - Deploy to Strapi Cloud
- **[CLAUDE.md](./CLAUDE.md)** - AI assistant guidelines

## 🎯 Available Scripts

### Development

```bash
npm run develop        # Start with auto-reload (recommended)
npm run dev           # Alias for develop
npm run start:custom  # Start with custom server and enhanced logging
```

### Production

```bash
npm run build         # Build admin panel and compile TypeScript
npm run start         # Start production server
NODE_ENV=production npm run build  # Production build
```

### Testing

```bash
npm run test:ai       # Test AI integration (server must be running)
```

### Data Management

```bash
npm run transfer           # Interactive data transfer
npm run transfer:push      # Push local data to cloud
npm run transfer:pull      # Pull cloud data to local
npm run transfer:cloud     # Guided transfer helper script

npm run export            # Export data
npm run import            # Import data
npm run backup            # Create timestamped backup
```

### Utilities

```bash
npm run console           # Open Strapi console
npm run strapi            # Access Strapi CLI
npm run deploy            # Deploy to Strapi Cloud
```

## 🏗️ Project Structure

```
strapi-ai-project/
├── config/                    # Strapi configuration
│   ├── admin.ts              # Admin panel config
│   ├── api.ts                # API config
│   ├── database.ts           # Database config
│   ├── middlewares.ts        # Middleware stack
│   ├── plugins.ts            # Plugin config
│   └── server.ts             # Server config
├── src/
│   ├── api/
│   │   ├── ai-assistant/     # AI integration
│   │   │   ├── controllers/  # Request handlers
│   │   │   ├── routes/       # API routes
│   │   │   └── services/     # Business logic
│   │   ├── page/             # Page content type
│   │   └── category/         # Category content type
│   ├── components/
│   │   ├── global/           # Site-wide components
│   │   │   ├── header.json
│   │   │   ├── footer.json
│   │   │   └── seo.json
│   │   ├── shared/           # Reusable components
│   │   │   ├── link.json
│   │   │   ├── button.json
│   │   │   └── address.json
│   │   └── sections/         # Dynamic zone sections
│   │       ├── hero-section.json
│   │       ├── feature-grid.json
│   │       ├── testimonial.json
│   │       └── faq-block.json
│   ├── admin/                # Admin customizations
│   ├── extensions/           # Plugin extensions
│   └── index.ts              # App lifecycle hooks
├── scripts/
│   └── transfer-to-cloud.sh # Cloud transfer helper
├── .env                      # Environment variables (not in git)
├── .env.example             # Environment template
├── server.js                # Custom server entry point
├── test-ai-integration.js   # AI test suite
└── package.json             # Dependencies and scripts
```

## 🤖 AI Integration

### Available Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/ai-assistant/health` | GET | Check AI status |
| `/api/ai-assistant/generate` | POST | Generate AI responses |
| `/api/ai-assistant/content` | POST | Generate specific content |
| `/api/ai-assistant/analyze` | POST | Analyze text |

### Quick Example

```bash
# Check AI status
curl http://localhost:1337/api/ai-assistant/health

# Generate content
curl -X POST http://localhost:1337/api/ai-assistant/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Write a welcome message for a restaurant"}'
```

See [AI_INTEGRATION_README.md](./AI_INTEGRATION_README.md) for complete API documentation.

## 🧩 Component System

### Global Components
- **Header** - Site navigation with logo, links, and CTA
- **Footer** - Site footer with social links and sitemap
- **SEO** - Meta tags and Open Graph data

### Shared Components
- **Link** - Reusable links with icons
- **Button** - 3 styles × 3 sizes
- **Address** - Physical address component

### Dynamic Zone Sections
- **Hero Section** - Full-width hero with image and CTAs
- **Feature Grid** - Grid/list/carousel of features
- **Testimonial** - Customer reviews with ratings
- **FAQ Block** - Accordion/grid/list Q&A

See [COMPONENT_SYSTEM_DOCS.md](./COMPONENT_SYSTEM_DOCS.md) for complete specifications.

## ☁️ Deploying to Strapi Cloud

### Quick Deploy

```bash
# Interactive mode
npm run transfer:cloud

# Or direct push (after configuring .env)
npm run transfer:push
```

### Configuration

Add to your `.env`:

```env
STRAPI_TRANSFER_URL=https://your-project.strapiapp.com/admin
STRAPI_TRANSFER_TOKEN=your-transfer-token-here
```

See [STRAPI_CLOUD_TRANSFER.md](./STRAPI_CLOUD_TRANSFER.md) for detailed deployment guide.

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Server
HOST=0.0.0.0
PORT=1337

# AI Integration (Required)
STRAPI_AI_API_KEY=your-strapi-ai-api-key

# Cloud Transfer (Optional)
STRAPI_TRANSFER_URL=https://your-project.strapiapp.com/admin
STRAPI_TRANSFER_TOKEN=your-transfer-token

# Database (default: SQLite)
DATABASE_CLIENT=sqlite
DATABASE_FILENAME=.tmp/data.db
```

### Database Options

**Development** (default):
- SQLite (included)

**Production** (recommended):
- PostgreSQL
- MySQL
- MariaDB

Update `config/database.ts` and environment variables for production databases.

## 📖 API Documentation

### Content API

Auto-generated REST API for all content types:

```bash
# Pages
GET    /api/pages
GET    /api/pages/:id
POST   /api/pages
PUT    /api/pages/:id
DELETE /api/pages/:id

# Categories
GET    /api/categories
GET    /api/categories/:id
POST   /api/categories
PUT    /api/categories/:id
DELETE /api/categories/:id
```

### AI API

```bash
# Health check
GET /api/ai-assistant/health

# Generate AI response
POST /api/ai-assistant/generate
Body: { "prompt": "your prompt", "options": {...} }

# Generate content
POST /api/ai-assistant/content
Body: { "contentType": "article", "context": {...} }

# Analyze text
POST /api/ai-assistant/analyze
Body: { "text": "text to analyze", "analysisType": "sentiment" }
```

## 🛠️ Customization

### Adding Content Types

1. Use Content-Type Builder in admin panel
2. Or create schema in `src/api/[name]/content-types/`
3. Restart server

### Adding Components

1. Create JSON file in `src/components/[category]/`
2. Define fields and attributes
3. Restart server
4. Add to dynamic zones if needed

### Integrating AI

```javascript
// In any controller or service
const aiService = strapi.service('api::ai-assistant.ai-assistant');

const result = await aiService.generateResponse(
  'Your prompt here',
  { temperature: 0.7, max_tokens: 300 }
);

if (result.success) {
  console.log(result.data);
}
```

## 🧪 Testing

### AI Integration Tests

```bash
# Start server
npm run develop

# In another terminal
npm run test:ai
```

### Manual API Testing

```bash
# Test with curl
curl http://localhost:1337/api/ai-assistant/health

# Or use Postman, Insomnia, etc.
```

## 🐛 Troubleshooting

### Server won't start
- Check `.env` file exists
- Verify Node.js version (18-22)
- Run `npm install`

### AI endpoints not working
- Verify `STRAPI_AI_API_KEY` in `.env`
- Check internet connection
- Test health endpoint first

### Components not showing
- Restart server after adding components
- Check JSON syntax
- Verify component names in schemas

### Transfer fails
- Check Strapi Cloud is running
- Verify transfer token is valid
- Ensure URL includes `/admin`

See [STRAPI_CLOUD_TRANSFER.md](./STRAPI_CLOUD_TRANSFER.md) for transfer troubleshooting.

## 📊 Project Stats

- **Strapi Version**: 5.30.1
- **Components**: 10
- **Content Types**: 2 (+ built-in types)
- **AI Endpoints**: 4
- **Documentation Files**: 7
- **Dependencies**: 1,442 packages

## 🎓 Learning Resources

### Official Documentation
- [Strapi Documentation](https://docs.strapi.io)
- [Strapi AI Features](https://strapi.io/ai)
- [Strapi Cloud](https://cloud.strapi.io)
- [Strapi CLI](https://docs.strapi.io/dev-docs/cli)

### Community
- [Discord](https://discord.strapi.io) - Chat with the community
- [Forum](https://forum.strapi.io) - Ask questions and share projects
- [GitHub](https://github.com/strapi/strapi) - Source code and issues

### This Project
- Start with [QUICK_START.md](./QUICK_START.md)
- Read [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md) for overview
- Check [AI_INTEGRATION_README.md](./AI_INTEGRATION_README.md) for AI docs
- Review [USAGE_EXAMPLES.md](./USAGE_EXAMPLES.md) for examples

## 🤝 Contributing

This project uses:
- TypeScript for type safety
- ESLint for code quality
- Prettier for code formatting

## 📝 License

This project is based on Strapi, which is licensed under the MIT License.

## 🙏 Acknowledgments

- Built with [Strapi](https://strapi.io)
- Powered by [Strapi AI](https://strapi.io/ai)
- Hosted on [Strapi Cloud](https://cloud.strapi.io)

## 📞 Support

- Check documentation files in this repo
- Visit [Strapi Forum](https://forum.strapi.io)
- Join [Discord Community](https://discord.strapi.io)
- Read [Official Docs](https://docs.strapi.io)

---

**Ready to build?** Start with:

```bash
npm run develop
```

Then visit http://localhost:1337/admin to create your first admin user!

🎉 Happy building with Strapi AI!
