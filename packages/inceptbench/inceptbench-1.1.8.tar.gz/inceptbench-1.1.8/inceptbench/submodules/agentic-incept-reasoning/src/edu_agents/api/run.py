import uvicorn
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())

if __name__ == "__main__":
    uvicorn.run(
        "edu_agents.api.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 