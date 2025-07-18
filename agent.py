from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain.agents import AgentType, AgentExecutor
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory
from langchain.agents.conversational.base import ConversationalAgent
from langsmith import traceable

from langchain_community.utilities.duckduckgo_search import DuckDuckGoSearchAPIWrapper
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from Api.OpenWeatherApi import weather
from Api.OMDBApi import movieDetailes
from Api.TimeModule import get_time, get_date, get_day, get_datetime, get_precise_timezone

import os
from dotenv import load_dotenv
import warnings
import json
from datetime import datetime
from pathlib import Path

# Suppress warnings
warnings.filterwarnings('ignore')

# Load environment variables from .env file
load_dotenv()

key = os.getenv("GROQ_API_KEY")
if not key:
    raise ValueError("GROQ_API_KEY environment variable is not set.")

#langsmith API key
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGSMITH_PROJECT"]="Gedion"
os.environ["LANGSMITH_ENDPOINT"]="https://api.smith.langchain.com"

# Wrapper
search = DuckDuckGoSearchAPIWrapper()
wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())

# Logging setup
LOG_PATH = Path("logs/feedback_log.jsonl")
#LOG_PATH.parent.mkdir(exist_ok=True)

def log_step(agent_input: str, tool_used: str, output: str):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "input": agent_input,
        "tool": tool_used,
        "output": output,
    }
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")


# Memory
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    input_key="input",
    output_key="output",
    k=5  # Number of messages to keep in memory
)
#Tools
search_tool = Tool(
    name="Search",  
    func=search.run,
    description="Useful for when you need to answer questions about current events or find information that is not in the model's training data. Input should be a search query.",)

wikipedia_tool = Tool(
    name="Wikipedia",       
    func=wikipedia.run,
    description="Useful for when you need to answer questions about general knowledge, historical topics, or definitions. Input should be a search query or a topic name.",)

# weather tool
weather_tool = Tool(
    name="OpenWeather",
    func=weather,
    description="Useful for when you need to answer questions about current weather conditions, forecasts, or alerts in any city or region. Input should be a city name or region."
)

# Movie details tool
movie_tool = Tool(
    name="MovieDetails",
    func=movieDetailes,
    description="Useful for when you need to get detailed information about a movie. Input should be the movie name."
)

# Time tools
time_tool = Tool(
    name="GetTime",
    func=get_time,
    description="Returns the current time in the format HH:MM AM/PM."
)

# Date tool
date_tool = Tool(
    name="GetDate",
    func=get_date,
    description="Returns today's date in the format DD Month YYYY." 
)

# Day tool
day_tool = Tool(
    name="GetDay",
    func=get_day,
    description="Returns the current day of the week."      
)

# Datetime tool
datetime_tool = Tool(   
    name="GetDateTime",
    func=get_datetime,
    description="Returns the full current date, time, and day in the format 'Day, DD Month YYYY, HH:MM AM/PM'."
)

# Precise timezone tool
precise_timezone_tool = Tool(
    name="GetPreciseTimezone",
    func=get_precise_timezone,
    description="Returns the full IANA timezone name like Asia/Kolkata."
)

# Template
template = """
    You are a smart AI agent that can use various tools to assist the user.
    You have access to the following tools:

    1. 🕸️ DuckDuckGo Search – Use this for recent, factual, or web-based information (news, weather, live updates).
    2. 📚 Wikipedia – Use this for factual knowledge, historical topics, general concepts, definitions, and educational information.
    3. 🌦️ OpenWeather – Use for weather-related questions like current weather, temperature, forecast, or weather alerts in any city or region.
    4. 🎬 MovieDetails – Use this to get detailed information about a movie, including actors, director, plot, and ratings.
    5. ⏰ GetTime – Returns the current time in HH:MM AM/PM format.
    6. 📅 GetDate – Returns today's date in DD Month YYYY format.
    7. 📆 GetDay – Returns the current day of the week.
    8. 📅 GetDateTime – Returns the full current date, time, and day in the format 'Day, DD Month YYYY, HH:MM AM/PM'.
    9. 🌐 GetPreciseTimezone – Returns the full IANA timezone name like Asia/Kolkata.

    When answering a question, follow this reasoning process:

    1. Understand the user’s intent.
    2. Choose a tool only if the task cannot be answered using your own knowledge.
    3. If the user is asking for recent or web-based information, use DuckDuckGo with a focused search phrase.
    4. Otherwise, use the most appropriate tool or respond directly.
    5. Respond clearly and concisely with a helpful answer.
    6. Use DuckDuckGo for real-time web info (non-weather).
    7. Use Wikipedia for general knowledge or historical facts.
    8. Use OpenWeather when the user asks about weather conditions.
    9. Respond clearly and concisely with useful information from the tools.
    10. In context of movies, use the MovieDetails tool to provide comprehensive information about a movie.
    11. In context of weather, use the OpenWeather tool to provide current weather conditions, forecasts, or alerts.
    12. I want you to be answer questions in a conversational manner, like a human would.
    13. To the point answers, no long explanations.unless necessary.
    14. Use the time, date, day, and datetime tools to provide current time, date, day of the week, or full datetime information when requested.
    15. Use the precise timezone tool to provide the full IANA timezone name when requested.whenver the user asks for timezone information.

    🧠 Memory – You can remember past interactions to provide contextually relevant responses.
    

    Only use one tool at a time unless otherwise required.

    Current Conversation History : {memory}
    User Input : {input}
    Thought : {agent_scratchpad}

    Stay helpful, safe, and precise."""    

# Prompt Template
prompt = PromptTemplate(
    input_variables=["memory", "input", "agent_scratchpad"],
    template=template
)   

# Initialize the Groq chat model
llm =ChatGroq(model="llama-3.3-70b-versatile",
              temperature=0.1,
              max_tokens=1000)

# Agent initialization
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
    return_intermediate_steps=True,
    output_key="output"
)

# Traceable decorator for LangSmith
@traceable(name="gedion_cli_agent_run", metadata={"mode": "cli", "source": "terminal"})
def run_agent(user_input: str):

    response = agent_executor.invoke(
        {"input": user_input},
        return_only_outputs=False)  # required to get intermediate_steps)
    
    # Extract output and intermediate steps
    output = response.get("output", "")
    intermediate_steps = response.get("intermediate_steps", [])

    tool_used = "None"
    if intermediate_steps:
        tool_action = intermediate_steps[-1][0]
        tool_used = getattr(tool_action, "tool", "Unknown")

    print(f"Agent: {output}") 

    # Do NOT print intermediate_steps — only use tool_used
    log_step(agent_input=user_input, tool_used=tool_used, output=output)

# Agent Execution Loop
print("Welcome to the Gedion Agent! Type 'exit' to stop the agent.")
while True:
    user_input = input("User: ")
    
    if user_input.lower() in ["exit", "quit", "stop"]:
        print("Exiting the agent.")
        break

    run_agent(user_input)
