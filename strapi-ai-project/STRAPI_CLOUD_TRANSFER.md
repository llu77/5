# Strapi Cloud Transfer Guide

## Overview

This guide explains how to transfer your Strapi AI project to Strapi Cloud using the `strapi transfer` command.

## Understanding Strapi Transfer

The `strapi transfer` command moves:
- ✅ **Entities**: All content (articles, pages, etc.)
- ✅ **Assets**: Media files (images, videos, documents)
- ✅ **Links**: Relationships between content
- ✅ **Configuration**: Content types, components, permissions

**Important**: The transfer will DELETE existing data on the destination!

## Prerequisites

### 1. Local Requirements
```bash
# Your project must be built and have data
cd /home/user/5/strapi-ai-project
npm run build
npm run develop  # Create admin user and add some content
```

### 2. Remote Strapi Cloud Instance
- Sign up at https://cloud.strapi.io
- Create a new project
- Note the project URL (e.g., `https://your-project.strapiapp.com`)

### 3. Transfer Token
Generate a transfer token on Strapi Cloud:
1. Go to Settings → Transfer Tokens
2. Click "Create new Transfer Token"
3. Set permissions (Full Access recommended)
4. Copy the token (you'll only see it once!)

## Transfer Methods

### Method 1: Environment Variables (Recommended)

Add to your `.env` file:

```env
# Strapi Cloud Transfer
STRAPI_TRANSFER_URL=https://your-project.strapiapp.com/admin
STRAPI_TRANSFER_TOKEN=your-transfer-token-here
STRAPI_TRANSFER_REMOTE_URL=https://your-project.strapiapp.com/admin
```

Then run:
```bash
npm run strapi transfer -- --to remote
# or with yarn
yarn strapi transfer --to remote
```

### Method 2: Interactive Mode

```bash
npm run strapi transfer
# or
yarn strapi transfer
```

Then follow the prompts:
1. Choose transfer direction: `Push local data to remote Strapi`
2. Enter remote URL: `https://your-project.strapiapp.com/admin`
3. Enter transfer token: `[paste your token]`
4. Confirm deletion warning: `Yes`

### Method 3: Command Line Arguments

```bash
npm run strapi transfer -- \
  --to https://your-project.strapiapp.com/admin \
  --to-token your-transfer-token-here
```

## Transfer Workflow

### Step 1: Prepare Local Environment

```bash
cd /home/user/5/strapi-ai-project

# Build the project
npm run build

# Start development server
npm run develop
```

### Step 2: Create Content Locally

1. Access admin panel: http://localhost:1337/admin
2. Create first admin user
3. Add sample content:
   - Create some Pages with dynamic sections
   - Add Categories
   - Upload some images
   - Configure global Header/Footer

### Step 3: Set Up Strapi Cloud

1. Go to https://cloud.strapi.io
2. Create new project
3. Wait for deployment
4. Generate Transfer Token:
   - Settings → Transfer Tokens
   - Create new token
   - Copy token securely

### Step 4: Configure Environment

Edit `.env`:
```bash
# Add these lines
STRAPI_TRANSFER_URL=https://your-project.strapiapp.com/admin
STRAPI_TRANSFER_TOKEN=your-token-here
```

### Step 5: Execute Transfer

```bash
# Using npm
npm run strapi transfer -- --to remote

# Using yarn
yarn strapi transfer --to remote

# Or interactive
npm run strapi transfer
```

### Step 6: Verify Transfer

After transfer completes:
1. Go to your Strapi Cloud admin
2. Check Content Manager for your data
3. Verify Media Library has your assets
4. Test API endpoints

## Transfer Directions

### Push (Local → Remote)
```bash
npm run strapi transfer -- --to remote
```
Sends your local data to Strapi Cloud

### Pull (Remote → Local)
```bash
npm run strapi transfer -- --from remote
```
Downloads data from Strapi Cloud to local

### Between Two Remote Instances
```bash
npm run strapi transfer -- \
  --from https://source.strapiapp.com/admin \
  --from-token source-token \
  --to https://destination.strapiapp.com/admin \
  --to-token destination-token
```

## What Gets Transferred

### ✅ Included
- Content types schemas
- Component definitions
- All content entries
- Media files
- Relationships between content
- API permissions
- Role configurations
- Plugin settings
- Locale configurations

### ❌ Not Included
- Admin users and passwords
- API tokens
- Webhooks
- Environment variables (`.env`)
- Custom code (controllers, services)
- Plugin code
- `node_modules`

## Transfer Options

### Force Transfer (Skip Confirmation)
```bash
npm run strapi transfer -- --to remote --force
```

### Exclude Assets
```bash
npm run strapi transfer -- --to remote --exclude files
```

### Only Specific Content Types
```bash
npm run strapi transfer -- --to remote --only api::page.page
```

### Throttle Transfer Speed
```bash
npm run strapi transfer -- --to remote --throttle 100
```

## After Transfer

### Update Remote Environment Variables

In Strapi Cloud dashboard:
1. Go to Settings → Environment Variables
2. Add your AI API key:
   ```
   STRAPI_AI_API_KEY=your-ai-key-here
   ```
3. Redeploy the project

### Configure Custom Domain

1. Go to Settings → Domains
2. Add your custom domain
3. Configure DNS records
4. Enable SSL

### Set Up CI/CD

Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy to Strapi Cloud

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npm run build
      - name: Transfer to Cloud
        env:
          STRAPI_TRANSFER_URL: ${{ secrets.STRAPI_TRANSFER_URL }}
          STRAPI_TRANSFER_TOKEN: ${{ secrets.STRAPI_TRANSFER_TOKEN }}
        run: npm run strapi transfer -- --to remote --force
```

## Troubleshooting

### Error: "Failed to connect to remote"
- Check URL format includes `/admin`
- Verify Strapi Cloud instance is running
- Check your internet connection

### Error: "Invalid token"
- Regenerate transfer token
- Ensure token has Full Access permissions
- Check for extra spaces when pasting

### Error: "Transfer timeout"
- Your data might be too large
- Try excluding assets: `--exclude files`
- Upload assets separately via admin panel

### Error: "Content type mismatch"
- Destination must have same Strapi version
- Ensure schemas are compatible
- Try fresh Cloud instance

### Large Transfer Takes Too Long
```bash
# Split into multiple transfers
npm run strapi transfer -- --to remote --only api::page.page
npm run strapi transfer -- --to remote --only api::category.category
npm run strapi transfer -- --to remote --exclude entities
```

## Best Practices

### 1. Always Backup First
```bash
# Export before transfer
npm run strapi export -- --file backup-$(date +%Y%m%d).tar.gz
```

### 2. Test in Staging First
- Create staging Cloud instance
- Transfer to staging
- Verify everything works
- Then transfer to production

### 3. Version Control
- Commit all schema changes
- Tag releases
- Keep changelog

### 4. Incremental Updates
For regular updates, use API instead of full transfer:
```javascript
// Update specific entries via API
const response = await fetch('https://your-cloud.strapiapp.com/api/pages', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${API_TOKEN}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ data: yourData })
});
```

### 5. Monitor Transfers
```bash
# Save transfer logs
npm run strapi transfer -- --to remote 2>&1 | tee transfer.log
```

## Transfer Example Output

```
Starting transfer...
✔ entities: 58 transferred (size: 48.1 KB) (elapsed: 4207 ms)
✔ assets: 8 transferred (size: 300 KB) (elapsed: 1964 ms)
✔ links: 174 transferred (size: 32.6 KB) (elapsed: 1987 ms)
✔ configuration: 48 transferred (size: 141.8 KB) (elapsed: 1318 ms)

┌─────────────────────┬───────┬──────────┐
│ Type                │ Count │ Size     │
├─────────────────────┼───────┼──────────┤
│ entities            │    58 │  48.1 KB │
│ assets              │     8 │ 300.0 KB │
│ links               │   174 │  32.6 KB │
│ configuration       │    48 │ 141.8 KB │
├─────────────────────┼───────┼──────────┤
│ Total               │   288 │ 522.5 KB │
└─────────────────────┴───────┴──────────┘

Transfer process has been completed successfully!
```

## Alternative: Manual Deployment

If transfer doesn't work, deploy code and rebuild:

1. **Push to GitHub**
   ```bash
   git push origin main
   ```

2. **Connect GitHub to Strapi Cloud**
   - In Cloud dashboard
   - Settings → GitHub
   - Connect repository
   - Auto-deploy on push

3. **Rebuild on Cloud**
   - Cloud will pull code
   - Run npm install
   - Build admin panel
   - Deploy

## Security Notes

- **Never commit transfer tokens** to Git
- Store tokens in environment variables
- Rotate tokens regularly
- Use read-only tokens when possible
- Enable 2FA on Strapi Cloud

## Resources

- [Official Transfer Documentation](https://docs.strapi.io/dev-docs/data-management/transfer)
- [Strapi Cloud Docs](https://docs.strapi.io/cloud/getting-started/intro)
- [Transfer CLI Reference](https://docs.strapi.io/dev-docs/cli#strapi-transfer)

## Quick Reference Commands

```bash
# Interactive transfer
npm run strapi transfer

# Push to remote
npm run strapi transfer -- --to remote

# Pull from remote
npm run strapi transfer -- --from remote

# With specific URL and token
npm run strapi transfer -- \
  --to https://your-cloud.strapiapp.com/admin \
  --to-token your-token

# Exclude assets
npm run strapi transfer -- --to remote --exclude files

# Force without confirmation
npm run strapi transfer -- --to remote --force

# Export backup
npm run strapi export -- --file backup.tar.gz

# Import backup
npm run strapi import -- --file backup.tar.gz
```

## Next Steps After Transfer

1. ✅ Verify all content transferred correctly
2. ✅ Test API endpoints
3. ✅ Configure environment variables
4. ✅ Set up custom domain
5. ✅ Enable SSL
6. ✅ Test AI integration with Cloud API key
7. ✅ Configure backups
8. ✅ Set up monitoring
9. ✅ Update frontend to use Cloud URL
10. ✅ Document deployment process

Your Strapi project is now live on the cloud! 🚀
