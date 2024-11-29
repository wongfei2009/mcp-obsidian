# mcp-knowledge-base MCP server

Example MCP server to interact with Obsidian vaults.

## Components

### Tools

The server implements two tools:
- list_files_in_vault: Lists all files and directories in the root directory of your Obsidian vault
  - Takes no arguments
  - Returns a JSON list of files and directories
- list_files_in_dir: Lists all files and directories in a specific Obsidian directory
  - Takes "dirpath" as a string argument
  - Returns a JSON list of files and directories in the specified path

### Example prompts

- List all files in my vault
- List all files in the XYZ directory
- Get the contents of the last architecture call note

## Configuration

### Environment Variables

Create a `.env` file in the root directory with the following required variable:

```
OBSIDIAN_API_KEY=your_api_key_here
```

Without this API key, the server will not be able to function.

## Quickstart

### Install

#### Claude Desktop

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>Development/Unpublished Servers Configuration</summary>
  
```json
{
  "mcpServers": {
    "mcp-knowledge-base": {
      "command": "uv",
      "args": [
        "--directory",
        "<dir_to>/mcp-knowledge-base",
        "run",
        "mcp-knowledge-base"
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
    "mcp-knowledge-base": {
      "command": "uvx",
      "args": [
        "mcp-knowledge-base"
      ]
    }
  }
}
```
</details>

## Development

### Building and Publishing

To prepare the package for distribution:

1. Sync dependencies and update lockfile:
```bash
uv sync
```

2. Build package distributions:
```bash
uv build
```

This will create source and wheel distributions in the `dist/` directory.

3. Publish to PyPI:
```bash
uv publish
```

Note: You'll need to set PyPI credentials via environment variables or command flags:
- Token: `--token` or `UV_PUBLISH_TOKEN`
- Or username/password: `--username`/`UV_PUBLISH_USERNAME` and `--password`/`UV_PUBLISH_PASSWORD`

### Debugging

Since MCP servers run over stdio, debugging can be challenging. For the best debugging
experience, we strongly recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).

You can launch the MCP Inspector via [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) with this command:

```bash
npx @modelcontextprotocol/inspector uv --directory /path/to/mcp-knowledge-base run mcp-knowledge-base
```

Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.

You can also watch the server logs with this command:

```bash
tail -n 20 -f ~/Library/Logs/Claude/mcp-server-mcp-knowledge-base.log
```
