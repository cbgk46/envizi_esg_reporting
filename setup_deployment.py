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

def test_kaleido():
    """Test Kaleido installation and chart generation capability"""
    print("🔄 Testing Kaleido chart generation...")
    try:
        # Test basic chart generation without triggering Chrome download
        import plotly.graph_objects as go
        import plotly.io as pio
        
        # Create a simple test figure
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[1, 2, 3], y=[4, 5, 6], name="test"))
        
        # Test image generation (this will trigger Kaleido initialization if needed)
        img_bytes = pio.to_image(fig, format="png", width=400, height=300)
        
        print(f"✅ Kaleido chart generation test successful: {len(img_bytes)} bytes generated")
        logger.info(f"Kaleido test successful: {len(img_bytes)} bytes generated")
        return True
    except Exception as e:
        print(f"⚠️  Kaleido test failed: {e}")
        print("   📝 Note: Kaleido will auto-initialize when first used by the application")
        logger.warning(f"Kaleido test failed: {e}")
        # Don't fail the setup for Kaleido issues since we have lazy initialization
        return True

def setup_playwright():
    """Install Playwright browsers"""
    return run_command("playwright install", "Installing Playwright browsers")

def setup_playwright_chromium_only():
    """Install only Chromium browser for Playwright (faster for production)"""
    return run_command("playwright install chromium", "Installing Playwright Chromium browser")

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
        'plotly', 'kaleido', 'openai', 'markdown'
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
    if is_production:
        # In production, only install Chromium to save space and time
        if not setup_playwright_chromium_only():
            success = False
    else:
        # In development/staging, install all browsers
        if not setup_playwright():
            success = False
    
    # Step 3: Test Playwright
    if success:
        if not test_playwright():
            success = False
    
    # Step 4: Test Kaleido (non-blocking)
    print("\n3️⃣ TESTING CHART GENERATION")
    print("-" * 30)
    test_kaleido()  # This doesn't affect success since we have lazy initialization
    
    # Step 5: Test application imports
    print("\n4️⃣ TESTING APPLICATION")
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
        print("\n🔧 Troubleshooting:")
        print("   1. Ensure you have internet connectivity")
        print("   2. Check that you have sufficient disk space")
        print("   3. Verify Python and pip are properly installed")
        print("   4. Run with verbose logging:")
        print("      LOG_LEVEL=DEBUG python setup_deployment.py")
        print("   5. Check the deployment debugging guide:")
        print("      cat DEPLOYMENT_DEBUGGING.md")
        print("   6. Run the diagnostic script:")
        print("      python deployment_debug.py")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 