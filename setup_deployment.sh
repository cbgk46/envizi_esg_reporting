#!/bin/bash

# Simple deployment setup script for ESG Reporting Application
set -e  # Exit on any error

echo "🚀 Setting up ESG Reporting Application..."

# Check if we're in the right directory
if [ ! -f "main.py" ] || [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Run this script from the envizi_esg_reporting directory"
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt || {
    echo "❌ Failed to install dependencies. Try: pip install --upgrade pip"
    exit 1
}

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