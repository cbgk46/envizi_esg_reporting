#!/bin/bash

# Deployment setup script for ESG Reporting Application
# Handles installation of dependencies and browser setup

set -e  # Exit on any error

echo "🚀 Starting deployment setup for ESG Reporting Application..."
echo "============================================================"

# Function to print status messages
print_status() {
    echo "🔄 $1..."
}

print_success() {
    echo "✅ $1 completed successfully"
}

print_error() {
    echo "❌ $1 failed"
}

# Install Python dependencies
print_status "Installing Python dependencies"
pip install -r requirements.txt
print_success "Python dependencies installation"

# Install Playwright browsers
print_status "Installing Playwright browsers"
if [ "${ENVIRONMENT,,}" = "production" ]; then
    # In production, only install Chromium to save space and time
    playwright install chromium
    print_success "Playwright Chromium browser installation"
else
    # In development/staging, install all browsers
    playwright install
    print_success "Playwright browsers installation"
fi

# Run Python setup for Kaleido
print_status "Running Python setup (Kaleido initialization)"
python setup_deployment.py
print_success "Python setup"

echo "============================================================"
echo "🎉 Deployment setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "   1. Start your application: python main.py"
echo "   2. Or use uvicorn: uvicorn main:app --host 0.0.0.0 --port 8000"
echo ""
echo "🔧 Environment variables you can set:"
echo "   - ENVIRONMENT=production (for production optimizations)" 

python main.py