# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records (ADRs) for Clauxton.

## What is an ADR?

An Architecture Decision Record (ADR) captures an important architectural decision made along with its context and consequences.

## ADR Index

- [ADR-001: YAML for Data Storage](./ADR-001-yaml-storage.md)
- [ADR-002: TF-IDF for Search](./ADR-002-tfidf-search.md)
- [ADR-003: DAG for Task Dependencies](./ADR-003-dag-dependencies.md)
- [ADR-004: MCP Protocol](./ADR-004-mcp-protocol.md)
- [ADR-005: File-Based Storage](./ADR-005-file-based-storage.md)

## ADR Template

```markdown
# ADR-XXX: Title

**Status**: [Accepted | Deprecated | Superseded]
**Date**: YYYY-MM-DD
**Deciders**: [Name(s)]

## Context

What is the issue we're seeing that is motivating this decision or change?

## Decision

What is the change that we're proposing and/or doing?

## Consequences

What becomes easier or more difficult to do because of this change?

### Positive

- ...

### Negative

- ...

## Alternatives Considered

What other options were considered?

1. **Option**: Description
   - **Pros**: ...
   - **Cons**: ...
```
