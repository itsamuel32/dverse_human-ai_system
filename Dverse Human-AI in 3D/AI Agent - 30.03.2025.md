


## AI agent with Ollama 


Initial agent has been created using https://ollama.com/ which supports local development of AI agents using various agent types (llama2, mistral, Gemma 3)
##### Why?
Ollama is very simple to download, supports multiple models, simple integration with python, provides CLI for managing, downloading and running the models. 

Currently, the Mistral has been used to train the agent.


### Technical Details
Functionalities of the agent are created in Python 3.13 dependencies listed below...

requirements.txt
``` 
langchain ~= 0.3.21  
langchain-community~=0.3.20  
langchain-ollama ~= 0.3.0  
requests ~= 2.32.3  
python-dotenv ~= 1.1.0
```



#### NEEDS SOME ATTENTION

Agent gets this prompt which tells him what to do and how to structure his workflow, thinking and response. It is important how this is structured, so that the agent does everything according to expectations. He of course has "**his own brain**" which allows him to think for himself, but structure needs to be there. Below is the initial example, but this needs to be further improved.
```
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
```


### Functional Details

