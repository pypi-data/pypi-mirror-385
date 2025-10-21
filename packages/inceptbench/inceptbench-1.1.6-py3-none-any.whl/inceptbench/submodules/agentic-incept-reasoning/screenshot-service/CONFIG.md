# Screenshot Service Configuration

This document describes the configuration options for the Node.js screenshot service.

## Environment Variables

### Core Configuration
- `PORT`: Service port (default: 8001)
- `NODE_ENV`: Environment mode (production/development)
- `MAX_BROWSERS`: Maximum browser instances (default: 50)

### Performance Tuning
- `MAX_PAGES_PER_BROWSER`: Pages per browser (default: 5)
- `SCREENSHOT_TIMEOUT`: Default screenshot timeout in seconds (default: 30)
- `BROWSER_TIMEOUT`: Browser creation timeout in seconds (default: 30)

### Memory Management  
- `MEMORY_LIMIT`: Memory limit per browser in MB (default: 400)
- `CLEANUP_INTERVAL`: Browser cleanup interval in minutes (default: 5)
- `MAX_BROWSER_AGE`: Maximum browser age in minutes (default: 30)
- `MAX_BROWSER_USAGE`: Maximum uses per browser (default: 100)

## Browser Pool Sizing

For **r7i.2xlarge** (8 vCPUs, 64GB RAM):

### Recommended Configuration
```bash
MAX_BROWSERS=50
MAX_PAGES_PER_BROWSER=5
# Total concurrent operations: 250
# Memory usage: ~25GB (50 browsers * 400MB + overhead)
```

### Memory Calculation
- Base browser: ~300MB
- Page overhead: ~20MB per page
- Browser with 5 pages: ~400MB
- 50 browsers: ~20GB
- Service overhead: ~3-5GB
- **Total: ~25GB**

### Performance Expectations
- **Throughput**: 100-200 screenshots/minute
- **Latency**: 1-3 seconds per screenshot
- **Concurrency**: 250 parallel operations
- **Memory**: 25GB RAM usage

## Scaling Guidelines

### Light Load (< 50 requests/minute)
```bash
MAX_BROWSERS=10
MAX_PAGES_PER_BROWSER=3
# Memory: ~5GB
```

### Medium Load (50-100 requests/minute)  
```bash
MAX_BROWSERS=25
MAX_PAGES_PER_BROWSER=4
# Memory: ~12GB
```

### Heavy Load (100+ requests/minute)
```bash
MAX_BROWSERS=50
MAX_PAGES_PER_BROWSER=5
# Memory: ~25GB
```

## Monitoring

### Health Check
```bash
curl http://localhost:8001/health
```

### Performance Stats
```bash
curl http://localhost:8001/stats
```

### Key Metrics
- `totalBrowsers`: Current browser count
- `availableBrowsers`: Available for new requests
- `screenshotsTaken`: Total screenshots completed
- `avgScreenshotTime`: Average processing time
- `concurrentOperations`: Active requests
- `totalErrors`: Error count
