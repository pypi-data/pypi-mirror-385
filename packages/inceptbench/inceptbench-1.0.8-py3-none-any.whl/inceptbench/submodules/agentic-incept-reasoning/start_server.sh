#!/bin/bash

# Educational Agents Local Development Server
# Starts both Python API and Screenshot Service

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Educational Agents Local Development Environment${NC}"

# Set environment variables for Cairo and Manim dependencies
export DYLD_LIBRARY_PATH="/opt/homebrew/opt/cairo/lib:$DYLD_LIBRARY_PATH"
export LD_LIBRARY_PATH="/opt/homebrew/opt/cairo/lib:$LD_LIBRARY_PATH"
export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig:$PKG_CONFIG_PATH"
export PYTHONPATH="$(pwd):$PYTHONPATH"

# Ensure FFmpeg is in PATH for Manim video rendering
export PATH="$PATH:/opt/homebrew/bin"

# Screenshot service environment for local development
export NODE_ENV="development"
export MAX_BROWSERS=2
export MAX_PAGES_PER_BROWSER=3
export PORT=8001

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down services...${NC}"
    
    # Kill screenshot service
    if [ ! -z "$SCREENSHOT_PID" ] && kill -0 $SCREENSHOT_PID 2>/dev/null; then
        echo -e "${YELLOW}   Stopping screenshot service (PID: $SCREENSHOT_PID)${NC}"
        kill -TERM $SCREENSHOT_PID 2>/dev/null || true
        wait $SCREENSHOT_PID 2>/dev/null || true
    fi
    
    # Kill any remaining node processes for screenshot service
    pkill -f "screenshot-service" 2>/dev/null || true
    
    echo -e "${GREEN}✅ Services stopped${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM EXIT

# Activate virtual environment if not already activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo -e "${BLUE}📦 Activating Python virtual environment...${NC}"
    source .venv/bin/activate
fi

# Check if screenshot service directory exists
if [ ! -d "screenshot-service" ]; then
    echo -e "${RED}❌ Screenshot service directory not found${NC}"
    echo -e "${YELLOW}   Please run the setup first or check your working directory${NC}"
    exit 1
fi

# Install screenshot service dependencies if needed
if [ ! -d "screenshot-service/node_modules" ]; then
    echo -e "${BLUE}📦 Installing screenshot service dependencies...${NC}"
    cd screenshot-service
    npm install
    cd ..
fi

# Create logs directory
mkdir -p logs

# Start screenshot service
echo -e "${BLUE}🖥️  Starting screenshot service (local config: 2 browsers)...${NC}"
cd screenshot-service
nohup npm start > ../logs/screenshot-service-local.log 2>&1 &
SCREENSHOT_PID=$!
cd ..

echo -e "${GREEN}   Screenshot service started with PID: $SCREENSHOT_PID${NC}"

# Wait for screenshot service to be ready
echo -e "${BLUE}⏳ Waiting for screenshot service to be ready...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Screenshot service is ready!${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Screenshot service failed to start within 30 seconds${NC}"
        echo -e "${YELLOW}   Check logs/screenshot-service-local.log for details${NC}"
        exit 1
    fi
    sleep 1
done

# Show service status
echo -e "\n${BLUE}📊 Service Status:${NC}"
SCREENSHOT_STATUS=$(curl -s -w "%{http_code}" -o /dev/null http://localhost:8001/health 2>/dev/null || echo "000")
echo -e "   Screenshot Service (port 8001): ${GREEN}$SCREENSHOT_STATUS${NC}"

if [ "$SCREENSHOT_STATUS" = "200" ]; then
    echo -e "${BLUE}   Screenshot service stats:${NC}"
    curl -s http://localhost:8001/stats 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f'      Max browsers: {data.get(\"maxBrowsers\", \"unknown\")}')
    print(f'      Current browsers: {data.get(\"totalBrowsers\", \"unknown\")}')
    print(f'      Available browsers: {data.get(\"availableBrowsers\", \"unknown\")}')
except:
    print('      Could not get detailed stats')
"
fi

echo -e "\n${BLUE}🚀 Starting Python API server...${NC}"
echo -e "${YELLOW}   Both services will run until you press Ctrl+C${NC}"
echo -e "${YELLOW}   Logs: logs/screenshot-service-local.log${NC}"
echo -e "${YELLOW}   URLs:${NC}"
echo -e "${YELLOW}     - Main API: http://localhost:8000${NC}"
echo -e "${YELLOW}     - Screenshot Service: http://localhost:8001${NC}"
echo -e ""

# Start the Python server (this will block)
uvicorn edu_agents.api.server:app --reload --host 127.0.0.1 --port 8000 