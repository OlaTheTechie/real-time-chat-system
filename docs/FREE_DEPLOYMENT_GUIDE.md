# free deployment guide 

## overview

This guide shows you how to deploy your realtime chat server **completely free** using modern cloud platforms.

---

##  recommended free deployment stack

### option 1: best for production (recommended)
- **Backend**: Railway.app (Free tier)
- **Frontend**: Vercel (Free tier)
- **Database**: Railway PostgreSQL (Free tier)
- **Redis**: Railway Redis (Free tier)

### option 2: all-in-one
- **Everything**: Render.com (Free tier)

### option 3: maximum free resources
- **Backend**: Fly.io (Free tier)
- **Frontend**: Netlify (Free tier)
- **Database**: Supabase (Free tier)
- **Redis**: Upstash (Free tier)

---

##  option 1: railway + vercel (recommended)

### why this stack?
-  Easy setup (5-10 minutes)
-  Automatic deployments from GitHub
-  Built-in PostgreSQL and Redis
-  WebSocket support
-  Custom domains
-  SSL certificates included
-  Good free tier limits

### step 1: prepare your code

#### 1.1 create production requirements
```bash
cd backend
cat > requirements.txt << 'EOF'
fastapi[all]==0.121.0
uvicorn==0.38.0
sqlalchemy==2.0.0
psycopg2-binary==2.9.0
redis==5.0.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.0
bcrypt==4.0.1
python-multipart==0.0.6
alembic==1.13.0
websockets==12.0
pydantic[email]==2.0.0
python-dotenv==1.0.0
sqladmin==0.16.0
EOF
```

#### 1.2 create procfile for railway
```bash
cd backend
cat > Procfile << 'EOF'
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
EOF
```

#### 1.3 create railway.json
```bash
cd backend
cat > railway.json << 'EOF'
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
EOF
```

#### 1.4 update cors settings
Edit `backend/app/core/config.py`:
```python
ALLOWED_HOSTS: list = [
    "http://localhost:3000",
    "http://localhost:8000",
    "https://your-frontend.vercel.app",  # Add your Vercel URL
    "*"  # Remove in production, add specific domains
]
```

### step 2: deploy backend to railway

#### 2.1 sign up
1. Go to https://railway.app
2. Sign up with GitHub (free)
3. Verify your email

#### 2.2 create new project
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Connect your GitHub account
4. Select your repository
5. Choose the `backend` folder as root

#### 2.3 add postgresql database
1. In your project, click **"+ New"**
2. Select **"Database"**
3. Choose **"PostgreSQL"**
4. Railway will create and connect it automatically

#### 2.4 add redis
1. Click **"+ New"** again
2. Select **"Database"**
3. Choose **"Redis"**
4. Railway will create and connect it automatically

#### 2.5 configure environment variables
1. Click on your backend service
2. Go to **"Variables"** tab
3. Add these variables:
```bash
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_HOSTS=https://your-frontend.vercel.app,*
```

#### 2.6 deploy
1. Railway will automatically deploy
2. Wait 2-3 minutes for build
3. Get your backend URL (e.g., `https://your-app.railway.app`)

### step 3: deploy frontend to vercel

#### 3.1 sign up
1. Go to https://vercel.com
2. Sign up with GitHub (free)

#### 3.2 prepare frontend
Create `frontend/.env.production`:
```bash
REACT_APP_API_BASE_URL=https://your-backend.railway.app
REACT_APP_WS_BASE_URL=wss://your-backend.railway.app
```

#### 3.3 deploy
1. Click **"Add New Project"**
2. Import your GitHub repository
3. Select the `frontend` folder as root
4. Framework Preset: **Create React App**
5. Build Command: `npm run build`
6. Output Directory: `build`
7. Add environment variables:
   - `REACT_APP_API_BASE_URL`: Your Railway backend URL
   - `REACT_APP_WS_BASE_URL`: Your Railway backend URL (with wss://)
8. Click **"Deploy"**

#### 3.4 get your url
- Vercel will give you a URL like: `https://your-app.vercel.app`
- Update the CORS settings in Railway with this URL

### step 4: test your deployment
1. Visit your Vercel URL
2. Register a new user
3. Login
4. Create a chat
5. Send messages
6. Test real-time messaging

---

##  option 2: render.com (all-in-one)

### why render?
-  Everything in one place
-  Free PostgreSQL database
-  Free Redis (limited)
-  Easy setup
-  Good documentation

### step 1: prepare code

#### 1.1 create render.yaml
```bash
cat > render.yaml << 'EOF'
services:
  # backend api
  - type: web
    name: chat-backend
    env: python
    region: oregon
    plan: free
    buildCommand: "pip install -r backend/requirements.txt"
    startCommand: "cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: chat-db
          property: connectionString
      - key: REDIS_URL
        fromDatabase:
          name: chat-redis
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: PYTHON_VERSION
        value: 3.10.0

  # frontend
  - type: web
    name: chat-frontend
    env: static
    buildCommand: "cd frontend && npm install && npm run build"
    staticPublishPath: frontend/build
    envVars:
      - key: REACT_APP_API_BASE_URL
        value: https://chat-backend.onrender.com

databases:
  # postgresql
  - name: chat-db
    plan: free
    databaseName: chatdb
    user: chatuser

  # redis
  - name: chat-redis
    plan: free
EOF
```

### step 2: deploy to render

1. Go to https://render.com
2. Sign up with GitHub
3. Click **"New +"** → **"Blueprint"**
4. Connect your repository
5. Render will read `render.yaml` and create everything
6. Wait 5-10 minutes for deployment

### step 3: configure
1. Get your backend URL from Render dashboard
2. Update frontend environment variable with backend URL
3. Redeploy frontend

---

##  option 3: fly.io + netlify + supabase

### backend on fly.io

#### 1. install fly cli
```bash
curl -L https://fly.io/install.sh | sh
```

#### 2. login
```bash
fly auth login
```

#### 3. create fly.toml
```bash
cd backend
cat > fly.toml << 'EOF'
app = "your-chat-app"

[build]
  builder = "paketobuildpacks/builder:base"

[env]
  PORT = "8000"

[[services]]
  http_checks = []
  internal_port = 8000
  processes = ["app"]
  protocol = "tcp"

  [[services.ports]]
    force_https = true
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443
EOF
```

#### 4. deploy
```bash
fly launch
fly deploy
```

### frontend on netlify

#### 1. create netlify.toml
```bash
cd frontend
cat > netlify.toml << 'EOF'
[build]
  command = "npm run build"
  publish = "build"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
EOF
```

#### 2. deploy
1. Go to https://netlify.com
2. Sign up with GitHub
3. Click **"Add new site"** → **"Import an existing project"**
4. Select your repository
5. Configure:
   - Base directory: `frontend`
   - Build command: `npm run build`
   - Publish directory: `build`
6. Add environment variables
7. Deploy

### database on supabase

1. Go to https://supabase.com
2. Create new project
3. Get PostgreSQL connection string
4. Add to Fly.io secrets:
```bash
fly secrets set DATABASE_URL="postgresql://..."
```

### redis on upstash

1. Go to https://upstash.com
2. Create Redis database
3. Get connection URL
4. Add to Fly.io secrets:
```bash
fly secrets set REDIS_URL="redis://..."
```

---

##  pre-deployment checklist

### backend
- [ ] Create `requirements.txt` from `pyproject.toml`
- [ ] Set `DEBUG=False` in production
- [ ] Configure proper CORS origins
- [ ] Set strong `SECRET_KEY`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Configure Redis URL
- [ ] Set up environment variables
- [ ] Test database migrations

### frontend
- [ ] Update API URLs to production backend
- [ ] Update WebSocket URLs (wss:// not ws://)
- [ ] Build production bundle
- [ ] Test production build locally
- [ ] Configure environment variables

### security
- [ ] Change default SECRET_KEY
- [ ] Restrict CORS to specific domains
- [ ] Enable HTTPS only
- [ ] Set secure cookie flags
- [ ] Add rate limiting
- [ ] Configure admin authentication

---

##  environment variables reference

### backend (.env)
```bash
# database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# redis
REDIS_URL=redis://host:6379

# security
SECRET_KEY=your-super-secret-key-min-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# cors
ALLOWED_HOSTS=https://your-frontend.vercel.app,https://your-frontend.netlify.app

# app
DEBUG=False
PROJECT_NAME="Realtime Chat Server"
VERSION="1.0.0"
```

### frontend (.env.production)
```bash
REACT_APP_API_BASE_URL=https://your-backend.railway.app
REACT_APP_WS_BASE_URL=wss://your-backend.railway.app
```

---

##  free tier limits

### railway
-  500 hours/month (enough for 1 app)
-  1GB RAM
-  1GB storage
-  PostgreSQL included
-  Redis included

### vercel
-  Unlimited deployments
-  100GB bandwidth/month
-  Automatic SSL
-  Custom domains

### render
-  750 hours/month
-  512MB RAM
-  PostgreSQL (90 days, then expires)
-  Redis (25MB)

### fly.io
-  3 shared VMs
-  256MB RAM each
-  3GB storage
-  160GB bandwidth

### netlify
-  100GB bandwidth/month
-  300 build minutes/month
-  Automatic SSL

---

##  common issues & solutions

### issue 1: websocket not working
**Solution**: Ensure you're using `wss://` (not `ws://`) for production

### issue 2: cors errors
**Solution**: Add your frontend URL to `ALLOWED_HOSTS` in backend

### issue 3: database connection failed
**Solution**: Check `DATABASE_URL` format and credentials

### issue 4: build failed
**Solution**: Check Python version (use 3.10) and requirements.txt

### issue 5: app sleeps (free tier)
**Solution**: Use a service like UptimeRobot to ping your app every 5 minutes

---

##  post-deployment

### 1. test everything
- [ ] Registration works
- [ ] Login works
- [ ] Chat creation works
- [ ] Real-time messaging works
- [ ] Admin panel accessible
- [ ] Password reset works

### 2. monitor
- Check deployment logs
- Monitor error rates
- Track response times
- Watch database usage

### 3. optimize
- Enable caching
- Compress responses
- Optimize images
- Minify frontend assets

---

##  pro tips

1. **Use Railway + Vercel** for easiest setup
2. **Keep free tier limits in mind** - apps may sleep after inactivity
3. **Use UptimeRobot** to keep your app awake
4. **Enable automatic deployments** from GitHub
5. **Set up custom domains** (free on most platforms)
6. **Monitor your usage** to avoid hitting limits
7. **Use environment variables** for all secrets
8. **Enable HTTPS** everywhere (automatic on most platforms)

---

##  additional resources

### railway
- Docs: https://docs.railway.app
- Discord: https://discord.gg/railway

### vercel
- Docs: https://vercel.com/docs
- Discord: https://vercel.com/discord

### render
- Docs: https://render.com/docs
- Discord: https://render.com/discord

### fly.io
- Docs: https://fly.io/docs
- Discord: https://fly.io/discord

---

##  deployment checklist

- [ ] Choose deployment platform
- [ ] Create accounts (GitHub, Railway, Vercel)
- [ ] Prepare backend code
- [ ] Prepare frontend code
- [ ] Set up database
- [ ] Set up Redis
- [ ] Configure environment variables
- [ ] Deploy backend
- [ ] Deploy frontend
- [ ] Update CORS settings
- [ ] Test all features
- [ ] Set up monitoring
- [ ] Configure custom domain (optional)

---

##  you're ready to deploy!

Choose your preferred option and follow the steps. **Railway + Vercel** is the easiest and most reliable for beginners.

Good luck with your deployment! 
