#!/bin/bash
# Secure API Key Setup Script
# This script safely stores your API keys as Cloudflare secrets

set -e  # Exit on error

echo "🔐 Setting up API Keys securely in Cloudflare..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if wrangler is installed
if ! command -v wrangler &> /dev/null; then
    echo -e "${RED}❌ Error: wrangler CLI is not installed${NC}"
    echo "Install it with: npm install -g wrangler"
    exit 1
fi

echo -e "${GREEN}✓ Wrangler CLI found${NC}"
echo ""

# Check if user is logged in
if ! wrangler whoami &> /dev/null; then
    echo -e "${YELLOW}⚠️  Not logged in to Cloudflare${NC}"
    echo "Logging in..."
    wrangler login
fi

echo -e "${GREEN}✓ Authenticated with Cloudflare${NC}"
echo ""

# Display security warning
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}⚠️  SECURITY BEST PRACTICES${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "This script will store your API keys as Cloudflare secrets."
echo ""
echo "Best practices:"
echo "  ✓ Secrets are encrypted and never exposed in code"
echo "  ✓ Different keys for development vs production"
echo "  ✓ Regular key rotation (every 90 days recommended)"
echo "  ✓ Never commit keys to git repositories"
echo "  ✓ Use separate keys per environment"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Function to store a secret
store_secret() {
    local secret_name=$1
    local secret_value=$2
    local env=$3

    if [ -z "$env" ]; then
        echo -e "${YELLOW}Storing ${secret_name} for production...${NC}"
        echo "$secret_value" | wrangler secret put "$secret_name"
    else
        echo -e "${YELLOW}Storing ${secret_name} for ${env} environment...${NC}"
        echo "$secret_value" | wrangler secret put "$secret_name" --env "$env"
    fi

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Successfully stored ${secret_name}${NC}"
        echo ""
    else
        echo -e "${RED}❌ Failed to store ${secret_name}${NC}"
        echo ""
    fi
}

# Your provided API keys
API_KEY_1="sk-RbQ0xi7yOFho0jTsCgMK9CA6uDtHbe6OkWZvyihtwAXU2p3Q"
API_KEY_2="bt-st-F1NAIK0bQ1KBkGc49h2JjtTYVB1AAxp59Ny1KHo150bSjAzn"

echo "The following API keys will be stored:"
echo "  1. ANTHROPIC_API_KEY_1: ${API_KEY_1:0:10}...${API_KEY_1: -10}"
echo "  2. ANTHROPIC_API_KEY_2: ${API_KEY_2:0:10}...${API_KEY_2: -10}"
echo ""

read -p "Do you want to proceed with storing these keys? (y/n) " -n 1 -r
echo
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

# Store API keys for production
echo -e "${BLUE}━━━ Storing Production Secrets ━━━${NC}"
echo ""
store_secret "ANTHROPIC_API_KEY_1" "$API_KEY_1"
store_secret "ANTHROPIC_API_KEY_2" "$API_KEY_2"

# Ask if user wants to set up development environment
read -p "Do you want to set up development environment secrets? (y/n) " -n 1 -r
echo
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}━━━ Storing Development Secrets ━━━${NC}"
    echo ""
    echo "It's recommended to use different (test) API keys for development."
    read -p "Use the same keys for development? (y/n) " -n 1 -r
    echo
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        store_secret "ANTHROPIC_API_KEY_1" "$API_KEY_1" "dev"
        store_secret "ANTHROPIC_API_KEY_2" "$API_KEY_2" "dev"
    else
        echo "Please enter your development API keys:"
        read -p "Development API Key 1: " DEV_KEY_1
        read -p "Development API Key 2: " DEV_KEY_2
        echo ""
        store_secret "ANTHROPIC_API_KEY_1" "$DEV_KEY_1" "dev"
        store_secret "ANTHROPIC_API_KEY_2" "$DEV_KEY_2" "dev"
    fi
fi

# Ask if user wants to set up staging environment
read -p "Do you want to set up staging environment secrets? (y/n) " -n 1 -r
echo
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}━━━ Storing Staging Secrets ━━━${NC}"
    echo ""
    store_secret "ANTHROPIC_API_KEY_1" "$API_KEY_1" "staging"
    store_secret "ANTHROPIC_API_KEY_2" "$API_KEY_2" "staging"
fi

echo ""
echo -e "${GREEN}✅ API Key setup complete!${NC}"
echo ""
echo "Your API keys are now securely stored as Cloudflare secrets."
echo ""
echo "To access them in your code:"
echo ""
echo -e "${YELLOW}// In your Worker/Pages Function:${NC}"
echo "export async function onRequest(context) {"
echo "  const apiKey1 = context.env.ANTHROPIC_API_KEY_1;"
echo "  const apiKey2 = context.env.ANTHROPIC_API_KEY_2;"
echo "  // Use the keys..."
echo "}"
echo ""
echo "To update a secret later:"
echo "  wrangler secret put ANTHROPIC_API_KEY_1"
echo ""
echo "To list all secrets:"
echo "  wrangler secret list"
echo ""
echo "To delete a secret:"
echo "  wrangler secret delete ANTHROPIC_API_KEY_1"
echo ""
echo -e "${YELLOW}⚠️  Remember to rotate your keys regularly!${NC}"
echo ""
