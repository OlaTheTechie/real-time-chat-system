# Deployment Guide

## Backend Deployment (Render with Docker)

### Recommended: Manual Setup (Simpler for Free Tier)

1. **Push your code to GitHub**

2. **Connect to Render:**
   - Go to https://render.com
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Select the `backend` directory as the root
   - Render will automatically detect `render.yaml` and create all services

3. **Update environment variables:**
   - After deployment, go to your backend service
   - Update `ALLOWED_HOSTS` with your Vercel frontend URL
   - Example: `["https://your-app.vercel.app"]`

### Option 2: Manual Setup

1. **Create PostgreSQL Database:**
   - Go to Render Dashboard → "New +" → "PostgreSQL"
   - Name: `chatapp-db`
   - Plan: Free
   - Copy the Internal Database URL

2. **Create Redis:**
   - Go to Render Dashboard → "New +" → "Redis"
   - Name: `chatapp-redis`
   - Plan: Free
   - Copy the Redis URL

3. **Deploy Backend:**
   - Go to Render Dashboard → "New +" → "Web Service"
   - Connect your GitHub repository
   - Settings:
     - Name: `chatapp-backend`
     - Environment: Docker
     - Region: Oregon (or your preferred region)
     - Branch: main
     - Root Directory: `backend` (important!)
     - Dockerfile Path: `./Dockerfile`
     - Plan: Free
   
4. **Set Environment Variables:**
   ```
   DATABASE_URL=<your-postgres-internal-url>
   REDIS_URL=<your-redis-url>
   SECRET_KEY=<generate-a-strong-random-key>
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_DAYS=7
   ALLOWED_HOSTS=https://your-frontend.vercel.app
   ```
   
   Note: For multiple origins, use comma-separated values:
   `ALLOWED_HOSTS=https://your-app.vercel.app,https://your-app-preview.vercel.app`

5. **Deploy** - Render will build and deploy your Docker container

### Backend URL
After deployment, your backend will be available at:
`https://chatapp-backend.onrender.com`

---

## Frontend Deployment (Vercel)

### Deploy to Vercel

1. **Install Vercel CLI (optional):**
   ```bash
   npm i -g vercel
   ```

2. **Deploy via Vercel Dashboard (Recommended):**
   - Go to https://vercel.com
   - Click "Add New" → "Project"
   - Import your GitHub repository
   - Configure:
     - Framework Preset: Create React App
     - Root Directory: `frontend`
     - Build Command: `npm run build`
     - Output Directory: `build`
   
3. **Set Environment Variables:**
   - Go to Project Settings → Environment Variables
   - Add:
     ```
     REACT_APP_API_URL=https://chatapp-backend.onrender.com
     ```

4. **Deploy** - Vercel will automatically build and deploy

### Or Deploy via CLI:

```bash
cd frontend
vercel --prod
```

### Frontend URL
After deployment, your frontend will be available at:
`https://your-app.vercel.app`

---

## Post-Deployment Steps

1. **Update CORS Settings:**
   - Go to your Render backend service
   - Update `ALLOWED_HOSTS` environment variable with your Vercel URL
   - Example: `https://your-app.vercel.app`
   - For multiple origins: `https://your-app.vercel.app,https://preview.vercel.app`

2. **Update Frontend API URL:**
   - Go to your Vercel project settings
   - Update `REACT_APP_API_URL` with your Render backend URL
   - Example: `https://chatapp-backend.onrender.com`

3. **Test the deployment:**
   - Visit your Vercel frontend URL
   - Try registering a new user
   - Test login and chat functionality

---

## Important Notes

### Render Free Tier Limitations:
- Services spin down after 15 minutes of inactivity
- First request after spin-down takes 30-60 seconds
- PostgreSQL database has 1GB storage limit
- Redis has 25MB storage limit

### Vercel Free Tier Limitations:
- 100GB bandwidth per month
- Serverless function execution limit

### Security Checklist:
- ✅ Change `SECRET_KEY` to a strong random value
- ✅ Update `ALLOWED_HOSTS` with your actual frontend URL
- ✅ Never commit `.env` files to git
- ✅ Use environment variables for all secrets

---

## Troubleshooting

### Backend Issues:

**Service won't start:**
- Check Render logs for errors
- Verify all environment variables are set
- Ensure DATABASE_URL is the internal URL (not external)

**Database connection errors:**
- Use the Internal Database URL from Render
- Format: `postgresql://user:password@host/database`

**CORS errors:**
- Verify `ALLOWED_HOSTS` includes your Vercel URL
- Include `https://` in the URL
- Redeploy after changing environment variables

### Frontend Issues:

**API calls failing:**
- Check `REACT_APP_API_URL` is set correctly
- Verify backend is running (visit `/docs` endpoint)
- Check browser console for CORS errors

**Build failures:**
- Check Vercel build logs
- Verify all dependencies are in `package.json`
- Try building locally: `npm run build`

---

## Monitoring

### Render:
- View logs: Dashboard → Service → Logs
- Monitor metrics: Dashboard → Service → Metrics

### Vercel:
- View deployments: Dashboard → Project → Deployments
- Check analytics: Dashboard → Project → Analytics

---

## Updating Your App

### Backend Updates:
1. Push changes to GitHub
2. Render automatically rebuilds and deploys

### Frontend Updates:
1. Push changes to GitHub
2. Vercel automatically rebuilds and deploys

Both platforms support automatic deployments from GitHub!
