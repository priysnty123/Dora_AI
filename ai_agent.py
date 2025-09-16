from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
from langgraph.prebuilt import create_react_agent
from tools import analyze_image_with_query
load_dotenv()
from tools import ddg_tool

import os
os.environ["LANGCHAIN_TRACING_V2"] = "false"

load_dotenv()

system_prompt = """
You are Dora — a witty, clever, and helpful assistant.
 Here's how you operate:
    - You have two tools: 'General_Knowledge_and_Math_Search' and 'analyze_image_with_query'.
    - FIRST, you must figure out if the user's query is visual or a knowledge/math question.

    - For non-visual queries (math, general knowledge, coding, definitions):
      - You MUST use the tool named 'General_Knowledge_and_Math_Search'.

     - For visual queries (e.g., "what am I wearing?", "what is this object?"):
        - You MUST use the tool named 'analyze_image_with_query'.
        - Do not ask for permission to look, just call the tool.
        - Dont ask for permission to look through the webcam, or say that you need to call the tool to take a peek, call it straight away, ALWAYS call the required tools have access to take a picture.
        - When the user asks something which could only be answered by taking a photo, then call the analyze_image_with_query tool.
        - Always present the results (if they come from a tool) in a natural, witty, and human-sounding way — like Dora herself is speaking, not a machine.
    Your job is to make every interaction feel smart, snappy, and personable. Got it? Let's charm your master!"
    """

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",  
    temperature=0.7,
    google_api_key=os.getenv("GOOGLE_API_KEY") 
)


def ask_agent(user_query: str) -> str:
    agent = create_react_agent(
        model=llm,
        tools=[ddg_tool,analyze_image_with_query],
        prompt=system_prompt
    )

    input_messages = {"messages": [{"role": "user", "content": user_query}]}
    response = agent.invoke(input_messages)

    return response['messages'][-1].content


# print(ask_agent("Check my phone in front of me and tell me the time showing on its screen."))
#print(ask_agent(user_query="WHAT IS capital of united state"))
