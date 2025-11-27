/**
 * MCP Resources for Logseq Graphs
 *
 * Exposes Logseq graph data as MCP resources.
 */

import type { Resource, ResourceTemplate } from "@modelcontextprotocol/sdk/types.js";
import type { LogseqHttpClient } from "../client/logseq-http.js";

/**
 * Get static resource definitions
 */
export function getResourceTemplates(): ResourceTemplate[] {
  return [
    {
      uriTemplate: "logseq://page/{title}",
      name: "Logseq Page",
      description: "A page from the Logseq graph with its blocks",
      mimeType: "application/json",
    },
    {
      uriTemplate: "logseq://block/{uuid}",
      name: "Logseq Block",
      description: "A specific block from the Logseq graph",
      mimeType: "application/json",
    },
    {
      uriTemplate: "logseq://pages",
      name: "All Logseq Pages",
      description: "List of all pages in the Logseq graph",
      mimeType: "application/json",
    },
    {
      uriTemplate: "logseq://graph",
      name: "Graph Info",
      description: "Information about the current Logseq graph",
      mimeType: "application/json",
    },
    {
      uriTemplate: "logseq://today",
      name: "Today's Journal",
      description: "Today's journal page in Logseq",
      mimeType: "application/json",
    },
  ];
}

/**
 * List available resources
 */
export async function listResources(client: LogseqHttpClient): Promise<Resource[]> {
  const resources: Resource[] = [];

  try {
    // Add graph info resource
    const graph = await client.getCurrentGraph();
    if (graph) {
      resources.push({
        uri: "logseq://graph",
        name: `Graph: ${graph.name}`,
        description: `Current Logseq graph at ${graph.path}`,
        mimeType: "application/json",
      });
    }

    // Add today's journal
    const today = new Date().toISOString().split("T")[0];
    resources.push({
      uri: "logseq://today",
      name: "Today's Journal",
      description: `Journal page for ${today}`,
      mimeType: "application/json",
    });

    // Add all pages resource
    resources.push({
      uri: "logseq://pages",
      name: "All Pages",
      description: "Index of all pages in the graph",
      mimeType: "application/json",
    });

    // Add some recent/important pages
    const pages = await client.getAllPages();
    const nonJournalPages = pages
      .filter((p) => !p["journal?"])
      .slice(0, 20);

    for (const page of nonJournalPages) {
      resources.push({
        uri: `logseq://page/${encodeURIComponent(page.name)}`,
        name: page.name,
        description: `Page: ${page.name}`,
        mimeType: "application/json",
      });
    }
  } catch (error) {
    // If we can't connect, return empty list
    console.error("Failed to list resources:", error);
  }

  return resources;
}

/**
 * Read a resource by URI
 */
export async function readResource(
  client: LogseqHttpClient,
  uri: string
): Promise<{ contents: Array<{ uri: string; mimeType: string; text: string }> }> {
  const url = new URL(uri);
  const path = url.pathname.replace(/^\/+/, "");

  // Handle different resource types
  if (uri === "logseq://graph") {
    const graph = await client.getCurrentGraph();
    const config = await client.getUserConfigs();

    return {
      contents: [
        {
          uri,
          mimeType: "application/json",
          text: JSON.stringify({ graph, config }, null, 2),
        },
      ],
    };
  }

  if (uri === "logseq://pages") {
    const pages = await client.getAllPages();

    const pageList = pages.map((p) => ({
      name: p.name,
      uuid: p.uuid,
      isJournal: p["journal?"] ?? false,
    }));

    return {
      contents: [
        {
          uri,
          mimeType: "application/json",
          text: JSON.stringify(
            {
              count: pageList.length,
              pages: pageList,
            },
            null,
            2
          ),
        },
      ],
    };
  }

  if (uri === "logseq://today") {
    // Format today's date as Logseq journal title
    const today = new Date();
    const journalFormats = [
      // Try common journal date formats
      today.toISOString().split("T")[0], // 2024-01-15
      `${today.toLocaleString("en-US", { month: "short" })} ${today.getDate()}, ${today.getFullYear()}`, // Jan 15, 2024
      `${today.toLocaleString("en-US", { month: "long" })} ${today.getDate()}, ${today.getFullYear()}`, // January 15, 2024
    ];

    for (const format of journalFormats) {
      const page = await client.getPage(format);
      if (page) {
        const blocks = await client.getPageBlocksTree(page.name);
        return {
          contents: [
            {
              uri,
              mimeType: "application/json",
              text: JSON.stringify({ page, blocks }, null, 2),
            },
          ],
        };
      }
    }

    // No journal found, return empty
    return {
      contents: [
        {
          uri,
          mimeType: "application/json",
          text: JSON.stringify({ error: "Today's journal not found" }, null, 2),
        },
      ],
    };
  }

  if (uri.startsWith("logseq://page/")) {
    const title = decodeURIComponent(path.replace("page/", ""));
    const page = await client.getPage(title);

    if (!page) {
      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify({ error: `Page not found: ${title}` }, null, 2),
          },
        ],
      };
    }

    const blocks = await client.getPageBlocksTree(page.name);

    return {
      contents: [
        {
          uri,
          mimeType: "application/json",
          text: JSON.stringify({ page, blocks }, null, 2),
        },
      ],
    };
  }

  if (uri.startsWith("logseq://block/")) {
    const uuid = path.replace("block/", "");
    const block = await client.getBlock(uuid);

    if (!block) {
      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify({ error: `Block not found: ${uuid}` }, null, 2),
          },
        ],
      };
    }

    return {
      contents: [
        {
          uri,
          mimeType: "application/json",
          text: JSON.stringify({ block }, null, 2),
        },
      ],
    };
  }

  throw new Error(`Unknown resource URI: ${uri}`);
}
