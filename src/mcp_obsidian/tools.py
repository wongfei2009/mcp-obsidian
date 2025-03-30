from collections.abc import Sequence
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
import json
import os
from . import obsidian

api_key = os.getenv("OBSIDIAN_API_KEY", "")
if api_key == "":
    raise ValueError(f"OBSIDIAN_API_KEY environment variable required. Working directory: {os.getcwd()}")

TOOL_LIST_FILES_IN_VAULT = "obsidian_list_files_in_vault"
TOOL_LIST_FILES_IN_DIR = "obsidian_list_files_in_dir"
TOOL_GET_FILE_CONTENTS = "obsidian_get_file_contents"
TOOL_SIMPLE_SEARCH = "obsidian_simple_search"
TOOL_APPEND_CONTENT = "obsidian_append_content"
TOOL_PATCH_CONTENT = "obsidian_patch_content"
TOOL_COMPLEX_SEARCH = "obsidian_complex_search"
TOOL_BATCH_GET_FILE_CONTENTS = "obsidian_batch_get_file_contents"
TOOL_GET_PERIODIC_NOTE = "obsidian_get_periodic_note"
TOOL_GET_RECENT_PERIODIC_NOTES = "obsidian_get_recent_periodic_notes"
TOOL_GET_RECENT_CHANGES = "obsidian_get_recent_changes"

class ToolHandler():
    def __init__(self, tool_name: str):
        self.name = tool_name

    def get_tool_description(self) -> Tool:
        raise NotImplementedError()

    def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        raise NotImplementedError()
    
class ListFilesInVaultToolHandler(ToolHandler):
    def __init__(self):
        super().__init__(TOOL_LIST_FILES_IN_VAULT)

    def get_tool_description(self):
        return Tool(
            name=self.name,
            description="Lists all files and directories at the root level of your Obsidian vault. This provides an overview of your vault's top-level organization without requiring any parameters.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        )

    def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:

        api = obsidian.Obsidian(api_key=api_key)

        files = api.list_files_in_vault()

        return [
            TextContent(
                type="text",
                text=json.dumps(files, indent=2)
            )
        ]
    
class ListFilesInDirToolHandler(ToolHandler):
    def __init__(self):
        super().__init__(TOOL_LIST_FILES_IN_DIR)

    def get_tool_description(self):
        return Tool(
            name=self.name,
            description="Lists all files and directories within a specific folder in your Obsidian vault. Use this when you need to explore the contents of a particular directory rather than the root level.",
            inputSchema={
                "type": "object",
                "properties": {
                    "dirpath": {
                        "type": "string",
                        "description": "Path to the directory you want to explore (relative to your vault root, e.g., 'Projects' or 'Daily Notes'). Note that empty directories will not be returned."
                    },
                },
                "required": ["dirpath"]
            }
        )

    def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:

        if "dirpath" not in args:
            raise RuntimeError("dirpath argument missing in arguments")

        api = obsidian.Obsidian(api_key=api_key)

        files = api.list_files_in_dir(args["dirpath"])

        return [
            TextContent(
                type="text",
                text=json.dumps(files, indent=2)
            )
        ]
    
class GetFileContentsToolHandler(ToolHandler):
    def __init__(self):
        super().__init__(TOOL_GET_FILE_CONTENTS)

    def get_tool_description(self):
        return Tool(
            name=self.name,
            description="Retrieves the complete content of a specific file from your Obsidian vault. Use this tool when you need to access or analyze the full text of a note.",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the file you want to read (relative to your vault root, e.g., 'Projects/project-ideas.md' or 'Meeting Notes/2023-05-15.md').",
                        "format": "path"
                    },
                },
                "required": ["filepath"]
            }
        )

    def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        if "filepath" not in args:
            raise RuntimeError("filepath argument missing in arguments")

        api = obsidian.Obsidian(api_key=api_key)

        content = api.get_file_contents(args["filepath"])

        return [
            TextContent(
                type="text",
                text=json.dumps(content, indent=2)
            )
        ]
    
class SearchToolHandler(ToolHandler):
    def __init__(self):
        super().__init__(TOOL_SIMPLE_SEARCH)

    def get_tool_description(self):
        return Tool(
            name=self.name,
            description="""Performs a text-based search across all files in your Obsidian vault and returns matches with surrounding context.
            Use this tool when you need to find specific information, keywords, or phrases anywhere in your notes without complex search criteria.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The text to search for in your vault (e.g., 'project ideas', 'meeting with John', or 'productivity techniques')."
                    },
                    "context_length": {
                        "type": "integer",
                        "description": "How many characters of surrounding text to include around each match to provide context (default: 100).",
                        "default": 100
                    }
                },
                "required": ["query"]
            }
        )

    def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        if "query" not in args:
            raise RuntimeError("query argument missing in arguments")

        context_length = args.get("context_length", 100)
        
        api = obsidian.Obsidian(api_key=api_key)
        results = api.search(args["query"], context_length)
        
        formatted_results = []
        for result in results:
            formatted_matches = []
            for match in result.get('matches', []):
                context = match.get('context', '')
                match_pos = match.get('match', {})
                start = match_pos.get('start', 0)
                end = match_pos.get('end', 0)
                
                formatted_matches.append({
                    'context': context,
                    'match_position': {'start': start, 'end': end}
                })
                
            formatted_results.append({
                'filename': result.get('filename', ''),
                'score': result.get('score', 0),
                'matches': formatted_matches
            })

        return [
            TextContent(
                type="text",
                text=json.dumps(formatted_results, indent=2)
            )
        ]
    
class AppendContentToolHandler(ToolHandler):
   def __init__(self):
       super().__init__(TOOL_APPEND_CONTENT)

   def get_tool_description(self):
       return Tool(
           name=self.name,
           description="Adds new content to the end of an existing note, or creates a new note if the file doesn't exist yet. This is useful for adding information to notes without modifying existing content.",
           inputSchema={
               "type": "object",
               "properties": {
                   "filepath": {
                       "type": "string",
                       "description": "Path to the file you want to append to (relative to vault root, e.g., 'Daily Notes/today.md' or 'Projects/ideas.md')",
                       "format": "path"
                   },
                   "content": {
                       "type": "string",
                       "description": "The text content you want to add to the end of the file (can include markdown formatting)"
                   }
               },
               "required": ["filepath", "content"]
           }
       )

   def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
       if "filepath" not in args or "content" not in args:
           raise RuntimeError("filepath and content arguments required")

       api = obsidian.Obsidian(api_key=api_key)
       api.append_content(args.get("filepath", ""), args["content"])

       return [
           TextContent(
               type="text",
               text=f"Successfully appended content to {args['filepath']}"
           )
       ]
   
class PatchContentToolHandler(ToolHandler):
   def __init__(self):
       super().__init__(TOOL_PATCH_CONTENT)

   def get_tool_description(self):
       return Tool(
           name=self.name,
           description="Precisely modifies a specific section of an existing note by inserting, adding to, or replacing content relative to a heading, block reference, or frontmatter field. Use this for targeted edits to specific parts of a note rather than appending to the end.",
           inputSchema={
               "type": "object",
               "properties": {
                   "filepath": {
                       "type": "string",
                       "description": "Path to the file you want to modify (relative to vault root, e.g., 'Projects/project-plan.md')",
                       "format": "path"
                   },
                   "operation": {
                       "type": "string",
                       "description": "The type of modification to perform: 'append' (add after target), 'prepend' (add before target), or 'replace' (replace target with new content)",
                       "enum": ["append", "prepend", "replace"]
                   },
                   "target_type": {
                       "type": "string",
                       "description": "What type of element you're targeting: 'heading' (a section heading), 'block' (a block reference), or 'frontmatter' (YAML metadata field)",
                       "enum": ["heading", "block", "frontmatter"]
                   },
                   "target": {
                       "type": "string", 
                       "description": "The specific target identifier: for headings use the heading text (e.g., '## Project Goals'), for blocks use the block ID, for frontmatter use the field name"
                   },
                   "content": {
                       "type": "string",
                       "description": "The new content to insert (can include markdown formatting)"
                   }
               },
               "required": ["filepath", "operation", "target_type", "target", "content"]
           }
       )

   def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
       required = ["filepath", "operation", "target_type", "target", "content"]
       if not all(key in args for key in required):
           raise RuntimeError(f"Missing required arguments: {', '.join(required)}")

       api = obsidian.Obsidian(api_key=api_key)
       api.patch_content(
           args.get("filepath", ""),
           args.get("operation", ""),
           args.get("target_type", ""),
           args.get("target", ""),
           args.get("content", "")
       )

       return [
           TextContent(
               type="text",
               text=f"Successfully patched content in {args['filepath']}"
           )
       ]
   
class ComplexSearchToolHandler(ToolHandler):
   def __init__(self):
       super().__init__(TOOL_COMPLEX_SEARCH)

   def get_tool_description(self):
       return Tool(
           name=self.name,
           description="""Advanced search functionality using structured JsonLogic queries to find notes that match specific criteria.
           
           Use this tool when you need to perform more sophisticated searches than simple text matching, such as finding:
           - Notes with specific tags or YAML frontmatter values
           - Files matching specific patterns or in specific locations
           - Content that matches regular expressions
           - Combinations of criteria using AND/OR logic
           
           This is more powerful but complex than the simple search tool.
           """,
           inputSchema={
               "type": "object",
               "properties": {
                   "query": {
                       "type": "object",
                       "description": "JsonLogic query object specifying search criteria. Examples: \n- Find all markdown files: {\"glob\": [\"*.md\", {\"var\": \"path\"}]}\n- Find files with specific tag: {\"in\": [\"productivity\", {\"var\": \"tags\"}]}\n- Find files modified recently: {\">\": [{\"var\": \"mtime\"}, 1672531200000]}"
                   }
               },
               "required": ["query"]
           }
       )

   def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
       if "query" not in args:
           raise RuntimeError("query argument missing in arguments")

       api = obsidian.Obsidian(api_key=api_key)
       results = api.search_json(args.get("query", ""))

       return [
           TextContent(
               type="text",
               text=json.dumps(results, indent=2)
           )
       ]

class BatchGetFileContentsToolHandler(ToolHandler):
    def __init__(self):
        super().__init__(TOOL_BATCH_GET_FILE_CONTENTS)

    def get_tool_description(self):
        return Tool(
            name=self.name,
            description="Retrieves the contents of multiple files at once from your Obsidian vault and returns them together with clear section headers. Use this when you need to analyze or compare information across several notes simultaneously.",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepaths": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "description": "Path to a file (relative to your vault root, e.g., 'Meeting Notes/2023-05-15.md')",
                            "format": "path"
                        },
                        "description": "List of file paths you want to retrieve (e.g., ['Projects/project1.md', 'Projects/project2.md'])"
                    },
                },
                "required": ["filepaths"]
            }
        )

    def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        if "filepaths" not in args:
            raise RuntimeError("filepaths argument missing in arguments")

        api = obsidian.Obsidian(api_key=api_key)
        content = api.get_batch_file_contents(args["filepaths"])

        return [
            TextContent(
                type="text",
                text=content
            )
        ]

class PeriodicNotesToolHandler(ToolHandler):
    def __init__(self):
        super().__init__(TOOL_GET_PERIODIC_NOTE)

    def get_tool_description(self):
        return Tool(
            name=self.name,
            description="Retrieves the current time period's note from your Periodic Notes in Obsidian. For example, get today's daily note, this week's weekly note, or this month's monthly note. This is useful for accessing your current time-based notes.",
            inputSchema={
                "type": "object",
                "properties": {
                    "period": {
                        "type": "string",
                        "description": "The type of periodic note you want to retrieve (daily = today's note, weekly = this week's note, etc.)",
                        "enum": ["daily", "weekly", "monthly", "quarterly", "yearly"]
                    }
                },
                "required": ["period"]
            }
        )

    def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        if "period" not in args:
            raise RuntimeError("period argument missing in arguments")

        period = args["period"]
        valid_periods = ["daily", "weekly", "monthly", "quarterly", "yearly"]
        if period not in valid_periods:
            raise RuntimeError(f"Invalid period: {period}. Must be one of: {', '.join(valid_periods)}")

        api = obsidian.Obsidian(api_key=api_key)
        content = api.get_periodic_note(period)

        return [
            TextContent(
                type="text",
                text=content
            )
        ]
        
class RecentPeriodicNotesToolHandler(ToolHandler):
    def __init__(self):
        super().__init__(TOOL_GET_RECENT_PERIODIC_NOTES)

    def get_tool_description(self):
        return Tool(
            name=self.name,
            description="Retrieves a list of your most recent periodic notes of a specified type (e.g., the last several daily notes or weekly notes). Use this to review what you've been working on or thinking about over the past days, weeks, or months.",
            inputSchema={
                "type": "object",
                "properties": {
                    "period": {
                        "type": "string",
                        "description": "The type of periodic notes you want to retrieve (e.g., daily notes, weekly notes, etc.)",
                        "enum": ["daily", "weekly", "monthly", "quarterly", "yearly"]
                    },
                    "limit": {
                        "type": "integer",
                        "description": "How many recent notes to return (default: 5, maximum: 50)",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 50
                    },
                    "include_content": {
                        "type": "boolean",
                        "description": "Whether to include the full text of each note (true) or just metadata (false, default)",
                        "default": False
                    }
                },
                "required": ["period"]
            }
        )

    def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        if "period" not in args:
            raise RuntimeError("period argument missing in arguments")

        period = args["period"]
        valid_periods = ["daily", "weekly", "monthly", "quarterly", "yearly"]
        if period not in valid_periods:
            raise RuntimeError(f"Invalid period: {period}. Must be one of: {', '.join(valid_periods)}")

        limit = args.get("limit", 5)
        if not isinstance(limit, int) or limit < 1:
            raise RuntimeError(f"Invalid limit: {limit}. Must be a positive integer")
            
        include_content = args.get("include_content", False)
        if not isinstance(include_content, bool):
            raise RuntimeError(f"Invalid include_content: {include_content}. Must be a boolean")

        api = obsidian.Obsidian(api_key=api_key)
        results = api.get_recent_periodic_notes(period, limit, include_content)

        return [
            TextContent(
                type="text",
                text=json.dumps(results, indent=2)
            )
        ]
        
class RecentChangesToolHandler(ToolHandler):
    def __init__(self):
        super().__init__(TOOL_GET_RECENT_CHANGES)

    def get_tool_description(self):
        return Tool(
            name=self.name,
            description="Retrieves a list of files that have been recently modified in your Obsidian vault, sorted by modification date. This is useful for seeing what you've been working on lately or finding notes you recently updated.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of recently modified files to return (default: 10, maximum: 100)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 100
                    },
                    "days": {
                        "type": "integer",
                        "description": "Only include files modified within this many days in the past (default: 90 days)",
                        "minimum": 1,
                        "default": 90
                    }
                }
            }
        )

    def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        limit = args.get("limit", 10)
        if not isinstance(limit, int) or limit < 1:
            raise RuntimeError(f"Invalid limit: {limit}. Must be a positive integer")
            
        days = args.get("days", 90)
        if not isinstance(days, int) or days < 1:
            raise RuntimeError(f"Invalid days: {days}. Must be a positive integer")

        api = obsidian.Obsidian(api_key=api_key)
        results = api.get_recent_changes(limit, days)

        return [
            TextContent(
                type="text",
                text=json.dumps(results, indent=2)
            )
        ]
