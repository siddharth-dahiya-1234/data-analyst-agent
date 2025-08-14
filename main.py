from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from agent import DataAnalystAgent
import json # Make sure json is imported

app = FastAPI()

@app.get("/")
def health_check():
    return {"status": "ok"}

@app.post("/api/")
async def analyze_data(request: Request):
    try:
        # The agent is now created safely inside the function. (CHANGE #1)
        agent = DataAnalystAgent()

        # Get all the form data from the incoming request.
        form_data = await request.form()
        
        # Find the uploaded file among the form values.
        uploaded_files = [value for value in form_data.values() if isinstance(value, UploadFile)]

        # Check if a file was actually sent.
        if not uploaded_files:
            raise HTTPException(status_code=400, detail="No file was found in the request.")

        # Process the first file found.
        the_file = uploaded_files[0]
        question_bytes = await the_file.read()
        text_query = question_bytes.decode("utf-8")
        
        # Correctly call the agent's run method and return the response. (CHANGE #2)
        response = agent.run(text_query)
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
