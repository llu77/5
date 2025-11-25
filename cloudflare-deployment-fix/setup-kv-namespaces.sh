#!/bin/bash
# KV Namespace Setup Script
# This script creates the required KV namespaces for your Cloudflare deployment

set -e  # Exit on error

echo "🚀 Setting up Cloudflare KV Namespaces..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
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

# Function to create KV namespace
create_kv_namespace() {
    local name=$1
    local description=$2

    echo -e "${YELLOW}Creating KV namespace: ${name}${NC}"

    # Create production namespace
    echo "Creating production namespace..."
    PROD_OUTPUT=$(wrangler kv:namespace create "$name")
    PROD_ID=$(echo "$PROD_OUTPUT" | grep -oP 'id = "\K[^"]+' || echo "")

    # Create preview namespace
    echo "Creating preview namespace..."
    PREVIEW_OUTPUT=$(wrangler kv:namespace create "${name}_preview")
    PREVIEW_ID=$(echo "$PREVIEW_OUTPUT" | grep -oP 'id = "\K[^"]+' || echo "")

    if [ -n "$PROD_ID" ] && [ -n "$PREVIEW_ID" ]; then
        echo -e "${GREEN}✓ Created namespace: ${name}${NC}"
        echo "  Production ID: $PROD_ID"
        echo "  Preview ID: $PREVIEW_ID"
        echo ""
        echo "Add this to your wrangler.toml:"
        echo "[[kv_namespaces]]"
        echo "binding = \"$(echo $name | tr '[:lower:]' '[:upper:]')\""
        echo "id = \"$PROD_ID\""
        echo "preview_id = \"$PREVIEW_ID\""
        echo ""
    else
        echo -e "${RED}❌ Failed to create namespace: ${name}${NC}"
    fi
}

# Create required namespaces
echo "Creating KV namespaces..."
echo ""

# Main cache namespace (this is the one causing your deployment error)
create_kv_namespace "cache" "General purpose cache for application data"

# Optional: API keys namespace (for storing API keys securely in KV)
read -p "Do you want to create an API_KEYS namespace? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    create_kv_namespace "api_keys" "Secure storage for API keys"
fi

# Optional: Sessions namespace
read -p "Do you want to create a SESSIONS namespace? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    create_kv_namespace "sessions" "User session storage"
fi

# Optional: Config namespace
read -p "Do you want to create a CONFIG namespace? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    create_kv_namespace "config" "Application configuration storage"
fi

echo ""
echo -e "${GREEN}✅ KV Namespace setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Update your wrangler.toml with the namespace IDs shown above"
echo "2. Run './setup-api-keys.sh' to securely store your API keys"
echo "3. Deploy your application with: wrangler pages deploy"
echo ""
