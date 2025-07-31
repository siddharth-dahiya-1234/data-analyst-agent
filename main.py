from fastapi import FastAPI, UploadFile, File, HTTPException
from agent import DataAnalystAgent

app = FastAPI()
agent = DataAnalystAgent()

@app.get("/")
def health_check():
    """A simple endpoint to check if the API is running."""
    return {"status": "ok"}

@app.post("/api/")
async def analyze_data(file: UploadFile = File(...)):
    """Receives the analysis task and runs the agent."""
    try:
        question_bytes = await file.read()
        question = question_bytes.decode("utf-8")
        result = agent.run(question)
        return result
    except Exception as e:
        # This provides more detailed error messages for debugging
        raise HTTPException(status_code=500, detail=str(e))