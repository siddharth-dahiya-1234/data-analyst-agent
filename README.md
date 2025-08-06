# Data Analyst Agent API

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python)
![Framework](https://img.shields.io/badge/FastAPI-0.111-green?style=for-the-badge&logo=fastapi)
![LLM](https://img.shields.io/badge/Google-Gemini-purple?style=for-the-badge&logo=google)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

A powerful, AI-driven API that uses Google's Gemini model to source, prepare, analyze, and visualize data based on natural language instructions.

## 📝 Project Overview

This project is a FastAPI web service that exposes a single API endpoint to a sophisticated Data Analyst Agent. The agent is built using the LangChain framework and leverages the reasoning capabilities of Google's Gemini models. It is designed to handle multi-step data analysis tasks that require fetching data from the web, performing complex queries and calculations, and generating visualizations.

### ✨ Key Features

* **Multi-Source Data Handling**: Capable of sourcing data from both web pages (HTML scraping) and large cloud datasets (e.g., Parquet files in S3 via DuckDB).
* **Dynamic Code Generation**: The agent writes and executes its own Python code to perform analysis, ensuring it can adapt to a wide variety of questions.
* **Robust Agentic Architecture**: Built on a `ReAct` (Reason+Act) framework with specialized, fault-tolerant tools for scraping and code execution.
* **Dynamic Visualization**: Can generate plots and charts on the fly and return them as base64-encoded data URIs.
* **Ready for Deployment**: Containerized with a `Dockerfile` for easy deployment on platforms like Render.

---

## 🚀 Getting Started

Follow these instructions to set up and run the project locally.

### Prerequisites

* Python 3.11+
* Git

### 1. Clone the Repository

```bash
git clone <your-github-repository-url>
cd data-analyst-agent
2. Set Up the Environment
Create and activate a Python virtual environment.

Windows (Command Prompt):

DOS

python -m venv venv
venv\Scripts\activate
macOS / Linux:

Bash

python3 -m venv venv
source venv/bin/activate
3. Install Dependencies
Install all the required libraries using the requirements.txt file.

Bash

pip install -r requirements.txt
4. Configure Your API Key
You must add your Google Gemini API key to the project.

Open the agent.py file.

Find this line:

Python

os.environ["GOOGLE_API_KEY"] = "AIzaSyDzODRcVEuSxD9D2Ze-Y8jsJldsUPQ7-v0"
Replace the key with your own if you are using a different one.

5. Run the Application
Start the FastAPI server using uvicorn.

Bash

uvicorn main:app --reload
The API will now be running at http://127.0.0.1:8000.

🛠️ Usage
Interact with the agent by sending a POST request to the /api/ endpoint.

Endpoint: POST /api/

Body: multipart/form-data

The request must contain a single key named file.

The value for this key should be a text file (e.g., question.txt) containing the natural language prompt for the agent.

Example curl Request
Create a file named question.txt with your data analysis task.

Run the following command in your terminal:

Bash

curl -X POST \
  -F "file=@question.txt" \
  [http://127.0.0.1:8000/api/](http://127.0.0.1:8000/api/)
Example Success Response
A successful response will be a JSON object containing the agent's final answer.

JSON

{
  "output": [
    5,
    "Titanic",
    0.48578218083889235,
    "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg..."
  ]
}
📄 License
This project is licensed under the MIT License. See the LICENSE file for details.
