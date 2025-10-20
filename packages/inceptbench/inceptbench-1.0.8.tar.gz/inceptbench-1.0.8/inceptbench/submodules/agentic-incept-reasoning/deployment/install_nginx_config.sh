#!/bin/bash
# Script to install the Educational Content Generator API Nginx configuration

# Ensure running as root
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

# Domain name
DOMAIN="inceptapi.rp.devfactory.com"

# Define paths
API_CONF_SRC="./deployment/edu_agents_api_initial.conf"
NGINX_CONF_DIR="/etc/nginx/conf.d"
NGINX_HTTP_CONF="/etc/nginx/nginx.conf"

# Install certbot if not already installed
if ! command -v certbot &> /dev/null; then
    echo "Installing certbot..."
    yum install certbot python3-certbot-nginx -y
fi

# Copy the initial API configuration (HTTP only)
echo "Installing initial API configuration..."
cp $API_CONF_SRC $NGINX_CONF_DIR/edu_agents_api.conf

# Add rate limiting zone if not already present
if ! grep -q "zone=api_limit:" $NGINX_HTTP_CONF; then
    echo "Adding rate limiting zone to nginx.conf..."
    # Insert before the closing brace of the http block
    sed -i '/http {/a \    # Rate limiting for API\n    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;' $NGINX_HTTP_CONF
else
    echo "Rate limiting zone already configured in nginx.conf"
fi

# Test initial Nginx configuration
echo "Testing Nginx configuration..."
nginx -t

if [ $? -eq 0 ]; then
    echo "Configuration test successful, restarting Nginx..."
    systemctl restart nginx
    
    # Wait a moment for Nginx to start
    sleep 10
    
    # Get SSL certificate
    echo "Obtaining SSL certificate for $DOMAIN..."
    certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email shawn.sullivan@trilogy.com \
        --redirect --keep-until-expiring
    
    if [ $? -eq 0 ]; then
        # Setup auto-renewal
        echo "Setting up automatic certificate renewal..."
        systemctl enable certbot-renew.timer
        systemctl start certbot-renew.timer
        
        echo "Done! The API is now accessible at https://$DOMAIN/api/"
        echo "Test with: curl -X POST https://$DOMAIN/api/respond -H 'Content-Type: application/json' -d '{\"prompt\":\"Hello\"}'"
    else
        echo "Failed to obtain SSL certificate. The API is still accessible via HTTP at http://$DOMAIN/api/"
        echo "Test with: curl -X POST http://$DOMAIN/api/respond -H 'Content-Type: application/json' -d '{\"prompt\":\"Hello\"}'"
        exit 1
    fi
else
    echo "Configuration test failed. Please check the Nginx error log."
    exit 1
fi 