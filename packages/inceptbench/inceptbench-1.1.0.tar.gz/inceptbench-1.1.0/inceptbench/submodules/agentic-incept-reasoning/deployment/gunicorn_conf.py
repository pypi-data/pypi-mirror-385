import multiprocessing
import os

# Server socket
bind = "127.0.0.1:8000"  # Only listen on localhost
backlog = 2048

# Worker processes - optimized for 100 parallel requests with memory-intensive workloads
# Strategy: Balance between parallelism and memory management for matplotlib/Chrome usage
cpu_cores = multiprocessing.cpu_count()
if cpu_cores <= 2:
    # Small instances (like r7i.large): Use 2 workers to leave CPU for thread pool
    workers = 2
elif cpu_cores <= 4:
    # Medium instances: Conservative scaling
    workers = cpu_cores
else:
    # Large instances (r7i.2xlarge): Optimize for 100 concurrent requests
    # With thread-safe matplotlib cleanup and 300 requests/worker recycling,
    # we can support more workers while maintaining memory stability
    workers = min(6, cpu_cores - 2)  # Leave 2 vCPUs for thread pool overhead

worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000  # Each worker can handle many connections due to async nature
timeout = 1200  # 20 minutes - match client timeout expectations
keepalive = 2

# Memory management settings optimized for high concurrency with async architecture
# With async design, workers are much more stable and memory-efficient
# Recycling too frequently causes unnecessary disruption during high load
max_requests = 2000  # Recycle after 2000 requests (increased from 350)
max_requests_jitter = 200  # Add randomness to prevent thundering herd
worker_tmp_dir = "/dev/shm"  # Use RAM for temporary files if available
preload_app = True  # Share memory between workers

# Worker timeout management
worker_timeout = 1800  # 30 minutes - longer than request timeout to allow cleanup

# Logging
accesslog = "-"  # stdout
errorlog = "-"   # stderr
loglevel = "info"

# Process naming
proc_name = "edu_agents_api"

# Security
limit_request_line = 0  # unlimited - some prompts might be long
limit_request_fields = 32768
limit_request_field_size = 0  # unlimited

# Development
reload = False  # set to True for development 

# SSE streaming optimization - prevent response buffering
sendfile = False  # Disable sendfile for streaming responses
enable_stdio_inheritance = True  # Allow real-time streaming output