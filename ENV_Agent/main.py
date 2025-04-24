import uvicorn
from contextlib import asynccontextmanager

from fastapi import FastAPI

# AutoGen‑extra adapters
from autogen_ext.tools.mcp import mcp_server_tools
from autogen_ext.tools.mcp import SseServerParams
from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ModelInfo, ModelFamily


# ─────────────────────────  lifespan  ────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    server_params = SseServerParams(url="http://localhost:8000/sse")

    tools = await mcp_server_tools(server_params)
    print(f"[startup] {len(tools)} tools loaded from MCP")

    model_client = OllamaChatCompletionClient(model="mistral",
                                              model_info=ModelInfo(function_calling=True,
                                                                   json_output=False,
                                                                   vision=False,
                                                                   structured_output=True,
                                                                   family=ModelFamily.UNKNOWN
                                                                   )
                                              )

    agent = AssistantAgent(
        name="ENV_Agent",
        model_client=model_client,
        tools=tools,
        system_message=(
            "You are an assistant for Unreal Engine.\n"
            "Do NOT generate code snippets.\n"
            "Use appropriate the tools. Do not explain.\n"),
        reflect_on_tool_use=True
    )

    app.state.agent = agent
    yield


app = FastAPI(title="Unreal Agent", lifespan=lifespan)


# ─────────────────────────  endpoint  ────────────────────────────────
@app.post("/ask")
async def ask(prompt: str):
    agent = app.state.agent
    messages = await agent.run(task=prompt)

    return messages


# ─────────────────────────  run  ─────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run(app, port=8080)
