from typing import List
from langchain_openai import ChatOpenAI
from langchain_classic.agents import AgentExecutor
from langchain_classic.agents import create_react_agent
from langchain_core.tools import Tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable # For generic agent type

from langchain_core.prompts import PromptTemplate

# Can pull reAct prompt from langchain hub alternatively: hub.pull("hwchase17/react")
# To understand better the reAct prompt is elaborated here to tweak if required.
# Example agent system prompt. This will require iteration and prompt engineering.
REACT_PROMPT_TEMPLATE = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

New question: {input}
{agent_scratchpad}"""


def create_rag_agent(llm: ChatOpenAI, tools: List[Tool]) -> Runnable:
    """Creates and returns the Langchain agent for Chat Mode."""
    prompt = PromptTemplate.from_template(REACT_PROMPT_TEMPLATE)

    # Use create_react_agent (or similar) to construct the agent
    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True, # Set to False in production
        handle_parsing_errors=True # Good for MVP
    )
    return agent_executor
