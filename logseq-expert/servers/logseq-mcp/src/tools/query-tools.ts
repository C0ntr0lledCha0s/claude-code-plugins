/**
 * MCP Query Tools for Logseq
 *
 * Tools for executing Datalog queries against Logseq graphs.
 */

import type { Tool } from "@modelcontextprotocol/sdk/types.js";
import type { LogseqHttpClient } from "../client/logseq-http.js";

export const queryTools: Tool[] = [
  {
    name: "logseq_datalog_query",
    description: `Execute a Datalog query against the Logseq database.
Use this for complex queries that can't be done with other tools.
Returns raw query results as arrays.

Common patterns:
- Find pages with property: [:find ?name :where [?p :block/name ?name] [?p :block/properties ?props] [(get ?props :type) ?type] [(= ?type "Book")]]
- Find blocks with tag: [:find ?content :where [?b :block/content ?content] [?b :block/refs ?r] [?r :block/name "mytag"]]
- Find TODO items: [:find ?content :where [?b :block/content ?content] [?b :block/marker ?m] [(contains? #{"TODO" "DOING"} ?m)]]`,
    inputSchema: {
      type: "object",
      properties: {
        query: {
          type: "string",
          description: "Datalog query in EDN format",
        },
      },
      required: ["query"],
    },
  },
  {
    name: "logseq_find_by_property",
    description:
      "Find all pages/blocks that have a specific property value. Simpler than raw Datalog queries.",
    inputSchema: {
      type: "object",
      properties: {
        property: {
          type: "string",
          description: "Property name to search for",
        },
        value: {
          description: "Property value to match (optional - if not provided, finds all with that property)",
        },
      },
      required: ["property"],
    },
  },
  {
    name: "logseq_find_by_tag",
    description: "Find all blocks that reference a specific tag/page.",
    inputSchema: {
      type: "object",
      properties: {
        tag: {
          type: "string",
          description: "Tag name (without #)",
        },
        limit: {
          type: "number",
          description: "Maximum results to return (default: 100)",
          default: 100,
        },
      },
      required: ["tag"],
    },
  },
  {
    name: "logseq_find_tasks",
    description: "Find tasks/todos with optional status filter.",
    inputSchema: {
      type: "object",
      properties: {
        status: {
          type: "string",
          description: "Task status filter: TODO, DOING, DONE, NOW, LATER, WAITING, CANCELLED",
          enum: ["TODO", "DOING", "DONE", "NOW", "LATER", "WAITING", "CANCELLED"],
        },
        includeContent: {
          type: "boolean",
          description: "Include full block content (default: true)",
          default: true,
        },
        limit: {
          type: "number",
          description: "Maximum results (default: 100)",
          default: 100,
        },
      },
    },
  },
  {
    name: "logseq_find_recent_blocks",
    description: "Find recently modified blocks across all pages.",
    inputSchema: {
      type: "object",
      properties: {
        days: {
          type: "number",
          description: "Number of days to look back (default: 7)",
          default: 7,
        },
        limit: {
          type: "number",
          description: "Maximum results (default: 50)",
          default: 50,
        },
      },
    },
  },
  {
    name: "logseq_find_page_hierarchy",
    description:
      "Find all pages under a namespace (e.g., 'Project' finds 'Project/Alpha', 'Project/Beta').",
    inputSchema: {
      type: "object",
      properties: {
        namespace: {
          type: "string",
          description: "Parent namespace to search under",
        },
      },
      required: ["namespace"],
    },
  },
];

export async function handleQueryTool(
  client: LogseqHttpClient,
  name: string,
  args: Record<string, unknown>
): Promise<unknown> {
  switch (name) {
    case "logseq_datalog_query": {
      const query = args.query as string;

      try {
        const results = await client.datascriptQuery(query);
        return {
          query,
          count: Array.isArray(results) ? results.length : 0,
          results,
        };
      } catch (error) {
        return {
          error: `Query failed: ${error instanceof Error ? error.message : String(error)}`,
          query,
        };
      }
    }

    case "logseq_find_by_property": {
      const property = args.property as string;
      const value = args.value;

      let query: string;
      if (value !== undefined) {
        // Find with specific value
        const valueStr = typeof value === "string" ? `"${value}"` : String(value);
        query = `
          [:find (pull ?b [:block/uuid :block/content :block/properties {:block/page [:block/name]}])
           :where
           [?b :block/properties ?props]
           [(get ?props :${property}) ?v]
           [(= ?v ${valueStr})]]
        `;
      } else {
        // Find all with property
        query = `
          [:find (pull ?b [:block/uuid :block/content :block/properties {:block/page [:block/name]}])
           :where
           [?b :block/properties ?props]
           [(get ?props :${property}) _]]
        `;
      }

      const results = await client.datascriptQuery<[Record<string, unknown>]>(query);

      return {
        property,
        value,
        count: results.length,
        results: results.map(([block]) => ({
          uuid: block["block/uuid"],
          content: block["block/content"],
          page: (block["block/page"] as Record<string, unknown>)?.["block/name"],
          properties: block["block/properties"],
        })),
      };
    }

    case "logseq_find_by_tag": {
      const tag = args.tag as string;
      const limit = (args.limit as number) ?? 100;

      const query = `
        [:find (pull ?b [:block/uuid :block/content {:block/page [:block/name]}])
         :where
         [?b :block/refs ?r]
         [?r :block/name ?name]
         [(clojure.string/lower-case ?name) ?lower]
         [(= ?lower "${tag.toLowerCase()}")]]
      `;

      const results = await client.datascriptQuery<[Record<string, unknown>]>(query);
      const limited = results.slice(0, limit);

      return {
        tag,
        count: limited.length,
        totalMatches: results.length,
        results: limited.map(([block]) => ({
          uuid: block["block/uuid"],
          content: block["block/content"],
          page: (block["block/page"] as Record<string, unknown>)?.["block/name"],
        })),
      };
    }

    case "logseq_find_tasks": {
      const status = args.status as string | undefined;
      const includeContent = args.includeContent !== false;
      const limit = (args.limit as number) ?? 100;

      let query: string;
      if (status) {
        query = `
          [:find (pull ?b [:block/uuid :block/content :block/marker :block/priority {:block/page [:block/name]}])
           :where
           [?b :block/marker ?m]
           [(= ?m "${status}")]]
        `;
      } else {
        query = `
          [:find (pull ?b [:block/uuid :block/content :block/marker :block/priority {:block/page [:block/name]}])
           :where
           [?b :block/marker ?m]
           [(contains? #{"TODO" "DOING" "DONE" "NOW" "LATER" "WAITING" "CANCELLED"} ?m)]]
        `;
      }

      const results = await client.datascriptQuery<[Record<string, unknown>]>(query);
      const limited = results.slice(0, limit);

      return {
        status: status ?? "ALL",
        count: limited.length,
        totalMatches: results.length,
        tasks: limited.map(([block]) => ({
          uuid: block["block/uuid"],
          marker: block["block/marker"],
          priority: block["block/priority"],
          page: (block["block/page"] as Record<string, unknown>)?.["block/name"],
          ...(includeContent && { content: block["block/content"] }),
        })),
      };
    }

    case "logseq_find_recent_blocks": {
      const days = (args.days as number) ?? 7;
      const limit = (args.limit as number) ?? 50;

      // Calculate timestamp for N days ago (in milliseconds)
      const daysAgo = Date.now() - days * 24 * 60 * 60 * 1000;

      const query = `
        [:find (pull ?b [:block/uuid :block/content :block/updated-at {:block/page [:block/name]}])
         :where
         [?b :block/updated-at ?t]
         [(> ?t ${daysAgo})]]
      `;

      const results = await client.datascriptQuery<[Record<string, unknown>]>(query);

      // Sort by updated-at descending
      const sorted = results.sort((a, b) => {
        const timeA = (a[0]["block/updated-at"] as number) ?? 0;
        const timeB = (b[0]["block/updated-at"] as number) ?? 0;
        return timeB - timeA;
      });

      const limited = sorted.slice(0, limit);

      return {
        days,
        count: limited.length,
        totalMatches: results.length,
        blocks: limited.map(([block]) => ({
          uuid: block["block/uuid"],
          content: block["block/content"],
          page: (block["block/page"] as Record<string, unknown>)?.["block/name"],
          updatedAt: block["block/updated-at"]
            ? new Date(block["block/updated-at"] as number).toISOString()
            : null,
        })),
      };
    }

    case "logseq_find_page_hierarchy": {
      const namespace = args.namespace as string;
      const lowerNamespace = namespace.toLowerCase();

      const query = `
        [:find (pull ?p [:block/uuid :block/name :block/original-name])
         :where
         [?p :block/name ?name]
         [(clojure.string/starts-with? ?name "${lowerNamespace}/")]]
      `;

      const results = await client.datascriptQuery<[Record<string, unknown>]>(query);

      // Also get the parent namespace itself
      const parent = await client.getPage(namespace);

      return {
        namespace,
        parent: parent ? { uuid: parent.uuid, name: parent.name } : null,
        count: results.length,
        children: results.map(([page]) => ({
          uuid: page["block/uuid"],
          name: page["block/name"] ?? page["block/original-name"],
        })),
      };
    }

    default:
      throw new Error(`Unknown query tool: ${name}`);
  }
}
