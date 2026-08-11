# 🌐 Swarms-on-Edge: Architectural Blueprint

## Executive Summary

**Swarms-on-Edge** is a next-generation distributed multi-agent orchestrator built on top of the **Model Context Protocol (MCP)**. As AI workflows scale from single-agent setups to enterprise-wide automation fleets, managing isolated tools and fragmented LLM contexts becomes a critical bottleneck. Swarms-on-Edge solves this by introducing a decentralized **MCP Gateway & Worker Architecture** that allows remote, containerized MCP servers (Workers) to dynamically register, collaborate, and execute complex workflows under a unified Command Node.

---

## System Architecture

The architecture separates control and execution planes, enabling scalable, secure, and fault-tolerant multi-agent operations across distributed infrastructure.

```mermaid
graph TD
    subgraph Client Layer [AI Client Layer]
        Claude[Claude Desktop / Cursor]
    end

    subgraph Command Node [Command Node (MCP Gateway)]
        Gateway[Fast Gateway / SSE Router]
        Registry[Worker Registry]
        Router[Tool Router & Dispatcher]
    end

    subgraph Edge Worker Fleet [Distributed Edge Workers]
        W1[Worker 1: Code Gen / Python]
        W2[Worker 2: Data & Database]
        W3[Worker 3: CRM / GoHighLevel]
        W4[Worker 4: Web Scraping / Puppeteer]
    end

    Client Claude <-->|JSON-RPC via SSE| Gateway
    Gateway --> Registry
    Gateway --> Router
    Router -->|HTTP / SSE| W1
    Router -->|HTTP / SSE| W2
    Router -->|HTTP / SSE| W3
    Router -->|HTTP / SSE| W4
```

### Component Breakdown

| Component | Description | Technologies |
| :--- | :--- | :--- |
| **Command Node (Gateway)** | Acts as the unified front door for AI clients. Translates local stdio or standard HTTP calls into distributed JSON-RPC messages routed to active workers. | Node.js, Hono, MCP SDK |
| **Worker Registry** | Maintains a real-time ledger of active edge workers, their health metrics, latency profiles, and exposed tool schemas. | In-Memory / Redis |
| **Tool Router** | Dynamically aggregates tools from all registered workers and presents them as a single cohesive capability set to the primary LLM. | TypeScript, JSON-RPC 2.0 |
| **Edge Workers** | Autonomous, containerized services running specialized tools (e.g., DB queries, browser automation, API integrations). | Python, Node.js, Docker |

---

## Core Workflows

### 1. Dynamic Worker Registration
When an edge worker boots up on any remote server or local machine, it pings the Command Node with its manifest:
```json
{
  "worker_id": "worker-db-01",
  "endpoint": "https://db-worker.edgeagency.pro/mcp",
  "capabilities": ["sql_query", "schema_introspection", "migration_run"]
}
```
The Command Node validates the worker, adds it to the **Worker Registry**, and instantly exposes its tools to connected LLM clients without requiring a gateway restart.

### 2. Distributed Task Execution
1. The user asks Claude/Cursor to perform a complex task (e.g., *"Scrape competitor pricing, update the database, and draft a CRM campaign"*).
2. The Command Node receives the aggregated tool call.
3. The **Tool Router** splits the request and dispatches parallel sub-tasks via Server-Sent Events (SSE) to **Worker 4** (Scraping), **Worker 2** (Database), and **Worker 3** (CRM).
4. Results are synthesized and returned securely to the client.

---

## Security & Enterprise Governance

- **Mutual TLS (mTLS)**: All communication between the Command Node and Edge Workers is encrypted and authenticated via certificates.
- **Role-Based Tool Access (RBAC)**: Workers can be restricted to specific namespaces, preventing unauthorized tool execution.
- **Audit Logging**: Every JSON-RPC request and response is streamed to an immutable ledger for compliance and debugging.

---

*Authored by **Edge Agency** — Shaping the Autonomous Future.*
