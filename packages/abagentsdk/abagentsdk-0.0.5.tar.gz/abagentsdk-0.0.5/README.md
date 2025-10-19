# ================================
# 🚀 ABZ Agent SDK Quick Start Guide
# ================================

# 1️⃣ Install ABZ Agent SDK
pip install abagentsdk
# or
uv add abagentsdk

# 2️⃣ Create a .env file and add your keys
echo "GEMINI_API_KEY=your_gemini_key_here" >> .env
echo "TAVILY_API_KEY=your_tavily_key_here" >> .env

# 3️⃣ Create a new Python file (app.py)
# ------------------------------------
from dotenv import load_dotenv
load_dotenv()
import os
from abagentsdk import Agent, Memory, function_tool
from tavily import TavilyClient

# Load API keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Initialize Tavily client
tavily = TavilyClient(api_key=TAVILY_API_KEY)

# Define a Tavily search tool
@function_tool
def tavily_search(query: str) -> str:
    """Search the web using Tavily."""
    result = tavily.search(query)
    return str(result)

# Create an Agent
agent = Agent(
    name="Research Agent",
    instructions="You are a helpful researcher. Use tavily_search to find information.",
    model="gemini-2.0-flash",
    api_key=GEMINI_API_KEY,
    tools=[tavily_search],
    memory=Memory(),
)

# Run the Agent in a chat loop
while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        break
    response = agent.run(user_input)
    print("Agent:", response.content)

# 4️⃣ Run your agent
python app.py

# ✅ Example
# You: Search for BMW 7 Series
# Agent: The BMW 7 Series is a luxury sedan lineup introduced in 1977, featuring advanced comfort and performance technologies.
