# MCP Knowledge Base Server

A local, text‑only knowledge base exposed as an MCP server with optional HTTP/SSE transports and a built‑in web UI. Supports creating, reading, updating, searching, and soft‑deleting UTF‑8 text files. Optionally mirrors content to Chroma for semantic search and 2D/3D vector visualization.

## Highlights

- **MCP tools** for file lifecycle + search
- **HTTP/SSE transports** and a minimal **built‑in UI**
- **Deterministic path validation** and **soft deletes**
- **Metadata catalogue** persisted to `.data/database.json` with per-document stats and tags
- **Optional Chroma mirroring** for semantic search and vector plotting
- **No lock‑in**: works with any Python toolchain (pip/pipx/Poetry/PDM/Rye/etc.)

---

## Table of contents

- [Quick start](#quick-start)
- [How it works](#how-it-works)
- [CLI usage](#cli-usage)
- [MCP tools](#mcp-tools)
- [Human UI](#human-ui)
- [UI HTTP API](#ui-http-api)
- [Optional: ChromaDB mirroring](#optional-chromadb-mirroring)
- [Reindexing CLI](#reindexing-cli)
- [Persistent CLI defaults](#persistent-cli-defaults)
- [Path rules & safety](#path-rules--safety)
- [Testing](#testing)
- [Integrating with LLM clients](#integrating-with-llm-clients)
- [Troubleshooting](#troubleshooting)

---

## Quick start

**Prereqs:** Python 3.11+ is required. :contentReference[oaicite:1]{index=1}

**Install (choose one):**

- From PyPI:

  ```bash
  python -m pip install mcp-kb
  ```

**Run the server (HTTP transport + UI):**

```bash
mcp-kb-server --root /path/to/knowledgebase --transport http
# Alternative if entry points aren't on PATH:
python -m mcp_kb.cli.main --root /path/to/knowledgebase --transport http
```

On first launch, a documentation file is installed at `.data/KNOWLEDBASE_DOC.md`. The UI binds to port **8765** by default and increments until free, logging a URL like:

```
UI available at http://127.0.0.1:8765
```

> **Note:** The server defaults to `stdio` only. Add `--transport sse` and/or `--transport http` to enable network transports.

---

## How it works

- **KnowledgeBase**: safe, validated file operations (create/read/append/regex/soft‑delete).
- **MCP server**: exposes the operations as MCP tools over chosen transports.
- **Human UI**: small web UI for browsing, editing, and searching files.
- **Metadata index**: automatically maintained `.data/database.json` summarising every document.
- **Optional vector layer**: if Chroma is configured, semantic search and a 3D scatter of embeddings appear in the UI.

---

## CLI usage

The package exposes these entry points: `mcp-kb` / `mcp-kb-server` (run server) and `mcp-kb-reindex` (offline reindex).

Common flags (server):

- `--root <path>`: KB root directory (relative paths are enforced internally)
- `--transport {stdio|sse|http}` (repeatable; default: `stdio`)
- `--host <ip>` / `--port <int>`: apply to HTTP/SSE transports
- `--ui-port <int>`: starting port for UI (default 8765; auto‑increments if busy)
- `--no-ui`: disable the UI even if HTTP/SSE is active
- `--project <name>`: activate a specific project at startup. When omitted the
  server boots without an active project and the UI project selector (or MCP tool)
  can be used to choose one interactively.

Examples:

```bash
# stdio only (default):
mcp-kb-server --root /path/to/kb

# HTTP + SSE + stdio:
mcp-kb-server --root /path/to/kb \
  --transport stdio --transport sse --transport http \
  --host 0.0.0.0 --port 9000
```

---

## MCP tools

All tools operate on **relative** paths inside the KB root and respect soft‑deletes.
Multi-project workspaces expose two management tools up front; the rest require
an active project.

- `list_projects() -> [str]` _(sorted directory names under the workspace root; available only when no project is pre-selected via `--project`)_
- `activate_project(name) -> str` _(rebuilds the knowledge base sandbox for `name`; hidden when `--project` is supplied)_

- `create_file(path, content, tags?) -> str` _(optional explicit tags persisted to `.data/database.json`)_
- `read_file(path, start_line?, end_line?) -> {path, start_line, end_line, content}`
- `append_file(path, content, tags?) -> str`
- `regex_replace(path, pattern, replacement) -> {replacements}`
- `delete(path) -> str` _(soft delete; renames file with sentinel)_
- `search(query, limit=5) -> [FileSegment...]` _(semantic first if Chroma is on; otherwise literal scan)_
- `overview() -> str` _(tree plus unique tag inventory)_
- `documentation() -> str`
- `add_tags(path, tags) -> str`
- `remove_tags(path, tags) -> str`
- `list_files_by_tags(tags, match_mode?) -> [{ path, matched_tags, match_count, all_tags, tags }]`

`read_file` and `search` return **FileSegment** objects with `start_line`, `end_line`, and `content`. Line indices are **0‑based inclusive** in the JSON the server emits.

---

## Human UI

- Menu: **Browse** (always) and **Vectors** (when a vector store is available).
- Project selector: choose the active project from the top bar. The UI is served
  immediately even before a project is active; the editor and file actions stay
  disabled until a selection is made.
- Browse: left tree, right editor, Save/Cancel/Delete, and **New File**.
- Search: sidebar search filters the tree; clicking a result opens the file and highlights the matched lines. When vectors are available, the plot highlights results and the query point.

---

## UI HTTP API

Base path is the UI origin.

- `GET /api/tree` → file tree (nested `{name, path, type, children}`)
- `GET /api/file?path=<rel>` → `{path, start_line, end_line, content}`
- `PUT /api/file` (JSON `{path, content}`) → `204` on success
- `DELETE /api/file?path=<rel>` → `204` on success
- `GET /api/projects` → `{ projects: [...], active: <str|null> }`
- `POST /api/projects/activate` (JSON `{name}`) → `{ projects: [...], active: <str> }`
- `GET /api/search?query=<text>&limit=<int>` →

  ```json
  {
    "results": [
      { "path": "notes/a.md", "start_line": 10, "end_line": 12, "content": "..." }
    ],
    "meta": {
      "query_embeddings": [ ... ],
      "query_embeddings_umap2d": [x, y],
      "query_embeddings_umap3d": [x, y, z]
    }
  }
  ```

  _(Meta fields appear when Chroma is enabled.)_

**Vector endpoints** (visible when Chroma is configured):

- `GET /api/vector/status` → `{ "available": bool, "dimensions": int|null, "count": int|null }`
- `GET /api/vector/embeddings?limit=<int>&offset=<int>&path=<rel?>` → `[ { id, document_id, path, chunk, embedding, umap2d?, umap3d? } ]`
- `GET /api/vector/query_embedding?query=<text>` → `{ embedding: number[], used_model: string|null }`
- `POST /api/vector/reindex` → `{ status: "queued"|"running"|"unavailable"|"error" }`
- `POST /api/vector/refit` → `{ status: "queued"|"unavailable"|"error" }`

---

## Optional: ChromaDB mirroring

Install the vector extras (pick what you need):

```bash
# core vector support (Chroma, UMAP integration, splitters)
python -m pip install 'mcp-kb[vector]'

# add Sentence Transformers embedding support
python -m pip install 'mcp-kb[sentence-transformer]'
```

Enable via CLI flags (examples):

```bash
mcp-kb-server \
  --root /path/to/kb \
  --transport http \
  --chroma-client ephemeral \
  --chroma-collection local-kb \
  --chroma-embedding default
```

Supported clients: `off`, `ephemeral`, `persistent`, `http`, `cloud`. All `--chroma-*` flags have `MCP_KB_CHROMA_*` env var equivalents (e.g., `MCP_KB_CHROMA_CLIENT=http`, `MCP_KB_CHROMA_HOST=...`). Chunking can be tuned with `--chroma-chunk-size` and `--chroma-chunk-overlap`.

In multi-project workspaces the configured collection name acts as a **prefix**:
each active project uses `<collection>-<slug>` along with an ID prefix of
`<id_prefix><slug>::`. The slug normalises the project name to
`[a-zA-Z0-9._-]`. Persistent clients also switch to `<project>/.data/chroma`
so vector stores remain isolated.

---

## Reindexing CLI

Rebuild the Chroma index from disk without running the MCP transports:

```bash
mcp-kb-reindex --root /path/to/kb \
  --chroma-client persistent \
  --chroma-data-dir /path/to/chroma \
  --chroma-collection knowledge-base \
  --chroma-embedding default
```

This processes all active text files and updates the collection; some tests assert the reindex path mirrors content exactly.

---

## Persistent CLI defaults

Resolved CLI/environment settings are persisted per KB root at:

```
<root>/cli-config.json
```

Future runs inherit these defaults unless overridden by new flags or env vars. Delete or edit the file to reset.

---

## Workspace layout

Each knowledge base workspace hosts multiple projects:

```
.knowledgebase/
  cli-config.json
  <project>/
    .data/
      database.json
    ...
```

Call `list_projects` to enumerate the available `<project>` directories and
`activate_project` to select one before using the rest of the MCP tools.

---

## Path rules & safety

- **Relative paths only.** Absolute paths and `..` traversal are rejected.
- **`.data/` is read‑only** for writes (reads allowed).
- **Soft delete**: files renamed with a sentinel; hidden from listing/search.
- Writes are serialized with per‑file locks to avoid corruption.

These rules are enforced in the validation and filesystem helpers.

---

## Testing

Install test deps and run:

```bash
python -m pip install pytest
pytest -q
```

Vector‑related tests are skipped if Chroma isn’t installed. To run them:

```bash
python -m pip install 'mcp-kb[vector]'
pytest -q
```

The suite exercises the real HTTP UI, vector endpoints, CLI config persistence, and FastMCP flows.

---

## Integrating with LLM clients

Provide the server command your client can execute. Two portable options:

- **Executable** (preferred if on PATH):

  ```json
  {
    "command": "mcp-kb-server",
    "args": ["--root", "/absolute/path/.knowledgebase", "--transport", "stdio"]
  }
  ```

- **Python module** (works even without entry points on PATH):

  ```json
  {
    "command": "python",
    "args": [
      "-m",
      "mcp_kb.cli.main",
      "--root",
      "/absolute/path/.knowledgebase",
      "--transport",
      "stdio"
    ]
  }
  ```

Examples:

- **Claude Desktop** (`claude_desktop_config.json`):

  ```json
  {
    "mcpServers": {
      "local-kb": {
        "command": "mcp-kb-server",
        "args": [
          "--root",
          "/absolute/path/.knowledgebase",
          "--transport",
          "stdio"
        ]
      }
    }
  }
  ```

- **VS Code (Claude MCP Extension)** (`settings.json`):

  ```json
  {
    "claudeMcp.servers": {
      "local-kb": {
        "command": "mcp-kb-server",
        "args": [
          "--root",
          "/absolute/path/.knowledgebase",
          "--transport",
          "stdio"
        ],
        "env": { "MCP_KB_ROOT": "/absolute/path/.knowledgebase" }
      }
    }
  }
  ```

---

## Troubleshooting

- **“Absolute paths are not permitted”** → Use a **relative** path in tools and UI.
- **“Writes are not allowed inside the protected folder '.data'”** → Choose a different directory (e.g., `docs/`).
- **Vector endpoints missing** → You didn’t install/enable the vector extras or a Chroma client.
- **UI port in use** → Set `--ui-port` to another number; it auto‑increments if busy.
