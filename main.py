from fastapi import FastAPI, UploadFile, HTTPException, Request
from agent import DataAnalystAgent
import json

app = FastAPI()

@app.get("/")
def health_check():
    return {"status": "ok"}

@app.post("/api/")
async def analyze_data(request: Request):
    try:
        agent = DataAnalystAgent()
        
        form_data = await request.form()
        if not form_data:
            raise HTTPException(status_code=400, detail="No form data received")
        
        the_file: UploadFile = None
        for key, value in form_data.items():
            if isinstance(value, UploadFile) and value.filename:
                the_file = value
                break

        if not the_file:
            raise HTTPException(status_code=400, detail="No valid file was found in the request form")
        
        if the_file.size == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        try:
            question_bytes = await the_file.read()
            text_query = question_bytes.decode("utf-8").strip()
            if not text_query:
                raise HTTPException(status_code=400, detail="File contains no text content")
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="File encoding not supported (must be UTF-8)")

        print(f"--- Received query from file: {the_file.filename} ---")
        response = agent.run(text_query)
        
        return response

    except HTTPException:
        raise
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
