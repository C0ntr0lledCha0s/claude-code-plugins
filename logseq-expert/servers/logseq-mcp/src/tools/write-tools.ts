/**
 * MCP Write Tools for Logseq
 *
 * Tools for writing/modifying data in Logseq graphs.
 */

import type { Tool } from "@modelcontextprotocol/sdk/types.js";
import type { LogseqHttpClient } from "../client/logseq-http.js";

export const writeTools: Tool[] = [
  {
    name: "logseq_create_page",
    description:
      "Create a new page in Logseq with optional properties and initial content.",
    inputSchema: {
      type: "object",
      properties: {
        title: {
          type: "string",
          description: "Page title",
        },
        properties: {
          type: "object",
          description: "Page properties (e.g., {type: 'Project', status: 'Active'})",
          additionalProperties: true,
        },
        content: {
          type: "string",
          description: "Initial content for the first block",
        },
      },
      required: ["title"],
    },
  },
  {
    name: "logseq_delete_page",
    description: "Delete a page from Logseq. This action cannot be undone.",
    inputSchema: {
      type: "object",
      properties: {
        title: {
          type: "string",
          description: "Page title to delete",
        },
      },
      required: ["title"],
    },
  },
  {
    name: "logseq_create_block",
    description: "Create a new block under a parent page or block.",
    inputSchema: {
      type: "object",
      properties: {
        parent: {
          type: "string",
          description: "Parent page title or block UUID",
        },
        content: {
          type: "string",
          description: "Block content (supports markdown)",
        },
        properties: {
          type: "object",
          description: "Block properties",
          additionalProperties: true,
        },
        sibling: {
          type: "boolean",
          description: "Insert as sibling instead of child (default: false)",
          default: false,
        },
      },
      required: ["parent", "content"],
    },
  },
  {
    name: "logseq_update_block",
    description: "Update the content of an existing block.",
    inputSchema: {
      type: "object",
      properties: {
        uuid: {
          type: "string",
          description: "Block UUID to update",
        },
        content: {
          type: "string",
          description: "New block content",
        },
      },
      required: ["uuid", "content"],
    },
  },
  {
    name: "logseq_delete_block",
    description: "Delete a block and all its children. This action cannot be undone.",
    inputSchema: {
      type: "object",
      properties: {
        uuid: {
          type: "string",
          description: "Block UUID to delete",
        },
      },
      required: ["uuid"],
    },
  },
  {
    name: "logseq_append_to_page",
    description:
      "Append content to the end of a page. Creates the page if it doesn't exist.",
    inputSchema: {
      type: "object",
      properties: {
        title: {
          type: "string",
          description: "Page title",
        },
        content: {
          type: "string",
          description: "Content to append",
        },
      },
      required: ["title", "content"],
    },
  },
  {
    name: "logseq_set_property",
    description: "Set a property on a block or page.",
    inputSchema: {
      type: "object",
      properties: {
        uuid: {
          type: "string",
          description: "Block/page UUID",
        },
        key: {
          type: "string",
          description: "Property name",
        },
        value: {
          description: "Property value (string, number, boolean)",
        },
      },
      required: ["uuid", "key", "value"],
    },
  },
  {
    name: "logseq_remove_property",
    description: "Remove a property from a block or page.",
    inputSchema: {
      type: "object",
      properties: {
        uuid: {
          type: "string",
          description: "Block/page UUID",
        },
        key: {
          type: "string",
          description: "Property name to remove",
        },
      },
      required: ["uuid", "key"],
    },
  },
  {
    name: "logseq_sync_notes",
    description:
      "Sync conversation notes to a Logseq page with timestamp. Ideal for saving Claude conversation summaries.",
    inputSchema: {
      type: "object",
      properties: {
        title: {
          type: "string",
          description: "Note title (will be prefixed with 'Claude Notes/')",
        },
        notes: {
          type: "string",
          description: "Note content to sync",
        },
        pagePrefix: {
          type: "string",
          description: "Page prefix (default: 'Claude Notes')",
          default: "Claude Notes",
        },
      },
      required: ["title", "notes"],
    },
  },
];

export async function handleWriteTool(
  client: LogseqHttpClient,
  name: string,
  args: Record<string, unknown>
): Promise<unknown> {
  switch (name) {
    case "logseq_create_page": {
      const title = args.title as string;
      const properties = args.properties as Record<string, unknown> | undefined;
      const content = args.content as string | undefined;

      // Check if page exists
      const existing = await client.getPage(title);
      if (existing) {
        return { error: `Page already exists: ${title}`, page: existing };
      }

      const page = await client.createPage(title, properties, {
        createFirstBlock: true,
      });

      // Add initial content if provided
      if (content && page) {
        const blocks = await client.getPageBlocksTree(title);
        if (blocks.length > 0) {
          await client.updateBlock(blocks[0].uuid, content);
        }
      }

      return { success: true, page };
    }

    case "logseq_delete_page": {
      const title = args.title as string;

      const page = await client.getPage(title);
      if (!page) {
        return { error: `Page not found: ${title}` };
      }

      await client.deletePage(title);
      return { success: true, deleted: title };
    }

    case "logseq_create_block": {
      const parent = args.parent as string;
      const content = args.content as string;
      const properties = args.properties as Record<string, unknown> | undefined;
      const sibling = args.sibling as boolean | undefined;

      // Resolve parent - could be page title or block UUID
      let parentUuid = parent;

      // If not a UUID format, try as page title
      if (!/^[0-9a-f-]{36}$/i.test(parent)) {
        const page = await client.getPage(parent);
        if (!page) {
          return { error: `Parent not found: ${parent}` };
        }
        // Get first block of page to use as parent
        const blocks = await client.getPageBlocksTree(page.name);
        if (blocks.length > 0) {
          parentUuid = blocks[0].uuid;
        } else {
          parentUuid = page.uuid;
        }
      }

      const block = await client.insertBlock(parentUuid, content, {
        sibling: sibling ?? false,
        properties,
      });

      return { success: true, block };
    }

    case "logseq_update_block": {
      const uuid = args.uuid as string;
      const content = args.content as string;

      const block = await client.getBlock(uuid);
      if (!block) {
        return { error: `Block not found: ${uuid}` };
      }

      await client.updateBlock(uuid, content);
      const updated = await client.getBlock(uuid);

      return { success: true, block: updated };
    }

    case "logseq_delete_block": {
      const uuid = args.uuid as string;

      const block = await client.getBlock(uuid);
      if (!block) {
        return { error: `Block not found: ${uuid}` };
      }

      await client.removeBlock(uuid);
      return { success: true, deleted: uuid };
    }

    case "logseq_append_to_page": {
      const title = args.title as string;
      const content = args.content as string;

      // Get or create page
      let page = await client.getPage(title);
      if (!page) {
        page = await client.createPage(title, {}, { createFirstBlock: true });
      }

      // Get blocks and find the last one
      const blocks = await client.getPageBlocksTree(title);

      let block;
      if (blocks.length > 0) {
        // Insert after last block
        const lastBlock = blocks[blocks.length - 1];
        block = await client.insertBlock(lastBlock.uuid, content, {
          sibling: true,
        });
      } else {
        // Page is empty, insert first block
        block = await client.insertBlock(page!.uuid, content, {
          sibling: false,
        });
      }

      return { success: true, block };
    }

    case "logseq_set_property": {
      const uuid = args.uuid as string;
      const key = args.key as string;
      const value = args.value;

      await client.upsertBlockProperty(uuid, key, value);
      const props = await client.getBlockProperties(uuid);

      return { success: true, properties: props };
    }

    case "logseq_remove_property": {
      const uuid = args.uuid as string;
      const key = args.key as string;

      await client.removeBlockProperty(uuid, key);
      const props = await client.getBlockProperties(uuid);

      return { success: true, properties: props };
    }

    case "logseq_sync_notes": {
      const title = args.title as string;
      const notes = args.notes as string;
      const pagePrefix = (args.pagePrefix as string) ?? "Claude Notes";

      const pageTitle = `${pagePrefix}/${title}`;
      const timestamp = new Date().toISOString().replace("T", " ").slice(0, 16);

      const content = `## ${timestamp}\n\n${notes}\n\n---`;

      // Get or create page
      let page = await client.getPage(pageTitle);
      if (!page) {
        page = await client.createPage(pageTitle, {
          type: "Claude Notes",
          created: timestamp.split(" ")[0],
        });
      }

      // Append notes
      const blocks = await client.getPageBlocksTree(pageTitle);
      let block;

      if (blocks.length > 0) {
        const lastBlock = blocks[blocks.length - 1];
        block = await client.insertBlock(lastBlock.uuid, content, {
          sibling: true,
        });
      } else {
        block = await client.insertBlock(page!.uuid, content, {
          sibling: false,
        });
      }

      return { success: true, page: pageTitle, block };
    }

    default:
      throw new Error(`Unknown write tool: ${name}`);
  }
}
