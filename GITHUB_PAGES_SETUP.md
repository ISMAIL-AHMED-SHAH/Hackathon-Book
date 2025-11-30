# GitHub Pages Setup - Quick Guide

## ✅ Current Status

Your textbook code is ready for deployment! All files are committed and pushed to GitHub.

## 🚀 Enable GitHub Pages (2 minutes)

Follow these exact steps:

### Step 1: Go to Repository Settings

Open this link in your browser:
```
https://github.com/ISMAIL-AHMED-SHAH/Hackathon-Book/settings/pages
```

### Step 2: Configure Source

1. Under **"Build and deployment"** section
2. Find **"Source"** dropdown
3. Select **"GitHub Actions"** (NOT "Deploy from a branch")
4. The page will auto-save

### Step 3: Trigger Deployment

Option A - **Merge to main** (Recommended):
```bash
git checkout main
git merge 001-docusaurus-textbook
git push origin main
```

Option B - **Manual trigger from current branch**:
1. Go to: https://github.com/ISMAIL-AHMED-SHAH/Hackathon-Book/actions
2. Click **"Deploy to GitHub Pages"** in the left sidebar
3. Click **"Run workflow"** button (top right)
4. Select branch: `001-docusaurus-textbook`
5. Click green **"Run workflow"** button

### Step 4: Monitor Deployment

1. Go to: https://github.com/ISMAIL-AHMED-SHAH/Hackathon-Book/actions
2. You'll see a workflow run starting
3. Click on it to watch progress
4. Wait for both jobs to complete:
   - ✅ **build** job (~2 minutes)
   - ✅ **deploy** job (~30 seconds)

### Step 5: Access Your Live Site! 🎉

Once deployment completes, visit:
```
https://ismail-ahmed-shah.github.io/Hackathon-Book/
```

## 🔍 Verify Deployment

Check that your textbook:
- ✅ Loads within 3 seconds
- ✅ Shows all 4 modules in sidebar
- ✅ All 10 chapters are accessible
- ✅ Code blocks have syntax highlighting
- ✅ Navigation (next/previous) works
- ✅ Mobile responsive
- ✅ Chatbot widget appears (bottom-right)

## 📊 What's Being Deployed

Your complete Physical AI textbook:
- **Module 1: ROS 2 Fundamentals** (4 chapters)
- **Module 2: Gazebo Simulation** (2 chapters)
- **Module 3: NVIDIA Isaac** (2 chapters)
- **Module 4: Vision-Language-Action** (2 chapters)
- **Capstone Project** (comprehensive integration)

Total: **10 chapters + 1 intro + 1 capstone = 12 pages**

## ⚡ Auto-Deploy on Future Changes

After initial setup, any push to `main` or `001-docusaurus-textbook` automatically triggers rebuild!

## 🆘 Troubleshooting

### Issue: Workflow doesn't appear

**Solution**: Make sure you selected "GitHub Actions" as the source in Pages settings.

### Issue: Build fails

**Solution**:
1. Check workflow logs at: https://github.com/ISMAIL-AHMED-SHAH/Hackathon-Book/actions
2. Look for error messages in the "build" job
3. Most common issue: Missing `package-lock.json` - run `npm install` in frontend/

### Issue: 404 on site

**Solution**:
1. Wait 2-3 minutes after deployment completes
2. Clear browser cache
3. Verify URL is exactly: `https://ismail-ahmed-shah.github.io/Hackathon-Book/` (case-sensitive!)

### Issue: CSS/Images not loading

**Solution**: Check `frontend/docusaurus.config.ts`:
- `baseUrl` should be `/Hackathon-Book/` (must match repo name exactly)
- `url` should be `https://ismail-ahmed-shah.github.io`

## 🎯 Quick Links

- **Repository**: https://github.com/ISMAIL-AHMED-SHAH/Hackathon-Book
- **Settings**: https://github.com/ISMAIL-AHMED-SHAH/Hackathon-Book/settings/pages
- **Actions**: https://github.com/ISMAIL-AHMED-SHAH/Hackathon-Book/actions
- **Your Site**: https://ismail-ahmed-shah.github.io/Hackathon-Book/

---

**Total Time to Deploy**: Less than 5 minutes! 🚀
