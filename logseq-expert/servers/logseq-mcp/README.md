# Logseq MCP Server

Model Context Protocol (MCP) server for Logseq integration with Claude Code.

## Features

- **Read Operations**: Get pages, blocks, search, backlinks
- **Write Operations**: Create/update/delete pages and blocks, set properties
- **Query Operations**: Execute Datalog queries, find by property/tag, search tasks
- **Resources**: Access graph info, pages, and blocks as MCP resources

## Prerequisites

1. **Logseq** with HTTP API enabled (Settings > Features > HTTP APIs server)
2. **API Token** from Logseq (Settings > Features > Authorization tokens)
3. **Node.js** 18 or higher

## Installation

```bash
cd logseq-expert/servers/logseq-mcp
npm install
npm run build
```

## Configuration

Set environment variables:

```bash
export LOGSEQ_API_TOKEN="your-api-token"
export LOGSEQ_API_URL="http://127.0.0.1:12315"  # optional, this is default
```

## Usage

### As MCP Server

Add to your Claude Code MCP configuration:

```json
{
  "mcpServers": {
    "logseq": {
      "command": "node",
      "args": ["/path/to/logseq-mcp/build/index.js"],
      "env": {
        "LOGSEQ_API_TOKEN": "your-token"
      }
    }
  }
}
```

### Development Mode

```bash
# Run with ts-node for development
LOGSEQ_API_TOKEN=xxx npm run dev
```

## Available Tools

### Read Tools

| Tool | Description |
|------|-------------|
| `logseq_get_page` | Get page by title/UUID with blocks |
| `logseq_get_block` | Get block by UUID |
| `logseq_list_pages` | List all pages (filter by journal) |
| `logseq_search` | Full-text search |
| `logseq_get_backlinks` | Find pages linking to a page |
| `logseq_get_graph_info` | Get graph metadata |

### Write Tools

| Tool | Description |
|------|-------------|
| `logseq_create_page` | Create new page |
| `logseq_delete_page` | Delete page |
| `logseq_create_block` | Create block under parent |
| `logseq_update_block` | Update block content |
| `logseq_delete_block` | Delete block |
| `logseq_append_to_page` | Append to end of page |
| `logseq_set_property` | Set block property |
| `logseq_remove_property` | Remove block property |
| `logseq_sync_notes` | Sync notes with timestamp |

### Query Tools

| Tool | Description |
|------|-------------|
| `logseq_datalog_query` | Execute raw Datalog query |
| `logseq_find_by_property` | Find by property value |
| `logseq_find_by_tag` | Find blocks with tag |
| `logseq_find_tasks` | Find TODO/DOING/DONE items |
| `logseq_find_recent_blocks` | Find recently modified |
| `logseq_find_page_hierarchy` | Find namespace children |

## Resources

| URI | Description |
|-----|-------------|
| `logseq://graph` | Current graph info |
| `logseq://pages` | List of all pages |
| `logseq://today` | Today's journal |
| `logseq://page/{title}` | Specific page content |
| `logseq://block/{uuid}` | Specific block content |

## Examples

### Get a page

```json
{
  "tool": "logseq_get_page",
  "arguments": {
    "title": "My Notes",
    "includeBlocks": true
  }
}
```

### Create a page with content

```json
{
  "tool": "logseq_create_page",
  "arguments": {
    "title": "Meeting Notes",
    "properties": {
      "type": "Meeting",
      "date": "2024-01-15"
    },
    "content": "## Agenda\n\n- Item 1\n- Item 2"
  }
}
```

### Find all TODO items

```json
{
  "tool": "logseq_find_tasks",
  "arguments": {
    "status": "TODO",
    "limit": 20
  }
}
```

### Execute Datalog query

```json
{
  "tool": "logseq_datalog_query",
  "arguments": {
    "query": "[:find ?name :where [?p :block/name ?name] [?p :block/properties ?props] [(get ?props :type) ?t] [(= ?t \"Book\")]]"
  }
}
```

### Sync conversation notes

```json
{
  "tool": "logseq_sync_notes",
  "arguments": {
    "title": "Project Discussion",
    "notes": "Key decisions:\n- Approved design\n- Set deadline for Q2"
  }
}
```

## Troubleshooting

### Connection Failed

1. Ensure Logseq is running
2. Enable HTTP API in Logseq settings
3. Check the API URL (default port is 12315)
4. Verify your token is correct

### Permission Denied

Make sure your API token has the required permissions for the operations you're trying to perform.

### Query Errors

Datalog queries must be valid EDN format. Common issues:
- Missing brackets
- Incorrect variable binding
- Invalid attribute names

## License

MIT
