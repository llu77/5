#!/bin/bash
# Modal Quick Start Script
# Automates Modal setup and deployment

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
MODAL_TOKEN_ID="ak-CNC6lcJihRz4vhP3WnR2YE"
MODAL_TOKEN_SECRET="as-BRa4kKXSby7B8NhgFBFfak"
WEBHOOK_TOKEN_ID="wk-MqtJuh2UbPbBHNuKTf8BOm"
WEBHOOK_TOKEN_SECRET="ws-erJAdpAlGXBKXJFXzhlWR3"
ACCOUNT_ID="ac-qp2iIJLVPa4JpwLDc95lW3"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         Modal + Claude AI - Quick Start Script                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${BLUE}➜${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check if Modal is installed
print_status "Checking Modal installation..."
if ! command -v modal &> /dev/null; then
    print_error "Modal CLI not found. Installing..."
    pip install modal
    print_success "Modal installed"
else
    print_success "Modal is already installed ($(modal --version))"
fi

# Authenticate with Modal
print_status "Authenticating with Modal..."
if modal token set --token-id "$MODAL_TOKEN_ID" --token-secret "$MODAL_TOKEN_SECRET"; then
    print_success "Authentication successful"
else
    print_error "Authentication failed. Please check your credentials."
    exit 1
fi

# Check if Anthropic API key is provided
echo ""
print_status "Anthropic API Key Setup"
echo -e "${YELLOW}Please enter your Anthropic API key:${NC}"
read -p "ANTHROPIC_API_KEY: " ANTHROPIC_KEY

if [ -z "$ANTHROPIC_KEY" ]; then
    print_error "API key cannot be empty"
    exit 1
fi

# Create Anthropic secret
print_status "Creating Anthropic secret in Modal..."
if modal secret create anthropic-secret ANTHROPIC_API_KEY="$ANTHROPIC_KEY" 2>/dev/null; then
    print_success "Secret created successfully"
else
    print_warning "Secret may already exist or creation failed"
    echo "You can update it with: modal secret create anthropic-secret ANTHROPIC_API_KEY=your-key --force"
fi

# List available examples
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    Available Examples                          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "1. Thinking Agent (thinking_agent_modal.py)"
echo "   - Extended thinking with serverless execution"
echo ""
echo "2. Orchestrator-Workers (orchestrator_workers_modal.py)"
echo "   - Distributed task processing with parallel workers"
echo ""
echo "3. Code Analyzer (code_analyzer_modal.py)"
echo "   - Repository analysis and security auditing"
echo ""
echo "4. Batch Processor (resilient_batch_processor.py)"
echo "   - Fault-tolerant batch processing"
echo ""

# Ask user what to do
echo -e "${YELLOW}What would you like to do?${NC}"
echo "1. Test examples locally (modal run)"
echo "2. Deploy to Modal cloud (modal deploy)"
echo "3. Both (test then deploy)"
echo "4. Skip for now"
read -p "Choice (1-4): " CHOICE

if [ "$CHOICE" = "1" ] || [ "$CHOICE" = "3" ]; then
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                    Testing Examples                            ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    # Test Thinking Agent
    print_status "Testing Thinking Agent..."
    echo ""
    modal run thinking_agent_modal.py \
        --task "What is 10 factorial?" \
        --domain math \
        --thinking-budget 1000 || print_warning "Test may have failed"

    echo ""
    print_success "Thinking Agent test complete"
fi

if [ "$CHOICE" = "2" ] || [ "$CHOICE" = "3" ]; then
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                   Deploying to Modal                           ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    # Deploy Thinking Agent
    print_status "Deploying Thinking Agent..."
    if modal deploy thinking_agent_modal.py; then
        print_success "Thinking Agent deployed"
    else
        print_error "Deployment failed"
    fi

    echo ""

    # Deploy Code Analyzer
    print_status "Deploying Code Analyzer..."
    if modal deploy code_analyzer_modal.py; then
        print_success "Code Analyzer deployed"
    else
        print_error "Deployment failed"
    fi

    echo ""

    # Deploy Orchestrator-Workers
    print_status "Deploying Orchestrator-Workers..."
    if modal deploy orchestrator_workers_modal.py; then
        print_success "Orchestrator-Workers deployed"
    else
        print_error "Deployment failed"
    fi

    echo ""
    print_success "All deployments complete!"
    echo ""
    echo -e "${GREEN}Your endpoints are now live!${NC}"
    echo "Visit https://modal.com/dashboard to see your deployed apps"
fi

# Show webhook credentials
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                   Webhook Credentials                          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "For webhooks with proxy auth, include these headers:"
echo ""
echo "Modal-Key: $WEBHOOK_TOKEN_ID"
echo "Modal-Secret: $WEBHOOK_TOKEN_SECRET"
echo ""
echo "Example:"
echo 'curl -X POST https://your-endpoint.modal.run \'
echo "  -H \"Content-Type: application/json\" \\"
echo "  -H \"Modal-Key: $WEBHOOK_TOKEN_ID\" \\"
echo "  -H \"Modal-Secret: $WEBHOOK_TOKEN_SECRET\" \\"
echo "  -d '{\"task\": \"Your question\"}'"
echo ""

# Show next steps
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                      Next Steps                                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "1. View your apps:"
echo "   modal app list"
echo ""
echo "2. View logs:"
echo "   modal app logs thinking-agent-modal"
echo ""
echo "3. Test webhooks:"
echo "   python test_webhook.py"
echo ""
echo "4. Check usage:"
echo "   Visit https://modal.com/dashboard"
echo ""
echo "5. Read documentation:"
echo "   cat README.md"
echo "   cat SETUP.md"
echo ""

print_success "Setup complete! 🚀"
