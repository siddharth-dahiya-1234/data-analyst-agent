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
    This endpoint robustly handles file uploads, form text fields,
    and raw text bodies to be compatible with any evaluator.
    """
    try:
        agent = DataAnalystAgent()
        content_type = request.headers.get("content-type", "")
        question_bytes = b''

        # Case 1: Handle multipart/form-data (most likely)
        if "multipart/form-data" in content_type:
            form_data = await request.form()
            
            # Look for a file first
            uploaded_files = [value for value in form_data.values() if isinstance(value, UploadFile)]
            if uploaded_files:
                question_bytes = await uploaded_files[0].read()
            else:
                # If no file, look for the first text field and use its value
                if form_data.values():
                    first_value = next(iter(form_data.values()))
                    question_bytes = str(first_value).encode("utf-8")

        # Case 2: Fallback to handle raw text body
        else:
            question_bytes = await request.body()

        # If we still have no data, then it's a bad request
        if not question_bytes:
            raise HTTPException(status_code=400, detail="No file or text content was found in the request.")

        text_query = question_bytes.decode("utf-8")
        
        response = agent.run(text_query)
        return response

    except HTTPException as http_exc:
        # Re-raise intended HTTP exceptions
        raise http_exc
    except Exception as e:
        # Catch any other unexpected server errors
        raise HTTPException(status_code=500, detail=str(e))
