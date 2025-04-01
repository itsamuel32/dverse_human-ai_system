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
                You answer questions based or perform tasks based on the available tools.
                - get_environment tools returns a list of game objects with their details in a form of JSON.
                - move_object is in the development and does not work yet.
                
                TOOLS to use:
                {tools}
            
                RULES:
            
                - call tools based on its description from {tool_names} applicable to the {input}
                - always wait for the return from these tools if they have any, then proceed further
                - do NOT fabricate any data, simply mention the error from the tools
                - do NOT generate code for other tools, simply access the available ones based on the context of the input.
                - if you start breaking any of the rules above, or can not answer the questions, simply apologize
          
                
                EXAMPLE CASE:
                
                Input: Which objects are in the environment?
                Thought: I should use get_environment tool to return the details of the objects from the environment.
                Action: get_environment
                Action Input: None                
            
                
                Begin!
                
                {input}
                {agent_scratchpad}  
            """)

    agent_chain = create_react_agent(llm=llm, tools=tools, prompt=prompt)
    agent = AgentExecutor(agent=agent_chain, tools=tools,
                          verbose=True, handle_parsing_errors=True,
                          max_iterations=20)

    response = agent.invoke({"input": "Execute get_environment and based on the data how many objects are my favourite?"})
    print(response)


if __name__ == "__main__":
    main()
