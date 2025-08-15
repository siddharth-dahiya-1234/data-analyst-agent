import os
import json
import pandas as pd
from io import StringIO
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent, Tool
from langchain_core.prompts import PromptTemplate
from langchain_experimental.tools import PythonREPLTool

# --- Configuration ---
os.environ["GOOGLE_API_KEY"] = "AIzaSyDzODRcVEuSxD9D2Ze-Y8jsJldsUPQ7-v0"

# --- Specialized Tools ---

def scrape_website_table(url: str) -> str:
    """
    Finds the correct 'Highest-grossing films' table by matching text in its caption,
    cleans its headers, and returns it as a clean JSON string.
    """
    try:
        tables = pd.read_html(url, match="Highest-grossing films")
        if not tables:
            return "Error: Could not find the table with the caption 'Highest-grossing films'."
        df = tables[0]
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(-1)
        df = df.iloc[:, :6]
        df.columns = ['Rank', 'Peak', 'Title', 'Worldwide_gross', 'Year', 'Reference']
        if 'rank' in str(df['Rank'].iloc[0]).lower():
            df = df.iloc[1:].reset_index(drop=True)
        print(f"Found and cleaned the correct table with shape: {df.shape}")
        return df.to_json(orient='records')
    except Exception as e:
        return f"Error: An exception occurred during scraping. Details: {e}"

# --- Tool Definitions ---

smart_scrape_tool = Tool(
    name="Smart_Table_Scraper",
    func=scrape_website_table,
    description="Use this tool to get data from a URL. It scrapes a page's main data table and returns it as a clean JSON string."
)

python_tool = Tool(
    name="Python_REPL",
    func=PythonREPLTool().run,
    description="A Python shell. Use this to execute python code for data analysis, calculations, or plotting. It can also be used to save data to files and read from them."
)

# --- ReAct Agent Prompt (Final, With Professional Strategy) ---
AGENT_PROMPT_TEMPLATE = """
Answer the following questions as best you can. You have access to the following tools:

{tools}

**IMPORTANT STRATEGY HINT**:
For complex tasks involving large amounts of data, it is highly recommended to follow this two-step process:
1.  Use the `Smart_Table_Scraper` to get the data.
2.  In a second step, use the `Python_REPL` tool to first save that data to a local file (e.g., `with open('data.json', 'w') as f: f.write(data_string)`).
3.  In a third step, use the `Python_REPL` tool again to write a script that reads from 'data.json' (`pd.read_json('data.json')`) and then performs the full analysis to answer the user's questions.
This file-based approach is more robust and avoids errors with large data.

Take care you will encouter an error stating "SyntaxError('leading zeros in decimal integer literals are not permitted; use an 0o prefix for octal integers" and this is because of "The problem is that the AI, when asked to write the analysis code, is incorrectly pasting the huge data string back into its own script. This is what's causing the Python interpreter to crash." make sure you do not make this same mistake again

**IMPORTANT STRATEGY HINT FOR S3/DUCKDB:**
When you need to query a public S3 bucket using `duckdb`, you MUST first enable anonymous access. Run the SQL command `SET s3_unsigned=true;` before your main `SELECT` query. For example: `con.execute("SET s3_unsigned=true;")`.
Use the following format:

Question: the input question you must answer
Thought: your reasoning and plan for the next step. 
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question. This must be a JSON array of the final answers.

Begin!

Question: {input}
{agent_scratchpad}
"""

# --- Main Agent Class (Using ReAct) ---

class DataAnalystAgent:
    def __init__(self):
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0)
        self.tools = [smart_scrape_tool, python_tool]
        prompt = PromptTemplate.from_template(AGENT_PROMPT_TEMPLATE)
        agent = create_react_agent(llm, self.tools, prompt)
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=10 # Increased slightly for the 3-step process
        )
        print("ReAct Data Analyst Agent (Final Version) initialized successfully.")

    def run(self, query: str) -> dict:
        try:
            print(f"Running ReAct agent with query: {query}")
            response = self.agent_executor.invoke({"input": query})
            final_answer_str = response.get("output", "No output found.")
            try:
                return {"output": json.loads(final_answer_str)}
            except (json.JSONDecodeError, TypeError):
                return {"output": final_answer_str}
        except Exception as e:
            return {"error": str(e)}
