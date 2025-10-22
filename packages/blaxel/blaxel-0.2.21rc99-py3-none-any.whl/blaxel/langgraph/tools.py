from typing import Any

from langchain_core.tools import StructuredTool
from mcp.types import CallToolResult, EmbeddedResource, ImageContent, TextContent

from blaxel.core.tools import bl_tools as bl_tools_core
from blaxel.core.tools.types import Tool, ToolException

NonTextContent = ImageContent | EmbeddedResource

def get_langchain_tool(tool: Tool) -> StructuredTool:
    async def langchain_coroutine(
       **arguments: dict[str, Any],
    ) -> tuple[str | list[str], list[NonTextContent] | None]:
        result: CallToolResult = await tool.coroutine(**arguments)
        text_contents: list[TextContent] = []
        non_text_contents = []
        for content in result.content:
            if isinstance(content, TextContent):
                text_contents.append(content)
            else:
                non_text_contents.append(content)

        tool_content: str | list[str] = [content.text for content in text_contents]
        if len(text_contents) == 1:
            tool_content = tool_content[0]

        if result.isError:
            raise ToolException(tool_content)

        return tool_content, non_text_contents or None

    return StructuredTool(
        name=tool.name,
        description=tool.description,
        args_schema=tool.input_schema,
        coroutine=langchain_coroutine,
        sync_coroutine=tool.sync_coroutine,
    )


async def bl_tools(tools_names: list[str], **kwargs) -> list[StructuredTool]:
    tools = bl_tools_core(tools_names, **kwargs)
    await tools.initialize()
    return [get_langchain_tool(tool) for tool in tools.get_tools()]