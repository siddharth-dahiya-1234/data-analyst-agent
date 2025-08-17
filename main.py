from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse
from agent import DataAnalystAgent
from typing import Optional, Union
import json
import logging

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/")
def health_check():
    return {"status": "ok", "version": "1.1.0"}

@app.post("/api/")
async def analyze_data(
    request: Request,
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None)
):
    """
    Endpoint that accepts either:
    - File upload (via form-data)
    - Direct text submission (via form-urlencoded)
    """
    try:
        agent = DataAnalystAgent()
        text_query = None

        # Check for file upload
        if file:
            logger.info(f"Received file upload: {file.filename} ({file.size} bytes)")
            
            # Validate file type
            if not file.filename.lower().endswith('.txt'):
                raise HTTPException(400, "Only .txt files are accepted")
            
            content = await file.read()
            if not content:
                raise HTTPException(400, "Uploaded file is empty")
            
            try:
                text_query = content.decode('utf-8').strip()
            except UnicodeDecodeError:
                raise HTTPException(400, "File must contain UTF-8 text")
        
        # Check for direct text input
        elif text:
            logger.info("Received direct text input")
            text_query = text.strip()
        
        # No valid input found
        else:
            # Fallback to checking raw form data
            form_data = await request.form()
            logger.warning(f"No direct input found, form data: {form_data}")
            raise HTTPException(400, "Either 'file' or 'text' parameter must be provided")

        # Validate we have content to process
        if not text_query:
            raise HTTPException(400, "No text content found to analyze")

        logger.info(f"Processing query: {text_query[:100]}...")  # Log first 100 chars

        # Process with agent
        try:
            response = agent.run(text_query)
            return JSONResponse({
                "status": "success",
                "input_type": "file" if file else "text",
                "result": response
            })
            
        except json.JSONDecodeError as e:
            logger.error(f"Agent JSON error: {str(e)}")
            raise HTTPException(500, "Agent response formatting error")
            
    except HTTPException as he:
        logger.error(f"Client error: {he.detail}")
        raise
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        raise HTTPException(500, "Internal processing error")
