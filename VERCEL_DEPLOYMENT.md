# Vercel Deployment Guide for Connect App

## Overview
This guide will help you deploy both the React Frontend and Agent API to Vercel.

## Project Structure
```
Connect/
├── frontend/          # React app
├── api/              # Vercel serverless functions
│   ├── ask.py       # Main agent endpoint
│   ├── health.py    # Health check
│   └── _cors.py     # CORS handler
├── agent/           # Agent code (used by serverless functions)
├── vercel.json      # Vercel configuration
└── requirements.txt # Python dependencies
```

## Prerequisites
1. Vercel account (sign up at vercel.com)
2. GitHub repository with your code
3. Environment variables ready:
   - NEO4J_URI
   - NEO_USERNAME
   - NEO_PASSWORD
   - OPENAI_API_KEY

## Deployment Steps

### 1. Install Vercel CLI (Optional)
```bash
npm install -g vercel
```

### 2. Login to Vercel
```bash
vercel login
```

### 3. Deploy from GitHub (Recommended)

#### A. Go to Vercel Dashboard
- Visit https://vercel.com/dashboard
- Click "Add New..." → "Project"
- Import your GitHub repository (Connect)

#### B. Configure Project
- **Framework Preset**: Create React App
- **Root Directory**: Leave as `.` (root)
- **Build Command**: `cd frontend && npm install && npm run build`
- **Output Directory**: `frontend/build`
- **Install Command**: `cd frontend && npm install`

#### C. Add Environment Variables
In Vercel dashboard, go to Settings → Environment Variables:

```
NEO4J_URI = neo4j+s://your-instance.databases.neo4j.io
NEO_USERNAME = neo4j
NEO_PASSWORD = your_password
OPENAI_API_KEY = sk-...
```

Make sure to add them for **Production**, **Preview**, and **Development** environments.

### 4. Deploy from CLI (Alternative)

```bash
cd /Users/arjunheregeek/Code/Connect
vercel
```

Follow the prompts:
- Set up and deploy? **Y**
- Which scope? Select your account
- Link to existing project? **N** (first time)
- What's your project's name? **connect-app**
- In which directory is your code located? **.**
- Want to override the settings? **Y**
  - Build Command: `cd frontend && npm run build`
  - Output Directory: `frontend/build`
  - Development Command: `cd frontend && npm start`

### 5. Set Environment Variables (CLI)
```bash
vercel env add NEO4J_URI
vercel env add NEO_USERNAME
vercel env add NEO_PASSWORD
vercel env add OPENAI_API_KEY
```

### 6. Verify Deployment

Once deployed, Vercel will give you URLs:
```
Production: https://connect-app.vercel.app
API Endpoint: https://connect-app.vercel.app/api/ask
Health Check: https://connect-app.vercel.app/api/health
```

Test the API:
```bash
curl -X POST https://connect-app.vercel.app/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Who has Python skills?"}'
```

### 7. Update Frontend API URL

The frontend is already configured to use `/api` which will automatically route to the serverless functions on Vercel.

## How It Works

### Architecture on Vercel:
```
User Request → Vercel Edge Network
    ↓
    ├→ Static Files (React) → /frontend/*
    └→ Serverless Functions → /api/*
           ↓
           Python Handler (api/ask.py)
           ↓
           LangGraph Agent
           ↓
           MCP Server (Render)
           ↓
           Neo4j Database
```

### Routing:
- `/` → React Frontend
- `/api/ask` → Agent serverless function
- `/api/health` → Health check

### Cold Starts:
- First request after inactivity: ~3-5 seconds
- Subsequent requests: ~500ms-2s
- Free tier: Functions sleep after 15 min

## Troubleshooting

### Issue: Function Timeout
**Error**: Function exceeded maximum duration
**Solution**: 
- Upgrade to Pro plan (60s timeout)
- Optimize agent to respond faster
- Consider deploying Agent API to Render instead

### Issue: Module Not Found
**Error**: `ModuleNotFoundError: No module named 'agent'`
**Solution**: Check that `requirements.txt` includes all dependencies

### Issue: Environment Variables Not Set
**Error**: Database connection failed
**Solution**: Verify environment variables in Vercel dashboard

### Issue: CORS Errors
**Error**: CORS policy blocked the request
**Solution**: The `_cors.py` handler should fix this, but verify headers

## Production Checklist

- [ ] All environment variables set in Vercel
- [ ] requirements.txt includes all dependencies
- [ ] Frontend builds successfully
- [ ] API endpoints respond correctly
- [ ] CORS configured properly
- [ ] MCP Server is accessible from Vercel
- [ ] Neo4j database allows connections from Vercel IPs

## Monitoring

### View Logs:
```bash
vercel logs
```

### View Deployment:
```bash
vercel ls
```

### View Functions:
```bash
vercel inspect [deployment-url]
```

## Cost Considerations

### Free Tier Includes:
- 100GB bandwidth
- 100 serverless function executions/day
- No credit card required

### Pro Plan ($20/month):
- 1TB bandwidth
- Unlimited function executions
- 60s function timeout (vs 10s)
- Better cold start performance

## Next Steps

After successful deployment:
1. Test all endpoints
2. Monitor function execution times
3. Check error logs
4. Set up custom domain (optional)
5. Configure preview deployments for branches

## Support

- Vercel Documentation: https://vercel.com/docs
- Vercel Support: https://vercel.com/support

## Notes

- Python runtime: 3.9+ (Vercel default)
- Function region: Auto (closest to user)
- Execution limit: 10s (Free), 60s (Pro)
- Memory: 1024MB default
