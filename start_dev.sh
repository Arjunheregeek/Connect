#!/bin/bash

# Connect Development Server Startup Script
# Starts both Agent API and React Frontend

echo "🌟 Connect Development Server"
echo "============================="
echo ""

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source /Users/arjunheregeek/Code/Connect/venv/bin/activate

echo "Starting both:"
echo "- Agent API (LangGraph): http://localhost:8000"  
echo "- React Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers."
echo ""

# Function to cleanup processes on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $AGENT_PID $REACT_PID 2>/dev/null
    wait $AGENT_PID $REACT_PID 2>/dev/null
    echo "✅ All servers stopped."
    exit 0
}

# Set trap to cleanup on Ctrl+C
trap cleanup SIGINT

# Start Agent API in background
echo "🚀 Starting Agent API server..."
cd "/Users/arjunheregeek/Code/Connect"
/Users/arjunheregeek/Code/Connect/venv/bin/python app/api.py --host 0.0.0.0 --port 8000 &
AGENT_PID=$!

# Wait a bit for agent to start
sleep 3

# Start React frontend in background  
echo "🚀 Starting React frontend..."
cd "/Users/arjunheregeek/Code/Connect/frontend"
BROWSER=none npm start &
REACT_PID=$!

echo ""
echo "✅ Both servers starting..."
echo ""
echo "Agent API: http://localhost:8000"
echo "Frontend:  http://localhost:3000"
echo ""
echo "Waiting for servers to be ready..."

# Wait for both processes
wait $AGENT_PID $REACT_PID