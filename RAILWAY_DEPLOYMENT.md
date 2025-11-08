# railway deployment guide

## the issue you encountered

railway couldn't determine which folder to build because your repo has both `backend` and `frontend` folders at the root.

## solution: set root directory in railway

### step 1: configure railway project

when creating your railway project:

1. go to https://railway.app
2. click "new project"
3. select "deploy from github repo"
4. choose your repository
5. **important**: click on "settings" or "configure"
6. set **root directory** to `backend`
7. railway will now only look at the backend folder

### step 2: add postgresql database

1. in your railway project, click "+ new"
2. select "database"
3. choose "postgresql"
4. railway will automatically create a `DATABASE_URL` variable

### step 3: add redis

1. click "+ new" again
2. select "database"
3. choose "redis"
4. railway will automatically create a `REDIS_URL` variable

### step 4: configure environment variables

in your backend service settings, add these variables:

```bash
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
SECRET_KEY=your-super-secret-key-change-this-now
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_HOSTS=*
DEBUG=False
```

### step 5: deploy

railway will automatically deploy. wait 2-3 minutes.

## alternative: use railway cli

if you prefer using the cli:

```bash
# install railway cli
npm i -g @railway/cli

# login
railway login

# initialize in backend folder
cd backend
railway init

# link to your project
railway link

# deploy
railway up
```

## files created for you

i've created these files in your backend folder:

1. **railway.json** - railway configuration
2. **nixpacks.toml** - build configuration
3. **Procfile** - start command
4. **requirements.txt** - updated with all dependencies

## verify deployment

once deployed:

1. get your railway url (e.g., `https://your-app.up.railway.app`)
2. test the api: `https://your-app.up.railway.app/docs`
3. test admin panel: `https://your-app.up.railway.app/admin`
4. test health: `https://your-app.up.railway.app/health`

## frontend deployment (vercel)

after backend is deployed:

1. go to https://vercel.com
2. import your repository
3. set **root directory** to `frontend`
4. add environment variable:
   - `REACT_APP_API_BASE_URL`: your railway backend url
   - `REACT_APP_WS_BASE_URL`: your railway backend url (with wss://)
5. deploy

## update cors

after deploying frontend, update your railway backend:

1. go to railway backend service
2. add environment variable:
   ```
   ALLOWED_HOSTS=https://your-frontend.vercel.app,*
   ```
3. redeploy

## troubleshooting

### build fails

**error**: "could not determine how to build"
**solution**: make sure root directory is set to `backend` in railway settings

### import errors

**error**: "module not found"
**solution**: check that all dependencies are in `requirements.txt`

### database connection fails

**error**: "could not connect to database"
**solution**: verify `DATABASE_URL` is set correctly in environment variables

### port issues

**error**: "port already in use"
**solution**: make sure your app uses `$PORT` environment variable:
```python
# this is already correct in your code
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## quick checklist

- [ ] set root directory to `backend` in railway
- [ ] add postgresql database
- [ ] add redis database
- [ ] configure environment variables
- [ ] deploy backend
- [ ] get backend url
- [ ] deploy frontend to vercel
- [ ] update cors settings
- [ ] test everything

## next steps

1. push your changes to github:
   ```bash
   git add .
   git commit -m "add railway deployment config"
   git push
   ```

2. go to railway and set root directory to `backend`

3. railway will automatically redeploy

4. your backend will be live in 2-3 minutes

## important notes

- **root directory**: must be set to `backend` in railway settings
- **environment variables**: set all required variables before deploying
- **database**: railway provides free postgresql and redis
- **cors**: update after deploying frontend

your backend is now configured and ready to deploy on railway.
