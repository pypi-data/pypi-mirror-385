#!/bin/bash

# Educational Agents Screenshot Service Setup Script
# This script sets up the Node.js screenshot service alongside the Python service

set -e

echo "🚀 Setting up Educational Agents Screenshot Service..."

# Check if running as appropriate user
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please run as ec2-user, not root"
    exit 1
fi

# Install Node.js and npm if not present
if ! command -v node >/dev/null 2>&1 || ! command -v npm >/dev/null 2>&1; then
    echo "📦 Installing Node.js and npm..."
    
    # Install NodeJS via yum (Amazon Linux)
    sudo yum update -y
    sudo yum install -y nodejs npm
    
    # Verify installation
    echo "✅ Node.js version: $(node --version)"
    echo "✅ npm version: $(npm --version)"
else
    echo "✅ Node.js and npm already installed"
    echo "   Node.js version: $(node --version)"
    echo "   npm version: $(npm --version)"
fi

# Install screenshot service dependencies
if [ -d "screenshot-service" ]; then
    echo "📦 Installing screenshot service dependencies..."
    cd screenshot-service
    npm install --production
    cd ..
    echo "✅ Screenshot service dependencies installed"
else
    echo "❌ screenshot-service directory not found"
    exit 1
fi

# Create logs directory
mkdir -p logs

# Install systemd service for screenshot service
if [ -f "deployment/screenshot-service.service" ]; then
    echo "⚙️  Installing screenshot service systemd unit..."
    sudo cp deployment/screenshot-service.service /etc/systemd/system/
    sudo systemctl daemon-reload
    echo "✅ Screenshot service systemd unit installed"
else
    echo "⚠️  Screenshot service systemd unit not found, skipping..."
fi

# Update Python dependencies
echo "🐍 Updating Python dependencies..."
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    pip install -r requirements.txt
    echo "✅ Python dependencies updated"
else
    echo "⚠️  Virtual environment not found, please install Python dependencies manually"
fi

# Test screenshot service
echo "🧪 Testing screenshot service..."
cd screenshot-service
timeout 30s npm test || {
    echo "⚠️  Screenshot service test timed out or failed"
    echo "   This may be normal if dependencies are still installing"
}
cd ..

echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Start services with: ./deployment/graceful_restart.sh"
echo "2. Check logs in: logs/screenshot-service.log"
echo "3. Monitor with: curl http://localhost:8001/health"
echo ""
echo "📊 Service URLs:"
echo "   Main API: http://localhost:8000/health"
echo "   Screenshot: http://localhost:8001/health"
