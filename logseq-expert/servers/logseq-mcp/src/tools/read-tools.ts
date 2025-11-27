/**
 * MCP Read Tools for Logseq
 *
 * Tools for reading data from Logseq graphs.
 */

import type { Tool } from "@modelcontextprotocol/sdk/types.js";
import type { LogseqHttpClient, Page, Block } from "../client/logseq-http.js";

export const readTools: Tool[] = [
  {
    name: "logseq_get_page",
    description:
      "Get a page from Logseq by title or UUID. Returns page metadata and optionally its block tree.",
    inputSchema: {
      type: "object",
      properties: {
        title: {
          type: "string",
          description: "Page title or UUID",
        },
        includeBlocks: {
          type: "boolean",
          description: "Include the page's block tree (default: true)",
          default: true,
        },
      },
      required: ["title"],
    },
  },
  {
    name: "logseq_get_block",
    description: "Get a specific block by UUID with its content and properties.",
    inputSchema: {
      type: "object",
      properties: {
        uuid: {
          type: "string",
          description: "Block UUID",
        },
      },
      required: ["uuid"],
    },
  },
  {
    name: "logseq_list_pages",
    description:
      "List all pages in the Logseq graph. Can filter by journal status.",
    inputSchema: {
      type: "object",
      properties: {
        limit: {
          type: "number",
          description: "Maximum number of pages to return",
        },
        journalsOnly: {
          type: "boolean",
          description: "Only return journal pages",
          default: false,
        },
        excludeJournals: {
          type: "boolean",
          description: "Exclude journal pages",
          default: false,
        },
      },
    },
  },
  {
    name: "logseq_search",
    description:
      "Search for content across all pages and blocks in the Logseq graph.",
    inputSchema: {
      type: "object",
      properties: {
        query: {
          type: "string",
          description: "Search query text",
        },
        limit: {
          type: "number",
          description: "Maximum number of results (default: 50)",
          default: 50,
        },
      },
      required: ["query"],
    },
  },
  {
    name: "logseq_get_backlinks",
    description:
      "Get all pages and blocks that link to a specific page (backlinks/references).",
    inputSchema: {
      type: "object",
      properties: {
        title: {
          type: "string",
          description: "Page title to find backlinks for",
        },
      },
      required: ["title"],
    },
  },
  {
    name: "logseq_get_graph_info",
    description: "Get information about the current Logseq graph.",
    inputSchema: {
      type: "object",
      properties: {},
    },
  },
];

export async function handleReadTool(
  client: LogseqHttpClient,
  name: string,
  args: Record<string, unknown>
): Promise<unknown> {
  switch (name) {
    case "logseq_get_page": {
      const title = args.title as string;
      const includeBlocks = args.includeBlocks !== false;

      const page = await client.getPage(title);
      if (!page) {
        return { error: `Page not found: ${title}` };
      }

      const result: { page: Page; blocks?: Block[] } = { page };

      if (includeBlocks) {
        result.blocks = await client.getPageBlocksTree(page.name);
      }

      return result;
    }

    case "logseq_get_block": {
      const uuid = args.uuid as string;
      const block = await client.getBlock(uuid);

      if (!block) {
        return { error: `Block not found: ${uuid}` };
      }

      return { block };
    }

    case "logseq_list_pages": {
      const limit = args.limit as number | undefined;
      const journalsOnly = args.journalsOnly as boolean | undefined;
      const excludeJournals = args.excludeJournals as boolean | undefined;

      let pages = await client.getAllPages();

      if (journalsOnly) {
        pages = pages.filter((p) => p["journal?"]);
      } else if (excludeJournals) {
        pages = pages.filter((p) => !p["journal?"]);
      }

      if (limit && limit > 0) {
        pages = pages.slice(0, limit);
      }

      return {
        count: pages.length,
        pages: pages.map((p) => ({
          name: p.name,
          uuid: p.uuid,
          isJournal: p["journal?"] ?? false,
        })),
      };
    }

    case "logseq_search": {
      const query = args.query as string;
      const limit = (args.limit as number) ?? 50;

      const results = await client.search(query);
      const limited = results.slice(0, limit);

      return {
        query,
        count: limited.length,
        results: limited,
      };
    }

    case "logseq_get_backlinks": {
      const title = args.title as string;

      // Use Datalog query to find backlinks
      const query = `
        [:find (pull ?b [:block/uuid :block/content {:block/page [:block/name]}])
         :where
         [?p :block/name ?name]
         [(clojure.string/lower-case ?name) ?lower-name]
         [(= ?lower-name "${title.toLowerCase()}")]
         [?b :block/refs ?p]]
      `;

      const results = await client.datascriptQuery<[Block]>(query);

      return {
        page: title,
        count: results.length,
        backlinks: results.map(([block]) => ({
          uuid: block.uuid,
          content: block.content,
          page: block.page?.name ?? "unknown",
        })),
      };
    }

    case "logseq_get_graph_info": {
      const graph = await client.getCurrentGraph();
      const config = await client.getUserConfigs();

      return {
        graph,
        preferredFormat: config["preferred-format"],
        preferredWorkflow: config["preferred-workflow"],
      };
    }

    default:
      throw new Error(`Unknown read tool: ${name}`);
  }
}
