# Agentic Incept Reasoning - Educational Content Generator

A sophisticated AI-powered API for generating and evaluating educational content using OpenAI's advanced models. This system leverages agentic reasoning to create high-quality educational materials with built-in evaluation capabilities.

## 🌟 Features

- **AI-Powered Content Generation**: Create educational content using advanced reasoning agents
- **Multiple AI Models**: Support for both Incept and O3 models
- **Mathematical Animations**: Generate high-quality educational animations using Manim Community Edition
- **Interactive HTML Animations**: Create engaging HTML/CSS/JavaScript animations for educational concepts
- **Real-time Streaming**: Stream responses as Server-Sent Events for responsive user experience
- **Content Evaluation**: Built-in evaluation system for generated educational content
- **Request Logging**: Comprehensive logging and analytics with Supabase integration
- **Feedback System**: User feedback collection for continuous improvement
- **RESTful API**: Clean, well-documented API endpoints
- **Command-Line Interface**: CLI for direct interaction with the system

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Cairo graphics library (for SVG/image processing)
- FFmpeg (for Manim video rendering)
- LaTeX distribution (for mathematical typesetting in animations)
- Virtual environment (recommended)

### System Dependencies

Install required system dependencies:

**macOS (using Homebrew):**
```bash
# Install required system dependencies
brew install cairo ffmpeg pkg-config
brew install --cask mactex  # For LaTeX support

# Set environment variables for pkg-config (add to your shell profile)
export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig:$PKG_CONFIG_PATH"
```

**Linux (CentOS/RHEL):**
```bash
sudo yum install -y cairo cairo-devel ffmpeg texlive-latex-base texlive-fonts-recommended texlive-latex-extra
```

**Linux (Amazon Linux 2):**
```bash
# Update and install graphics libraries
sudo yum update -y
sudo yum install -y cairo-devel pango-devel gdk-pixbuf2-devel libffi-devel pkgconfig gcc gcc-c++ make

# Install multimedia and LaTeX support
sudo amazon-linux-extras install epel -y
sudo yum install -y ffmpeg texlive texlive-latex texlive-collection-fontsrecommended texlive-collection-latexextra
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install libcairo2-dev ffmpeg texlive-latex-base texlive-fonts-recommended texlive-latex-extra
```

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd agentic-incept-reasoning
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Python dependencies:**
   
   **Option A: Direct pip install (requires system dependencies above):**
   ```bash
   pip install -r requirements.txt
   ```
   
   **Option B: If you encounter Cairo/pycairo issues on macOS:**
   ```bash
   # First install everything except manim
   pip install -r requirements.txt --ignore-installed manim
   
   # Then install manim with conda (which handles Cairo better)
   conda install -c conda-forge manim
   ```
   
   **Option C: Use pre-compiled wheels:**
   ```bash
   # Install Cairo dependencies via Homebrew first, then:
   export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig:$PKG_CONFIG_PATH"
   pip install --only-binary=all -r requirements.txt
   ```

4. **Install development dependencies (optional):**
   ```bash
   pip install -r requirements-dev.txt
   ```

5. **Set up environment variables:**
   Create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   ```

### Running the Server

**Using the start script:**
```bash
chmod +x start_server.sh
./start_server.sh
```

**Or manually with uvicorn:**
```bash
uvicorn edu_agents.api.server:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Troubleshooting Installation

**Cairo/pycairo Issues on macOS:**

If you encounter errors related to Cairo or pycairo during installation:

1. **Install missing dependencies:**
   ```bash
   # Install pkg-config if missing
   brew install pkg-config
   
   # Ensure Cairo is properly installed
   brew reinstall cairo
   ```

2. **Set environment variables:**
   ```bash
   # For Apple Silicon Macs (M1/M2)
   export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig:$PKG_CONFIG_PATH"
   
   # For Intel Macs
   export PKG_CONFIG_PATH="/usr/local/lib/pkgconfig:$PKG_CONFIG_PATH"
   
   # Add to your shell profile to make permanent
   echo 'export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig:$PKG_CONFIG_PATH"' >> ~/.zshrc
   ```

3. **Alternative: Use conda for Manim:**
   ```bash
   # Install everything except manim first
   pip install $(grep -v manim requirements.txt | tr '\n' ' ')
   
   # Then install manim via conda
   conda install -c conda-forge manim
   ```

**LaTeX Issues:**

If LaTeX rendering fails in Manim:
```bash
# Ensure LaTeX is in PATH
which latex || echo "LaTeX not found - install MacTeX"

# For basic LaTeX support without full MacTeX
brew install texlive
```

## 📖 API Documentation

### Base URLs

- **Local Development**: `http://localhost:8000`
- **Production**: `https://inceptapi.rp.devfactory.com/api/`

### Endpoints

#### 1. Generate Educational Content
**POST** `/respond`

Generate educational content using AI models with real-time streaming.

**Request Body:**
```json
{
  "prompt": "Create an MCQ about the causes of the American Civil War",
  "model": "incept",
  "conversation_id": "optional-conversation-id",
  "timeout_seconds": 600
}
```

**Parameters:**
- `prompt` (required): The educational content prompt
- `model` (optional): AI model to use (`"incept"` or `"o3"`, defaults to `"incept"`)
- `conversation_id` (optional): ID of conversation for conversation continuity
- `timeout_seconds` (optional): Request timeout in seconds (1-1200, defaults to 600)

**HTTP Status Codes:**
- `200 OK`: Successful request, returns Server-Sent Events stream
- `400 Bad Request`: Invalid JSON, missing prompt, invalid model/timeout parameters

**Response:**
Server-Sent Events stream with the following event types:

```javascript
// Text generation events
{
  "type": "text_delta",
  "data": {"text": "partial content..."},
  "request_id": "req_12345..."
}

// Reasoning process events
{
  "type": "reasoning_delta", 
  "data": {"text": "reasoning step..."},
  "request_id": "req_12345..."
}

// Final response
{
  "type": "response_final",
  "data": {
    "text": "complete educational content",
    "conversation_id": "148f064e-8ec2-4f88-a997-e101812668f4"
  },
  "request_id": "req_12345..."
}

// Error events
{
  "type": "error",
  "data": {
    "text": "Error message",
    "error_type": "RateLimitError"
  },
  "request_id": "req_12345..."
}

// Retry events
{
  "type": "retry_attempt",
  "data": {
    "text": "Request timed out, retrying... (attempt 2)",
    "attempt": 2,
    "max_attempts": 3
  },
  "request_id": "req_12345..."
}

// Heartbeat events
{
  "type": "heartbeat",
}
```

**Example using curl:**
```bash
# First request (new conversation)
curl -X POST "https://inceptapi.rp.devfactory.com/api/respond" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a multiple choice question about photosynthesis",
    "model": "incept"
  }' \
  --no-buffer

# Follow-up request (continuing conversation)  
curl -X POST "https://inceptapi.rp.devfactory.com/api/respond" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Make it easier for 5th grade",
    "model": "incept",
    "conversation_id": "148f064e-8ec2-4f88-a997-e101812668f4"
  }' \
  --no-buffer
```

#### 2. Evaluate Educational Content
**POST** `/evaluate`

Evaluate the quality of educational content using GPT-4o.

**Request Body:**
```json
{
  "content": "# MCQ: Photosynthesis\n\nWhat is the primary product of photosynthesis?\nA) Oxygen\nB) Carbon dioxide\nC) Glucose\nD) Water",
  "response_id": "optional-request-id-to-link"
}
```

**Parameters:**
- `content` (required): Educational content to evaluate (markdown format)
- `response_id` (optional): Link evaluation to specific request. Will attempt to fall back to request/response content if no ID is provided.

**HTTP Status Codes:**
- `200 OK`: Successful evaluation
- `400 Bad Request`: Missing content parameter
- `500 Internal Server Error`: Evaluation service error

**Response:**
```json
{
  "evaluation": {
    "category": {
      "reason": "reasoning...",
      "result": "RATING"  // PASS/FAIL, SUPERIOR/ACCEPTABLE/INFERIOR, etc.
    },
    ...
  }
}
```

#### 3. Submit Feedback
**POST** `/feedback`

Submit user feedback for generated content.

**Request Body:**
```json
{
  "request_id": "req_12345...",
  "rating": 1,
  "comments": "Great content, very helpful!"
}
```

**Parameters:**
- `request_id` (required): ID of the request to provide feedback for
- `rating` (optional): Integer rating (`1` = positive, `0` = neutral, `-1` = negative)
- `comments` (optional): Text feedback (max 5000 characters)

**HTTP Status Codes:**
- `200 OK`: Feedback submitted successfully
- `400 Bad Request`: Missing request_id, invalid rating/comments format
- `404 Not Found`: Request ID not found
- `500 Internal Server Error`: Database error

**Response:**
```json
{
  "message": "Feedback submitted successfully",
  "request_id": "req_12345...",
  "rating": 1,
  "comments_received": true
}
```

#### 4. Get Request Log
**GET** `/logs/{request_id}`

Retrieve detailed information about a specific request.

**Parameters:**
- `request_id` (required, path): ID of the request to retrieve

**HTTP Status Codes:**
- `200 OK`: Log retrieved successfully
- `404 Not Found`: Request ID not found
- `500 Internal Server Error`: Database error

**Response:**
```json
{
  "log": {
    "request_id": "req_12345...",
    "prompt": "Create an MCQ...",
    "response": "Generated content...",
    "model": "incept",
    "response_time": 2.345,
    "evaluation": {...},
    "feedback": {...},
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

#### 5. Get API Version
**GET** `/version`

Get the current API version.

**HTTP Status Codes:**
- `200 OK`: Version retrieved successfully

**Response:**
```json
{
  "version": "0.9.0"
}
```

#### 6. Health Check
**GET** `/health`

Check the API health status.

**HTTP Status Codes:**
- `200 OK`: API is healthy and running

**Response:**
```json
{
  "status": "healthy",
  "version": "2",
  "timestamp": 1704067200.123
}
```

#### 7. QC System Statistics
**GET** `/qc-stats`

Get Quality Control system performance and Chrome manager statistics.

**HTTP Status Codes:**
- `200 OK`: Statistics retrieved successfully
- `500 Internal Server Error`: Error retrieving statistics

**Response:**
```json
{
  "chrome_instances_created": 3,
  "chrome_instances_destroyed": 1,
  "screenshots_taken": 27,
  "cache_hits": 15,
  "cache_misses": 12,
  "concurrent_operations": 2,
  "total_errors": 0,
  "screenshot_retries": 3,
  "screenshot_timeouts": 1,
  "pool_size": 2,
  "max_pool_size": 5,
  "max_concurrent": 5,
  "pool_instances": [
    {
      "id": "chrome_140247589",
      "created_at": 1704067200.123,
      "last_used": 1704067220.456,
      "usage_count": 8,
      "is_available": true,
      "age_seconds": 45.2
    }
  ],
  "cache_stats": {
    "size": 15,
    "max_size": 1000,
    "entries": ["hash1...", "hash2..."]
  }
}
```

#### 8. Convert to QTI Format
**POST** `/convert-to-qti`

Convert educational content to QTI 3.0 format for learning management systems.

**Request Body:**
```json
{
  "content": "# MCQ: Photosynthesis\n\nWhat is the primary product of photosynthesis?\nA) Oxygen\nB) Carbon dioxide\nC) Glucose\nD) Water\n\n**Answer Information**\nCorrect Answer: C) Glucose",
  "timeout_seconds": 180
}
```

**Parameters:**
- `content` (required): Educational content in markdown format
- `timeout_seconds` (optional): Request timeout in seconds (1-1200, defaults to 180)

**HTTP Status Codes:**
- `200 OK`: QTI package generated successfully, returns ZIP file
- `400 Bad Request`: Invalid JSON, missing content, invalid timeout
- `500 Internal Server Error`: Generation failed, API errors, image download errors
- `504 Gateway Timeout`: Request timeout after retries

**Response:**
ZIP file download with Content-Type: `application/zip`

#### 9. Convert to Structured JSON
**POST** `/convert-to-athena`

Convert educational content to structured JSON format for data processing.

**Request Body:**
```json
{
  "content": "# MCQ: Photosynthesis\n\nWhat is the primary product of photosynthesis?\nA) Oxygen\nB) Carbon dioxide\nC) Glucose\nD) Water\n\n**Answer Information**\nCorrect Answer: C) Glucose",
  "timeout_seconds": 180
}
```

**Parameters:**
- `content` (required): Educational content in markdown format
- `timeout_seconds` (optional): Request timeout in seconds (1-1200, defaults to 180)

**HTTP Status Codes:**
- `200 OK`: Content converted successfully
- `400 Bad Request`: Invalid JSON, missing content, invalid timeout
- `422 Unprocessable Entity`: Unknown or unsupported content type
- `500 Internal Server Error`: Conversion failed, API errors
- `504 Gateway Timeout`: Request timeout after retries

**Response:**
```json
{
  "request_id": "athena_12345...",
  "structured_content": {
    "type": "multiple_choice_question",
    "question": "What is the primary product of photosynthesis?",
    "choices": [
      {"id": "A", "text": "Oxygen"},
      {"id": "B", "text": "Carbon dioxide"},
      {"id": "C", "text": "Glucose"},
      {"id": "D", "text": "Water"}
    ],
    "correct_answer": "C",
    "explanation": "..."
  }
}
```

### HTTP Status Codes Reference

The API uses standard HTTP status codes to indicate the success or failure of requests:

#### Success Codes
- **200 OK**: Request successful
  - All GET endpoints (version, health, logs)
  - Successful POST operations (evaluate, feedback, convert-to-athena)
  - File downloads (convert-to-qti)
  - Streaming responses (respond endpoint)

#### Client Error Codes
- **400 Bad Request**: Invalid request parameters
  - Missing required fields (prompt, content, request_id)
  - Invalid JSON in request body
  - Invalid parameter values (model, timeout_seconds, rating)
  - Parameter validation failures (comment length, timeout range)

- **404 Not Found**: Resource not found
  - Request log not found for given request_id
  - Request ID not found when submitting feedback

- **422 Unprocessable Entity**: Content format issues
  - Unknown content type (convert-to-athena)
  - Unsupported content type (convert-to-athena)

#### Server Error Codes
- **500 Internal Server Error**: Server-side errors
  - OpenAI API errors (rate limits, API failures)
  - Database connection errors
  - Content generation/conversion failures
  - Image download errors (QTI conversion)
  - JSON parsing errors (structured content)

- **504 Gateway Timeout**: Request timeouts
  - Request exceeded specified timeout_seconds
  - Multiple retry attempts failed due to timeouts

#### Error Response Format

All error responses follow this structure:

```json
{
  "error": "Human-readable error message",
  "error_type": "ErrorType"  // Optional, for programmatic handling
}
```

**Common Error Types:**
- `TimeoutError`: Request or operation timed out
- `RateLimitError`: OpenAI rate limit exceeded
- `ConnectionError`: Network connectivity issues
- `APIError`: OpenAI API errors
- `RequestTimeout`: Total request timeout exceeded
- `ImageDownloadError`: Failed to download images for QTI conversion

## 🖥️ Command Line Interface

The CLI provides direct access to the content generation system:

**Basic usage:**
```bash
python -m cli.main "Create a quiz about the solar system"
```

**With API URL configuration:**
```bash
export INCEPT_API_URL="https://inceptapi.rp.devfactory.com/api/respond"
python -m cli.main "Generate a lesson plan on fractions"
```

The CLI will display:
- 🔄 Reasoning process (in cyan)
- 📝 Generated content (in green)
- 📊 Evaluation results (in orange)

## 🔧 Development

### Project Structure

```
agentic-incept-reasoning/
├── src/
│   └── edu_agents/
│       ├── api/           # FastAPI server and endpoints
│       ├── core/          # Core agent infrastructure
│       ├── generator/     # Content generation agents
│       ├── eval/          # Content evaluation system
│       ├── tools/         # Agent tools and utilities
│       └── quality/       # Quality assurance components
├── cli/                   # Command-line interface
├── utils/                 # Utility functions (Supabase, etc.)
├── deployment/            # Deployment configurations
├── requirements.txt       # Python dependencies
├── pyproject.toml        # Project configuration
└── start_server.sh       # Server startup script
```

### Code Quality

The project includes comprehensive development tools:

- **Linting**: Ruff for fast Python linting
- **Formatting**: Black for code formatting
- **Import Sorting**: isort for organized imports
- **Type Checking**: MyPy for static type analysis
- **Testing**: pytest for unit testing

Run quality checks:
```bash
# Format code
black src/ cli/

# Sort imports
isort src/ cli/

# Lint code
ruff check src/ cli/

# Type checking
mypy src/

# Run tests
pytest
```

### Environment Variables

Required environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key
- `SUPABASE_URL`: Supabase project URL (for logging)
- `SUPABASE_KEY`: Supabase API key (for logging)
- `INCEPT_API_URL`: API URL for CLI (optional, defaults to localhost)

## ⚡ Performance Optimizations

### Chrome Management System

The API includes an optimized Chrome management system for screenshot-based quality control:

**Features:**
- **Chrome Process Pooling**: Reuses Chrome instances instead of creating new ones for each screenshot
- **Screenshot Caching**: Caches screenshots by content hash to eliminate redundant operations  
- **Concurrency Limiting**: Semaphore-based limits prevent resource exhaustion under high load
- **Retry Logic**: Exponential backoff (10s, 40s) for Chrome availability issues
- **Automatic Cleanup**: Health monitoring and periodic cleanup of old Chrome instances
- **Fallback Mechanisms**: Graceful degradation to text-only QC when Chrome fails

**Configuration:**
- **Pool Size**: Default 5 Chrome instances maximum
- **Concurrency**: Default 5 concurrent screenshot operations (matches pool size)
- **Instance Lifecycle**: 30 minutes max age, 100 uses max per instance
- **Cache Size**: 1000 screenshots cached with 10-minute TTL

**Monitoring:**
Use the `/qc-stats` endpoint to monitor Chrome pool performance and identify optimization opportunities.

### System Requirements

For optimal performance under load:
- **Chrome Dependencies**: Ensure Chrome/Chromium is properly installed
- **Memory**: 4GB+ RAM recommended for Chrome pool operations
- **File Descriptors**: Increase system limits for high-concurrency scenarios
- **Swap**: Monitor swap usage; high swap can cause Chrome timeouts

## 🚀 Deployment

The project includes deployment configurations in the `deployment/` directory. 

For production deployment:
1. Set up proper environment variables
2. Configure reverse proxy (nginx recommended)
3. Use a production WSGI server like Gunicorn
4. Set up SSL certificates
5. Configure logging and monitoring
6. Monitor QC system performance via `/qc-stats` endpoint

## 💬 Conversation Management

The API supports multi-turn conversations by using `conversation_id` to maintain context across requests.

### How It Works

1. **First Request**: Send a prompt without `conversation_id` - this creates a new conversation
2. **Response**: The `response_final` event includes a `conversation_id` in the data payload
3. **Follow-up Requests**: Include the `conversation_id` to continue the same conversation

### Example Flow

```javascript
// Step 1: Initial request (no conversation_id)
POST /respond
{
  "prompt": "Create a math question for 3rd grade"
}

// Step 1 Response: Extract conversation_id
{
  "type": "response_final",
  "data": {
    "text": "What is 5 + 3?",
    "conversation_id": "148f064e-8ec2-4f88-a997-e101812668f4"
  }
}

// Step 2: Follow-up request (include conversation_id)
POST /respond  
{
  "prompt": "Make it a multiple choice question",
  "conversation_id": "148f064e-8ec2-4f88-a997-e101812668f4"
}

// Step 2 Response: Continues same conversation
{
  "type": "response_final", 
  "data": {
    "text": "What is 5 + 3?\nA) 6\nB) 7\nC) 8\nD) 9",
    "conversation_id": "148f064e-8ec2-4f88-a997-e101812668f4"
  }
}
```

### Best Practices

- **Store conversation_id**: Extract and store the `conversation_id` from `response_final` events
- **Optional parameter**: Always make `conversation_id` optional in your client - omit for new conversations
- **Error handling**: If a conversation_id is invalid/expired, the API will create a new conversation
- **Timeouts**: Conversations have no built-in expiration, but very old conversations may be cleaned up

## 📝 Examples

### JavaScript/Frontend Integration

```javascript
// Example: Streaming educational content generation with conversation management
let currentConversationId = null;

async function generateContent(prompt, model = 'incept', conversationId = null) {
  const requestBody = { prompt, model };
  if (conversationId) {
    requestBody.conversation_id = conversationId;
  }

  const response = await fetch('https://inceptapi.rp.devfactory.com/api/respond', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(requestBody)
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    
    const chunk = decoder.decode(value);
    const events = chunk.split('\n').filter(line => line.trim());
    
    for (const eventStr of events) {
      try {
        const event = JSON.parse(eventStr);
        
        switch (event.type) {
          case 'text_delta':
            console.log('Content:', event.data.text);
            break;
          case 'reasoning_delta':
            console.log('Reasoning:', event.data.text);
            break;
          case 'response_final':
            console.log('Final response:', event.data.text);
            // Store conversation_id for future requests
            currentConversationId = event.data.conversation_id;
            break;
          case 'error':
            console.error('Error:', event.data.text);
            break;
          case 'heartbeat':
            pass // ignore heartbeat events
        }
      } catch (e) {
        // Skip invalid JSON
      }
    }
  }
}

// Usage examples
// First message (new conversation)
await generateContent("Create an MCQ about photosynthesis");

// Follow-up message (continue conversation)
await generateContent("Make it easier for 3rd grade", 'incept', currentConversationId);
```

### Python Client

```python
import requests
import json

class EducationalContentClient:
    def __init__(self, base_url="https://inceptapi.rp.devfactory.com/api"):
        self.base_url = base_url
        self.current_conversation_id = None
    
    def generate_content(self, prompt, model="incept", conversation_id=None):
        """Generate educational content using the API."""
        url = f"{self.base_url}/respond"
        data = {"prompt": prompt, "model": model}
        
        # Use provided conversation_id or stored one
        if conversation_id:
            data["conversation_id"] = conversation_id
        elif self.current_conversation_id:
            data["conversation_id"] = self.current_conversation_id
        
        response = requests.post(url, json=data, stream=True)
        
        for line in response.iter_lines():
            if line:
                try:
                    event = json.loads(line.decode('utf-8'))
                    if event['type'] == 'response_final':
                        # Store conversation_id for future requests
                        self.current_conversation_id = event['data'].get('conversation_id')
                        return event['data']['text']
                except json.JSONDecodeError:
                    continue
        
        return None
    
    def start_new_conversation(self):
        """Start a new conversation by clearing the stored conversation_id."""
        self.current_conversation_id = None

# Usage
client = EducationalContentClient()

# First message (new conversation)
content1 = client.generate_content("Create a quiz about the solar system")
print("First response:", content1)

# Follow-up message (continues conversation)
content2 = client.generate_content("Make it easier for 5th grade")
print("Follow-up response:", content2)

# Start a new conversation
client.start_new_conversation()
content3 = client.generate_content("Create a lesson plan about fractions")
print("New conversation:", content3)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the API logs using the `/logs/{request_id}` endpoint
- Review the error messages in the API responses

## 🔗 Links

- **Production API**: https://inceptapi.rp.devfactory.com/api/
- **API Documentation**: Available at `/docs` endpoint when server is running
- **Interactive API Explorer**: Available at `/redoc` endpoint
- **Health Check**: https://inceptapi.rp.devfactory.com/api/health
- **API Version**: https://inceptapi.rp.devfactory.com/api/version
- **QC Statistics**: https://inceptapi.rp.devfactory.com/api/qc-stats

## 🛡️ Error Handling and Reliability

The API includes comprehensive error handling and timeout management to ensure reliable operation:

### Timeout Configuration

**Default Timeouts:**
- Request timeout: 600 seconds (10 minutes) - configurable per request (1-1200 seconds)
- OpenAI client timeout: 600 seconds for conversation calls
- Content evaluation timeout: 180 seconds
- QTI/Athena conversion timeout: 180 seconds (default), configurable per request
- Individual retry timeout with exponential backoff (2s, 4s, max 10s)

**Custom Timeout:**
```javascript
const response = await fetch('/api/respond', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    prompt: "Your prompt here",
    timeout_seconds: 300  // Custom 5-minute timeout
  })
});
```

### Error Handling

**Automatic Retry Logic:**
- Timeout errors are automatically retried up to 2 additional times
- Exponential backoff between retries (2s, 4s, max 10s)
- Clients receive `retry_attempt` events during retries

**Error Types:**
- `TimeoutError`: Request or API call timed out
- `RateLimitError`: OpenAI rate limit exceeded
- `ConnectionError`: Network connectivity issues
- `APIError`: OpenAI API errors
- `RequestTimeout`: Total request exceeded specified timeout

**Error Event Format:**
```javascript
{
  "type": "error",
  "data": {
    "text": "User-friendly error message",
    "error_type": "TimeoutError"
  },
  "request_id": "req_12345..."
}
```

**Retry Event Format:**
```javascript
{
  "type": "retry_attempt", 
  "data": {
    "text": "Request timed out, retrying... (attempt 2)",
    "attempt": 2,
    "max_attempts": 3
  },
  "request_id": "req_12345..."
}
```
