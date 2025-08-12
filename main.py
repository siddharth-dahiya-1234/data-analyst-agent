from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from agent import DataAnalystAgent

app = FastAPI()
agent = DataAnalystAgent()

@app.get("/")
def health_check():
    return {"status": "ok"}

@app.post("/api/")
async def analyze_data(request: Request):
    try:
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
        
        # Call your solver function with the content of the file.
        result_str = solve_film_query(text_query)
        
        # Return the final parsed output.
        return {"output": json.loads(result_str)}

    except Exception as e:
        # Return any errors in a clean format.
        raise HTTPException(status_code=500, detail=str(e))