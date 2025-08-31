#!/usr/bin/env python3
"""
Deployment setup script for ESG Reporting Application
Handles initialization of Kaleido and Playwright for remote server deployment
"""

import subprocess
import sys
import os
import kaleido


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr.strip()}")
        return False

def setup_kaleido():
    """Initialize Kaleido Chrome for chart generation"""
    print("🔄 Initializing Kaleido Chrome...")
    try:
        import kaleido
        kaleido.get_chrome_sync()
        print("✅ Kaleido Chrome initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Kaleido Chrome initialization failed: {e}")
        return False

def setup_playwright():
    """Install Playwright browsers"""
    return run_command("playwright install", "Installing Playwright browsers")

def setup_playwright_chromium_only():
    """Install only Chromium browser for Playwright (faster for production)"""
    return run_command("playwright install chromium", "Installing Playwright Chromium browser")

def main():
    """Main setup function"""
    print("🚀 Starting deployment setup for ESG Reporting Application...")
    print("=" * 60)
    
    # Check if running in production environment
    is_production = os.getenv('ENVIRONMENT', '').lower() == 'production'
    setup_kaleido()
    success = True
    
    # Setup Kaleido
    if not setup_kaleido():
        success = False
    
    # Setup Playwright
    if is_production:
        # In production, only install Chromium to save space and time
        if not setup_playwright_chromium_only():
            success = False
    else:
        # In development/staging, install all browsers
        if not setup_playwright():
            success = False
    
    print("=" * 60)
    
    if success:
        print("🎉 Deployment setup completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Start your application: python main.py")
        print("   2. Or use uvicorn: uvicorn main:app --host 0.0.0.0 --port 8000")
        return 0
    else:
        print("💥 Deployment setup failed!")
        print("\n🔧 Troubleshooting:")
        print("   1. Ensure you have internet connectivity")
        print("   2. Check that you have sufficient disk space")
        print("   3. Verify Python and pip are properly installed")
        print("   4. Try running the setup script again")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 