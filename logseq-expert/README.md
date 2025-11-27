# Logseq Expert Plugin

Expert plugin for working with Logseq's database-based architecture with full CRUD capabilities. Provides Datascript schema knowledge, Datalog query building, HTTP API integration, MCP server, and comprehensive read/write operations for Logseq graphs.

## What's New in v2.0.0

- **HTTP API Integration**: Read and write data directly to running Logseq instance
- **MCP Server**: Model Context Protocol server for AI tool integration
- **CRUD Operations**: Create, read, update, and delete pages and blocks
- **Note Syncing**: Save conversation summaries to Logseq automatically
- **Auto-Detection**: Automatically detect and configure available backends

## Features

### Agent
- **logseq-db-expert**: Expert agent for Logseq DB architecture, queries, and API operations

### Skills (Auto-Invoke)

| Skill | Triggers On |
|-------|-------------|
| `understanding-db-schema` | Questions about Datascript, classes, properties, schema |
| `building-logseq-plugins` | Plugin development, Logseq API, DB-compatible plugins |
| `querying-logseq-data` | Datalog queries, query optimization, pull syntax |
| `migrating-to-db` | MD to DB migration, import/export, compatibility |
| `connecting-to-logseq` | Connection setup, HTTP API, authentication, troubleshooting |
| `reading-logseq-data` | Getting pages, blocks, searching, backlinks |
| `writing-to-logseq` | Creating pages, blocks, setting properties, syncing notes |

### Commands

#### Schema & Queries
| Command | Purpose |
|---------|---------|
| `/logseq-expert:query <description>` | Build Datalog queries from natural language |
| `/logseq-expert:define-property <name>` | Define typed properties with schema |
| `/logseq-expert:define-class <name>` | Define classes with inherited properties |
| `/logseq-expert:check-migration [path]` | Analyze MD graph for DB compatibility |
| `/logseq-expert:explain <concept>` | Explain DB schema concepts |

#### API Operations
| Command | Purpose |
|---------|---------|
| `/logseq-expert:init` | Initialize environment with setup wizard |
| `/logseq-expert:status` | Check connection status and configuration |
| `/logseq-expert:get-page <title>` | Retrieve a page with its blocks |
| `/logseq-expert:search <query>` | Search across all pages and blocks |
| `/logseq-expert:create-page <title>` | Create a new page |
| `/logseq-expert:add-block <page> <content>` | Add block to a page |
| `/logseq-expert:sync-notes <title>` | Sync conversation notes to Logseq |
| `/logseq-expert:get-tasks [status]` | Get TODO/DOING/DONE items |
| `/logseq-expert:today` | Get today's journal page |

### MCP Server

The plugin includes a TypeScript MCP server at `servers/logseq-mcp/` with:

| Category | Tools |
|----------|-------|
| **Read** | `logseq_get_page`, `logseq_get_block`, `logseq_list_pages`, `logseq_search`, `logseq_get_backlinks`, `logseq_get_graph_info` |
| **Write** | `logseq_create_page`, `logseq_delete_page`, `logseq_create_block`, `logseq_update_block`, `logseq_delete_block`, `logseq_append_to_page`, `logseq_set_property`, `logseq_remove_property`, `logseq_sync_notes` |
| **Query** | `logseq_datalog_query`, `logseq_find_by_property`, `logseq_find_by_tag`, `logseq_find_tasks`, `logseq_find_recent_blocks`, `logseq_find_page_hierarchy` |

## Installation

```bash
# Clone the plugins repository
git clone https://github.com/C0ntr0lledCha0s/claude-code-plugins.git

# Symlink to Claude Code plugins directory
ln -s $(pwd)/claude-code-plugins/logseq-expert ~/.claude/plugins/logseq-expert
```

## Configuration

### Quick Setup

Run the initialization wizard:
```bash
/logseq-expert:init
```

Or configure manually:

### 1. Enable Logseq HTTP API

In Logseq:
1. Go to **Settings** > **Features**
2. Enable **HTTP APIs server**
3. Create an **Authorization token**
4. Copy the token

### 2. Set Environment Variables

```bash
export LOGSEQ_API_TOKEN="your-token-here"
export LOGSEQ_API_URL="http://127.0.0.1:12315"  # optional, this is default
```

### 3. Create Configuration File (Optional)

Create `.claude/logseq-expert/env.json`:

```json
{
  "backend": "auto",
  "http": {
    "url": "http://127.0.0.1:12315",
    "token": "${LOGSEQ_API_TOKEN}"
  },
  "preferences": {
    "confirmWrites": false,
    "backupBeforeWrite": false
  }
}
```

### 4. Verify Connection

```bash
/logseq-expert:status
```

## Usage Examples

### Read Operations

```bash
# Get a specific page
/logseq-expert:get-page Meeting Notes

# Search across the graph
/logseq-expert:search project deadline

# Get today's journal
/logseq-expert:today

# Get all TODO items
/logseq-expert:get-tasks TODO
```

### Write Operations

```bash
# Create a new page
/logseq-expert:create-page Project Alpha

# Add content to a page
/logseq-expert:add-block "Project Alpha" "## Goals\n- Ship v1.0"

# Sync conversation notes
/logseq-expert:sync-notes "Code Review Discussion"
```

### Query Building

```bash
/logseq-expert:query find all books rated 5 stars by Stephen King
```

Output:
```clojure
[:find (pull ?b [:block/title :user.property/rating :user.property/author])
 :where
 [?b :block/tags ?t]
 [?t :block/title "Book"]
 [?b :user.property/rating 5]
 [?b :user.property/author "Stephen King"]]
```

### Define Schema

```bash
/logseq-expert:define-class Person
```

```bash
/logseq-expert:define-property rating
```

## MCP Server Setup

To use the MCP server with Claude Code:

```bash
cd logseq-expert/servers/logseq-mcp
npm install
npm run build
```

Add to your MCP configuration:

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

## Logseq DB Schema Overview

### Core Concepts

| Concept | Description |
|---------|-------------|
| **Nodes** | Unified term for pages and blocks |
| **Classes** | Tags with inherited properties (supertags) |
| **Properties** | Typed key-value metadata |
| **Datascript** | Clojure in-memory database engine |

### Property Types

| Type | Use Case | Example |
|------|----------|---------|
| `:default` | Text content | "Hello world" |
| `:number` | Numeric values | 42, 3.14 |
| `:date` | Calendar dates | Journal links |
| `:datetime` | Date + time | Scheduling |
| `:checkbox` | Boolean | true/false |
| `:url` | Web links | https://... |
| `:node` | References | [[Page]] |
| `:class` | Class refs | #Book |

### Built-in Classes

```
:logseq.class/Root
├── :logseq.class/Page
├── :logseq.class/Tag
├── :logseq.class/Property
├── :logseq.class/Task
├── :logseq.class/Query
├── :logseq.class/Asset
└── :logseq.class/Journal
```

## API Reference

### HTTP API Operations

| Operation | Description |
|-----------|-------------|
| `create_page(title, content, properties)` | Create new page |
| `get_page(title)` | Get page with blocks |
| `delete_page(title)` | Delete page |
| `create_block(parent, content)` | Add block |
| `update_block(uuid, content)` | Modify block |
| `delete_block(uuid)` | Remove block |
| `append_to_page(title, content)` | Add to end of page |
| `set_property(uuid, key, value)` | Set property |
| `search(query)` | Full-text search |
| `datalog_query(query)` | Execute Datalog |
| `sync_notes(title, notes)` | Sync with timestamp |

### Python Client

```python
from logseq_client import LogseqClient

client = LogseqClient()

# Read operations
page = client.get_page("My Notes")
results = client.search("meeting")
tasks = client.datalog_query('[:find ?content :where [?b :block/marker "TODO"] [?b :block/content ?content]]')

# Write operations
from write_operations import LogseqWriter

writer = LogseqWriter()
writer.create_page("New Page", properties={"type": "Note"})
writer.append_to_page("Daily Log", "- New entry")
writer.sync_notes("Discussion", "Key points from our conversation...")
```

## DB vs MD Comparison

| Feature | MD Version | DB Version |
|---------|------------|------------|
| Storage | Markdown files | SQLite |
| Tags | Page references | Classes with properties |
| Properties | Text strings | Typed values |
| Queries | Limited | Full Datalog |
| Sync | File-based | Real-time (Pro) |
| API | Limited | Full HTTP API |

## Troubleshooting

### Connection Issues

1. **Logseq not running**: Start Logseq desktop app
2. **HTTP API disabled**: Settings > Features > Enable HTTP APIs server
3. **Invalid token**: Regenerate token in Settings > Features > Authorization tokens
4. **Port blocked**: Check if port 12315 is available

### Check status:
```bash
/logseq-expert:status
```

### Test connection directly:
```bash
python3 logseq-expert/scripts/test-connection.py --verbose
```

## Current Status

Logseq DB is in alpha (as of early 2025)

- Some features still in development (whiteboards)
- Plugin compatibility varies
- Multi-device sync requires subscription
- Export options limited

## Resources

- [Logseq DB Documentation](https://github.com/logseq/docs/blob/master/db-version.md)
- [Database Schema DeepWiki](https://deepwiki.com/logseq/logseq/4.2-views-and-tables)
- [Logseq Plugin SDK](https://plugins-doc.logseq.com/)
- [Logseq DB Unofficial FAQ](https://discuss.logseq.com/t/logseq-db-unofficial-faq/32508)

## Contributing

Found an issue or want to improve the Logseq expertise? Contributions welcome!

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT
