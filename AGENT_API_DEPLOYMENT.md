# Agent API Deployment Guide - Render

This document provides complete instructions for deploying the Connect Agent API to Render.

---

## 📋 Pre-Deployment Checklist

✅ **Files Ready:**
- `requirements.txt` - All Python dependencies listed
- `app/api.py` - Main FastAPI application
- `app/agent_run.py` - ConnectAgent class
- `agent/` - LangGraph workflow components
- `.gitignore` - Updated with node_modules and build artifacts

✅ **Dependencies Verified:**
- FastAPI, Uvicorn for web server
- LangGraph, LangChain for agent
- Neo4j driver for database
- OpenAI for AI capabilities
- All 20+ required packages in requirements.txt

✅ **Local Testing Complete:**
- ✅ Agent API running on localhost:8000
- ✅ Successfully processed test queries
- ✅ Connected to MCP server on Render
- ✅ Retrieved data from Neo4j (1,992 profiles)

---

## 🚀 Render Deployment Configuration

### **Service Details**

| Setting | Value |
|---------|-------|
| **Service Type** | Web Service |
| **Environment** | Python 3 |
| **Region** | Choose closest to your users |
| **Branch** | `front-end` (or `main`) |
| **Root Directory** | `.` (project root) |

### **Build & Start Commands**

#### **Build Command:**
```bash
pip install -r requirements.txt
```

#### **Start Command:**
```bash
uvicorn app.api:app --host 0.0.0.0 --port $PORT
```

**Note:** Render automatically provides the `$PORT` environment variable.

---

## 🔐 Environment Variables

Add these environment variables in Render Dashboard → Environment:

### **Required Variables:**

```bash
# Neo4j Database Configuration
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO_USERNAME=neo4j
NEO_PASSWORD=your_neo4j_password

# OpenAI API Key
OPENAI_API_KEY=sk-proj-your-openai-api-key

# MCP Server Configuration (already deployed)
MCP_API_KEY=f435d1c3b1c5e66db047585265bbe4535a4b5f3389e134b54abe482b7b637ac3

# Server Configuration (Optional - Render handles these)
HOST=0.0.0.0
# PORT is automatically set by Render
```

### **Environment Variable Sources:**
- `NEO4J_URI`, `NEO_USERNAME`, `NEO_PASSWORD` - From your Neo4j Aura console
- `OPENAI_API_KEY` - From OpenAI platform (https://platform.openai.com/api-keys)
- `MCP_API_KEY` - Already configured for deployed MCP server

---

## 📁 Project Structure

```
Connect/
├── app/
│   ├── api.py              # Main FastAPI application (ENTRY POINT)
│   └── agent_run.py        # ConnectAgent wrapper class
├── agent/
│   ├── workflow/
│   │   └── graph_builder.py
│   ├── nodes/
│   │   ├── planner/
│   │   ├── executor/
│   │   └── synthesizer/
│   ├── state/
│   └── mcp_client/         # MCP server client
├── requirements.txt        # All Python dependencies
└── .env                    # Local env (not deployed)
```

**Entry Point:** `app/api.py` → `app:app` FastAPI instance

---

## 🔗 API Endpoints

Once deployed, your Agent API will expose:

### **Health Check:**
```bash
GET https://your-app.onrender.com/
```

**Response:**
```json
{
  "status": "healthy",
  "agent_info": {
    "agent_type": "SimplifiedConnectAgent",
    "version": "1.0.0",
    "capabilities": [...],
    "workflow": "Linear LangGraph (Planning → Execution → Synthesis)",
    "tools": "24+ MCP tools for Neo4j knowledge graph",
    "data_size": "1,992+ professional profiles"
  }
}
```

### **Ask Question:**
```bash
POST https://your-app.onrender.com/ask
Content-Type: application/json

{
  "question": "Find Python developers",
  "conversation_id": "optional-conv-id"
}
```

**Response:**
```json
{
  "response": "Here are the results...",
  "success": true,
  "metadata": {
    "conversation_id": "...",
    "execution_time": 3.98,
    "tools_used": [],
    "data_found": 1,
    "workflow_status": "completed"
  }
}
```

### **Agent Info:**
```bash
GET https://your-app.onrender.com/agent/info
```

### **Session Management:**
```bash
GET https://your-app.onrender.com/session/summary
POST https://your-app.onrender.com/session/clear
```

---

## 📝 Step-by-Step Deployment

### **1. Create New Web Service**
1. Go to Render Dashboard (https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository

### **2. Configure Service**
```
Name: connect-agent-api
Environment: Python 3
Region: Oregon (US West) or closest to you
Branch: front-end
Root Directory: .
```

### **3. Build Settings**
```
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.api:app --host 0.0.0.0 --port $PORT
```

### **4. Environment Variables**
Add all variables from the "Environment Variables" section above.

### **5. Deploy**
- Click **"Create Web Service"**
- Wait for build to complete (~3-5 minutes)
- Check logs for "Uvicorn running on..."

### **6. Verify Deployment**
```bash
# Test health endpoint
curl https://your-app.onrender.com/

# Test query endpoint
curl -X POST https://your-app.onrender.com/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Find Python developers"}'
```

---

## 🔍 Testing Checklist

After deployment, verify:

- [ ] Health check returns status "healthy"
- [ ] Agent info shows correct version and capabilities
- [ ] Test query: "Find Python developers" returns results
- [ ] Test query: "Who works at Google?" returns results
- [ ] Response time < 10 seconds
- [ ] No errors in Render logs
- [ ] CORS allows requests from frontend domain

---

## 🐛 Troubleshooting

### **Build Fails**
- Check requirements.txt includes all dependencies
- Verify Python version compatibility (3.8+)
- Check Render build logs for specific errors

### **Start Command Fails**
- Ensure `app/api.py` exists and is executable
- Verify `app:app` FastAPI instance is defined
- Check for syntax errors in Python files

### **Runtime Errors**
- Verify all environment variables are set
- Check Neo4j credentials are correct
- Ensure MCP server (https://connect-vxll.onrender.com) is accessible
- Review Render runtime logs

### **Slow Responses**
- Cold start (first request after idle) takes ~10-20 seconds
- Consider upgrading to paid plan to prevent spin-down
- Check Neo4j Aura connection performance

### **CORS Issues**
- Update `app/api.py` CORS settings with frontend domain
- Change `allow_origins=["*"]` to specific domains in production

---

## 📊 Expected Deployment URL

After successful deployment:
```
https://connect-agent-api-XXXX.onrender.com
```

**Save this URL** - you'll need it for:
1. React frontend configuration (update `AGENT_API_URL` in `frontend/src/App.js`)
2. API testing and integration
3. Production monitoring

---

## 🔄 System Architecture

```
React Frontend (Vercel)
    ↓ HTTP POST /ask
Agent API (Render) ← YOU ARE HERE
    ↓ HTTP MCP Protocol
MCP Server (Render) ← https://connect-vxll.onrender.com
    ↓ Cypher Queries
Neo4j Aura (Cloud Database)
```

---

## 📈 Next Steps After Deployment

1. **Test deployed API** with curl/Postman
2. **Update React frontend** with deployed API URL
3. **Deploy React frontend** to Vercel
4. **Test end-to-end flow** from UI
5. **Set up monitoring** (Render provides basic monitoring)
6. **Configure custom domain** (optional)

---

## 💡 Production Recommendations

### **Performance:**
- Enable Auto-Scaling if traffic increases
- Consider Render's paid plans for always-on service
- Monitor response times and optimize slow queries

### **Security:**
- Add API key authentication to Agent API endpoints
- Restrict CORS to specific frontend domains
- Regularly rotate environment variable secrets

### **Monitoring:**
- Set up Render's monitoring and alerts
- Log all queries for debugging
- Track success/failure rates

### **Cost Optimization:**
- Free tier spins down after inactivity
- Upgrade to paid plan for production use
- Monitor usage to avoid unexpected costs

---

## 📞 Support

- **Render Docs:** https://render.com/docs
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **LangGraph Docs:** https://langchain-ai.github.io/langgraph/

---

**Ready to deploy?** Follow the steps above and your Agent API will be live in ~5 minutes! 🚀
