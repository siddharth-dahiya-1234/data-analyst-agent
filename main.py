from fastapi import FastAPI, UploadFile, HTTPException, Request
from fastapi.responses import JSONResponse
from agent import DataAnalystAgent
import logging
import json

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/api/")
async def analyze_data(request: Request):
    try:
        # Get raw form data (bypassing normal FastAPI processing)
        form_data = await request.form()
        files = []
        
        # Extreme robustness - handle any form of file upload
        for field_name, field_value in form_data.items():
            if hasattr(field_value, 'filename'):  # Detect UploadFile-like objects
                try:
                    content = await field_value.read()
                    if content:
                        files.append({
                            'name': field_name,
                            'filename': getattr(field_value, 'filename', 'unknown'),
                            'content': content.decode('utf-8', errors='replace').strip(),
                            'type': getattr(field_value, 'content_type', 'unknown')
                        })
                except Exception as e:
                    logger.warning(f"Couldn't process {field_name}: {str(e)}")
                    continue
        
        logger.info(f"Processed files: {[f['name'] for f in files]}")
        
        if not files:
            # Final fallback - try to read raw body
            body = await request.body()
            if body:
                try:
                    files.append({
                        'name': 'raw_body',
                        'content': body.decode('utf-8', errors='replace').strip()
                    })
                except Exception:
                    pass
        
        if not files:
            raise HTTPException(400, "No processable content found")
        
        # Prepare input text from all sources
        input_text = "\n\n".join(
            f"=== File: {f.get('filename', f['name'])} ===\n{f['content']}"
            for f in files
        )
        
        logger.info(f"Analysis input (first 500 chars):\n{input_text[:500]}...")
        
        # Process with agent
        try:
            agent = DataAnalystAgent()
            response = agent.run(input_text)
            return JSONResponse({
                "status": "success",
                "files_processed": len(files),
                "result": response
            })
        except Exception as e:
            logger.error(f"Agent error: {str(e)}")
            raise HTTPException(500, "Analysis failed")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(500, "Processing error")
