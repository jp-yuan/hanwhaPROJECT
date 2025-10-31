# Deployment Guide

This guide explains how to deploy your AI Test Prep app online so others can access it via web browser.

## Architecture

- **Backend (FastAPI)**: Deployed on Render
- **Frontend (Expo Web)**: Deployed on Vercel
- **Cost**: Free tier (Render free, Vercel free) or ~$7/month if you need Render's paid tier

## Prerequisites

1. GitHub account (to store your code)
2. Render account (sign up at https://render.com)
3. Vercel account (sign up at https://vercel.com)
4. Your OpenAI API key

## Step 1: Push Code to GitHub

First, make sure your code is on GitHub (you'll need to fix the git push issue first):

```bash
# Remove .git_backup folder
rm -rf .git_backup

# Commit and push
git add .
git commit -m "Prepare for deployment"
git push -u origin main --force
```

## Step 2: Deploy Backend to Render

### 2.1 Create Render Account
1. Go to https://render.com and sign up
2. Connect your GitHub account

### 2.2 Create New Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: test-prep-api (or your choice)
   - **Region**: Oregon (closest to you, or choose your region)
   - **Branch**: main
   - **Root Directory**: backend
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free (or Starter for $7/month if you need always-on)

### 2.3 Add Environment Variables
In Render dashboard → Environment:
- **OPENAI_API_KEY**: your-actual-openai-key
- **ENVIRONMENT**: production
- **DEBUG**: False

### 2.4 Deploy
Click "Create Web Service" - Render will build and deploy automatically.

**Save your Render URL**: e.g., `https://test-prep-api.onrender.com`

### 2.5 Update Backend CORS (Important!)
After getting your Vercel URL (next step), update `backend/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:19006",
        "https://your-vercel-app.vercel.app"  # Add your Vercel URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Then commit and push - Render will auto-redeploy.

## Step 3: Deploy Frontend to Vercel

### 3.1 Create Vercel Account
1. Go to https://vercel.com and sign up
2. Connect your GitHub account

### 3.2 Import Project
1. Click "Add New..." → "Project"
2. Import your GitHub repository
3. Configure:
   - **Framework Preset**: Other
   - **Root Directory**: ./
   - **Build Command**: `expo export:web`
   - **Output Directory**: `web-build`
   - **Install Command**: `npm install`

### 3.3 Add Environment Variable
In Vercel dashboard → Settings → Environment Variables:
- **REACT_APP_API_URL**: https://test-prep-api.onrender.com (your Render URL)

### 3.4 Deploy
Click "Deploy" - Vercel will build and deploy automatically.

**Save your Vercel URL**: e.g., `https://your-app.vercel.app`

## Step 4: Final Configuration

### 4.1 Update Backend CORS
Update `backend/main.py` with your Vercel URL:

```python
allow_origins=[
    "http://localhost:19006",
    "https://your-app.vercel.app"  # Your actual Vercel URL
]
```

Commit and push - Render will auto-redeploy.

### 4.2 Test Your Deployment
1. Visit your Vercel URL: `https://your-app.vercel.app`
2. Try the chat functionality
3. Ensure API calls are working

## Important Notes

### Render Free Tier Limitations
- Spins down after 15 minutes of inactivity
- First request after spin-down takes 30-60 seconds to wake up
- Upgrade to Starter ($7/month) for always-on service

### Vercel Free Tier
- 100GB bandwidth/month (plenty for demos)
- Unlimited deployments
- Auto-deploys on git push

## Sharing Your App

Once deployed, share your Vercel URL with others:
```
https://your-app.vercel.app
```

They can access it from any web browser on desktop or mobile!

## Updating Your App

Any time you push to GitHub:
- Render will auto-deploy the backend
- Vercel will auto-deploy the frontend

```bash
# Make changes
git add .
git commit -m "Update feature"
git push
# Both services will auto-deploy in ~2-3 minutes
```

## Troubleshooting

### Backend Issues
- Check Render logs: Dashboard → Logs
- Verify environment variables are set
- Ensure `backend/requirements.txt` is up to date

### Frontend Issues
- Check Vercel deployment logs
- Verify `REACT_APP_API_URL` environment variable
- Check browser console for errors

### CORS Errors
- Ensure backend CORS includes your Vercel URL
- Redeploy backend after changing CORS settings

### API Key Issues
- Verify `OPENAI_API_KEY` is set in Render environment
- Check Render logs for API errors

## Cost Summary

**Free Option (Good for Demos)**:
- Render Free: $0/month (spins down after 15 min)
- Vercel Free: $0/month
- Total: **$0/month**

**Paid Option (Always-On)**:
- Render Starter: $7/month (always-on, more resources)
- Vercel Free: $0/month
- Total: **$7/month**

## Next Steps

1. Fix git push issue (remove .git_backup)
2. Push code to GitHub
3. Deploy backend to Render
4. Deploy frontend to Vercel
5. Update backend CORS with Vercel URL
6. Share your app URL!

Need help? Check the service documentation:
- Render: https://render.com/docs
- Vercel: https://vercel.com/docs

