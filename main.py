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
    This endpoint robustly handles both 'multipart/form-data' (file uploads)
    and 'text/plain' (raw text) request bodies.
    """
    try:
        agent = DataAnalystAgent()
        question_bytes = b''
        content_type = request.headers.get("content-type", "")

        # Check if the request is a file upload
        if "multipart/form-data" in content_type:
            form_data = await request.form()
            uploaded_files = [value for value in form_data.values() if isinstance(value, UploadFile)]
            if uploaded_files:
                question_bytes = await uploaded_files[0].read()
        else:
            # If not a file upload, assume it's a raw text body
            question_bytes = await request.body()

        # If we still have no data, then it's a bad request.
        if not question_bytes:
            raise HTTPException(status_code=400, detail="No file or text content was found in the request.")

        text_query = question_bytes.decode("utf-8")
        
        response = agent.run(text_query)
        return response

    except HTTPException as http_exc:
        # Re-raise HTTPExceptions so FastAPI can handle them correctly.
        raise http_exc
    except Exception as e:
        # Catch any other unexpected server errors.
        raise HTTPException(status_code=500, detail=str(e))
