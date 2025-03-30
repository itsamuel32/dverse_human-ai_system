from langchain.agents import create_react_agent, AgentExecutor
from langchain_ollama import OllamaLLM
from tools.tools import get_environment, move_object
from langchain.prompts import PromptTemplate


def main():
    tools = [get_environment, move_object]

    # local Mistral model
    llm = OllamaLLM(model="mistral", temperature=0.1)

    prompt = PromptTemplate(
        input_variables=["input", "tools", "tool_names", "agent_scratchpad"],
        template="""
                You are an intelligent assistant working in an Unreal Engine environment simulation.
            
                TOOLS:
                {tools}
            
                RULES:
            
                - based on the input, try to firstly call proper tool based on its description from {tool_names}
                - do NOT fabricate any data, simply mention the error from the tools
                - try accessing or executing the get_environment tool max 5 times in till you get a response 
            
                STRICT FORMAT:  
              
                Input: Can I ask you anything about the environment?  
                Thought: I need to get up-to-date data from the environment.    
                Action: get_environment 
                Action Input: ""
                Observation: [{{...}}]
                Final Answer: final response to the user, needs to be straightforward
                  
                Do not break this format.  
                  
                Begin!  
                  
                Input: {input}  
                {agent_scratchpad}  
            """)

    agent_chain = create_react_agent(llm=llm, tools=tools, prompt=prompt)
    agent = AgentExecutor(agent=agent_chain, tools=tools,
                          verbose=True, handle_parsing_errors=True,
                          max_iterations=10, return_intermediate_steps=True)

    response = agent.invoke({"input": "How many objects are my favourite?"})
    print(response)


if __name__ == "__main__":
    main()
