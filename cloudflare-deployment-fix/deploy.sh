#!/bin/bash
# Complete Deployment Script
# Sets up KV namespaces, secrets, and deploys the application

set -e  # Exit on error

echo "🚀 Starting Full-Stack Cloudflare Pages Deployment..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Step counter
STEP=1
TOTAL_STEPS=7

print_step() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}Step $STEP/$TOTAL_STEPS: $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    STEP=$((STEP + 1))
}

# Check prerequisites
print_step "Checking Prerequisites"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Node.js $(node --version)${NC}"

# Check npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ npm $(npm --version)${NC}"

# Check wrangler
if ! command -v wrangler &> /dev/null; then
    echo -e "${YELLOW}⚠️  wrangler not found, installing...${NC}"
    npm install -g wrangler
fi
echo -e "${GREEN}✓ wrangler $(wrangler --version)${NC}"

# Check if logged in
if ! wrangler whoami &> /dev/null; then
    echo -e "${YELLOW}⚠️  Not logged in to Cloudflare${NC}"
    echo "Please log in:"
    wrangler login
fi
echo -e "${GREEN}✓ Authenticated with Cloudflare${NC}"
echo ""

# Install dependencies
print_step "Installing Dependencies"
npm install
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Copy configuration files
print_step "Copying Configuration Files"

if [ ! -f "wrangler.toml" ]; then
    echo "Copying wrangler.toml..."
    cp cloudflare-deployment-fix/wrangler.toml ./wrangler.toml
    echo -e "${GREEN}✓ wrangler.toml created${NC}"
else
    echo -e "${YELLOW}⚠️  wrangler.toml already exists, skipping${NC}"
fi

# Create public directory if it doesn't exist
if [ ! -d "public" ]; then
    mkdir -p public
    echo -e "${GREEN}✓ Created public directory${NC}"
fi

# Copy _redirects and _headers
cp cloudflare-deployment-fix/public/_redirects ./public/_redirects 2>/dev/null || true
cp cloudflare-deployment-fix/public/_headers ./public/_headers 2>/dev/null || true
echo -e "${GREEN}✓ Copied _redirects and _headers${NC}"

# Copy functions directory
if [ ! -d "functions" ]; then
    echo "Copying functions directory..."
    cp -r cloudflare-deployment-fix/functions ./functions
    echo -e "${GREEN}✓ Functions directory created${NC}"
else
    echo -e "${YELLOW}⚠️  functions directory already exists, skipping${NC}"
    read -p "Do you want to overwrite it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf functions
        cp -r cloudflare-deployment-fix/functions ./functions
        echo -e "${GREEN}✓ Functions directory updated${NC}"
    fi
fi
echo ""

# Setup KV namespaces
print_step "Setting Up KV Namespaces"
./cloudflare-deployment-fix/setup-kv-namespaces.sh
echo ""

# Setup API keys
print_step "Setting Up API Keys (Secrets)"
./cloudflare-deployment-fix/setup-api-keys.sh
echo ""

# Build application
print_step "Building Application"
npm run build
echo -e "${GREEN}✓ Build complete${NC}"
echo ""

# Deploy
print_step "Deploying to Cloudflare Pages"

read -p "Ready to deploy? (y/n) " -n 1 -r
echo
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 0
fi

echo "Deploying..."
wrangler pages deploy dist --project-name=lmm-finance

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✅ Deployment Successful!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Your application is now live at:"
    echo -e "${BLUE}https://lmm-finance.pages.dev${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Test your API endpoints:"
    echo "     curl https://lmm-finance.pages.dev/api/health"
    echo ""
    echo "  2. Monitor your deployment:"
    echo "     wrangler pages deployment tail"
    echo ""
    echo "  3. View logs:"
    echo "     wrangler pages deployment list"
    echo ""
else
    echo ""
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}❌ Deployment Failed${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Please check the error messages above."
    echo ""
    echo "Common issues:"
    echo "  1. KV namespace not found - run ./setup-kv-namespaces.sh"
    echo "  2. Secrets not set - run ./setup-api-keys.sh"
    echo "  3. Build failed - check your build command"
    echo ""
    echo "For help, see: cloudflare-deployment-fix/README.md"
    exit 1
fi
