from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from agent import DataAnalystAgent
import logging
import json

app = FastAPI()

# Configure more detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.get("/")
def health_check():
    return {"status": "ok", "version": "FINAL-1.1"}

@app.post("/api/")
async def analyze_data(request: Request):
    """
    The ultimate endpoint that handles:
    - Direct text submissions
    - File uploads (any format)
    - Malformed requests
    """
    logger.info("Request received - headers: %s", request.headers)
    
    try:
        # 1. Read raw body with timeout protection
        body_bytes = await request.body()
        
        # 2. Detailed empty body analysis
        if not body_bytes:
            content_type = request.headers.get('content-type', '')
            logger.error(f"Empty body with content-type: {content_type}")
            raise HTTPException(400, "Request body cannot be empty")
        
        # 3. Advanced decoding with fallbacks
        try:
            text_content = body_bytes.decode('utf-8').strip()
        except UnicodeDecodeError:
            # Handle binary files by extracting possible text
            text_content = body_bytes.decode('utf-8', errors='replace').strip()
            logger.warning("Had to use replacement characters in decoding")
        
        if not text_content:
            raise HTTPException(400, "No readable text content found")
        
        logger.info("Processing %d chars starting with: %.100s...", 
                  len(text_content), text_content)
        
        # 4. Agent execution with validation
        agent = DataAnalystAgent()
        try:
            result = agent.run(text_content)
            
            # Ensure response is valid JSON
            if isinstance(result, dict):
                return JSONResponse(result)
            return JSONResponse({"result": result})
            
        except json.JSONDecodeError as e:
            logger.error("Agent returned invalid JSON: %s", str(e))
            raise HTTPException(500, "Result formatting error")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error during processing")
        raise HTTPException(500, "Processing failed")
