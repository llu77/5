/**
 * Custom Strapi server entry point
 * This file allows you to start Strapi programmatically with custom configuration
 */

const strapi = require('@strapi/strapi');

/**
 * Start Strapi with custom configuration
 */
async function startStrapi() {
  try {
    console.log('🚀 Starting Strapi server...');
    console.log('📦 Environment:', process.env.NODE_ENV || 'development');
    console.log('🔑 AI Integration:', process.env.STRAPI_AI_API_KEY ? '✓ Configured' : '✗ Not configured');

    // Create and start Strapi instance
    const app = await strapi.createStrapi({
      // Custom configuration can be added here
      distDir: './dist',
      autoReload: process.env.NODE_ENV !== 'production',
      serveAdminPanel: true,
    }).start();

    console.log('');
    console.log('✅ Strapi server started successfully!');
    console.log('');
    console.log('📍 Server running at:');
    console.log(`   - API: http://${process.env.HOST || 'localhost'}:${process.env.PORT || 1337}/api`);
    console.log(`   - Admin: http://${process.env.HOST || 'localhost'}:${process.env.PORT || 1337}/admin`);
    console.log('');
    console.log('🤖 AI Assistant endpoints:');
    console.log(`   - Health: GET http://${process.env.HOST || 'localhost'}:${process.env.PORT || 1337}/api/ai-assistant/health`);
    console.log(`   - Generate: POST http://${process.env.HOST || 'localhost'}:${process.env.PORT || 1337}/api/ai-assistant/generate`);
    console.log(`   - Content: POST http://${process.env.HOST || 'localhost'}:${process.env.PORT || 1337}/api/ai-assistant/content`);
    console.log(`   - Analyze: POST http://${process.env.HOST || 'localhost'}:${process.env.PORT || 1337}/api/ai-assistant/analyze`);
    console.log('');
    console.log('Press CTRL+C to stop');

    return app;
  } catch (error) {
    console.error('❌ Error starting Strapi:', error);
    process.exit(1);
  }
}

// Handle graceful shutdown
process.on('SIGINT', async () => {
  console.log('\n\n🛑 Shutting down Strapi server...');
  process.exit(0);
});

process.on('SIGTERM', async () => {
  console.log('\n\n🛑 Shutting down Strapi server...');
  process.exit(0);
});

// Handle uncaught errors
process.on('uncaughtException', (error) => {
  console.error('❌ Uncaught Exception:', error);
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('❌ Unhandled Rejection at:', promise, 'reason:', reason);
  process.exit(1);
});

// Start the server
startStrapi();
