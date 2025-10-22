# ADR-004: MCP Protocol for Claude Code Integration

**Status**: Accepted
**Date**: 2025-02-01
**Deciders**: Clauxton Core Team

## Context

Clauxton needs to integrate with Claude Code to provide seamless access to Knowledge Base and Task Management features directly within Claude's workflow.

Requirements:
1. **Seamless Integration**: Claude Code should access Clauxton without user intervention
2. **Tool Discovery**: Claude should discover available tools automatically
3. **Bi-directional Communication**: Request/response pattern
4. **Minimal Setup**: No complex configuration required
5. **Secure**: Local communication only (no network exposure)

## Decision

Use **MCP (Model Context Protocol)** for Claude Code integration.

MCP is a protocol designed for LLMs to interact with external tools:
- **Transport**: stdio (standard input/output)
- **Format**: JSON-RPC 2.0
- **Tools**: 17 tools exposed (kb_*, task_*, conflict_*, etc.)
- **Server**: Long-running process, started by Claude Code

```python
# MCP Server
from mcp.server import Server
from mcp.server.stdio import stdio_server

server = Server("clauxton")

@server.call_tool()
async def kb_search(query: str, limit: int = 10) -> List[Dict]:
    return clauxton.kb.search(query, limit)
```

## Consequences

### Positive

1. **Official Protocol**:
   - Designed specifically for LLM-tool integration
   - Supported by Claude Code officially
   - Future-proof (maintained by Anthropic)

2. **Automatic Discovery**:
   - Claude discovers tools via `tools/list`
   - Tool schemas auto-generated from type hints
   - No manual configuration

3. **Secure**:
   - stdio transport (no network port)
   - Local communication only
   - No authentication needed (trusted local process)

4. **Simple Setup**:
   - Add to `claude_desktop_config.json`
   - Claude Code starts server automatically
   - No daemon management required

5. **Type Safety**:
   - Pydantic models for request/response
   - Runtime validation
   - Clear error messages

### Negative

1. **Protocol Dependency**:
   - Tied to MCP protocol evolution
   - Breaking changes possible (mitigated: MCP is stable)

2. **Limited to Claude**:
   - MCP is Anthropic-specific (currently)
   - Other LLMs would need different integration
   - **Mitigation**: CLI provides universal access

3. **Debugging Difficulty**:
   - stdio communication hard to inspect
   - Requires MCP inspector tool
   - Error messages may be unclear

4. **Single Client**:
   - One Claude Code instance per server
   - No multi-client support
   - **Mitigation**: Not a requirement

5. **Long-Running Process**:
   - Server must stay running
   - Memory usage over time
   - **Mitigation**: Lightweight server (~50MB)

## Alternatives Considered

### 1. REST API

**Pros**:
- Universal (any HTTP client)
- Well-understood
- Easy to test (curl, Postman)

**Cons**:
- Requires port management
- Network exposure risk
- Authentication complexity
- More setup overhead

**Why Rejected**: Network exposure unnecessary for local tool.

### 2. CLI Wrapper

**Pros**:
- Simplest implementation
- No long-running process
- Universal access

**Cons**:
- Slow (start process per call)
- No state management
- Poor user experience (Claude calls CLI repeatedly)
- No automatic discovery

**Why Rejected**: Too slow for interactive use.

### 3. gRPC

**Pros**:
- Efficient binary protocol
- Type-safe (Protocol Buffers)
- Bi-directional streaming

**Cons**:
- More complex setup
- Requires port management
- Overkill for simple tool calls

**Why Rejected**: Too complex for local communication.

### 4. Unix Domain Sockets

**Pros**:
- Fast local communication
- No network exposure
- Secure

**Cons**:
- Not cross-platform (Windows support poor)
- Requires socket file management
- No standard protocol

**Why Rejected**: stdio is simpler and cross-platform.

### 5. Embedded Python (import clauxton)

**Pros**:
- Fastest (no IPC)
- No protocol overhead
- Direct Python access

**Cons**:
- Claude Code can't directly import Python
- Requires Python embedding
- Version conflicts (Claude's Python vs user's)

**Why Rejected**: Not feasible with Claude Code architecture.

## Implementation Notes

### Server Initialization

```python
# clauxton/mcp/server.py
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server

server = Server("clauxton")

# Register tools
@server.call_tool()
async def kb_search(query: str, limit: int = 10):
    kb = KnowledgeBase(Path.cwd())
    return [entry.model_dump() for entry in kb.search(query, limit)]

# Run server
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

### Claude Configuration

```json
{
  "mcpServers": {
    "clauxton": {
      "command": "clauxton-mcp",
      "args": [],
      "env": {}
    }
  }
}
```

### Tool Registration

```python
# 17 tools exposed:
# Knowledge Base (6 tools)
kb_search, kb_add, kb_list, kb_get, kb_update, kb_delete

# Task Management (7 tools)
task_add, task_import_yaml, task_list, task_get,
task_update, task_next, task_delete

# Conflict Detection (3 tools)
detect_conflicts, recommend_safe_order, check_file_conflicts

# Export (1 tool)
kb_export_docs
```

### Error Handling

```python
@server.call_tool()
async def kb_add(entry_data: Dict) -> Dict:
    try:
        entry = KnowledgeBaseEntry(**entry_data)
        kb = KnowledgeBase(Path.cwd())
        entry_id = kb.add(entry)
        return {"status": "success", "entry_id": entry_id}
    except ValidationError as e:
        return {"status": "error", "message": str(e)}
```

## Future Considerations

1. **Tool Expansion**: Add more tools as Clauxton features grow
2. **Streaming**: Support streaming for large results (logs, search)
3. **Multi-Repository**: Handle multiple repositories simultaneously
4. **Caching**: Cache frequent queries (search results)
5. **Standard Adoption**: If MCP becomes industry standard, expand to other LLMs

## Performance Characteristics

| Operation       | Latency | Notes                          |
|-----------------|---------|--------------------------------|
| Tool Call       | ~5-10ms | JSON-RPC overhead              |
| kb_search       | ~20ms   | TF-IDF search (100 entries)    |
| task_add        | ~30ms   | DAG validation + file I/O      |
| task_import_yaml| ~100ms  | Bulk import (10 tasks)         |

**Throughput**: ~100 requests/second (single-threaded, sufficient for interactive use).

## References

- [MCP Specification](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)
- [Claude Code Documentation](https://claude.com/claude-code)
