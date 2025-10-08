# 🚀 Agent API Deployment - Quick Reference

## ⚡ TL;DR - Deploy in 5 Minutes

### **Render Configuration:**
```
Service Type:    Web Service
Build Command:   pip install -r requirements.txt
Start Command:   uvicorn app.api:app --host 0.0.0.0 --port $PORT
Root Directory:  .
Branch:          front-end
```

### **Required Environment Variables:**
```bash
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO_USERNAME=neo4j
NEO_PASSWORD=your_password
OPENAI_API_KEY=sk-proj-your-key
MCP_API_KEY=f435d1c3b1c5e66db047585265bbe4535a4b5f3389e134b54abe482b7b637ac3
```

### **Test After Deployment:**
```bash
# Health check
curl https://your-app.onrender.com/

# Test query
curl -X POST https://your-app.onrender.com/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Find Python developers"}'
```

### **Next Step:**
Update React frontend `App.js`:
```javascript
const AGENT_API_URL = 'https://your-app.onrender.com';
```

---

## 📋 Pre-Deployment Verification

✅ All files ready:
- `requirements.txt` (20+ dependencies)
- `app/api.py` (FastAPI entry point)
- `app/agent_run.py` (ConnectAgent class)
- `agent/` directory (LangGraph workflow)
- `.gitignore` (updated with node_modules)

✅ Local testing passed:
- Agent API works on localhost:8000
- Successfully queries MCP server
- Returns results from Neo4j (1,992 profiles)

✅ Dependencies verified:
```
fastapi, uvicorn, langgraph, langchain, neo4j, 
openai, pydantic-settings, httpx, aiohttp, and more
```

---

## 🎯 Deployment Checklist

- [ ] Create Render account (if needed)
- [ ] Connect GitHub repository
- [ ] Create new Web Service
- [ ] Set Build Command: `pip install -r requirements.txt`
- [ ] Set Start Command: `uvicorn app.api:app --host 0.0.0.0 --port $PORT`
- [ ] Add all 5 environment variables
- [ ] Click "Create Web Service"
- [ ] Wait for build (~3-5 minutes)
- [ ] Test health endpoint
- [ ] Test /ask endpoint with sample query
- [ ] Save deployed URL
- [ ] Update React frontend with new URL

---

## 🔗 Architecture Flow

```
User → React (Vercel)
          ↓
      Agent API (Render) ← DEPLOYING THIS
          ↓
      MCP Server (Render) ← ALREADY DEPLOYED
          ↓
      Neo4j Aura ← ALREADY RUNNING
```

---

## 📊 Expected Results

**Deployment Time:** 3-5 minutes
**Expected URL:** `https://connect-agent-api-XXXX.onrender.com`
**First Response:** ~10-20 seconds (cold start)
**Normal Response:** 2-5 seconds

---

## ⚠️ Common Issues & Fixes

**Build fails?**
→ Check requirements.txt syntax
→ Verify all packages are available on PyPI

**Start command fails?**
→ Ensure `app/api.py` exists
→ Check for Python syntax errors

**Runtime errors?**
→ Verify environment variables are set
→ Check Neo4j credentials
→ Ensure MCP server is accessible

**Slow responses?**
→ First request after idle (cold start) is slow
→ Upgrade to paid plan to stay always-on

---

See `AGENT_API_DEPLOYMENT.md` for detailed instructions.
