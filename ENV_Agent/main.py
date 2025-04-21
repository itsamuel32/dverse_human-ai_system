# from autogen_ext.tools.mcp import SseServerParams, mcp_server_tools
# from autogen_ext.models.ollama import OllamaChatCompletionClient
# from autogen_agentchat.agents import AssistantAgent
#
#
# async def main() -> None:
#     # Setup server params for remote service
#     server_params = SseServerParams(url="http://localhost:8000/sse")
#
#     # Get all available tools
#     tools = await mcp_server_tools(server_params)
#
#     # Create an agent with all tools
#     agent = AssistantAgent(name="tool_user", model_client=OllamaChatCompletionClient(model="mistral"), tools=tools)
#
#     response = await agent.run(task="A+1235?")
#
#     print(response)
#
# if __name__ == '__main__':
#     asyncio.run(main())
# fastapi_autogen_mcp.py
import asyncio
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel

# AutoGen‑extra adapters
from autogen_ext.tools.mcp import mcp_server_tools
from autogen_ext.tools.mcp import SseServerParams
from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_agentchat.agents import AssistantAgent


# ─────────────────────────  lifespan  ────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    server_params = SseServerParams(url="http://localhost:8000/sse")

    tools = await mcp_server_tools(server_params)
    print(f"[startup] {len(tools)} tools loaded from MCP")

    model_client = OllamaChatCompletionClient(model="mistral")

    agent = AssistantAgent(
        name="UE_user",
        model_client=model_client,
        tools=tools,
        system_message=(
            "You are an assistant for Unreal Engine."),
        tool_call_summary_format="Tool '{tool_name}' returned: {result}",
        reflect_on_tool_use=True,
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
