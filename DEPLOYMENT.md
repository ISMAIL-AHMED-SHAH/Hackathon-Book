# Deployment Guide: Physical AI Textbook

This guide walks you through deploying the Docusaurus textbook to GitHub Pages.

## Prerequisites

- GitHub account
- Git installed locally
- Node.js 18+ installed
- Repository created on GitHub

## Step 1: Update Configuration

### 1.1 Update `frontend/docusaurus.config.ts`

Replace the placeholder values with your actual GitHub information:

```typescript
// Find these lines and update:
url: 'https://YOUR-USERNAME.github.io',  // Replace YOUR-USERNAME
organizationName: 'YOUR-USERNAME',        // Replace YOUR-USERNAME
projectName: 'hackathon-book',            // Your repository name
```

**Example**:
If your GitHub username is `johndoe` and repository is `ai-textbook`:
```typescript
url: 'https://johndoe.github.io',
organizationName: 'johndoe',
projectName: 'ai-textbook',
baseUrl: '/ai-textbook/',  // Must match projectName
```

### 1.2 Update Backend API URL (Optional)

If you have a deployed backend API, update the workflow file:

Edit `.github/workflows/deploy.yml` line 36:
```yaml
env:
  REACT_APP_API_URL: https://your-backend-api.com  # Update this
```

## Step 2: Create GitHub Repository

1. Go to https://github.com/new
2. Create a new repository named `hackathon-book` (or your chosen name)
3. Choose **Public** (required for free GitHub Pages)
4. Do **NOT** initialize with README (we already have content)

## Step 3: Connect Local Repository to GitHub

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Complete Physical AI textbook with 10 chapters"

# Add GitHub remote (replace YOUR-USERNAME and REPO-NAME)
git remote add origin https://github.com/YOUR-USERNAME/REPO-NAME.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 4: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** (top right)
3. Click **Pages** (left sidebar)
4. Under **Source**, select **GitHub Actions**
5. Click **Save**

## Step 5: Trigger Deployment

The GitHub Actions workflow will automatically run when you push to `main` or `001-docusaurus-textbook` branch.

To manually trigger:
1. Go to **Actions** tab in your repository
2. Click **Deploy to GitHub Pages** workflow
3. Click **Run workflow** → **Run workflow**

## Step 6: Monitor Deployment

1. Go to **Actions** tab
2. Click on the running workflow
3. Watch the **build** and **deploy** jobs
4. Build should complete in ~2-3 minutes

## Step 7: Access Your Textbook

Once deployment succeeds, your textbook will be available at:

```
https://YOUR-USERNAME.github.io/REPO-NAME/
```

**Example**: `https://johndoe.github.io/ai-textbook/`

## Troubleshooting

### Issue: 404 Page Not Found

**Solution**: Check `baseUrl` in `docusaurus.config.ts` matches your repository name exactly.

```typescript
baseUrl: '/your-repo-name/',  // Must have leading and trailing slash
```

### Issue: Workflow Fails on Build Step

**Solution**:
1. Check `.github/workflows/deploy.yml` syntax
2. Ensure `frontend/package.json` exists
3. Run `npm run build` locally to test

### Issue: CSS/Images Not Loading

**Solution**: Verify `url` and `baseUrl` are correct in `docusaurus.config.ts`.

### Issue: Chatbot Not Working

**Solution**:
1. Update `REACT_APP_API_URL` in workflow to your deployed backend
2. Ensure backend CORS allows your GitHub Pages domain
3. Check browser console for errors

## Local Testing Before Deployment

Test the production build locally:

```bash
cd frontend

# Build production version
npm run build

# Serve locally
npm run serve
```

Visit `http://localhost:3000/hackathon-book/` to preview.

## Updating the Textbook

After making changes:

```bash
# Make your edits to markdown files in frontend/docs/

# Commit changes
git add .
git commit -m "Update chapter content"

# Push to GitHub (triggers automatic redeployment)
git push origin main
```

Deployment takes ~2-3 minutes. Your site will be updated automatically.

## Custom Domain (Optional)

To use a custom domain (e.g., `textbook.example.com`):

1. Add a `CNAME` file to `frontend/static/` with your domain
2. Update `url` in `docusaurus.config.ts` to your custom domain
3. Configure DNS records (see [GitHub Docs](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site))

## Deployment Checklist

- [ ] Updated `url` in `docusaurus.config.ts`
- [ ] Updated `organizationName` in `docusaurus.config.ts`
- [ ] Updated `projectName` and `baseUrl` in `docusaurus.config.ts`
- [ ] Created GitHub repository
- [ ] Pushed code to GitHub
- [ ] Enabled GitHub Pages with "GitHub Actions" source
- [ ] Workflow completed successfully
- [ ] Site accessible at GitHub Pages URL
- [ ] Navigation works (sidebar, next/previous)
- [ ] Code blocks render with syntax highlighting
- [ ] Images load correctly
- [ ] Chatbot widget appears (if backend configured)

## Next Steps

After deployment:
- Test all 10 chapters load correctly
- Verify chatbot integration (if backend deployed)
- Run Lighthouse audit for accessibility (target: 90+)
- Share the URL with your hackathon judges!

---

**Need Help?** Check the [Docusaurus Deployment Docs](https://docusaurus.io/docs/deployment#deploying-to-github-pages)
