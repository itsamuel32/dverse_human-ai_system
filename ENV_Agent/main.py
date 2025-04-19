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
from autogen_ext.tools.mcp import SseServerParams, mcp_server_tools
from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen.agentchat.conversable_agent import ConversableAgent


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
            "1. You are an Unreal‑Engine Assistant named Kordo."
            "2. Based on the human input, you are responsible for assisting him with tasks/questions about 3D environment."
            "3. If you call a tool, first explain which tool and why is called in 1 sentence."
            "4. If no tool is relevant, -> (8)."
            "5. Do not fabricate/hallucinate data. In such case -> (7). "
            "6.  If you do not now something, apologize in -> (8)."
            "7. Answer in direct, formal way starting the response '(your name) sees, and (your name) knows', Let me get all dem hoes.'"
            "8. Keep the conversation alive if its necessary. Maybe ask if they need anything else, or do anything else based on the previous input context"
        ),
    )

    app.state.agent = agent
    yield


app = FastAPI(title="AutoGen‑MCP Agent", lifespan=lifespan)


# ─────────────────────────  endpoint  ────────────────────────────────
@app.post("/ask")
async def ask(prompt: str):

    agent = app.state.agent
    messages = await agent.run(task=prompt)
    return messages


# ─────────────────────────  run  ─────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run(app, port=8080)
