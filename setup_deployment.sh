#!/bin/bash

# Simple deployment setup script for ESG Reporting Application
set -e  # Exit on any error

echo "🚀 Setting up ESG Reporting Application..."

# Check if we're in the right directory
if [ ! -f "main.py" ] || [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Run this script from the envizi_esg_reporting directory"
    exit 1
fi

echo "📦 Installing Google Chrome..."

# Ensure required tools are installed
echo "🔧 Installing required tools (curl, gnupg)..."
sudo apt-get update && sudo apt-get install -y curl gnupg || {
    echo "⚠️  Failed to install required tools"
}

# Ensure keyring directory exists
sudo mkdir -p /usr/share/keyrings

# Download and install Google's signing key
echo "🔑 Adding Google's signing key..."
if command -v curl >/dev/null 2>&1; then
    curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | sudo gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg || {
        echo "⚠️  Failed to add Google signing key"
    }
elif command -v wget >/dev/null 2>&1; then
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg || {
        echo "⚠️  Failed to add Google signing key"
    }
else
    echo "❌ No download tool available"
fi

# Verify the key was installed
if [ -f "/usr/share/keyrings/google-chrome-keyring.gpg" ]; then
    echo "✅ Google signing key installed successfully"
    
    # Add repository with proper keyring reference
    echo "📂 Adding Google Chrome repository..."
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
    
    # Update package list and install Chrome
    echo "🌐 Installing Google Chrome..."
    sudo apt-get update && sudo apt-get install -y google-chrome-stable || {
        echo "⚠️  Failed to install Google Chrome via apt"
        echo "   Continuing without system Chrome installation..."
    }
else
    echo "❌ Failed to install Google signing key - skipping Chrome installation"
    echo "   Chrome will be installed via kaleido_get_chrome instead"
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt || {
    echo "❌ Failed to install dependencies. Try: pip install --upgrade pip"
    exit 1
}

# Install Chrome for Kaleido chart generation
echo "📊 Installing Chrome for Kaleido chart generation..."
kaleido_get_chrome || {
    echo "⚠️  Failed with kaleido_get_chrome, trying plotly_get_chrome..."
    plotly_get_chrome || {
        echo "⚠️  Both methods failed, trying Python fallback..."
        python -c "
try:
    import kaleido
    kaleido.get_chrome_sync()
    print('✅ Chrome installed via Python kaleido.get_chrome_sync()')
except Exception as e:
    print(f'❌ All Chrome installation methods failed: {e}')
    print('📝 Note: Charts may not be available in PDF reports')
    print('💡 You may need to install Chrome manually:')
    print('   - Ubuntu/Debian: sudo apt-get install google-chrome-stable')
    print('   - CentOS/RHEL: sudo yum install google-chrome-stable')
    print('   - macOS: brew install --cask google-chrome')
"
    }
}

# Test Kaleido chart generation
echo "🧪 Testing Kaleido chart generation..."
python -c "
import plotly.graph_objects as go
import plotly.io as pio
try:
    # Test if Kaleido can find Chrome
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[1, 2, 3], y=[4, 5, 6], name='test'))
    img_bytes = pio.to_image(fig, format='png', width=400, height=300)
    print(f'✅ Kaleido test successful: {len(img_bytes)} bytes generated')
    print('✅ Chrome is properly configured for Kaleido')
except Exception as e:
    if 'Chrome' in str(e) or 'chromium' in str(e).lower():
        print(f'❌ Chrome not found for Kaleido: {e}')
        print('💡 Try running: kaleido_get_chrome')
        print('💡 Or manually install Chrome for your system')
    else:
        print(f'⚠️  Kaleido test failed: {e}')
    print('📝 Note: Charts may not be available in PDF reports')
"

# Install Playwright system dependencies first
echo "🔧 Installing Playwright system dependencies..."
if ! playwright install-deps; then
    echo "⚠️  Standard installation failed, trying with sudo..."
    if ! sudo playwright install-deps; then
        echo "❌ CRITICAL: Failed to install Playwright system dependencies!"
        echo "   This will prevent PDF generation from working."
        echo "   Manual installation required - check system compatibility."
        exit 1
    fi
fi

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
if [ "$ENVIRONMENT" = "production" ] || [ "$ENVIRONMENT" = "PRODUCTION" ]; then
    echo "📦 Installing Chromium only (production mode)..."
    if ! playwright install chromium; then
        echo "⚠️  Standard installation failed, trying with --force..."
        if ! playwright install chromium --force; then
            echo "❌ CRITICAL: Failed to install Chromium browser!"
            echo "   PDF generation will not work without browser installation."
            exit 1
        fi
    fi
else
    echo "📦 Installing all browsers (development mode)..."
    if ! playwright install; then
        echo "⚠️  Standard installation failed, trying with --force..."
        if ! playwright install --force; then
            echo "❌ CRITICAL: Failed to install Playwright browsers!"
            echo "   PDF generation will not work without browser installation."
            exit 1
        fi
    fi
fi

# Verify Playwright installation
echo "🔍 Verifying Playwright browser installation..."
# Check if Chromium browser files exist in the Playwright cache
PLAYWRIGHT_CACHE_DIR="${HOME}/.cache/ms-playwright"
if [ -d "$PLAYWRIGHT_CACHE_DIR" ] && (ls "$PLAYWRIGHT_CACHE_DIR"/chromium* >/dev/null 2>&1 || ls "$PLAYWRIGHT_CACHE_DIR"/chromium_headless_shell* >/dev/null 2>&1); then
    echo "✅ Chromium browser successfully installed"
    echo "   Found in: $PLAYWRIGHT_CACHE_DIR"
    ls "$PLAYWRIGHT_CACHE_DIR"/chromium* 2>/dev/null || ls "$PLAYWRIGHT_CACHE_DIR"/chromium_headless_shell* 2>/dev/null | head -3
else
    echo "❌ CRITICAL: Chromium browser not found after installation!"
    echo "   Expected location: $PLAYWRIGHT_CACHE_DIR"
    echo "   Available browsers/files:"
    ls "$PLAYWRIGHT_CACHE_DIR" 2>/dev/null || echo "   Cache directory not found"
    
    # Try alternative verification using Python
    echo "🐍 Trying Python-based verification..."
    python -c "
import sys
try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        browser.close()
        print('✅ Chromium browser verification successful via Python')
        sys.exit(0)
except Exception as e:
    print(f'❌ Python verification failed: {e}')
    sys.exit(1)
    " || {
        echo "❌ CRITICAL: Both file-based and Python verification failed!"
        echo "   PDF generation will not work without browser installation."
        exit 1
    }
fi

# Run deployment setup
echo "🔧 Running deployment setup..."
python setup_deployment.py || {
    echo "❌ Setup failed. Run 'python deployment_debug.py' for diagnostics"
    exit 1
}

echo ""
echo "✅ Setup complete! Start the application with:"
echo "   python main.py"
echo ""
echo "🌍 App will be available at: http://localhost:8000"