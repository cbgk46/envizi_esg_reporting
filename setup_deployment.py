#!/usr/bin/env python3
"""
Deployment setup script for ESG Reporting Application
Handles initialization of dependencies and browsers for remote server deployment
"""

import subprocess
import sys
import os
import asyncio
import logging

# Setup logging for setup script
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    logger.info(f"Running command: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout.strip()}")
        logger.info(f"Command succeeded: {command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr.strip()}")
        logger.error(f"Command failed: {command} - {e.stderr.strip()}")
        return False



def setup_playwright_deps():
    """Install Playwright system dependencies"""
    success = run_command("playwright install-deps", "Installing Playwright system dependencies")
    if not success:
        # Try with sudo for system-level dependencies
        print("⚠️  Retrying with sudo...")
        success = run_command("sudo playwright install-deps", "Installing Playwright system dependencies (with sudo)")
    return success

def setup_playwright():
    """Install Playwright browsers"""
    # Try multiple installation approaches for robustness
    success = run_command("playwright install", "Installing Playwright browsers")
    if not success:
        print("⚠️  Standard installation failed, trying with --force...")
        success = run_command("playwright install --force", "Installing Playwright browsers (force)")
    return success

def setup_playwright_chromium_only():
    """Install only Chromium browser for Playwright (faster for production)"""
    # Try multiple installation approaches for robustness
    success = run_command("playwright install chromium", "Installing Playwright Chromium browser")
    if not success:
        print("⚠️  Standard installation failed, trying with --force...")
        success = run_command("playwright install chromium --force", "Installing Playwright Chromium browser (force)")
    return success

def verify_playwright_installation():
    """Verify that Playwright browsers are properly installed"""
    print("🔍 Verifying Playwright browser installation...")
    
    # Method 1: Check file system for browser installation
    try:
        import os.path
        playwright_cache = os.path.expanduser("~/.cache/ms-playwright")
        
        if os.path.isdir(playwright_cache):
            # Look for chromium directories (standard and headless shell)
            chromium_dirs = [d for d in os.listdir(playwright_cache) 
                           if d.startswith('chromium') and os.path.isdir(os.path.join(playwright_cache, d))]
            
            if chromium_dirs:
                print(f"✅ Chromium browser files found in: {playwright_cache}")
                print(f"   Installed versions: {', '.join(chromium_dirs)}")
                
                # Method 2: Try launching browser to verify it works
                try:
                    from playwright.sync_api import sync_playwright
                    with sync_playwright() as p:
                        browser = p.chromium.launch(headless=True)
                        browser.close()
                        print("✅ Chromium browser launch test successful")
                        return True
                except Exception as launch_error:
                    print(f"⚠️  Browser files found but launch test failed: {launch_error}")
                    print("   Files exist but browser may not be functional")
                    return False
            else:
                print(f"❌ No Chromium browser directories found in {playwright_cache}")
                print(f"   Available items: {os.listdir(playwright_cache) if os.path.exists(playwright_cache) else 'Directory does not exist'}")
                return False
        else:
            print(f"❌ Playwright cache directory not found: {playwright_cache}")
            return False
            
    except Exception as e:
        print(f"❌ Error during browser verification: {e}")
        logger.error(f"Browser verification error: {e}")
        
        # Method 3: Fallback - try direct browser launch
        try:
            print("🔄 Trying fallback verification with direct browser launch...")
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                browser.close()
                print("✅ Fallback verification successful - browser can be launched")
                return True
        except Exception as fallback_error:
            print(f"❌ Fallback verification failed: {fallback_error}")
            return False

def test_playwright():
    """Test Playwright PDF generation capability"""
    print("🔄 Testing Playwright PDF generation...")
    try:
        async def test_pdf():
            from playwright.async_api import async_playwright
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                await page.set_content("<h1>Test PDF</h1><p>Playwright is working!</p>")
                pdf_bytes = await page.pdf(format='A4')
                await browser.close()
                return len(pdf_bytes)
        
        pdf_size = asyncio.run(test_pdf())
        print(f"✅ Playwright PDF generation test successful: {pdf_size} bytes generated")
        logger.info(f"Playwright test successful: {pdf_size} bytes generated")
        return True
    except Exception as e:
        print(f"❌ Playwright test failed: {e}")
        logger.error(f"Playwright test failed: {e}")
        return False

def check_dependencies():
    """Check if all required Python packages are installed"""
    print("🔄 Checking Python dependencies...")
    required_packages = [
        'fastapi', 'uvicorn', 'jinja2', 'playwright', 
        'plotly', 'openai', 'markdown'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"⚠️  Missing packages: {', '.join(missing_packages)}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    print("✅ All required Python dependencies are installed")
    return True

def main():
    """Main setup function"""
    print("🚀 Starting deployment setup for ESG Reporting Application...")
    print("=" * 70)
    
    # Check if running in production environment
    is_production = os.getenv('ENVIRONMENT', '').lower() == 'production'
    print(f"🌍 Environment: {'Production' if is_production else 'Development'}")
    print(f"🐍 Python: {sys.version}")
    print(f"📁 Working directory: {os.getcwd()}")
    print("=" * 70)
    
    success = True
    
    # Step 1: Check dependencies
    print("\n1️⃣ CHECKING DEPENDENCIES")
    print("-" * 30)
    if not check_dependencies():
        print("⚠️  Please install missing dependencies first:")
        print("   pip install -r requirements.txt")
        success = False
    
    # Step 2: Setup Playwright
    print("\n2️⃣ SETTING UP PLAYWRIGHT")
    print("-" * 30)
    
    # First, install system dependencies - this is critical for Playwright to work
    print("📦 Installing Playwright system dependencies...")
    if not setup_playwright_deps():
        print("❌ CRITICAL: Playwright system dependencies installation failed!")
        print("   This will prevent PDF generation from working.")
        print("   Manual installation required:")
        print("   sudo playwright install-deps")
        success = False
    
    # Then install browsers - only continue if system deps succeeded or in non-critical mode
    if success or not is_production:
        print("🌐 Installing Playwright browsers...")
        browser_install_success = False
        
        if is_production:
            # In production, only install Chromium to save space and time
            browser_install_success = setup_playwright_chromium_only()
        else:
            # In development/staging, install all browsers
            browser_install_success = setup_playwright()
        
        if not browser_install_success:
            print("❌ CRITICAL: Playwright browser installation failed!")
            success = False
        else:
            # Verify installation worked
            if not verify_playwright_installation():
                print("❌ CRITICAL: Playwright browser verification failed!")
                success = False
    
    # Step 3: Test Playwright functionality
    if success:
        print("🧪 Testing Playwright functionality...")
        if not test_playwright():
            print("❌ CRITICAL: Playwright PDF generation test failed!")
            success = False
        else:
            print("✅ Playwright is properly configured and functional")
    
    # Step 4: Test application imports
    print("\n3️⃣ TESTING APPLICATION")
    print("-" * 30)
    try:
        print("🔄 Testing application imports...")
        # Test critical imports without starting the server
        import main
        import auth
        import config
        from services.chart_service import create_spider_chart
        from services.questionnaire_processor import process_questionnaire_responses
        print("✅ Application imports successful")
    except Exception as e:
        print(f"❌ Application import test failed: {e}")
        logger.error(f"Application import test failed: {e}")
        success = False
    
    print("\n" + "=" * 70)
    
    if success:
        print("🎉 DEPLOYMENT SETUP COMPLETED SUCCESSFULLY!")
        print("\n📋 Next steps:")
        print("   1. Start the application:")
        print("      python main.py")
        print("   2. Or use uvicorn with custom settings:")
        print("      uvicorn main:app --host 0.0.0.0 --port 8000")
        print("   3. Or with debug logging:")
        print("      LOG_LEVEL=DEBUG python main.py")
        print("\n🔧 Environment variables you can set:")
        print("   - LOG_LEVEL=DEBUG (for detailed logging)")
        print("   - ENVIRONMENT=production (for production optimizations)")
        print("   - HOST=0.0.0.0 (server bind address)")
        print("   - PORT=8000 (server port)")
        print("\n📊 Application will be available at:")
        print("   http://localhost:8000 (or your configured host:port)")
        return 0
    else:
        print("💥 DEPLOYMENT SETUP FAILED!")
        print("\n🔧 General Troubleshooting:")
        print("   1. Ensure you have internet connectivity")
        print("   2. Check that you have sufficient disk space (>2GB for browsers)")
        print("   3. Verify Python and pip are properly installed")
        print("   4. Run with verbose logging:")
        print("      LOG_LEVEL=DEBUG python setup_deployment.py")
        
        print("\n🎭 Playwright-Specific Troubleshooting:")
        print("   1. Install system dependencies manually:")
        print("      sudo playwright install-deps")
        print("   2. Install browsers manually:")
        print("      playwright install chromium")
        print("   3. Verify installation by checking cache:")
        print("      ls -la ~/.cache/ms-playwright/")
        print("   4. Test browser launch:")
        print("      python -c \"from playwright.sync_api import sync_playwright; p = sync_playwright().start(); browser = p.chromium.launch(); browser.close(); p.stop()\"")
        print("   5. Clear browser cache and reinstall:")
        print("      rm -rf ~/.cache/ms-playwright")
        print("      playwright install chromium")
        
        print("\n📚 Additional Resources:")
        print("   - Deployment debugging guide: cat DEPLOYMENT_DEBUGGING.md")
        print("   - Run diagnostic script: python deployment_debug.py")
        print("   - Playwright docs: https://playwright.dev/python/docs/browsers")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 