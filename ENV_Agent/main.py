import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import time
# AutoGen AI adapters
from autogen_ext.tools.mcp import mcp_server_tools
from autogen_ext.tools.mcp import SseServerParams
from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ModelInfo, ModelFamily



# ─────────────────────────  lifespan  ────────────────────────────────


load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    server_params = SseServerParams(url=os.getenv("MCP_SERVER_URL", "http://localhost:8000/sse"))

    tools = await mcp_server_tools(server_params)
    print(f"[startup] {len(tools)} tools loaded from MCP")

    # model_client = OllamaChatCompletionClient(model="llama3.1:8b",
    #                                           model_info=ModelInfo(function_calling=True,
    #                                                                json_output=False,
    #                                                                vision=False,
    #                                                                structured_output=True,
    #                                                                family=ModelFamily.UNKNOWN
    #                                                                )
    #                                           )

    model_client = OpenAIChatCompletionClient(
        model="gpt-4.1",
        api_key=os.getenv('OPENAI_API_KEY'),
        model_info=ModelInfo(function_calling=True, json_output=False, vision=False, structured_output=True,
                             family=ModelFamily.GPT_4)
    )

    agent = AssistantAgent(
        name="ENV_Agent",
        model_client=model_client,
        tools=tools,
        system_message=(
            """
                You are an assistant for Unreal Engine.
                When answering factual questions about the scene or object structure, first use tool resources.
                Do NOT generate code snippets. Focus on clear answers. Do not explain unless necessary.
                Do NOT explain how you would do tasks, make use of tools if applicable.
                Do NOT hallucinate data.
            """
        ),
        reflect_on_tool_use=True
    )

    app.state.agent = agent
    yield


app = FastAPI(title="Unreal Agent", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev/testing, wildcard is fine. In prod restrict.
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────  endpoint  ────────────────────────────────
@app.post("/ask")
async def ask(prompt: str):
    start_time = time.perf_counter()

    agent = app.state.agent
    messages = await agent.run(task=prompt)

    end_time = time.perf_counter()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time:.4f} seconds")
    print(messages)
    return messages, execution_time


# ─────────────────────────  run  ─────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run(app, port=8008)
