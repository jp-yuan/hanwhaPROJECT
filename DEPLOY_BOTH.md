# Complete Deployment Guide: Frontend + Backend Together

This guide walks you through deploying both your backend (FastAPI) and frontend (Expo Web) **step by step**.

## 📋 Prerequisites

- ✅ Code pushed to GitHub: [https://github.com/jp-yuan/hanwhaPROJECT](https://github.com/jp-yuan/hanwhaPROJECT)
- 🌐 Accounts (free):
  - [Render.com](https://render.com) (for backend)
  - [Vercel.com](https://vercel.com) (for frontend)
- 🔑 Your OpenAI API key

---

## 🚀 PART 1: Deploy Backend to Render (15 minutes)

### Step 1: Sign Up for Render
1. Go to [https://render.com](https://render.com)
2. Click **"Get Started for Free"**
3. Sign up with your **GitHub account** (recommended)
4. Authorize Render to access your GitHub repos

### Step 2: Create Web Service
1. In Render dashboard, click **"New +"** → **"Web Service"**
2. You'll see **"Connect a repository"**
   - Select **"jp-yuan/hanwhaPROJECT"** from the list
   - Or paste: `https://github.com/jp-yuan/hanwhaPROJECT`
   - Click **"Connect"**

### Step 3: Configure Backend Service
Fill in these settings:

```
Name: test-prep-api
Region: Oregon (or closest to you)
Branch: main
Root Directory: backend
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
Plan: Free (or Starter $7/month for always-on)
```

⚠️ **Important:** Make sure **Root Directory** is set to `backend`

### Step 4: Add Environment Variables
1. Scroll down to **"Environment Variables"** section
2. Click **"Add Environment Variable"** and add:

```
Key: OPENAI_API_KEY
Value: [paste your OpenAI API key - starts with sk-]
```

3. Add another one:

```
Key: ENVIRONMENT
Value: production
```

4. Add one more:

```
Key: DEBUG
Value: False
```

### Step 5: Deploy Backend
1. Scroll down and click **"Create Web Service"**
2. Render will start building and deploying (takes 2-5 minutes)
3. Watch the **"Logs"** tab for progress
4. When you see **"Your service is live"**, you'll get a URL like:
   ```
   https://test-prep-api.onrender.com
   ```

**📝 Save this URL!** You'll need it for the frontend.

### Step 6: Test Backend
1. Click on your service URL or visit: `https://test-prep-api.onrender.com`
2. You should see: `{"name":"Test Prep Agent API","version":"1.0.0","status":"running"}`
3. Try the health endpoint: `https://test-prep-api.onrender.com/health`

✅ **Backend is deployed!** Now let's deploy the frontend.

---

## 🎨 PART 2: Deploy Frontend to Vercel (10 minutes)

### Step 1: Sign Up for Vercel
1. Go to [https://vercel.com](https://vercel.com)
2. Click **"Sign Up"**
3. Sign up with your **GitHub account** (recommended)
4. Authorize Vercel to access your GitHub repos

### Step 2: Import Project
1. In Vercel dashboard, click **"Add New..."** → **"Project"**
2. You'll see your GitHub repos listed
3. Find **"hanwhaPROJECT"** and click **"Import"**

### Step 3: Configure Frontend Project
Vercel should auto-detect settings, but verify:

```
Framework Preset: Other
Root Directory: ./
Build Command: expo export:web
Output Directory: web-build
Install Command: npm install
```

If any are different, update them.

### Step 4: Add Environment Variable
1. Expand **"Environment Variables"** section
2. Click **"Add Environment Variable"**
3. Add:

```
Name: REACT_APP_API_URL
Value: https://test-prep-api.onrender.com
```

⚠️ **Replace with your actual Render URL** from Part 1!

### Step 5: Deploy Frontend
1. Click **"Deploy"** button at the bottom
2. Vercel will build and deploy (takes 2-4 minutes)
3. Watch the deployment logs
4. When complete, you'll get a URL like:
   ```
   https://hanwha-project.vercel.app
   ```

**📝 Save this Vercel URL!** You'll need it next.

✅ **Frontend is deployed!** But wait - we need to connect them.

---

## 🔗 PART 3: Connect Frontend to Backend (5 minutes)

### Step 1: Update Backend CORS
Your backend needs to allow requests from your Vercel frontend.

1. Open `backend/main.py` in your local code editor
2. Find the CORS middleware section (around line 16)
3. Update it to include your Vercel URL:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:19006",
        "https://hanwha-project.vercel.app"  # ← Add your Vercel URL here
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

4. Replace `"https://hanwha-project.vercel.app"` with **your actual Vercel URL**

### Step 2: Commit and Push Changes
```bash
git add backend/main.py
git commit -m "Update CORS to allow Vercel frontend"
git push origin main
```

✅ **Render will automatically redeploy** your backend with the new CORS settings (takes ~2 minutes).

---

## ✅ PART 4: Verify Everything Works

### Test 1: Frontend Loads
1. Visit your Vercel URL: `https://hanwha-project.vercel.app`
2. The app should load and show the chat interface

### Test 2: API Connection
1. Open browser **Developer Tools** (F12)
2. Go to **"Console"** tab
3. Try sending a message in the chat
4. Check for any errors in the console

### Test 3: Full Chat Flow
1. Send a message: "Hello"
2. Wait for the AI response
3. If you get a response, everything is working! 🎉

---

## 🎯 Quick Reference

### Your Deployment URLs:
- **Backend (Render):** `https://test-prep-api.onrender.com`
- **Frontend (Vercel):** `https://hanwha-project.vercel.app`

### Share Your App:
Send this URL to others: **`https://hanwha-project.vercel.app`**

---

## 🔄 Updating Your App

Any time you make changes:

1. **Make your changes** locally
2. **Commit and push** to GitHub:
   ```bash
   git add .
   git commit -m "Update feature"
   git push origin main
   ```
3. **Both services auto-deploy:**
   - Render redeploys backend (~2 min)
   - Vercel redeploys frontend (~2 min)
4. **Done!** Your changes are live

---

## ⚠️ Common Issues & Fixes

### Issue 1: Backend Returns CORS Error
**Fix:** Make sure your Vercel URL is in `backend/main.py` CORS `allow_origins` list

### Issue 2: Frontend Can't Connect to Backend
**Fix:** 
1. Check `REACT_APP_API_URL` in Vercel environment variables
2. Verify it matches your Render URL exactly
3. Make sure Render service is running (not spun down)

### Issue 3: Render Service Spun Down (Free Tier)
**Fix:** 
- First request after 15 min inactivity takes 30-60 sec to wake up
- Consider upgrading to Starter ($7/month) for always-on service

### Issue 4: Build Errors
**Fix:**
- Check service logs in Render/Vercel dashboard
- Verify all environment variables are set
- Ensure `requirements.txt` and `package.json` are up to date

---

## 💰 Cost Summary

**Free Tier (Good for Demos):**
- Render Free: $0/month (spins down after 15 min inactivity)
- Vercel Free: $0/month
- **Total: $0/month** ✅

**Paid Option (Always-On):**
- Render Starter: $7/month (always-on, faster)
- Vercel Free: $0/month
- **Total: $7/month**

---

## 📞 Need Help?

- **Render Docs:** [https://render.com/docs](https://render.com/docs)
- **Vercel Docs:** [https://vercel.com/docs](https://vercel.com/docs)
- **Check logs:** Dashboard → Logs (for both services)

---

## ✨ You're Done!

Your app is now live and accessible worldwide! 🌍

**Share it:** `https://hanwha-project.vercel.app`

