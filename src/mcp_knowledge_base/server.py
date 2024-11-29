
import json
import logging
from collections.abc import Sequence
from functools import lru_cache
from typing import Any

import subprocess
from dotenv import load_dotenv
from mcp.server import Server
import asyncio
from mcp.types import (

    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
from pydantic import AnyUrl

# Load environment variables
load_dotenv()

api_key = "x"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-knowledge-base")

app = Server("mcp-knowledge-base")

TOOL_LIST_FILES_IN_VAULT = "list_files_in_vault"
TOOL_LIST_FILES_IN_DIR = "list_files_in_dir"

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="list_files_in_vault",
            description="Lists all files and directories in the root directory of your Obsidian vault.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
        Tool(
            name="list_files_in_dir",
            description="Lists all files and directories that exist in a specific Obsidian directory.",
            inputSchema={
                "type": "object",
                "properties": {
                    "dirpath": {
                        "type": "string",
                        "description": "Path to list files from (relative to your vault root). Note that empty directories will not be returned."
                    },
                },
                "required": ["dirpath"]
            }
        )
    ]

class ToolHandler():
    def __init__(self, tool_name: str):
        self.name = tool_name

    def run_tool(self, args: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        pass

class ListFilesInVaultToolHandler(ToolHandler):
    def __init__(self):
        super().__init__(TOOL_LIST_FILES_IN_VAULT)

    def run_tool(self, args: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:

        files = [
            "a.txt",
            "b.txt",
            "c/"
        ]

        return [
            TextContent(
                type="text",
                text=json.dumps(files, indent=2)
            )
        ]
    
class ListFilesInDirToolHandler(ToolHandler):
    def __init__(self):
        super().__init__(TOOL_LIST_FILES_IN_DIR)

    def run_tool(self, args: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:

        files = [
            "a.txt",
            "b.txt",
            "c/"
        ]

        return [
            TextContent(
                type="text",
                text=json.dumps(files, indent=2)
            )
        ]
    
tool_handlers = {}
def add_tool_handler(tool_class: ToolHandler):
    global tool_handlers

    tool_handlers[tool_class.name] = tool_class

def get_tool_handler(name: str) -> ToolHandler | None:
    if name not in tool_handlers:
        return None
    
    return tool_handlers[name]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls for command line run."""
    
    add_tool_handler(ListFilesInDirToolHandler())
    add_tool_handler(ListFilesInVaultToolHandler())


    tool_handler = get_tool_handler(name)
    if not tool_handler:
        raise ValueError(f"Unknown tool: {name}")

    try:
        return tool_handler.run_tool(arguments)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise RuntimeError(f"Error: {str(e)}")


async def main():

    # Import here to avoid issues with event loops
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )



