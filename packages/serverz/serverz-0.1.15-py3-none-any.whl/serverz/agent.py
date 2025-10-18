# work
from llama_index.core.agent.workflow import FunctionAgent, ReActAgent
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
from llama_index.llms.openrouter import OpenRouter
from llamahelper.factory import LLMFactory,LLMType



# llm = OpenRouter(
#     api_key="sk-tQ17YaQSAvb6REf474A112Eb57064c5d9f6a9599F96a35A6",
#     api_base="https://api.bianxieai.com/v1",
#     # max_tokens=256,
#     # context_window=4096,
#     model=  "gemini-2.5-flash-preview-05-20-nothinking",
# )


class Agent():
    def __init__(self):
        self.llm = LLMFactory(LLMType.BIANXIELLM,model_name="gemini-2.5-flash-preview-05-20-nothinking",
                              system_prompt = "You are a helpful assistant.")

        # Connect to MCP server
        mcp_client = BasicMCPClient("http://127.0.0.1:8108/math/mcp")
        mcp_tool_spec = McpToolSpec(client=mcp_client)
        self.tools = mcp_tool_spec
        self.agent = self.build_agent(system_prompt = system_prompt)

    def build_agent(self,system_prompt):
        agent = ReActAgent(
            tools = self.tools,
            llm=self.llm,
            system_prompt=system_prompt,
            verbose=True,
            )
        return agent
    
    async def product(self,prompt):
        response = await self.agent.run(prompt)
        return response
    


'''
# TODO 持续学习改进MCP
https://github.com/modelcontextprotocol/python-sdk
uvx 是什么
# mcp_client = BasicMCPClient("http://127.0.0.1:8000/mcp")
# mcp_client = BasicMCPClient("uvx",args = ["prompt_writing_assistant"]) # 暂不可用
# mcp_client = BasicMCPClient("uvx",args = ["mcp-server-time"]) # 可用

# 多种链接方式
# Server-Sent Events
sse_client = BasicMCPClient("https://example.com/sse")

# Streamable HTTP
http_client = BasicMCPClient("https://example.com/mcp")

# Local process
local_client = BasicMCPClient("python", args=["server.py"])


########

from llama_index.tools.mcp import BasicMCPClient, McpToolSpec

# Connect to MCP server
mcp_client = BasicMCPClient("http://127.0.0.1:8000/mcp")
mcp_tool_spec = McpToolSpec(client=mcp_client)

# Get tools
tools = await mcp_tool_spec.to_tool_list_async()

## 添加MCP

from fastmcp import FastMCP
from llama_index.tools.notion import NotionToolSpec

# Get tools from ToolSpec
tool_spec = NotionToolSpec(integration_token="your_token")
tools = tool_spec.to_tool_list()

# Create MCP server
mcp_server = FastMCP("Tool Server")

# Register tools
for tool in tools:
    mcp_server.tool(
        name=tool.metadata.name, description=tool.metadata.description
    )(tool.real_fn)


'''