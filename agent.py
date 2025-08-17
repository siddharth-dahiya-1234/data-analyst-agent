import os
import ast
import json
import re
import pandas as pd
from io import StringIO
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent, Tool
from langchain_core.prompts import PromptTemplate
from langchain_experimental.tools import PythonREPLTool
from typing import Dict, Union, List, Any

# --- Configuration ---
os.environ["GOOGLE_API_KEY"] = "AIzaSyB_KUx5kaJWMq_R8x4HKfPeReJ7v47eLHc"

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
        # Save the cleaned DataFrame to a local file.
        df.to_json("data.json", orient='records', indent=2)
        # Return a success message, NOT the data itself.
        return "Successfully scraped the data and saved it to 'data.json'."
    except Exception as e:
        return f"Error: An exception occurred during scraping. Details: {e}"

# --- Tool Definitions ---

smart_scrape_tool = Tool(
    name="Smart_Table_Scraper",
    func=scrape_website_table,
    description="Use this tool first to get data from a URL. It scrapes a page's main data table, saves it to a file named 'data.json', and returns a success message."
)

python_tool = Tool(
    name="Python_REPL",
    func=PythonREPLTool().run,
    description="A Python shell. Use this to execute python code for data analysis. It is ideal for reading a local file (like 'data.json') into a pandas DataFrame and then performing calculations and plotting."
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
A VERY IMPORTANT AND CRITICAL FIX HERE YOU HAVE TO RETURN ONLY The raw JSON array or object DO NOT WRAP IT AT ALL THIS WILL FAIL THE EVALUATION STEP

**CRITICAL OUTPUT FORMATTING RULE:**
When using the `Python_REPL` tool to generate the final answer, you MUST import the `json` library and use `json.dumps()` to format your output. This ensures the output is a valid JSON string that the system can parse.
**Example:** `import json; my_data = [2, "Avatar", -1.0, "base64_string..."]; print(json.dumps(my_data))`
Final Answer: [ The raw JSON array or object ]

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

    def run(self, query: str) -> Union[Dict[str, Any], List[Any]]:
        """
        Process queries and return complete JSON output with special handling for:
        - Strings starting with [" and containing escaped quotes
        - Malformed JSON with backslashes
        - Mixed content including base64 images
        
        Args:
            query: Input query string
            
        Returns:
            Union[Dict, List]: The complete parsed JSON structure
        """
        try:
            print(f"Processing query: {query[:200]}...")  # Log first 200 chars
            
            # Get raw response from agent executor
            response = self.agent_executor.invoke({"input": query})
            raw_output = response.get("output", "{}")
            
            # Clean markdown fences if present
            clean_str = re.sub(r'^```(json)?\n?|```$', '', raw_output, flags=re.MULTILINE).strip()
            
            # SPECIAL HANDLING FOR YOUR SPECIFIC CASE
            if clean_str.startswith('["') and '\\"' in clean_str:
                try:
                    # First try with proper JSON parsing
                    return json.loads(clean_str)
                except json.JSONDecodeError:
                    # Handle the case with escaped quotes and backslashes
                    fixed_str = clean_str.replace('\\"', '"')
                    try:
                        return json.loads(fixed_str)
                    except json.JSONDecodeError:
                        # Fall back to literal eval if JSON still fails
                        try:
                            return ast.literal_eval(clean_str)
                        except (ValueError, SyntaxError):
                            pass
            
            # Regular JSON parsing for all other cases
            try:
                return json.loads(clean_str)
            except json.JSONDecodeError as json_err:
                # Try literal eval for Python structures
                try:
                    parsed = ast.literal_eval(clean_str)
                    if isinstance(parsed, (dict, list)):
                        return parsed
                    return {"result": parsed}
                except (ValueError, SyntaxError):
                    # Final fallback - return raw content
                    return {"raw_output": clean_str}

        except Exception as e:
            return {
                "error": str(e),
                "type": type(e).__name__,
                "status": "error"
            }
