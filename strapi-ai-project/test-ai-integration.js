/**
 * Test script for Strapi AI Integration
 * Run this after starting the Strapi server with `npm run develop`
 */

const axios = require('axios');

const BASE_URL = 'http://localhost:1337/api';

// Color codes for console output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
};

const log = {
  success: (msg) => console.log(`${colors.green}✓${colors.reset} ${msg}`),
  error: (msg) => console.log(`${colors.red}✗${colors.reset} ${msg}`),
  info: (msg) => console.log(`${colors.blue}ℹ${colors.reset} ${msg}`),
  warning: (msg) => console.log(`${colors.yellow}⚠${colors.reset} ${msg}`),
  header: (msg) => console.log(`\n${colors.bright}${msg}${colors.reset}\n`),
};

async function testHealthCheck() {
  log.header('Testing Health Check Endpoint');
  try {
    const response = await axios.get(`${BASE_URL}/ai-assistant/health`);
    log.success('Health check successful');
    console.log('Response:', JSON.stringify(response.data, null, 2));
    return true;
  } catch (error) {
    log.error(`Health check failed: ${error.message}`);
    if (error.response) {
      console.log('Response data:', error.response.data);
    }
    return false;
  }
}

async function testGenerateResponse() {
  log.header('Testing AI Response Generation');
  try {
    const response = await axios.post(`${BASE_URL}/ai-assistant/generate`, {
      prompt: 'Write a short welcome message for a modern restaurant website',
      options: {
        temperature: 0.7,
        max_tokens: 200,
      },
    });
    log.success('AI response generation successful');
    console.log('Response:', JSON.stringify(response.data, null, 2));
    return true;
  } catch (error) {
    log.error(`AI response generation failed: ${error.message}`);
    if (error.response) {
      console.log('Response data:', error.response.data);
    }
    return false;
  }
}

async function testContentGeneration() {
  log.header('Testing Content Generation');
  try {
    const response = await axios.post(`${BASE_URL}/ai-assistant/content`, {
      contentType: 'blog-post',
      context: {
        topic: 'Benefits of using Strapi CMS',
        tone: 'professional',
        length: 'short',
      },
    });
    log.success('Content generation successful');
    console.log('Response:', JSON.stringify(response.data, null, 2));
    return true;
  } catch (error) {
    log.error(`Content generation failed: ${error.message}`);
    if (error.response) {
      console.log('Response data:', error.response.data);
    }
    return false;
  }
}

async function testTextAnalysis() {
  log.header('Testing Text Analysis');
  try {
    const response = await axios.post(`${BASE_URL}/ai-assistant/analyze`, {
      text: 'This restaurant serves absolutely delicious food! The atmosphere is wonderful and the service is exceptional.',
      analysisType: 'sentiment',
    });
    log.success('Text analysis successful');
    console.log('Response:', JSON.stringify(response.data, null, 2));
    return true;
  } catch (error) {
    log.error(`Text analysis failed: ${error.message}`);
    if (error.response) {
      console.log('Response data:', error.response.data);
    }
    return false;
  }
}

async function runAllTests() {
  console.log(`
${colors.bright}╔════════════════════════════════════════════╗
║   Strapi AI Integration Test Suite        ║
╚════════════════════════════════════════════╝${colors.reset}
  `);

  log.info('Starting tests...');
  log.warning('Make sure Strapi is running on http://localhost:1337\n');

  const results = {
    healthCheck: await testHealthCheck(),
    generateResponse: await testGenerateResponse(),
    contentGeneration: await testContentGeneration(),
    textAnalysis: await testTextAnalysis(),
  };

  // Summary
  log.header('Test Summary');
  const passed = Object.values(results).filter((r) => r).length;
  const total = Object.keys(results).length;

  Object.entries(results).forEach(([test, result]) => {
    if (result) {
      log.success(`${test}: PASSED`);
    } else {
      log.error(`${test}: FAILED`);
    }
  });

  console.log(`\n${colors.bright}Total: ${passed}/${total} tests passed${colors.reset}\n`);

  if (passed === total) {
    log.success('All tests passed! 🎉');
  } else {
    log.warning(`${total - passed} test(s) failed. Please check the errors above.`);
  }
}

// Run tests
runAllTests().catch((error) => {
  log.error(`Test suite failed: ${error.message}`);
  process.exit(1);
});
