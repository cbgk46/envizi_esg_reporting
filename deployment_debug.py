#!/usr/bin/env python3
"""
Deployment Debug Script for ESG Reporting Application

This script helps diagnose deployment issues by:
1. Testing all critical imports
2. Checking file structure and permissions
3. Testing configuration loading
4. Validating environment setup
5. Testing basic application functionality
6. Providing detailed logging for troubleshooting
"""

import os
import sys
import json
import traceback
from pathlib import Path

def run_debug_checks():
    """Run comprehensive deployment debug checks"""
    print("=" * 70)
    print("🔍 ESG REPORTING APPLICATION - DEPLOYMENT DIAGNOSTICS")
    print("=" * 70)
    
    all_checks_passed = True
    
    # 1. Environment Check
    print("\n📋 1. ENVIRONMENT CHECK")
    print("-" * 30)
    
    try:
        print(f"✅ Python Version: {sys.version}")
        print(f"✅ Current Working Directory: {os.getcwd()}")
        print(f"✅ Script Location: {__file__}")
        print(f"✅ PYTHONPATH: {sys.path}")
        
        # Environment variables
        env_vars = ['LOG_LEVEL', 'ENVIRONMENT', 'DEBUG_MODE', 'HOST', 'PORT']
        print("\n🌍 Environment Variables:")
        for var in env_vars:
            value = os.getenv(var, 'Not Set')
            print(f"   {var}: {value}")
            
    except Exception as e:
        print(f"❌ Environment check failed: {e}")
        all_checks_passed = False
    
    # 2. File Structure Check
    print("\n📁 2. FILE STRUCTURE CHECK")
    print("-" * 30)
    
    required_files = [
        'main.py',
        'auth.py', 
        'config.py',
        'models.py',
        'requirements.txt',
        'routes/__init__.py',
        'routes/auth_routes.py',
        'routes/questionnaire_routes.py',
        'services/__init__.py',
        'services/chart_service.py',
        'services/openai_service.py',
        'services/questionnaire_processor.py',
        'templates/login.html',
        'templates/questionnaire.html',
        'templates/report.html',
        'templates/success.html',
        'static/css/styles.css'
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            missing_files.append(file_path)
            all_checks_passed = False
    
    if missing_files:
        print(f"\n🚨 CRITICAL: {len(missing_files)} files are missing!")
    
    # 3. Import Tests
    print("\n📦 3. IMPORT TESTS")
    print("-" * 30)
    
    import_tests = [
        ('fastapi', 'FastAPI, Request, HTTPException'),
        ('fastapi.staticfiles', 'StaticFiles'),
        ('fastapi.templating', 'Jinja2Templates'),
        ('fastapi.responses', 'HTMLResponse, RedirectResponse'),
        ('uvicorn', 'uvicorn'),
        ('playwright.async_api', 'async_playwright'),
        ('markdown', 'markdown'),
        ('plotly.graph_objects', 'go'),
        ('plotly.io', 'pio'),
        ('matplotlib.pyplot', 'plt'),
        ('openai', 'OpenAI'),
        ('datetime', 'datetime'),
        ('secrets', 'secrets'),
        ('logging', 'logging')
    ]
    
    import_failures = []
    for module_name, imports in import_tests:
        try:
            if imports:
                exec(f"from {module_name} import {imports}")
            else:
                exec(f"import {module_name}")
            print(f"✅ {module_name}")
        except ImportError as e:
            print(f"❌ {module_name} - FAILED: {e}")
            import_failures.append((module_name, str(e)))
            all_checks_passed = False
    
    if import_failures:
        print(f"\n🚨 IMPORT FAILURES: {len(import_failures)} modules failed to import")
        print("💡 Try: pip install -r requirements.txt")
    
    # 4. Application Module Tests
    print("\n🏗️  4. APPLICATION MODULE TESTS")
    print("-" * 30)
    
    app_modules = [
        'config',
        'auth', 
        'models',
        'routes.auth_routes',
        'routes.questionnaire_routes',
        'services.chart_service',
        'services.openai_service',
        'services.questionnaire_processor'
    ]
    
    module_failures = []
    for module_name in app_modules:
        try:
            exec(f"import {module_name}")
            print(f"✅ {module_name}")
        except Exception as e:
            print(f"❌ {module_name} - FAILED: {e}")
            module_failures.append((module_name, str(e)))
            all_checks_passed = False
    
    # 5. Configuration Loading Test
    print("\n⚙️  5. CONFIGURATION LOADING TEST")
    print("-" * 30)
    
    try:
        import config
        print(f"✅ Config module loaded")
        
        # Test critical config variables
        config_vars = ['USERS', 'QUESTIONS_DATA', 'DEBUG_MODE']
        for var in config_vars:
            if hasattr(config, var):
                value = getattr(config, var)
                if var == 'USERS':
                    print(f"✅ {var}: {len(value)} users configured")
                elif var == 'QUESTIONS_DATA':
                    questions = value.get('questionnaireReference', [])
                    print(f"✅ {var}: {len(questions)} questions loaded")
                else:
                    print(f"✅ {var}: {value}")
            else:
                print(f"❌ {var}: Not found in config")
                all_checks_passed = False
                
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        print(f"   Traceback: {traceback.format_exc()}")
        all_checks_passed = False
    
    # 6. FastAPI Application Test
    print("\n🚀 6. FASTAPI APPLICATION TEST")
    print("-" * 30)
    
    try:
        # Test basic application creation
        sys.path.insert(0, os.getcwd())
        
        # Set up minimal logging to avoid issues
        import logging
        logging.basicConfig(level=logging.INFO)
        
        from main import app
        print("✅ FastAPI application created successfully")
        
        # Test routes
        routes = [route.path for route in app.routes]
        print(f"✅ Routes available: {len(routes)}")
        for route in sorted(routes):
            print(f"   📍 {route}")
            
    except Exception as e:
        print(f"❌ FastAPI application test failed: {e}")
        print(f"   Traceback: {traceback.format_exc()}")
        all_checks_passed = False
    
    # 7. Playwright Test
    print("\n🎭 7. PLAYWRIGHT/PDF GENERATION TEST")  
    print("-" * 30)
    
    try:
        import asyncio
        from playwright.async_api import async_playwright
        
        async def test_playwright():
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                await page.set_content("<h1>Test</h1>")
                pdf_bytes = await page.pdf(format='A4')
                await browser.close()
                return len(pdf_bytes)
        
        pdf_size = asyncio.run(test_playwright())
        print(f"✅ Playwright PDF generation: {pdf_size} bytes generated")
        
    except Exception as e:
        print(f"❌ Playwright test failed: {e}")
        print("💡 Try: playwright install")
        # Don't mark as critical failure for now
        
    # 8. Permissions Test
    print("\n🔒 8. PERMISSIONS TEST")
    print("-" * 30)
    
    try:
        # Test write permissions for logs
        os.makedirs('logs', exist_ok=True)
        test_file = 'logs/test_write.txt'
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        print("✅ Write permissions: OK")
        
        # Test static files access
        static_files = ['static/css/styles.css']
        for file_path in static_files:
            if os.path.exists(file_path) and os.access(file_path, os.R_OK):
                print(f"✅ Read access: {file_path}")
            else:
                print(f"❌ Read access: {file_path}")
                all_checks_passed = False
                
    except Exception as e:
        print(f"❌ Permissions test failed: {e}")
        all_checks_passed = False
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 70)
    
    if all_checks_passed:
        print("🎉 ALL CHECKS PASSED! Application should deploy successfully.")
        print("\n✅ Next steps:")
        print("   1. Run: python main.py")
        print("   2. Or: uvicorn main:app --host 0.0.0.0 --port 8000")
        print("   3. Visit: http://localhost:8000")
    else:
        print("⚠️  SOME CHECKS FAILED! Please address the issues above.")
        print("\n🔧 Troubleshooting tips:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Install browsers: playwright install")
        print("   3. Check file permissions and paths")
        print("   4. Verify environment variables")
        print("   5. Run with DEBUG logging: LOG_LEVEL=DEBUG python main.py")
    
    print("\n📝 For detailed runtime logs, set LOG_LEVEL=DEBUG")
    print("📧 Check logs/ directory for detailed application logs")
    print("=" * 70)
    
    return all_checks_passed

if __name__ == "__main__":
    try:
        success = run_debug_checks()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Diagnostics interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n💥 Diagnostic script failed: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)
