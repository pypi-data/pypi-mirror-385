# Graceful Restart Setup

This directory contains tools for performing zero-downtime restarts of the Educational Agents API.

## Setup

1. **Make the restart script executable:**
   ```bash
   chmod +x deployment/graceful_restart.sh
   ```

2. **Update your systemd service file** to support graceful shutdown (if not already configured):
   ```ini
   # /etc/systemd/system/edu_agents.service
   [Unit]
   Description=Educational Agents API
   After=network.target

   [Service]
   Type=exec
   User=your-user
   WorkingDirectory=/path/to/your/app
   ExecStart=/path/to/your/venv/bin/uvicorn src.edu_agents.api.server:app --host 0.0.0.0 --port 8000
   Restart=always
   RestartSec=5
   
   # Graceful shutdown settings
   TimeoutStopSec=30
   KillSignal=SIGTERM
   KillMode=mixed

   [Install]
   WantedBy=multi-user.target
   ```

3. **Reload systemd and restart to apply changes:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl restart edu_agents
   ```

## Usage

### Graceful Restart (Recommended)
Instead of `sudo systemctl restart edu_agents`, use:
```bash
./deployment/graceful_restart.sh
```

This script will:
- ✅ Check current service health
- 📤 Send graceful shutdown signal
- ⏳ Wait for shutdown acknowledgment
- 🚀 Start new service instance
- ✅ Verify new instance is healthy

### Multiple Instance Setup (Advanced)

For true zero-downtime, run multiple instances behind a load balancer:

1. **Create multiple service files:**
   ```bash
   # Copy your service file for multiple instances
   sudo cp /etc/systemd/system/edu_agents.service /etc/systemd/system/edu_agents@.service
   ```

2. **Modify the template service:**
   ```ini
   # /etc/systemd/system/edu_agents@.service
   [Unit]
   Description=Educational Agents API Instance %i
   After=network.target

   [Service]
   Type=exec
   User=your-user
   WorkingDirectory=/path/to/your/app
   Environment=PORT=800%i
   ExecStart=/path/to/your/venv/bin/uvicorn src.edu_agents.api.server:app --host 0.0.0.0 --port $PORT
   Restart=always
   RestartSec=5
   TimeoutStopSec=30
   KillSignal=SIGTERM
   KillMode=mixed

   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable and start multiple instances:**
   ```bash
   sudo systemctl enable edu_agents@0.service
   sudo systemctl enable edu_agents@1.service
   sudo systemctl start edu_agents@0.service
   sudo systemctl start edu_agents@1.service
   ```

4. **Configure nginx/load balancer:**
   ```nginx
   upstream app_servers {
       server 127.0.0.1:8000 max_fails=3 fail_timeout=30s;
       server 127.0.0.1:8001 max_fails=3 fail_timeout=30s;
   }

   server {
       location / {
           proxy_pass http://app_servers;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_next_upstream error timeout http_502 http_503 http_504;
       }
       
       location /health {
           proxy_pass http://app_servers/health;
           access_log off;
       }
   }
   ```

5. **Rolling restart multiple instances:**
   ```bash
   # Restart instances one at a time
   sudo systemctl restart edu_agents@1.service
   sleep 10
   sudo systemctl restart edu_agents@0.service
   ```

## How It Works

The graceful restart system works by:

1. **Application-level shutdown handling**: The FastAPI app listens for SIGTERM and sets a shutdown flag
2. **Health endpoint changes**: During shutdown, `/health` returns 503 instead of 200
3. **Request rejection**: New requests (except health checks) are rejected with 503 during shutdown
4. **Chrome cleanup**: QC resources (Chrome instances, caches) are cleaned up during shutdown
5. **Coordination**: The restart script uses the health endpoint to coordinate the shutdown process

## Monitoring

You can monitor the restart process by watching:
```bash
# Watch the health endpoint
watch -n 1 'curl -s http://localhost:8000/health | python3 -m json.tool'

# Watch QC system performance
watch -n 5 'curl -s http://localhost:8000/qc-stats | python3 -m json.tool'

# Watch systemd status
watch -n 1 'sudo systemctl status edu_agents --no-pager'

# Watch logs
sudo journalctl -u edu_agents -f
```

## Troubleshooting

**Script fails to detect shutdown:**
- Check that curl is installed
- Verify the health endpoint URL is correct
- Ensure the service name in the script matches your systemd service

**Service doesn't respond to SIGTERM:**
- Check that your systemd service has `KillSignal=SIGTERM`
- Verify `TimeoutStopSec` is set appropriately (30s recommended)

**502 errors still occur:**
- Consider using multiple instances with a load balancer
- Increase the shutdown timeout
- Check that your application properly handles the shutdown event 