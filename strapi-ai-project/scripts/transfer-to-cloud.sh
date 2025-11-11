#!/bin/bash

# Strapi Cloud Transfer Helper Script
# This script simplifies the process of transferring data to Strapi Cloud

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "\n${BLUE}===================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}===================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check if .env file exists
check_env_file() {
    if [ ! -f .env ]; then
        print_error ".env file not found!"
        print_info "Please create a .env file with your configuration"
        exit 1
    fi
    print_success ".env file found"
}

# Check if required env variables are set
check_env_variables() {
    if [ -z "$STRAPI_TRANSFER_URL" ] || [ -z "$STRAPI_TRANSFER_TOKEN" ]; then
        print_warning "Transfer environment variables not found in .env"
        print_info "You can either:"
        echo "  1. Add them to .env file:"
        echo "     STRAPI_TRANSFER_URL=https://your-project.strapiapp.com/admin"
        echo "     STRAPI_TRANSFER_TOKEN=your-token-here"
        echo "  2. Use interactive mode (script will prompt you)"
        echo ""
        return 1
    fi
    print_success "Transfer variables configured"
    return 0
}

# Source .env file
source_env() {
    set -a
    source .env
    set +a
    print_success "Environment loaded"
}

# Check if project is built
check_build() {
    if [ ! -d "dist" ]; then
        print_warning "Project not built. Building now..."
        npm run build
        print_success "Build completed"
    else
        print_success "Project already built"
    fi
}

# Interactive mode - get transfer details
interactive_mode() {
    print_header "Interactive Transfer Configuration"

    echo -n "Enter your Strapi Cloud URL (e.g., https://your-project.strapiapp.com/admin): "
    read -r TRANSFER_URL

    echo -n "Enter your transfer token: "
    read -rs TRANSFER_TOKEN
    echo ""

    export STRAPI_TRANSFER_URL="$TRANSFER_URL"
    export STRAPI_TRANSFER_TOKEN="$TRANSFER_TOKEN"

    print_success "Configuration saved for this session"
}

# Backup local data before transfer
backup_local_data() {
    print_header "Creating Backup"

    BACKUP_FILE="backup-$(date +%Y%m%d-%H%M%S).tar.gz"

    print_info "Creating backup: $BACKUP_FILE"
    npm run strapi export -- --file "$BACKUP_FILE" --no-encrypt

    if [ -f "$BACKUP_FILE" ]; then
        print_success "Backup created: $BACKUP_FILE"
        print_info "Keep this file safe to restore if needed"
    else
        print_warning "Backup creation skipped or failed"
    fi
}

# Show transfer summary
show_summary() {
    print_header "Transfer Summary"

    if [ -n "$STRAPI_TRANSFER_URL" ]; then
        echo "Destination: $STRAPI_TRANSFER_URL"
    fi

    if [ -d ".tmp" ]; then
        DB_SIZE=$(du -sh .tmp 2>/dev/null | cut -f1)
        echo "Database size: $DB_SIZE"
    fi

    if [ -d "public/uploads" ]; then
        UPLOADS_SIZE=$(du -sh public/uploads 2>/dev/null | cut -f1)
        UPLOADS_COUNT=$(find public/uploads -type f 2>/dev/null | wc -l)
        echo "Media files: $UPLOADS_COUNT files ($UPLOADS_SIZE)"
    fi
}

# Execute transfer
execute_transfer() {
    print_header "Starting Transfer"

    print_warning "This will DELETE all existing data on the remote Strapi instance!"
    echo -n "Are you sure you want to continue? (yes/no): "
    read -r CONFIRM

    if [ "$CONFIRM" != "yes" ]; then
        print_info "Transfer cancelled"
        exit 0
    fi

    print_info "Transferring data to Strapi Cloud..."

    if npm run strapi transfer -- --to remote --force; then
        print_success "Transfer completed successfully!"
        return 0
    else
        print_error "Transfer failed!"
        return 1
    fi
}

# Post-transfer checklist
post_transfer_checklist() {
    print_header "Post-Transfer Checklist"

    echo "Please verify the following on Strapi Cloud:"
    echo ""
    echo "  [ ] Content Manager - Check all entries transferred"
    echo "  [ ] Media Library - Verify all files uploaded"
    echo "  [ ] Content Types - Confirm all types exist"
    echo "  [ ] API Permissions - Check permissions are correct"
    echo "  [ ] Environment Variables - Add STRAPI_AI_API_KEY"
    echo "  [ ] Test API endpoints"
    echo "  [ ] Test AI integration"
    echo ""
    print_info "Access your Strapi Cloud admin at:"
    echo "  $STRAPI_TRANSFER_URL"
}

# Main script
main() {
    print_header "Strapi Cloud Transfer Tool"

    # Check prerequisites
    check_env_file
    source_env

    # Check if env variables are set, if not use interactive mode
    if ! check_env_variables; then
        interactive_mode
    fi

    # Check build
    check_build

    # Show summary
    show_summary

    echo ""
    echo "Transfer Options:"
    echo "  1. Full transfer (with backup)"
    echo "  2. Full transfer (without backup)"
    echo "  3. Transfer without assets"
    echo "  4. Cancel"
    echo ""
    echo -n "Choose an option (1-4): "
    read -r OPTION

    case $OPTION in
        1)
            backup_local_data
            if execute_transfer; then
                post_transfer_checklist
            fi
            ;;
        2)
            if execute_transfer; then
                post_transfer_checklist
            fi
            ;;
        3)
            print_info "Transferring without assets..."
            if npm run strapi transfer -- --to remote --exclude files --force; then
                print_success "Transfer completed successfully!"
                post_transfer_checklist
            else
                print_error "Transfer failed!"
            fi
            ;;
        4)
            print_info "Transfer cancelled"
            exit 0
            ;;
        *)
            print_error "Invalid option"
            exit 1
            ;;
    esac
}

# Run main function
main
