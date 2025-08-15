from fastapi import FastAPI, UploadFile, HTTPException, Request
from agent import DataAnalystAgent
import json

app = FastAPI()

@app.get("/")
def health_check():
    return {"status": "ok"}

@app.post("/api/")
async def analyze_data(request: Request):
    """
    This endpoint robustly handles file uploads and raw text bodies
    to be compatible with any evaluator request format.
    """
    try:
        # Agent is created safely inside the function to prevent startup crashes.
        agent = DataAnalystAgent()
        
        content_type = request.headers.get("content-type", "")
        question_bytes = b''

        # Case 1: Handle multipart/form-data
        if "multipart/form-data" in content_type:
            form_data = await request.form()
            uploaded_files = [value for value in form_data.values() if isinstance(value, UploadFile)]
            if uploaded_files:
                # Read the bytes from the file object
                question_bytes = await uploaded_files[0].read()
            else:
                # Fallback for text fields in a form
                if form_data.values():
                    question_bytes = str(next(iter(form_data.values()))).encode("utf-8")
        
        # Case 2: Fallback for raw text body
        else:
            question_bytes = await request.body()

        if not question_bytes:
            raise HTTPException(status_code=400, detail="No file or text content was found in the request.")

        # Decode the bytes into the final text query string
        text_query = question_bytes.decode("utf-8")
        
        # Correctly call the agent with the TEXT, not the file object
        response = agent.run(text_query)
        
        return response

    except HTTPException as http_exc:
        # Re-raise intended HTTP exceptions
        raise http_exc
    except Exception as e:
        # Catch any other unexpected server errors
        raise HTTPException(status_code=500, detail=str(e))
