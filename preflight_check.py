#!/usr/bin/env python3
"""
Pre-flight check for FPL Agent
Verifies all dependencies and configuration before starting
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Check Python version >= 3.10"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("❌ Python 3.10+ required")
        print(f"   Current: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def check_env_file():
    """Check .env file exists and has required variables"""
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found")
        print("   Create .env with OPENAI_API_KEY, OPENAI_API_HOST, etc.")
        return False
    
    required_vars = [
        "OPENAI_API_KEY",
        "OPENAI_API_HOST",
        "OPENAI_DEPLOYMENT",
        "OPENAI_API_VERSION"
    ]
    
    env_content = env_path.read_text()
    missing = []
    for var in required_vars:
        if var not in env_content:
            missing.append(var)
    
    if missing:
        print("❌ Missing required environment variables:")
        for var in missing:
            print(f"   - {var}")
        return False
    
    print("✅ .env file configured")
    return True

def check_dependencies():
    """Check all required packages are installed"""
    required = [
        ("langchain", "LangChain"),
        ("langchain_openai", "LangChain OpenAI"),
        ("pydantic", "Pydantic"),
        ("rich", "Rich"),
        ("requests", "Requests"),
        ("tenacity", "Tenacity")
    ]
    
    missing = []
    for module, name in required:
        try:
            __import__(module)
            print(f"✅ {name} installed")
        except ImportError:
            missing.append(name)
            print(f"❌ {name} not installed")
    
    if missing:
        print("\n❌ Missing dependencies. Install with:")
        print("   pip install -r requirements.txt")
        return False
    
    return True

def check_api_modules():
    """Check all FPL API modules are present"""
    modules = [
        "config.settings",
        "fpl_api.client",
        "fpl_api.bootstrap",
        "fpl_api.managers",
        "fpl_api.players",
        "fpl_api.fixtures",
        "tools.player_tools"
    ]
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module} available")
        except ImportError as e:
            print(f"❌ {module} import failed: {e}")
            return False
    
    return True

def check_fpl_api_connection():
    """Test connection to FPL API"""
    try:
        from fpl_api.client import FPLClient
        from fpl_api.bootstrap import BootstrapAPI
        client = FPLClient()
        api = BootstrapAPI(client)
        players = api.get_all_players()
        total = api.get_total_players()
        print(f"✅ FPL API connected ({total} players)")
        return True
    except Exception as e:
        print(f"❌ FPL API connection failed: {e}")
        return False

def check_azure_openai():
    """Test Azure OpenAI configuration (not connection)"""
    try:
        from config.settings import Settings
        settings = Settings()
        
        if not settings.openai_api_key:
            print("❌ OPENAI_API_KEY is empty")
            return False
        
        if not settings.openai_api_host:
            print("❌ OPENAI_API_HOST is empty")
            return False
        
        print(f"✅ Azure OpenAI configured")
        print(f"   Endpoint: {settings.openai_api_host}")
        print(f"   Deployment: {settings.openai_deployment}")
        return True
    except Exception as e:
        print(f"❌ Azure OpenAI configuration failed: {e}")
        return False

def main():
    """Run all pre-flight checks"""
    print("🚀 FPL Agent Pre-flight Check\n")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Environment File", check_env_file),
        ("Dependencies", check_dependencies),
        ("API Modules", check_api_modules),
        ("FPL API Connection", check_fpl_api_connection),
        ("Azure OpenAI Config", check_azure_openai),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{name}:")
        print("-" * 50)
        result = check_func()
        results.append(result)
    
    print("\n" + "=" * 50)
    print("\n📊 Summary:")
    print("-" * 50)
    
    passed = sum(results)
    total = len(results)
    
    for i, (name, _) in enumerate(checks):
        status = "✅" if results[i] else "❌"
        print(f"{status} {name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All checks passed! Ready to launch.")
        print("\nRun: python main.py")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
