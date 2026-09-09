# TripMate AI

TripMate AI is a modular Agentic AI travel planning system being built using LangGraph, LangChain, Gemini, and Model Context Protocol (MCP).

## Current Features

- Gemini-powered travel agent
- Dynamic tool selection
- Trip duration calculation
- Trip budget calculation
- MCP server using FastMCP
- MCP tool discovery using LangChain MCP adapters
- stdio-based MCP communication
- Structured agent responses using Pydantic
- Unit and integration testing with pytest

## Current Architecture

User Request
→ Gemini Agent
→ LangChain MCP Adapter
→ MCP Server
→ Travel Tool
→ MCP Result
→ Gemini
→ Structured Response

## Development Status

- Phase 0 — Project Foundation ✅
- Phase 1 — Agent Fundamentals ✅
- Phase 2 — MCP Fundamentals ✅
- Phase 3 — LangGraph State & Workflow ⏳