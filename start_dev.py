#!/usr/bin/env python3
"""
Development Startup Script

Starts both the Agent API server (port 8000) and React frontend (port 3000)
in separate processes for development.
"""

import subprocess
import sys
import os
import time
import signal
from threading import Thread

def start_agent_api():
    """Start the Agent API server"""
    print("🚀 Starting Agent API server...")
    os.chdir("/Users/arjunheregeek/Code/Connect")
    
    # Use the virtual environment Python
    cmd = ["/Users/arjunheregeek/Code/Connect/venv/bin/python", "app/api.py", "--host", "0.0.0.0", "--port", "8000"]
    return subprocess.Popen(cmd)

def start_react_frontend():
    """Start the React frontend"""
    print("🚀 Starting React frontend...")
    os.chdir("/Users/arjunheregeek/Code/Connect/frontend")
    
    cmd = ["npm", "start"]
    env = os.environ.copy()
    env["BROWSER"] = "none"  # Don't auto-open browser
    return subprocess.Popen(cmd, env=env)

def main():
    """Main startup function"""
    print("""
🌟 Connect Development Server
=============================

Starting both:
- Agent API (LangGraph): http://localhost:8000
- React Frontend: http://localhost:3000

Press Ctrl+C to stop both servers.
""")
    
    processes = []
    
    try:
        # Start Agent API
        agent_process = start_agent_api()
        processes.append(agent_process)
        time.sleep(2)  # Give it time to start
        
        # Start React frontend
        react_process = start_react_frontend()
        processes.append(react_process)
        
        print("""
✅ Both servers starting...

Agent API: http://localhost:8000
Frontend:  http://localhost:3000

Waiting for servers to be ready...
""")
        
        # Wait for both processes
        try:
            for process in processes:
                process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping servers...")
            
    except Exception as e:
        print(f"❌ Error starting servers: {e}")
        
    finally:
        # Clean up processes
        for process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                try:
                    process.kill()
                except:
                    pass
        
        print("✅ All servers stopped.")

if __name__ == "__main__":
    main()