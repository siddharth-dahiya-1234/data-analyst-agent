import json
from fastapi import FastAPI, UploadFile, HTTPException, Request
from agent import DataAnalystAgent

# 1. Initialize the FastAPI Application
# This creates our web server.
app = FastAPI()

# 2. Create a Health Check Endpoint
# This is a simple endpoint at the root URL (/) that Render can use to check
# if your service is live and running. It's good practice.
@app.get("/")
def health_check():
    return {"status": "ok"}

# 3. Create the Main API Endpoint
# This is the core of our API. It listens for POST requests at the /api/ path.
@app.post("/api/")
async def analyze_data(request: Request):
    """
    This endpoint robustly handles file uploads and raw text bodies
    to be compatible with any evaluator.
    """
    try:
        # 4. Initialize the Agent Safely ("Lazy Loading")
        # We create the agent *inside* the request function. This is critical for
        # stability on Render, preventing the server from crashing on startup.
        agent = DataAnalystAgent()

        # 5. Robustly Read the Incoming Data
        # This logic handles any request format the evaluator might use.
        content_type = request.headers.get("content-type", "")
        question_bytes = b''

        # Case A: Handle standard file uploads
        if "multipart/form-data" in content_type:
            form_data = await request.form()
            uploaded_files = [value for value in form_data.values() if isinstance(value, UploadFile)]
            if uploaded_files:
                # Read the content of the first file found
                question_bytes = await uploaded_files[0].read()
        
        # Case B: Fallback to handle raw text bodies
        else:
            question_bytes = await request.body()

        # If we still have no data, the request was empty.
        if not question_bytes:
            raise HTTPException(status_code=400, detail="No content was found in the request.")

        # 6. Extract the Text and Call the Agent
        # We decode the raw bytes into a normal text string.
        text_query = question_bytes.decode("utf-8")
        
        # We call the agent with the text_query string, NOT the file object.
        response = agent.run(text_query)
        
        # 7. Return the Final Answer
        return response

    except Exception as e:
        # This will catch any unexpected errors and return them cleanly.
        raise HTTPException(status_code=500, detail=str(e))
