"""Project management helpers for multi-project knowledge base workspaces.

The knowledge base previously assumed a single project rooted at the workspace
directory. Multi-project environments introduce several constraints:

* Operators need a way to inspect which projects exist on disk before choosing
  one.
* The :class:`~mcp_kb.knowledge.store.KnowledgeBase` instance must be rebuilt
  whenever a different project becomes active so that all filesystem operations
  are sandboxed correctly.
* Setup tasks such as installing the packaged documentation should run against
  the active project rather than the workspace root.

This module centralises that logic in :class:`ProjectManager` so that the MCP
server can stay focused on wiring FastMCP tools. Consolidating the behaviour in
a single, well-documented class keeps the surface area small and future-proof:
additional features like on-demand project creation or metadata reporting can
hook into the manager without touching the server entry points.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional, Tuple

from mcp_kb.config import DATA_FOLDER_NAME
from mcp_kb.knowledge.bootstrap import install_default_documentation
from mcp_kb.knowledge.events import (
    KnowledgeBaseListener,
    KnowledgeBaseSearchListener,
)
from mcp_kb.knowledge.store import KnowledgeBase
from mcp_kb.security.path_validation import PathRules


class ProjectManager:
    """Coordinate active project state and knowledge base instances.

    Parameters
    ----------
    workspace_root:
        Absolute path that contains all project directories and the shared
        ``cli-config.json`` file. Each project is expected to live in a
        sub-directory immediately under this root.
    listeners:
        Optional iterable of :class:`KnowledgeBaseListener` instances. The same
        listener objects are reused for every activated project so that
        integrations like the Chroma ingestor maintain their internal state.

    Notes
    -----
    The manager intentionally avoids mutating the filesystem beyond ensuring
    that packaged documentation is installed for the active project. Project
    discovery is purely based on on-disk directories, which keeps the behaviour
    transparent and easy to reason about. Listeners that expose a
    ``for_project(project_name, project_root)`` callable are cloned for every
    activation so integrations like Chroma can maintain project-specific state.
    """

    def __init__(
        self,
        workspace_root: Path,
        *,
        listeners: Iterable[KnowledgeBaseListener] | None = None,
    ) -> None:
        self.workspace_root = workspace_root
        self._listeners: Tuple[KnowledgeBaseListener, ...] = tuple(listeners or ())
        self.active_project: Optional[str] = None
        self.kb: Optional[KnowledgeBase] = None
        self._active_listeners: Tuple[KnowledgeBaseListener, ...] = ()
        self._active_search_listeners: Tuple[KnowledgeBaseSearchListener, ...] = ()

    def list_projects(self) -> List[str]:
        """Return a sorted list of project directory names.

        Hidden directories (``.git`` etc.) and the reserved metadata directory
        (``.data``) are excluded so that clients only see meaningful project
        identifiers. Callers can present the result to end users before invoking
        :meth:`activate`.
        """

        projects: List[str] = []
        for child in self.workspace_root.iterdir():
            if not child.is_dir():
                continue
            if child.name == DATA_FOLDER_NAME:
                continue
            if child.name.startswith("."):
                continue
            projects.append(child.name)
        projects.sort()
        return projects

    def activate(self, name: str) -> KnowledgeBase:
        """Mark ``name`` as the active project and build its knowledge base.

        Activation re-creates the :class:`KnowledgeBase` so that all path rules
        anchor to ``workspace_root / name``. The method also ensures the default
        documentation bundle is installed for the project on first use.

        Parameters
        ----------
        name:
            Directory name of the target project relative to ``workspace_root``.

        Returns
        -------
        KnowledgeBase
            Configured knowledge base instance rooted at the project directory.

        Raises
        ------
        ValueError
            If the project directory does not exist or is not a directory.
        """

        project_root = self.workspace_root / name
        if not project_root.exists():
            project_root.mkdir(parents=True, exist_ok=True)
        if not project_root.is_dir():
            raise ValueError(
                f"Project '{name}' is not a directory under {self.workspace_root}"
            )

        scoped_listeners: List[KnowledgeBaseListener] = []
        for listener in self._listeners:
            factory = getattr(listener, "for_project", None)
            if callable(factory):
                scoped = factory(name, project_root)
                scoped_listeners.append(scoped)
            else:
                scoped_listeners.append(listener)

        rules = PathRules(root=project_root, protected_folders=(DATA_FOLDER_NAME,))
        knowledge_base = KnowledgeBase(rules, listeners=scoped_listeners)
        install_default_documentation(project_root)

        self.active_project = name
        self.kb = knowledge_base
        self._active_listeners = tuple(scoped_listeners)
        self._active_search_listeners = tuple(
            listener
            for listener in scoped_listeners
            if isinstance(listener, KnowledgeBaseSearchListener)
        )
        return knowledge_base

    def require_active(self) -> KnowledgeBase:
        """Return the active knowledge base or raise a descriptive error."""

        if self.kb is None:
            raise ValueError(
                "No project is active. Call list_projects() and activate_project(<name>) first."
            )
        return self.kb

    def active_search_listeners(self) -> Tuple[KnowledgeBaseSearchListener, ...]:
        """Return search-capable listeners scoped to the current project."""

        return self._active_search_listeners
