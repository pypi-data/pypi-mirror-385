"""FastMCP application that exposes knowledge base management tools.

The module builds a :class:`FastMCP` server configured with the knowledge base
operations defined elsewhere in the package. Using FastMCP drastically reduces
protocol boilerplate because the framework introspects type hints and
Docstrings to generate MCP-compatible tool schemas automatically.
"""

from __future__ import annotations

from typing import Iterable, List, Literal, Optional, Union
from pydantic import BaseModel

from mcp.server.fastmcp import FastMCP

from mcp_kb.config import DOC_FILENAME
from mcp_kb.knowledge.events import KnowledgeBaseListener
from mcp_kb.knowledge.search import build_tags_overview, build_tree_overview, read_documentation, search_text
from mcp_kb.knowledge.store import FileSegment, KnowledgeBase
from mcp_kb.projects import ProjectManager
from mcp_kb.security.path_validation import PathRules, PathValidationError
from pathlib import Path
from pydantic import model_validator


class ReadFileResult(BaseModel):
    """Structured output for the ``kb.read_file`` tool."""

    path: str
    start_line: int
    end_line: int
    content: str

    @model_validator(mode="before")
    @classmethod
    def check_path(cls, values: dict) -> dict:
        if isinstance(values["path"], Path):
            values["path"] = str(values["path"])
        return values

    def assert_path(self,rules: PathRules) -> None:
        rel_path = Path(self.path)
        if not rel_path.is_absolute():
            abspath = rules.root / rel_path
        else:
            abspath = rel_path
        # make sure the relative path is inside the knowledge base root
        if not abspath.is_relative_to(rules.root):
            raise ValueError(f"Relative path {rel_path} is not in the knowledge base root")
        # make sure the relative path is not in the protected folders
        self.path = str(abspath.relative_to(rules.root))


class RegexReplaceResult(BaseModel):
    """Structured output describing the number of replacements performed."""

    replacements: int


class TagMatchResult(BaseModel):
    """Structured output describing files returned by the tag lookup tool."""

    path: str
    matched_tags: List[str]
    match_count: int
    all_tags: List[str]
    tags: List[str]


def create_fastmcp_app(
    rules: PathRules,
    *,
    host: str | None = None,
    port: int | None = None,
    listeners: Iterable[KnowledgeBaseListener] | None = None,
    project_name: str | None = None,
) -> FastMCP:
    """Build and return a configured :class:`FastMCP` server instance.

    Parameters
    ----------
    rules:
        Sanitised filesystem rules that restrict all knowledge base operations to
        a designated root.
    host:
        Optional host interface for HTTP/SSE transports. ``None`` uses FastMCP's
        defaults.
    port:
        Optional TCP port for HTTP/SSE transports. ``None`` uses FastMCP's defaults.
    listeners:
        Optional iterable of :class:`KnowledgeBaseListener` implementations that
        should receive change notifications. The iterable is passed directly to
        :class:`~mcp_kb.knowledge.store.KnowledgeBase` so that integrations such
        as Chroma ingestion can react to file lifecycle events.
    project_name:
        Optional project to activate immediately. When omitted the server starts
        in a dormant state and only project management tools are available until
        :func:`activate_project` is invoked.
    """

    listener_tuple: tuple[KnowledgeBaseListener, ...] = tuple(listeners or ())
    project_manager = ProjectManager(rules.root, listeners=listener_tuple)
    kb: Optional[KnowledgeBase] = None
    if project_name:
        kb = project_manager.activate(project_name)

    fastmcp_kwargs: dict[str, object] = {}
    if host is not None:
        fastmcp_kwargs["host"] = host
    if port is not None:
        fastmcp_kwargs["port"] = port

    mcp = FastMCP(
        "mcp-knowledge-base",
        instructions=(
            "You are connected to a local text-based knowledge base. Use the provided "
            "tools to create, inspect, and organize content and search the knowledgebase for information.\n"
            "Call the documentation tool first to get the latest documentation."
        ),
        **fastmcp_kwargs,
    )

    # Attach the knowledge base and project manager to the FastMCP instance for
    # reuse by auxiliary servers (e.g., the human UI HTTP server). FastMCP does
    # not expose a public extension API for storing arbitrary state, but keeping
    # direct attributes is harmless and enables tight coupling where needed.
    # Downstream code should treat this as best-effort and feature-gated.
    setattr(mcp, "kb", kb)  # type: ignore[attr-defined]
    setattr(mcp, "projects", project_manager)  # type: ignore[attr-defined]

    def _require_project() -> KnowledgeBase:
        """Retrieve the active knowledge base, enforcing project activation.

        Multi-project workspaces start in a dormant state so that callers can
        examine available projects. Invoking this helper inside every
        filesystem-affecting tool guarantees that no operation escapes the
        sandbox: a :class:`ValueError` is raised with actionable instructions
        when no project is selected yet.
        """

        return project_manager.require_active()

    project_tools_enabled = project_name is None

    if project_tools_enabled:
        @mcp.tool(name="list_projects", title="List Projects", structured_output=True)
        def list_projects() -> List[str]:
            """Enumerate on-disk project identifiers.

            The tool scans direct children of the configured workspace root,
            filtering out hidden folders and the reserved ``.data`` directory.
            Clients typically invoke this before deciding which project to activate.
            """

            return project_manager.list_projects()

        @mcp.tool(name="activate_project", title="Activate Project")
        def activate_project(project: str) -> str:
            """Switch the active project to ``project``.

            Activation rebuilds the underlying :class:`KnowledgeBase` using the
            project's directory as its root and ensures the packaged documentation
            is available under that project. Subsequent tool calls operate strictly
            within the selected project's boundaries.
            """

            nonlocal kb
            kb = project_manager.activate(project)
            setattr(mcp, "kb", kb)  # type: ignore[attr-defined]
            return f"Activated project '{project}'"

    @mcp.tool(name="create_file", title="Create File")
    def create_file(path: str, content: str, tags: List[str] | None = None) -> str:
        """Create or overwrite a text file at ``path`` with ``content`` and tags."""

        try:
            created = _require_project().create_file(path, content, tags=tags)
        except PathValidationError as exc:
            raise ValueError(str(exc)) from exc
        return f"Created {created}"

    @mcp.tool(name="read_file", title="Read File", structured_output=True)
    def read_file(
        path: str, start_line: int | None = None, end_line: int | None = None
    ) -> ReadFileResult:
        """Read a text file returning metadata about the extracted segment. 
        start_line and end_line are 0-based line numbers.
        """

        kb_instance = _require_project()
        try:
            segment: FileSegment = kb_instance.read_file(
                path, start_line=start_line, end_line=end_line
            )
        except PathValidationError as exc:
            raise ValueError(str(exc)) from exc
        except FileNotFoundError as exc:
            raise ValueError(str(exc)) from exc

        result = ReadFileResult(
            path=str(segment.path),
            start_line=segment.start_line,
            end_line=segment.end_line,
            content=segment.content,
        )
        result.assert_path(kb_instance.rules)
        return result

    @mcp.tool(name="append_file", title="Append File")
    def append_file(path: str, content: str, tags: List[str] | None = None) -> str:
        """Append ``content`` to the file specified by ``path`` and update tags."""

        try:
            target = _require_project().append_file(path, content, tags=tags)
        except PathValidationError as exc:
            raise ValueError(str(exc)) from exc
        return f"Appended to {target}"

    @mcp.tool(name="regex_replace", title="Regex Replace", structured_output=True)
    def regex_replace(path: str, pattern: str, replacement: str) -> RegexReplaceResult:
        """Perform a regex-based replacement across the full file."""

        try:
            replacements = _require_project().regex_replace(path, pattern, replacement)
        except PathValidationError as exc:
            raise ValueError(str(exc)) from exc
        return RegexReplaceResult(replacements=replacements)

    @mcp.tool(name="delete", title="Soft Delete")
    def delete(path: str) -> str:
        """Soft delete the file at ``path`` by appending the configured sentinel."""

        try:
            deleted = _require_project().soft_delete(path)
        except PathValidationError as exc:
            raise ValueError(str(exc)) from exc
        except FileNotFoundError as exc:
            raise ValueError(str(exc)) from exc
        return f"Marked {deleted.name} as deleted"

    @mcp.tool(name="search", title="Search", structured_output=True)
    def search(query: str, limit: int = 5) -> List[FileSegment]:
        """Search for ``query`` across the knowledge base with semantic ranking.

        Registered listeners that implement the optional search interface are
        queried first (e.g., the Chroma ingestor). When no listener returns a
        result the tool falls back to streaming the markdown files directly so
        callers always receive deterministic text snippets.
        """

        if limit <= 0:
            raise ValueError("limit must be greater than zero")

        kb_instance = _require_project()
        providers = project_manager.active_search_listeners()
        matches = search_text(
            kb_instance,
            query,
            providers=providers,
            n_results=limit,
        )[0]

        for match in matches:
            match.assert_path(kb_instance.rules)
        return matches

    @mcp.tool(name="overview", title="Overview")
    def overview() -> str:
        """Return a textual tree describing the knowledge base structure."""

        kb_instance = _require_project()
        return build_tree_overview(kb_instance) + "\n\n" + build_tags_overview(kb_instance)

    @mcp.tool(name="documentation", title="Documentation")
    def documentation() -> str:
        """Read the knowledge base documentation if ``%s`` exists.""" % DOC_FILENAME

        text = read_documentation(_require_project())
        if not text:
            return "Documentation is not available."
        return text

    @mcp.tool(name="add_tags", title="Add Tags")
    def add_tags(path: str, tags: List[str]) -> str:
        """Merge ``tags`` into the explicit metadata list for ``path``."""

        try:
            kb_instance = _require_project()
            target = kb_instance.add_tags(path, tags)
        except PathValidationError as exc:
            raise ValueError(str(exc)) from exc
        except FileNotFoundError as exc:
            raise ValueError(str(exc)) from exc
        except ValueError as exc:
            raise ValueError(str(exc)) from exc
        relative = target.relative_to(kb_instance.rules.root)
        return f"Added tags to {relative}"

    @mcp.tool(name="remove_tags", title="Remove Tags")
    def remove_tags(path: str, tags: List[str]) -> str:
        """Remove ``tags`` from the explicit metadata list for ``path``."""

        try:
            kb_instance = _require_project()
            target = kb_instance.remove_tags(path, tags)
        except PathValidationError as exc:
            raise ValueError(str(exc)) from exc
        except FileNotFoundError as exc:
            raise ValueError(str(exc)) from exc
        except ValueError as exc:
            raise ValueError(str(exc)) from exc
        relative = target.relative_to(kb_instance.rules.root)
        return f"Removed tags from {relative}"

    @mcp.tool(
        name="list_files_by_tags",
        title="List Files By Tags",
        structured_output=True,
    )
    def list_files_by_tags(
        tags: Union[str, List[str]],
        match_mode: Literal["any", "all"] = "any",
    ) -> List[TagMatchResult]:
        """Return metadata for files matching ``tags`` under the requested rule."""

        if isinstance(tags, str):
            tag_values: List[str] = [tags]
        else:
            tag_values = list(tags)

        kb_instance = _require_project()
        try:
            matches = kb_instance.list_files_by_tags(tag_values, match_mode=match_mode)
        except ValueError as exc:
            raise ValueError(str(exc)) from exc

        return [
            TagMatchResult(
                path=item["path"],
                matched_tags=item["matched_tags"],
                match_count=item["match_count"],
                all_tags=item["all_tags"],
                tags=item["tags"],
            )
            for item in matches
        ]

    return mcp
