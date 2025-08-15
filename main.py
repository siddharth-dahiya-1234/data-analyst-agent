import os
import json
import pandas as pd
from io import BytesIO
from fastapi import FastAPI, UploadFile, HTTPException, Request
from agent import DataAnalystAgent

app = FastAPI(title="Data Analyst Agent")

@app.get("/")
def health_check():
    return {"status": "ok"}

@app.post("/api/")
async def analyze_data(request: Request):
    """
    This endpoint robustly handles a required 'question' file and an
    optional 'data' file, creating a dynamic prompt for the agent.
    """
    try:
        form_data = await request.form()
        
        # --- Flexible File Identification ---
        questions_file: UploadFile = None
        data_file: UploadFile = None

        for key, value in form_data.items():
            if isinstance(value, UploadFile):
                # Heuristic: Assume the .txt file is the question
                if value.filename.lower().endswith(".txt"):
                    questions_file = value
                else:
                    data_file = value
        
        if not questions_file:
            raise HTTPException(status_code=400, detail="A .txt file with questions is required.")

        # --- Read the Question File ---
        question_content = (await questions_file.read()).decode("utf-8")
        
        final_prompt = question_content
        
        # --- Pre-process Data File if it Exists ---
        if data_file:
            print(f"--- Data file found: {data_file.filename}. Pre-processing... ---")
            content = await data_file.read()
            filename = data_file.filename.lower()
            df = None

            if filename.endswith(".csv"):
                df = pd.read_csv(BytesIO(content))
            elif filename.endswith((".xls", ".xlsx")):
                df = pd.read_excel(BytesIO(content))
            elif filename.endswith(".parquet"):
                df = pd.read_parquet(BytesIO(content))
            elif filename.endswith(".json"):
                df = pd.read_json(BytesIO(content))
            
            if df is not None:
                # Create a preview of the DataFrame to show the agent
                df_preview = (
                    f"\n\nAn additional data file was uploaded. Use this data to answer the questions.\n"
                    f"Do not use any other tools to find data.\n"
                    f"Dataset preview ({len(df)} rows total):\n"
                    f"{df.head().to_markdown()}"
                )
                # Add the preview and instructions to the main prompt
                final_prompt += df_preview
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported data file type: {filename}")

        # --- Initialize and Run the Agent ---
        agent = DataAnalystAgent()
        print(f"--- Running agent with final prompt ---\n{final_prompt}\n--------------------")
        response = agent.run(final_prompt)
        return response

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
