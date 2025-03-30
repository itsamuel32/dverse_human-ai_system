from langchain.agents import initialize_agent, create_react_agent, AgentExecutor
from langchain.agents.agent_types import AgentType
# from langchain_community.llms import Ollama  # ✅ Use Ollama now
from langchain_ollama import OllamaLLM
from tools.tools import get_environment, move_object
from langchain.prompts import PromptTemplate


def main():
    tools = [get_environment, move_object]

    # local Mistral model
    llm = OllamaLLM(model="mistral")

    # agent = initialize_agent(
    #     tools=tools,
    #     llm=llm,
    #     agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    #     verbose=True,
    #     handle_parsing_errors = True
    # )

    prompt = PromptTemplate.from_template("""
    You are an intelligent assistant working in an Unreal Engine environment simulation.

    TOOLS:
    {tools}

    RULES:

    - try to firstly call proper tool based on its description from {tool_names}
    - do NOT fabricate any data, simply mention the error from the tools

    STRICT FORMAT:

    Input: {input}
    Thought: what you are going to do based on the input
    Action: What did you actually do
    Action Input: Based on the request
    Observation: results from executing the tool function, if any, if not , do not fabricate data but rather mention no data present
    Thought: what you learned
    Final Answer: final response to the user

    Do not break this format.

    Begin!

    Input: {input}
    {agent_scratchpad}
    """)

    agent_chain = create_react_agent(llm=llm, tools=tools, prompt=prompt)
    agent = AgentExecutor(agent=agent_chain, tools=tools,
                          verbose=True, handle_parsing_errors=True,
                          max_iterations=10, return_intermediate_steps=True)

    response = agent.invoke({"input": "How many objects are red?"})
    print(response)


if __name__ == "__main__":
    main()
