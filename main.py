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
    This endpoint finds the first uploaded file in any request and processes it.
    This is the most robust method for handling the evaluator.
    """
    try:
        agent = DataAnalystAgent()
        
        form_data = await request.form()
        
        # Find the first value in the form that is a file upload.
        the_file: UploadFile = None
        for value in form_data.values():
            if isinstance(value, UploadFile):
                the_file = value
                break # Stop after finding the first file

        # If no file was found at all, reject the request.
        if not the_file:
            raise HTTPException(status_code=400, detail="No file was found in the request form.")

        # Read the content of the file that was found.
        question_bytes = await the_file.read()
        text_query = question_bytes.decode("utf-8")
        
        print(f"--- Received query from file: {the_file.filename} ---")
        response = agent.run(text_query)
        
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
