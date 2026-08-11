"""Swarms-on-Edge reference worker.

This worker exposes a small HTTP contract used by the Command Node:
  GET  /tools -> tool manifests
  POST /call  -> execute a namespaced tool

The production version can replace the reference implementations with
Playwright, database, CRM, or MCP-backed capabilities without changing the
registration and routing contract.
"""

from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Swarms-on-Edge Reference Worker", version="1.0.0")


class ToolCall(BaseModel):
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


async def analyze_lead_website(arguments: dict[str, Any]) -> str:
    url = arguments.get("url", "")
    if not url:
        raise ValueError("url is required")
    return (
        f"Intelligence report for {url}: SaaS/Fintech positioning detected; "
        "recommended follow-up is an onboarding automation audit."
    )


async def search_business_leads(arguments: dict[str, Any]) -> str:
    niche = arguments.get("niche", "businesses")
    location = arguments.get("location", "the target market")
    return f"Reference worker found 15 {niche} leads in {location}."


TOOLS: dict[str, dict[str, Any]] = {
    "analyze_lead_website": {
        "name": "analyze_lead_website",
        "description": "Analyze a business website and return a concise intelligence report.",
        "inputSchema": {
            "type": "object",
            "properties": {"url": {"type": "string", "description": "Website URL"}},
            "required": ["url"],
        },
        "handler": analyze_lead_website,
    },
    "search_business_leads": {
        "name": "search_business_leads",
        "description": "Find candidate businesses by niche and location.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "niche": {"type": "string"},
                "location": {"type": "string"},
            },
            "required": ["niche", "location"],
        },
        "handler": search_business_leads,
    },
}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "worker_id": os.getenv("WORKER_ID", "reference-worker")}


@app.get("/tools")
async def list_tools() -> dict[str, list[dict[str, Any]]]:
    return {
        "tools": [
            {key: value for key, value in tool.items() if key != "handler"}
            for tool in TOOLS.values()
        ]
    }


@app.post("/call")
async def call_tool(call: ToolCall) -> dict[str, Any]:
    tool = TOOLS.get(call.name)
    if tool is None:
        raise HTTPException(status_code=404, detail=f"Unknown tool: {call.name}")
    try:
        result = await tool["handler"](call.arguments)
        return {"content": [{"type": "text", "text": result}]}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8001")))
