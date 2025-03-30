# MCP server for Obsidian

MCP server to interact with Obsidian via the Local REST API community plugin.

<a href="https://glama.ai/mcp/servers/3wko1bhuek"><img width="380" height="200" src="https://glama.ai/mcp/servers/3wko1bhuek/badge" alt="server for Obsidian MCP server" /></a>

## Components

> **Note about naming convention**: All tools in this MCP server use the "obsidian_" prefix (e.g., "obsidian_get_file_contents" instead of just "get_file_contents"). This naming convention helps prevent conflicts when multiple MCP servers are used simultaneously in Claude for Desktop.

### Tools

The server implements multiple tools to interact with Obsidian. All tools use the "obsidian_" prefix to avoid naming conflicts with other MCP servers.

#### File Navigation & Content Access
- **obsidian_list_files_in_vault**: Lists all files and directories at the root level of your Obsidian vault.
- **obsidian_list_files_in_dir**: Lists all files and directories within a specific folder in your vault.
- **obsidian_get_file_contents**: Retrieves the complete content of a specific file from your vault.
- **obsidian_batch_get_file_contents**: Retrieves multiple files at once and returns them with section headers.

#### Search Capabilities
- **obsidian_simple_search**: Performs a basic text search across all files and returns matches with context.
- **obsidian_complex_search**: Executes advanced searches using JsonLogic queries for finding notes with specific tags, metadata, or file patterns.

#### Content Creation & Editing
- **obsidian_append_content**: Adds new content to the end of an existing note or creates a new note.
- **obsidian_patch_content**: Precisely modifies specific sections of a note based on headings, blocks, or frontmatter.

#### Periodic Notes Integration
- **obsidian_get_periodic_note**: Retrieves the current time period's note (today's daily note, this week's note, etc.).
- **obsidian_get_recent_periodic_notes**: Gets a list of your most recent daily/weekly/monthly notes.
- **obsidian_get_recent_changes**: Lists recently modified files in your vault, sorted by modification date.

### Example Prompts for Claude

To get the best results, start by letting Claude know you want to work with your Obsidian vault. Here are some effective prompt examples:

#### Information Retrieval
- "Please check my Obsidian vault and retrieve my latest meeting notes from this week. Summarize the key action items."
- "Search my Obsidian notes for any mentions of 'project roadmap' and tell me where it's discussed."
- "Find all my personal development notes that contain goal-setting frameworks and summarize the different approaches."

#### Content Creation
- "Review my recent daily notes from this week, extract any tasks or TODOs, and create a new weekly summary note called 'Weekly Summary.md'."
- "Please create a new project note in my Projects folder that outlines the key points from our discussion today."
- "Take the ideas from my 'Book Notes/Atomic Habits.md' file and create a practical implementation plan in a new note."

#### Analysis & Organization
- "Look at my recent meeting notes and extract all decisions made about the product launch timeline."
- "Check my research notes on machine learning and create a structured outline grouping similar concepts together."
- "Find all notes in my vault containing #project-alpha tag and create a status report based on recent updates."

## Configuration

### Obsidian REST API Key

There are two ways to configure the environment with the Obsidian REST API Key. 

1. Add to server config (preferred)

```json
{
  "mcp-obsidian": {
    "command": "uvx",
    "args": [
      "mcp-obsidian"
    ],
    "env": {
      "OBSIDIAN_API_KEY":"<your_api_key_here>"
    }
  }
```

2. Create a `.env` file in the working directory with the following required variable:

```
OBSIDIAN_API_KEY=your_api_key_here
```

Note: You can find the key in the Obsidian plugin config.

## Quickstart

### Install

#### Obsidian REST API

You need the Obsidian REST API community plugin running: https://github.com/coddingtonbear/obsidian-local-rest-api

Install and enable it in the settings and copy the api key.

#### Claude Desktop

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`

On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>Development/Unpublished Servers Configuration</summary>
  
```json
{
  "mcpServers": {
    "mcp-obsidian": {
      "command": "uv",
      "args": [
        "--directory",
        "<dir_to>/mcp-obsidian",
        "run",
        "mcp-obsidian"
      ]
    }
  }
}
```
</details>

<details>
  <summary>Published Servers Configuration</summary>
  
```json
{
  "mcpServers": {
    "mcp-obsidian": {
      "command": "uvx",
      "args": [
        "mcp-obsidian"
      ],
      "env": {
        "OBSIDIAN_API_KEY" : "<YOUR_OBSIDIAN_API_KEY>"
      }
    }
  }
}
```
</details>

## Development

### Building

To prepare the package for distribution:

1. Sync dependencies and update lockfile:
```bash
uv sync
```

### Debugging

Since MCP servers run over stdio, debugging can be challenging. For the best debugging
experience, we strongly recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).

You can launch the MCP Inspector via [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) with this command:

```bash
npx @modelcontextprotocol/inspector uv --directory /path/to/mcp-obsidian run mcp-obsidian
```

Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.

You can also watch the server logs with this command:

```bash
tail -n 20 -f ~/Library/Logs/Claude/mcp-server-mcp-obsidian.log
```
