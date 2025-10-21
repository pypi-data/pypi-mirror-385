"""Persistent metadata index for knowledge base documents.

The MCP knowledge base exposes multiple transports and ancillary services that
benefit from fast metadata lookups without repeatedly reading every document
from disk.  This module centralises that responsibility in the
``KnowledgeBaseMetadata`` class which materialises a JSON catalogue under the
knowledge base ``.data`` directory.  The catalogue is intentionally
flat—mapping POSIX-style relative paths to dictionaries of descriptive fields—
so it remains easy to diff, inspect, and extend over time.

The metadata file is designed to be updated whenever documents change.  Each
entry tracks:

* ``length`` – number of characters in the file, useful for quota checks.
* ``line_count`` – number of newline-delimited lines, aiding editors.
* ``word_count`` – whitespace-delimited token count for heuristic summaries.
* ``checksum`` – SHA-256 digest of the file content for cache validation.
* ``tags`` – list of semantic tags derived from front matter heuristics.
* ``title`` – the first Markdown heading, offering a human-readable label.
* ``updated_at`` – UTC timestamp (ISO-8601) describing the last write.

Additional fields can be added in the future without breaking consumers so long
as they remain JSON-serialisable primitives.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from threading import Lock
from typing import Any, Callable, Dict, Iterable, List, MutableMapping, Optional, Sequence, Literal

from mcp_kb.config import DATA_FOLDER_NAME
from mcp_kb.utils.filesystem import read_text_file
from pydantic import BaseModel, Field


__all__ = ["KnowledgeBaseMetadata", "normalize_tags"]


def _current_timestamp() -> str:
    """Return the current UTC time encoded as an ISO-8601 string."""

    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _first_heading(content: str) -> Optional[str]:
    """Extract the first Markdown heading from ``content`` if present."""

    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip() or None
    return None



def _word_count(content: str) -> int:
    """Return the number of word-like tokens contained in ``content``."""

    if not content:
        return 0
    return len(re.findall(r"\b\w+\b", content))


def normalize_tags(tags: Iterable[str]) -> List[str]:
    """Normalise user-supplied ``tags`` into a sorted, deduplicated list."""

    cleaned: set[str] = set()
    for tag in tags:
        cleaned_tag = str(tag).strip().lower()
        if cleaned_tag:
            cleaned.add(cleaned_tag)
    return sorted(cleaned)


class MetadataEntry(BaseModel):
    """In-memory representation of a single row in ``database.json``."""

    length: int
    tags: List[str] = Field(default_factory=list)
    line_count: int
    word_count: int
    checksum: str
    title: Optional[str]
    updated_at: str


    

class TagMatchResult(BaseModel):
    """Structured output describing files returned by the tag lookup tool."""

    path: str
    matched_tags: List[str]
    match_count: int
    all_tags: List[str]
    tags: List[str]

class KnowledgeBaseMetadata:
    """Manage the ``database.json`` catalogue for a knowledge base instance.

    Parameters
    ----------
    root:
        Absolute path to the knowledge base root directory.
    data_folder:
        Name of the internal folder that stores metadata files.  Defaults to the
        conventional ``.data`` directory.
    filename:
        Target file name for the JSON catalogue.  The file is created if it does
        not already exist.
    clock:
        Optional callable returning the current time as a ``datetime`` string.
        The parameter exists primarily for unit testing where deterministic
        timestamps make assertions straightforward.
    """

    def __init__(
        self,
        root: Path,
        *,
        data_folder: str = DATA_FOLDER_NAME,
        filename: str = "database.json",
        clock: Callable[[], str] = _current_timestamp,
    ) -> None:
        self.root = root
        self.data_dir = self.root / data_folder
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.file_path = self.data_dir / filename
        self._clock = clock
        self._lock = Lock()
        self._state: Dict[str, MetadataEntry ] = self._load_state()
        self._persist()

    def _load_state(self) -> Dict[str,MetadataEntry]:
        """Read ``database.json`` if available, otherwise return an empty map."""

        try:
            raw = self.file_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return {}

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return {}

        if not isinstance(data, dict):
            return {}

        cleaned: Dict[str,MetadataEntry] = {}
        for key, value in data.items():
            if isinstance(key, str) and isinstance(value, dict):
                try:
                    cleaned[key] = MetadataEntry(**value)
                except Exception:
                    pass
        return cleaned

    def _persist(self) -> None:
        """Write the in-memory catalogue to disk using an atomic replace."""

        payload = json.dumps({
            k:v.model_dump() for k,v in self._state.items()
        }, indent=2, sort_keys=True)
        tmp_path = self.file_path.with_suffix(".tmp")
        tmp_path.write_text(payload, encoding="utf-8")
        tmp_path.replace(self.file_path)

    def sync_with_files(self, files: MutableMapping[str, Path]) -> None:
        """Reconcile the catalogue with the supplied ``files`` mapping.

        The mapping must use POSIX-style relative paths as keys and absolute
        ``Path`` objects as values.  Missing documents are removed from the
        catalogue while new or modified documents are re-read and indexed.
        """

        with self._lock:
            normalized_files: Dict[str, Path] = {
                Path(relative).as_posix(): absolute for relative, absolute in files.items()
            }
            existing_keys = set(self._state.keys())
            incoming_keys = set(normalized_files.keys())

            for obsolete in existing_keys - incoming_keys:
                self._state.pop(obsolete, None)

            for relative_posix, absolute_path in normalized_files.items():
                content = read_text_file(absolute_path)
                prior_entry = self._state.get(relative_posix)
                if prior_entry:
                    tags = normalize_tags(prior_entry.tags)
                else:
                    tags=[]
                self._state[relative_posix] = self._build_entry(
                    relative_posix,
                    content,
                    tags=tags,
                )

            self._persist()

    def update_document(
        self,
        relative_path: str,
        content: str,
        *,
        tags: Optional[Iterable[str]] = None,
        clear_tags: bool = False,
    ) -> None:
        """Update or insert metadata for ``relative_path`` using ``content``.

        Parameters
        ----------
        relative_path:
            POSIX-style path relative to the knowledge base root.
        content:
            Current UTF-8 text of the document.
        tags:
            Optional iterable of tags that should persist regardless of the
            document contents. When omitted, the previously stored explicit tags
            (if any) are reused.
        clear_tags:
            If True, the explicit tag list is cleared and replaced with the supplied tags instead of being extended.
        """

        relative_posix = Path(relative_path).as_posix()

        with self._lock:
            
            if clear_tags and tags is not None:
                resolved_explicit = normalize_tags(tags)
            else:
                prior_entry = self._state.get(relative_posix)
                if prior_entry:
                    resolved_explicit = normalize_tags(prior_entry.tags + tags if tags is not None else [])
                else:
                    resolved_explicit = normalize_tags(tags or [])
            
            entry = self._build_entry(
                relative_posix,
                content,
                tags=resolved_explicit,
            )
            self._state[relative_posix] = entry
            self._persist()

    def remove_document(self, relative_path: str) -> None:
        """Remove metadata associated with ``relative_path`` if present."""

        relative_posix = Path(relative_path).as_posix()
        with self._lock:
            if relative_posix in self._state:
                self._state.pop(relative_posix, None)
                self._persist()

    def get_entry(self, relative_path: str) -> Optional[MetadataEntry]:
        """Return a shallow copy of the metadata entry for ``relative_path``."""

        relative_posix = Path(relative_path).as_posix()
        with self._lock:
            entry = self._state.get(relative_posix)
            return entry

    def all_tags(self) -> List[str]:
        """Return a sorted list of every tag referenced in the catalogue.

        The helper merges both derived ``tags`` and ``tags`` to ensure
        consumers see the complete label set without worrying about how tags
        were produced. Duplicates and blank values are discarded during
        aggregation.
        """

        with self._lock:
            combined: set[str] = set()
            for entry in self._state.values():
                for tag in entry.tags:
                    cleaned = str(tag).strip()
                    if cleaned:
                        combined.add(cleaned)
        return sorted(combined)

    def find_files_by_tags(
        self,
        tags: Sequence[str],
        *,
        match_mode: Literal["any", "all"] = "any",
    ) -> List[TagMatchResult]:
        """Return metadata rows for files matching ``tags`` under the requested rule.

        Parameters
        ----------
        tags:
            Sequence of tag labels to match. Values are trimmed and deduplicated.
        match_mode:
            ``"any"`` returns files that contain at least one of the supplied tags.
            ``"all"`` returns only the files containing every supplied tag.

        Returns
        -------
        List[TagMatchResult]
            Each dictionary contains ``path``, ``matched_tags``, ``match_count``,
            ``all_tags`` and ``tags`` describing the document.
        """

        if match_mode not in ("any", "all"):
            raise ValueError("match_mode must be 'any' or 'all'")

        query = normalize_tags(tags)
        if not query:
            raise ValueError("tags must contain at least one value")

        query_lower = {tag.lower(): tag for tag in query}
        results: List[TagMatchResult] = []

        with self._lock:
            for path, entry in self._state.items():
                entry_tags = normalize_tags(entry.tags)
                matched_keys = [
                    key for key in entry_tags
                    if key in query_lower
                ]

                if match_mode == "all":
                    if len(matched_keys) != len(query_lower):
                        continue
                elif match_mode == "any":
                    if not matched_keys:
                        continue

                matched_tags = sorted(matched_keys)
                results.append(
                    TagMatchResult(
                        path=path,
                        matched_tags=matched_tags,
                        match_count=len(matched_tags),
                        all_tags=entry_tags,
                        tags=entry_tags,
                    )
                )

        if match_mode == "any":
            results.sort(key=lambda item: (-item.match_count, item.path))
        else:
            results.sort(key=lambda item: item.path)
        return results

    def _build_entry(
        self,
        relative_path: str,
        content: str,
        *,
        tags: Optional[Iterable[str]] = None,
    ) -> MetadataEntry:
        """Construct a :class:`MetadataEntry` for ``relative_path``."""

        explicit = normalize_tags(tags or [])  
        line_count = len(content.splitlines())
        checksum = sha256(content.encode("utf-8")).hexdigest()
        title = _first_heading(content)
        updated_at = self._clock()

        return MetadataEntry(
            length=len(content),
            tags=explicit,
            line_count=line_count,
            word_count=_word_count(content),
            checksum=checksum,
            title=title,
            updated_at=updated_at,
        )
