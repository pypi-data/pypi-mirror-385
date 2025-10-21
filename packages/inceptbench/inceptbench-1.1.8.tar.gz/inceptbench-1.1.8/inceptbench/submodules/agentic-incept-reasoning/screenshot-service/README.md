# Screenshot Service

High-performance Node.js screenshot service using Puppeteer with browser pooling.

## Features

- **Browser Pool Management**: Maintains 50 concurrent browser instances
- **High Concurrency**: Supports 250+ parallel screenshot operations  
- **Memory Optimized**: ~25GB RAM usage for maximum throughput
- **Auto-Scaling**: Creates browsers on-demand up to pool limit
- **Health Monitoring**: Built-in stats and health checks
- **Graceful Shutdown**: Proper cleanup of all browser instances

## API Endpoints

### POST /screenshot
Takes a screenshot of HTML content.

**Request:**
```json
{
  "html": "<html>...</html>",
  "width": 1400,
  "height": 2000,
  "timeout": 10000
}
```

**Response:** Binary PNG image data

### GET /health
Service health check with pool statistics.

### GET /stats  
Detailed browser pool and performance statistics.

## Installation

```bash
cd screenshot-service
npm install
```

## Usage

```bash
# Start service
npm start

# Development mode with auto-reload
npm run dev

# Run tests
npm test
```

## Configuration

Set environment variables:

- `MAX_BROWSERS`: Maximum browser instances (default: 50)
- `PORT`: Service port (default: 8001)

## Performance

- **Screenshot Time**: 1-3 seconds per image
- **Memory Usage**: ~400MB per browser instance
- **Concurrency**: 5 pages per browser = 250 parallel operations
- **Throughput**: 100+ screenshots per minute under load

## Integration

The service integrates with the Python QC system via HTTP API calls, replacing the previous Selenium-based Chrome management.
