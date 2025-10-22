from livekit.agents import function_tool, llm

from blaxel.core.tools import bl_tools as bl_tools_core
from blaxel.core.tools.types import Tool


def livekit_coroutine(tool: Tool):
    async def livekit_coroutine_wrapper(raw_arguments: dict[str, object]):
        result = await tool.coroutine(**raw_arguments)
        return result.model_dump_json()

    return livekit_coroutine_wrapper


def get_livekit_tools(tools: list[Tool]) -> list[llm.FunctionTool]:
    livekit_tools = []
    for tool in tools:
        livekit_tools.append(
            function_tool(
                livekit_coroutine(tool),
                raw_schema={
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.input_schema,
                },
            )
        )
    return livekit_tools


async def bl_tools(tools_names: list[str], **kwargs) -> list[llm.FunctionTool]:
    tools = bl_tools_core(tools_names, **kwargs)
    await tools.initialize()
    return get_livekit_tools(tools.get_tools())
