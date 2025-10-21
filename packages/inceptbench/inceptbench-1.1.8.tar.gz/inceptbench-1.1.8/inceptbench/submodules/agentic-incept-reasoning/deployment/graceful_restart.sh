#!/bin/bash

# Graceful restart script for Educational Agents API and Screenshot Service
# This script ensures zero-downtime restarts by:
# 1. Checking service health
# 2. Sending graceful shutdown signal  
# 3. Waiting for shutdown to complete
# 4. Starting both services
#
# NOTE: For Manim support, ensure your systemd service file includes:
# Environment="PKG_CONFIG_PATH=/usr/lib/pkgconfig:/usr/local/lib/pkgconfig"
# Environment="PATH=/usr/local/bin:/usr/bin:/bin"
# And that ffmpeg and texlive packages are installed system-wide

set -e

MAIN_SERVICE_NAME="edu_agents"
SCREENSHOT_SERVICE_NAME="screenshot-service"
MAIN_HEALTH_URL="http://localhost:8000/health"
SCREENSHOT_HEALTH_URL="http://localhost:8001/health"
MAX_WAIT_TIME=60
WAIT_INTERVAL=2

echo "🔄 Starting graceful restart of Educational Agents services..."

# Function to check if service is healthy
check_health() {
    local url=$1
    local response=$(curl -s -w "%{http_code}" -o /dev/null "$url" 2>/dev/null || echo "000")
    echo "$response"
}

# Function to wait for service to be healthy
wait_for_healthy() {
    local service_name=$1
    local health_url=$2
    local max_attempts=$((MAX_WAIT_TIME / WAIT_INTERVAL))
    local attempt=0
    
    echo "⏳ Waiting for $service_name to be healthy..."
    
    while [ $attempt -lt $max_attempts ]; do
        local status=$(check_health "$health_url")
        
        if [ "$status" = "200" ]; then
            echo "✅ $service_name is healthy!"
            return 0
        fi
        
        echo "   Attempt $((attempt + 1))/$max_attempts - Status: $status"
        sleep $WAIT_INTERVAL
        attempt=$((attempt + 1))
    done
    
    echo "❌ $service_name failed to become healthy within $MAX_WAIT_TIME seconds"
    return 1
}

# Function to wait for service to start shutting down
wait_for_shutdown() {
    local service_name=$1
    local health_url=$2
    local initial_wait=10  # Give service time to process SIGTERM
    local max_attempts=15  # Reduced since we're giving initial wait
    local attempt=0
    
    echo "⏳ Giving $service_name ${initial_wait}s to process shutdown signal..."
    sleep $initial_wait
    
    echo "⏳ Waiting for $service_name to complete shutdown..."
    
    while [ $attempt -lt $max_attempts ]; do
        local status=$(check_health "$health_url")
        
        # 503 means service is shutting down gracefully
        if [ "$status" = "503" ]; then
            echo "🛑 $service_name is shutting down gracefully"
            return 0
        fi
        
        # 000 means service is completely down
        if [ "$status" = "000" ]; then
            echo "🛑 $service_name is down"
            return 0
        fi
        
        # If still returning 200 after initial wait, that's expected
        if [ $attempt -lt 5 ]; then
            echo "   Attempt $((attempt + 1))/$max_attempts - Status: $status (processing shutdown...)"
        else
            echo "   Attempt $((attempt + 1))/$max_attempts - Status: $status"
        fi
        
        sleep $WAIT_INTERVAL
        attempt=$((attempt + 1))
    done
    
    echo "⚠️  $service_name is taking longer than expected to shut down, proceeding with force stop"
    return 1
}

# Function to install Node.js dependencies for screenshot service
install_screenshot_service_deps() {
    if [ ! -d "screenshot-service" ]; then
        echo "❌ Screenshot service directory not found. Please ensure screenshot-service/ exists."
        return 1
    fi
    
    cd screenshot-service
    
    if [ ! -f "package.json" ]; then
        echo "❌ package.json not found in screenshot-service/"
        cd ..
        return 1
    fi
    
    echo "📦 Installing screenshot service dependencies..."
    if command -v npm >/dev/null 2>&1; then
        npm install --production
        cd ..
        echo "✅ Screenshot service dependencies installed"
        return 0
    else
        echo "❌ npm not found. Please install Node.js and npm first."
        cd ..
        return 1
    fi
}

# Function to start screenshot service
start_screenshot_service() {
    echo "🖥️  Starting screenshot service..."
    
    cd screenshot-service
    nohup npm start > ../logs/screenshot-service.log 2>&1 &
    local pid=$!
    echo $pid > ../logs/screenshot-service.pid
    cd ..
    
    echo "📊 Screenshot service started with PID $pid"
    
    # Wait for it to be healthy
    if wait_for_healthy "Screenshot Service" "$SCREENSHOT_HEALTH_URL"; then
        echo "✅ Screenshot service is ready"
        return 0
    else
        echo "❌ Screenshot service failed to start properly"
        return 1
    fi
}

# Function to stop screenshot service
stop_screenshot_service() {
    echo "🛑 Stopping screenshot service..."
    
    if [ -f "logs/screenshot-service.pid" ]; then
        local pid=$(cat logs/screenshot-service.pid)
        if kill -0 "$pid" 2>/dev/null; then
            # Send SIGTERM for graceful shutdown
            kill -TERM "$pid"
            
            # Wait for graceful shutdown
            local count=0
            while kill -0 "$pid" 2>/dev/null && [ $count -lt 30 ]; do
                sleep 1
                count=$((count + 1))
            done
            
            # Force kill if still running
            if kill -0 "$pid" 2>/dev/null; then
                echo "⚠️ Force killing screenshot service"
                kill -KILL "$pid"
            fi
        fi
        rm -f logs/screenshot-service.pid
    fi
    
    # Also kill any remaining node processes for screenshot service
    pkill -f "screenshot-service" || true
    
    echo "✅ Screenshot service stopped"
}

# Ensure logs directory exists
mkdir -p logs

# Install screenshot service dependencies if needed
if [ ! -d "screenshot-service/node_modules" ]; then
    echo "📦 Screenshot service dependencies not found, installing..."
    install_screenshot_service_deps || {
        echo "❌ Failed to install screenshot service dependencies"
        exit 1
    }
fi

# Check current service status
echo "📊 Checking current service status..."
main_status=$(check_health "$MAIN_HEALTH_URL")
screenshot_status=$(check_health "$SCREENSHOT_HEALTH_URL")

echo "   Main service (8000): $main_status"
echo "   Screenshot service (8001): $screenshot_status"

# If services are not healthy, start them normally
if [ "$main_status" != "200" ] && [ "$screenshot_status" != "200" ]; then
    echo "⚠️ Both services are not healthy, starting normally..."
    
    # Start screenshot service first
    start_screenshot_service || {
        echo "❌ Failed to start screenshot service"
        exit 1
    }
    
    # Start main service
    sudo systemctl start $MAIN_SERVICE_NAME
    if wait_for_healthy "Main Service" "$MAIN_HEALTH_URL"; then
        echo "🎉 Services started successfully!"
        exit 0
    else
        echo "❌ Main service failed to start"
        exit 1
    fi
fi

# If only one service is unhealthy, handle individually
if [ "$main_status" != "200" ]; then
    echo "⚠️ Main service is not healthy, restarting..."
    sudo systemctl restart $MAIN_SERVICE_NAME
    wait_for_healthy "Main Service" "$MAIN_HEALTH_URL"
fi

if [ "$screenshot_status" != "200" ]; then
    echo "⚠️ Screenshot service is not healthy, restarting..."
    stop_screenshot_service
    start_screenshot_service || {
        echo "❌ Failed to restart screenshot service"
        exit 1
    }
fi

# Both services are healthy, proceed with graceful restart
echo "✅ Both services are currently healthy, proceeding with graceful restart..."

# Graceful shutdown of both services
echo "📤 Sending graceful shutdown signals..."

# Shutdown main service
sudo systemctl kill --signal=SIGTERM $MAIN_SERVICE_NAME

# Shutdown screenshot service
stop_screenshot_service

# Give services time for graceful shutdown processing
echo "⏳ Allowing time for graceful shutdown processing..."
sleep 15

# Stop services completely (this is expected after SIGTERM)
echo "🛑 Stopping services completely..."
sudo systemctl stop $MAIN_SERVICE_NAME

# Verify the main service is actually stopped
echo "⏳ Verifying main service shutdown..."
for i in {1..10}; do
    status=$(check_health "$MAIN_HEALTH_URL")
    if [ "$status" = "000" ]; then
        echo "✅ Main service has stopped"
        break
    fi
    echo "   Attempt $i/10 - Status: $status (still stopping...)"
    sleep 2
done

# Wait a moment for complete shutdown
sleep 2

# Start services
echo "🚀 Starting services..."

# Start screenshot service first (dependency)
start_screenshot_service || {
    echo "❌ Failed to start screenshot service"
    exit 1
}

# Start main service
sudo systemctl start $MAIN_SERVICE_NAME

# Wait for both services to be healthy
if wait_for_healthy "Main Service" "$MAIN_HEALTH_URL"; then
    echo "🎉 Graceful restart completed successfully!"
    
    # Show final status
    echo "📊 Final status:"
    echo "   Main service: $(check_health "$MAIN_HEALTH_URL")"
    echo "   Screenshot service: $(check_health "$SCREENSHOT_HEALTH_URL")"
    
    # Try to get detailed status from main service
    curl -s "$MAIN_HEALTH_URL" | python3 -m json.tool 2>/dev/null || echo "Could not get detailed main service status"
    echo ""
    curl -s "$SCREENSHOT_HEALTH_URL" | python3 -m json.tool 2>/dev/null || echo "Could not get detailed screenshot service status"
else
    echo "❌ Main service failed to start properly after restart"
    echo "📊 Service status:"
    sudo systemctl status $MAIN_SERVICE_NAME --no-pager
    exit 1
fi 