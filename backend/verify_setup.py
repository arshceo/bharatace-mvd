"""
Setup Verification Script
Checks if everything is properly configured
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("  ⚠️  Warning: Python 3.10+ recommended")
    return True

def check_env_file():
    """Check if .env file exists"""
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        print("✓ .env file found")
        return True
    else:
        print("✗ .env file not found")
        print("  Please copy .env.example to .env and configure it")
        return False

def check_packages():
    """Check if required packages are installed"""
    required_packages = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "supabase",
        "llama_index",
        "google.generativeai"
    ]
    
    all_installed = True
    for package in required_packages:
        try:
            __import__(package.replace(".", "_") if "." in package else package)
            print(f"✓ {package} installed")
        except ImportError:
            print(f"✗ {package} not installed")
            all_installed = False
    
    return all_installed

def check_env_variables():
    """Check if environment variables are set"""
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ["SUPABASE_URL", "SUPABASE_KEY", "GOOGLE_API_KEY"]
    all_set = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value and value != f"your-{var.lower().replace('_', '-')}":
            print(f"✓ {var} configured")
        else:
            print(f"✗ {var} not configured")
            all_set = False
    
    return all_set

def check_server():
    """Check if server is accessible"""
    try:
        import requests
        response = requests.get("http://localhost:8000", timeout=2)
        if response.status_code == 200:
            print("✓ Server is running on http://localhost:8000")
            return True
        else:
            print("✗ Server responded with error")
            return False
    except requests.exceptions.ConnectionError:
        print("⚠️  Server is not running")
        print("  Run: python main.py")
        return False
    except Exception as e:
        print(f"✗ Error checking server: {str(e)}")
        return False

def main():
    print("\n" + "="*50)
    print("BharatAce Backend - Setup Verification")
    print("="*50 + "\n")
    
    checks = {
        "Python Version": check_python_version(),
        "Environment File": check_env_file(),
        "Required Packages": check_packages(),
        "Environment Variables": check_env_variables(),
        "Server Status": check_server()
    }
    
    print("\n" + "="*50)
    print("Summary")
    print("="*50)
    
    passed = sum(checks.values())
    total = len(checks)
    
    for check, status in checks.items():
        status_icon = "✓" if status else "✗"
        print(f"{status_icon} {check}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All checks passed! Your setup is complete.")
        print("\nNext steps:")
        print("1. Visit http://localhost:8000/docs")
        print("2. Run: python test_api.py")
        print("3. Read: QUICKSTART.md")
    else:
        print("\n⚠️  Some checks failed. Please review the issues above.")
        print("\nRefer to README.md for setup instructions.")
    
    print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main()
