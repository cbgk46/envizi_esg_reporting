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
sudo apt-get install google-chrome-stable

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
playwright install-deps || {
    echo "⚠️  Failed to install system dependencies - you may need to run this with sudo:"
    echo "   sudo playwright install-deps"
    echo "   or manually install system dependencies for your OS"
}

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
if [ "$ENVIRONMENT" = "production" ] || [ "$ENVIRONMENT" = "PRODUCTION" ]; then
    playwright install chromium || {
        echo "❌ Failed to install Chromium"
        exit 1
    }
else
    playwright install || {
        echo "❌ Failed to install browsers"
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