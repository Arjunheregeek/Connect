#!/usr/bin/env python3
"""
Test script to verify Vercel deployment setup

Run this locally before deploying to catch any issues.
"""

import sys
import os

def check_files():
    """Check that all required files exist"""
    required_files = [
        'vercel.json',
        'requirements.txt',
        'api/ask.py',
        'api/health.py',
        'frontend/package.json',
        'frontend/src/App.js'
    ]
    
    print("🔍 Checking required files...")
    missing = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - MISSING!")
            missing.append(file)
    
    return len(missing) == 0

def check_imports():
    """Check that key imports work"""
    print("\n🔍 Checking Python imports...")
    
    try:
        sys.path.insert(0, os.getcwd())
        from agent.workflow.graph_builder import WorkflowGraphBuilder
        print("  ✅ WorkflowGraphBuilder")
        
        from agent.mcp_client import MCPClient
        print("  ✅ MCPClient")
        
        from app.agent_run import ConnectAgent
        print("  ✅ ConnectAgent")
        
        return True
    except ImportError as e:
        print(f"  ❌ Import failed: {e}")
        return False

def check_env_vars():
    """Check environment variables"""
    print("\n🔍 Checking environment variables...")
    
    required_vars = [
        'NEO4J_URI',
        'NEO_USERNAME',
        'NEO_PASSWORD',
        'OPENAI_API_KEY'
    ]
    
    missing = []
    for var in required_vars:
        if os.getenv(var):
            print(f"  ✅ {var} is set")
        else:
            print(f"  ⚠️  {var} - NOT SET (will need in Vercel)")
            missing.append(var)
    
    return missing

def main():
    """Run all checks"""
    print("""
╔═══════════════════════════════════════╗
║   Vercel Deployment Setup Checker    ║
╚═══════════════════════════════════════╝
""")
    
    files_ok = check_files()
    imports_ok = check_imports()
    missing_env = check_env_vars()
    
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    
    if files_ok:
        print("✅ All required files present")
    else:
        print("❌ Some files are missing")
    
    if imports_ok:
        print("✅ All imports working")
    else:
        print("❌ Import errors detected")
    
    if not missing_env:
        print("✅ All environment variables set")
    else:
        print(f"⚠️  {len(missing_env)} environment variables need to be set in Vercel:")
        for var in missing_env:
            print(f"   - {var}")
    
    print("\n" + "="*50)
    
    if files_ok and imports_ok:
        print("🎉 Ready for Vercel deployment!")
        print("\nNext steps:")
        print("1. Commit and push to GitHub")
        print("2. Import project in Vercel dashboard")
        print("3. Set environment variables in Vercel")
        print("4. Deploy!")
        return 0
    else:
        print("❌ Fix the issues above before deploying")
        return 1

if __name__ == "__main__":
    sys.exit(main())
