from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain.agents import AgentType, AgentExecutor
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory
from langchain.agents.conversational.base import ConversationalAgent
from langserve import add_routes
from fastapi import FastAPI
from dotenv import load_dotenv

from langchain_community.utilities.duckduckgo_search import DuckDuckGoSearchAPIWrapper
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from Api.OpenWeatherApi import weather
from Api.OMDBApi import movieDetailes
from Api.TimeModule import get_time, get_date, get_day, get_datetime, get_precise_timezone

import os
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Load environment variables
load_dotenv()

# LangSmith settings (optional, disable by removing env vars)
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGSMITH_PROJECT"] = "Gedion"
os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"

# Memory
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    input_key="input",
    output_key="output",
    k=5
)

# Tools
search_tool = Tool(
    name="Search",
    func=DuckDuckGoSearchAPIWrapper().run,
    description="Search the web for real-time info. Input: query."
)

wikipedia_tool = Tool(
    name="Wikipedia",
    func=WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper()).run,
    description="Search Wikipedia for general or historical info. Input: topic."
)

weather_tool = Tool(
    name="OpenWeather",
    func=weather,
    description="Get current weather. Input: city or region."
)

movie_tool = Tool(
    name="MovieDetails",
    func=movieDetailes,
    description="Get movie info. Input: movie name."
)

time_tool = Tool(name="GetTime", func=get_time, description="Get current time.")
date_tool = Tool(name="GetDate", func=get_date, description="Get today's date.")
day_tool = Tool(name="GetDay", func=get_day, description="Get current day of week.")
datetime_tool = Tool(name="GetDateTime", func=get_datetime, description="Get full date, time, and day.")
precise_timezone_tool = Tool(name="GetPreciseTimezone", func=get_precise_timezone, description="Get IANA timezone.")

# Prompt Template
template = """
You are a helpful AI assistant with access to the following tools:
1. Search: for real-time web data.
2. Wikipedia: for general knowledge.
3. OpenWeather: for weather updates.
4. MovieDetails: for movie info.
5. GetTime, GetDate, GetDay, GetDateTime, GetPreciseTimezone: for time info.

Only use one tool at a time unless necessary. Answer concisely.

Memory: {memory}
User Input: {input}
Thought: {agent_scratchpad}
"""

prompt = PromptTemplate(
    input_variables=["memory", "input", "agent_scratchpad"],
    template=template
)

# LLM
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.1,
    max_tokens=1000
)

# Conversational Agent
agent = ConversationalAgent.from_llm_and_tools(
    tools=[search_tool, wikipedia_tool, weather_tool, movie_tool, time_tool, date_tool, day_tool, datetime_tool, precise_timezone_tool],
    llm=llm,
    agent_type=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    prompt=prompt,
    memory=memory,
    verbose=False
)

# Agent Executor
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=[search_tool, wikipedia_tool, weather_tool, movie_tool, time_tool, date_tool, day_tool, datetime_tool, precise_timezone_tool],
    memory=memory,
    verbose=False,
    handle_parsing_errors=False,
    return_intermediate_steps=False,
    output_key="output"
)

# FastAPI + LangServe
app = FastAPI(title="Gedion LangServe Agent")
add_routes(app, agent_executor, path="/agent")

@app.get("/agent")
def read_root():
    return {"message": "LangServe API is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)