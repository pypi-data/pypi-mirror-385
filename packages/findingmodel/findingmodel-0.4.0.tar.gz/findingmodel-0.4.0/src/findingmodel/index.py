"""DuckDB-backed implementation of the finding model index."""

from __future__ import annotations

import hashlib
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from types import TracebackType

import duckdb
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from findingmodel import logger
from findingmodel.common import normalize_name
from findingmodel.config import settings
from findingmodel.contributor import Organization, Person
from findingmodel.finding_model import FindingModelFull
from findingmodel.tools.duckdb_utils import (
    batch_embeddings_for_duckdb,
    create_fts_index,
    create_hnsw_index,
    drop_search_indexes,
    get_embedding_for_duckdb,
    l2_to_cosine_similarity,
    normalize_scores,
    rrf_fusion,
    setup_duckdb_connection,
)

DEFAULT_CONTRIBUTOR_ROLE = "contributor"


class AttributeInfo(BaseModel):
    """Represents basic information about an attribute in a finding model."""

    attribute_id: str
    name: str
    type: str


class IndexEntry(BaseModel):
    """Represents an entry in the index with key metadata about a finding model."""

    oifm_id: str
    name: str
    slug_name: str
    filename: str
    file_hash_sha256: str
    description: str | None = None
    synonyms: list[str] | None = None
    tags: list[str] | None = None
    contributors: list[str] | None = None
    attributes: list[AttributeInfo] = Field(default_factory=list, min_length=1)

    def match(self, identifier: str) -> bool:
        """Check if the identifier matches the ID, name, or synonyms."""

        if self.oifm_id == identifier:
            return True
        if self.name.casefold() == identifier.casefold():
            return True
        return bool(self.synonyms and any(s.casefold() == identifier.casefold() for s in self.synonyms))


class IndexReturnType(StrEnum):
    """Indicates whether an entry was added, updated, or unchanged."""

    ADDED = "added"
    UPDATED = "updated"
    UNCHANGED = "unchanged"


@dataclass(slots=True)
class _BatchPayload:
    model_rows: list[tuple[object, ...]]
    synonym_rows: list[tuple[str, str]]
    tag_rows: list[tuple[str, str]]
    attribute_rows: list[tuple[str, str, str, str, str]]
    people_rows: list[tuple[str, str, str, str, str | None]]
    model_people_rows: list[tuple[str, str, str, int]]
    organization_rows: list[tuple[str, str, str | None]]
    model_organization_rows: list[tuple[str, str, str, int]]
    ids_to_delete: list[str]


@dataclass(slots=True)
class _RowData:
    model_rows: list[tuple[object, ...]]
    synonym_rows: list[tuple[str, str]]
    tag_rows: list[tuple[str, str]]
    attribute_rows: list[tuple[str, str, str, str, str]]
    people_rows: list[tuple[str, str, str, str, str | None]]
    model_people_rows: list[tuple[str, str, str, int]]
    organization_rows: list[tuple[str, str, str | None]]
    model_organization_rows: list[tuple[str, str, str, int]]


_SCHEMA_STATEMENTS: tuple[str, ...] = (
    """
    CREATE TABLE IF NOT EXISTS finding_models (
        oifm_id VARCHAR PRIMARY KEY,
        slug_name VARCHAR NOT NULL UNIQUE,
        name VARCHAR NOT NULL UNIQUE,
        filename VARCHAR NOT NULL UNIQUE,
        file_hash_sha256 VARCHAR NOT NULL,
        description TEXT,
        search_text TEXT NOT NULL,
        embedding FLOAT[512] NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS people (
        github_username VARCHAR PRIMARY KEY,
        name VARCHAR NOT NULL,
        email VARCHAR NOT NULL,
        organization_code VARCHAR,
        url VARCHAR,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS organizations (
        code VARCHAR PRIMARY KEY,
        name VARCHAR NOT NULL,
        url VARCHAR,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS model_people (
        oifm_id VARCHAR NOT NULL,
        person_id VARCHAR NOT NULL,
        role VARCHAR NOT NULL DEFAULT 'contributor',
        display_order INTEGER,
        PRIMARY KEY (oifm_id, person_id, role)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS model_organizations (
        oifm_id VARCHAR NOT NULL,
        organization_id VARCHAR NOT NULL,
        role VARCHAR NOT NULL DEFAULT 'contributor',
        display_order INTEGER,
        PRIMARY KEY (oifm_id, organization_id, role)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS synonyms (
        oifm_id VARCHAR NOT NULL,
        synonym VARCHAR NOT NULL,
        PRIMARY KEY (oifm_id, synonym)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS attributes (
        attribute_id VARCHAR PRIMARY KEY,
        oifm_id VARCHAR NOT NULL,
        model_name VARCHAR NOT NULL,
        attribute_name VARCHAR NOT NULL,
        attribute_type VARCHAR NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS tags (
        oifm_id VARCHAR NOT NULL,
        tag VARCHAR NOT NULL,
        PRIMARY KEY (oifm_id, tag)
    )
    """,
)


_INDEX_STATEMENTS: tuple[str, ...] = (
    "CREATE INDEX IF NOT EXISTS idx_finding_models_name ON finding_models(name)",
    "CREATE INDEX IF NOT EXISTS idx_finding_models_slug_name ON finding_models(slug_name)",
    "CREATE INDEX IF NOT EXISTS idx_finding_models_filename ON finding_models(filename)",
    "CREATE INDEX IF NOT EXISTS idx_synonyms_synonym ON synonyms(synonym)",
    "CREATE INDEX IF NOT EXISTS idx_synonyms_model ON synonyms(oifm_id)",
    "CREATE INDEX IF NOT EXISTS idx_tags_tag ON tags(tag)",
    "CREATE INDEX IF NOT EXISTS idx_tags_model ON tags(oifm_id)",
    "CREATE INDEX IF NOT EXISTS idx_model_people_model ON model_people(oifm_id)",
    "CREATE INDEX IF NOT EXISTS idx_model_people_person ON model_people(person_id)",
    "CREATE INDEX IF NOT EXISTS idx_model_orgs_model ON model_organizations(oifm_id)",
    "CREATE INDEX IF NOT EXISTS idx_model_orgs_org ON model_organizations(organization_id)",
    "CREATE INDEX IF NOT EXISTS idx_attributes_model ON attributes(oifm_id)",
    "CREATE INDEX IF NOT EXISTS idx_attributes_name ON attributes(attribute_name)",
)


class DuckDBIndex:
    """DuckDB-based index with read-only connections by default."""

    def __init__(self, db_path: str | Path | None = None, *, read_only: bool = True) -> None:
        if db_path:
            self.db_path = Path(db_path).expanduser()  # Honor explicit path
        else:
            # Use package data directory with optional download
            from findingmodel.config import ensure_db_file

            self.db_path = ensure_db_file(
                settings.duckdb_index_path,
                settings.remote_index_db_url,
                settings.remote_index_db_hash,
            )
        self.read_only = read_only
        self.conn: duckdb.DuckDBPyConnection | None = None
        self._openai_client: AsyncOpenAI | None = None

    async def setup(self) -> None:
        """Ensure the database exists, connection opened, and schema ready."""

        conn = self._ensure_connection()

        if self.read_only:
            return

        for statement in _SCHEMA_STATEMENTS:
            conn.execute(statement)
        for statement in _INDEX_STATEMENTS:
            conn.execute(statement)
        self._create_search_indexes(conn)

        # Load base contributors if tables are empty
        self._load_base_contributors(conn)

    async def __aenter__(self) -> DuckDBIndex:
        """Enter async context manager, ensuring a connection is available."""

        self._ensure_connection()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Close the database connection when leaving the context."""

        if self.conn is not None:
            self.conn.close()
            self.conn = None

    async def contains(self, identifier: str) -> bool:
        """Return True if an ID, name, or synonym exists in the index."""

        conn = self._ensure_connection()
        return self._resolve_oifm_id(conn, identifier) is not None

    async def get(self, identifier: str) -> IndexEntry | None:
        """Retrieve an index entry by ID, name, or synonym."""

        conn = self._ensure_connection()
        oifm_id = self._resolve_oifm_id(conn, identifier)
        if oifm_id is None:
            return None
        return self._fetch_index_entry(conn, oifm_id)

    async def count(self) -> int:
        """Return the number of finding models in the index."""

        conn = self._ensure_connection()
        row = conn.execute("SELECT COUNT(*) FROM finding_models").fetchone()
        return int(row[0]) if row else 0

    async def count_people(self) -> int:
        """Return the number of people in the normalized table."""

        conn = self._ensure_connection()
        row = conn.execute("SELECT COUNT(*) FROM people").fetchone()
        return int(row[0]) if row else 0

    async def count_organizations(self) -> int:
        """Return the number of organizations in the normalized table."""

        conn = self._ensure_connection()
        row = conn.execute("SELECT COUNT(*) FROM organizations").fetchone()
        return int(row[0]) if row else 0

    async def get_person(self, github_username: str) -> Person | None:
        """Retrieve a person by GitHub username."""

        conn = self._ensure_connection()
        row = conn.execute(
            """
            SELECT github_username, name, email, organization_code, url
            FROM people
            WHERE github_username = ?
            """,
            (github_username,),
        ).fetchone()
        if row is None:
            return None
        return Person.model_validate({
            "github_username": row[0],
            "name": row[1],
            "email": row[2],
            "organization_code": row[3],
            "url": row[4],
        })

    async def get_organization(self, code: str) -> Organization | None:
        """Retrieve an organization by code."""

        conn = self._ensure_connection()
        row = conn.execute(
            """
            SELECT code, name, url
            FROM organizations
            WHERE code = ?
            """,
            (code,),
        ).fetchone()
        if row is None:
            return None
        return Organization.model_validate({"code": row[0], "name": row[1], "url": row[2]})

    async def get_people(self) -> list[Person]:
        """Retrieve all people from the index."""
        conn = self._ensure_connection()
        rows = conn.execute(
            """
            SELECT github_username, name, email, organization_code, url
            FROM people
            ORDER BY name
            """
        ).fetchall()
        return [
            Person.model_validate({
                "github_username": row[0],
                "name": row[1],
                "email": row[2],
                "organization_code": row[3],
                "url": row[4],
            })
            for row in rows
        ]

    async def get_organizations(self) -> list[Organization]:
        """Retrieve all organizations from the index."""
        conn = self._ensure_connection()
        rows = conn.execute(
            """
            SELECT code, name, url
            FROM organizations
            ORDER BY name
            """
        ).fetchall()
        return [
            Organization.model_validate({"code": row[0], "name": row[1], "url": row[2]})
            for row in rows
        ]

    async def add_or_update_entry_from_file(
        self,
        filename: str | Path,
        model: FindingModelFull | None = None,
        *,
        allow_duplicate_synonyms: bool = False,
    ) -> IndexReturnType:
        """Insert or update a finding model from a `.fm.json` file."""

        conn = self._ensure_writable_connection()
        await self.setup()

        file_path = filename if isinstance(filename, Path) else Path(filename)
        if not file_path.name.endswith(".fm.json"):
            raise ValueError("Expect filename to end with '.fm.json'")

        file_hash = self._calculate_file_hash(file_path)
        if model is None:
            model = FindingModelFull.model_validate_json(file_path.read_text())

        existing_rows = conn.execute(
            """
            SELECT oifm_id, file_hash_sha256
            FROM finding_models
            WHERE oifm_id = ? OR filename = ?
            """,
            (model.oifm_id, file_path.name),
        ).fetchall()
        existing = existing_rows[0] if existing_rows else None

        status = IndexReturnType.ADDED
        if existing is not None:
            status = IndexReturnType.UPDATED
            if existing[1] == file_hash and existing[0] == model.oifm_id:
                return IndexReturnType.UNCHANGED

        # Only validate for new models or when OIFM ID changes
        # (updating same model with same ID shouldn't fail validation)
        if existing is None or existing[0] != model.oifm_id:
            validation_errors = [] if allow_duplicate_synonyms else self._validate_model(model)
            if validation_errors:
                raise ValueError(f"Model validation failed: {'; '.join(validation_errors)}")
        else:
            validation_errors = []

        embedding_payload = self._build_embedding_text(model)
        embedding = await get_embedding_for_duckdb(
            embedding_payload,
            client=await self._ensure_openai_client(),
        )
        if embedding is None:
            raise RuntimeError("Failed to generate embedding for finding model")

        search_text = self._build_search_text(model)
        slug_name = normalize_name(model.name)

        conn.execute("BEGIN TRANSACTION")
        try:
            self._drop_search_indexes(conn)
            self._delete_denormalized_records(conn, [row[0] for row in existing_rows])
            conn.execute(
                "DELETE FROM finding_models WHERE oifm_id = ? OR filename = ?",
                (model.oifm_id, file_path.name),
            )

            conn.execute(
                """
                INSERT INTO finding_models (
                    oifm_id,
                    slug_name,
                    name,
                    filename,
                    file_hash_sha256,
                    description,
                    search_text,
                    embedding
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    model.oifm_id,
                    slug_name,
                    model.name,
                    file_path.name,
                    file_hash,
                    model.description,
                    search_text,
                    embedding,
                ),
            )

            self._upsert_contributors(conn, model)
            self._replace_synonyms(conn, model.oifm_id, model.synonyms)
            self._replace_tags(conn, model.oifm_id, model.tags)
            self._replace_attributes(conn, model)

            conn.execute("COMMIT")
        except Exception:  # pragma: no cover - rollback path
            conn.execute("ROLLBACK")
            self._create_search_indexes(conn)
            raise

        self._create_search_indexes(conn)

        return status

    def _collect_directory_files(self, directory: Path) -> list[tuple[str, str, Path]]:
        files: list[tuple[str, str, Path]] = []
        for file_path in sorted(directory.glob("*.fm.json")):
            file_hash = self._calculate_file_hash(file_path)
            files.append((file_path.name, file_hash, file_path))
        return files

    def _stage_directory_files(self, conn: duckdb.DuckDBPyConnection, files: Sequence[tuple[str, str, Path]]) -> None:
        if not files:
            return

        values_clause = ", ".join(["(?, ?)"] * len(files))
        params: list[str] = []
        for filename, file_hash, _ in files:
            params.extend([filename, file_hash])
        conn.execute(f"INSERT INTO tmp_directory_files VALUES {values_clause}", params)

    def _classify_directory_changes(
        self,
        conn: duckdb.DuckDBPyConnection,
    ) -> tuple[set[str], dict[str, str], set[str]]:
        rows = conn.execute(
            """
            SELECT
                dir.filename AS directory_filename,
                dir.file_hash_sha256 AS directory_hash,
                fm.oifm_id AS index_oifm_id,
                fm.filename AS index_filename,
                fm.file_hash_sha256 AS index_hash
            FROM tmp_directory_files AS dir
            FULL OUTER JOIN finding_models AS fm
              ON dir.filename = fm.filename
            """
        ).fetchall()

        added_filenames: set[str] = set()
        updated_entries: dict[str, str] = {}
        removed_ids: set[str] = set()

        for dir_filename, dir_hash, index_oifm_id, index_filename, index_hash in rows:
            if dir_filename is not None and index_filename is None:
                added_filenames.add(str(dir_filename))
            elif dir_filename is not None and index_filename is not None:
                if dir_hash != index_hash and index_oifm_id is not None:
                    updated_entries[str(dir_filename)] = str(index_oifm_id)
            elif index_filename is not None and index_oifm_id is not None:
                removed_ids.add(str(index_oifm_id))

        return added_filenames, updated_entries, removed_ids

    async def _prepare_batch_payload(
        self,
        filenames_to_process: Sequence[str],
        files_by_name: Mapping[str, tuple[str, Path]],
        updated_entries: Mapping[str, str],
        removed_ids: Iterable[str],
        *,
        allow_duplicate_synonyms: bool = False,
    ) -> _BatchPayload:
        metadata, embedding_payloads = self._load_models_metadata(
            filenames_to_process,
            files_by_name,
            updated_entries,
            allow_duplicate_synonyms=allow_duplicate_synonyms,
        )
        embeddings = await self._generate_embeddings(embedding_payloads)
        row_data = self._build_row_data(metadata, embeddings)

        ids_to_delete_set = set(removed_ids)
        ids_to_delete_set.update(
            updated_entries[filename]
            for filename in filenames_to_process
            if filename in updated_entries and updated_entries[filename] is not None
        )

        return _BatchPayload(
            model_rows=row_data.model_rows,
            synonym_rows=row_data.synonym_rows,
            tag_rows=row_data.tag_rows,
            attribute_rows=row_data.attribute_rows,
            people_rows=row_data.people_rows,
            model_people_rows=row_data.model_people_rows,
            organization_rows=row_data.organization_rows,
            model_organization_rows=row_data.model_organization_rows,
            ids_to_delete=sorted(ids_to_delete_set),
        )

    def _execute_batch_directory_update(
        self,
        conn: duckdb.DuckDBPyConnection,
        payload: _BatchPayload,
        progress_callback: Callable[[str], None] | None = None,
    ) -> None:
        if not payload.ids_to_delete and not payload.model_rows:
            return

        if progress_callback:
            progress_callback("Dropping search indexes...")

        indexes_dropped = False
        conn.execute("BEGIN TRANSACTION")
        try:
            self._drop_search_indexes(conn)
            indexes_dropped = True

            # Delete old entries first if needed
            if payload.ids_to_delete:
                self._delete_old_entries(conn, payload.ids_to_delete, progress_callback)

            # Insert new/updated entries
            self._insert_models_with_progress(conn, payload, progress_callback)

            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            if indexes_dropped:
                self._create_search_indexes(conn)
            raise

        if progress_callback:
            progress_callback("Rebuilding search indexes...")
        self._create_search_indexes(conn)

    def _delete_old_entries(
        self,
        conn: duckdb.DuckDBPyConnection,
        ids_to_delete: list[str],
        progress_callback: Callable[[str], None] | None,
    ) -> None:
        """Delete old entries from all tables."""
        if progress_callback:
            progress_callback(f"Removing {len(ids_to_delete)} old entries...")
        self._delete_denormalized_records(conn, ids_to_delete)
        placeholders = ", ".join(["?"] * len(ids_to_delete))
        conn.execute(
            f"DELETE FROM finding_models WHERE oifm_id IN ({placeholders})",
            ids_to_delete,
        )

    def _insert_models_with_progress(
        self,
        conn: duckdb.DuckDBPyConnection,
        payload: _BatchPayload,
        progress_callback: Callable[[str], None] | None,
    ) -> None:
        """Insert models with progress updates for large batches."""
        total_models = len(payload.model_rows)
        chunk_size = 500

        if total_models > chunk_size:
            if progress_callback:
                progress_callback(f"Processing {total_models} models in chunks of {chunk_size}...")

            # Process in chunks
            for chunk_start in range(0, total_models, chunk_size):
                chunk_end = min(chunk_start + chunk_size, total_models)
                chunk_num = (chunk_start // chunk_size) + 1
                total_chunks = (total_models + chunk_size - 1) // chunk_size

                if progress_callback:
                    progress_callback(
                        f"Writing chunk {chunk_num}/{total_chunks} ({chunk_end}/{total_models} models)..."
                    )

                chunk_payload = self._create_chunk_payload(payload, chunk_start, chunk_end)
                self._apply_batch_mutations(conn, chunk_payload)
        else:
            if progress_callback:
                progress_callback(f"Writing {total_models} models to database...")
            # Create payload without deletions (already done in _delete_old_entries)
            no_delete_payload = _BatchPayload(
                model_rows=payload.model_rows,
                synonym_rows=payload.synonym_rows,
                tag_rows=payload.tag_rows,
                attribute_rows=payload.attribute_rows,
                people_rows=payload.people_rows,
                model_people_rows=payload.model_people_rows,
                organization_rows=payload.organization_rows,
                model_organization_rows=payload.model_organization_rows,
                ids_to_delete=[],
            )
            self._apply_batch_mutations(conn, no_delete_payload)

    def _create_chunk_payload(
        self,
        payload: _BatchPayload,
        start_idx: int,
        end_idx: int,
    ) -> _BatchPayload:
        """Create a chunk of the payload for batch processing."""
        # Get the oifm_ids in this chunk
        chunk_model_rows = payload.model_rows[start_idx:end_idx]
        chunk_oifm_ids = {row[0] for row in chunk_model_rows}  # oifm_id is first element

        # Filter all related rows to only those in this chunk
        chunk_synonym_rows = [row for row in payload.synonym_rows if row[0] in chunk_oifm_ids]
        chunk_tag_rows = [row for row in payload.tag_rows if row[0] in chunk_oifm_ids]
        chunk_attribute_rows = [
            row for row in payload.attribute_rows if row[1] in chunk_oifm_ids
        ]  # oifm_id is second element
        chunk_model_people_rows = [row for row in payload.model_people_rows if row[0] in chunk_oifm_ids]
        chunk_model_organization_rows = [row for row in payload.model_organization_rows if row[0] in chunk_oifm_ids]

        # For people and organizations, we need to include all that are referenced
        # (even if they're not in this chunk, to avoid conflicts)

        return _BatchPayload(
            model_rows=chunk_model_rows,
            synonym_rows=chunk_synonym_rows,
            tag_rows=chunk_tag_rows,
            attribute_rows=chunk_attribute_rows,
            people_rows=payload.people_rows,  # Include all people (upsert handles duplicates)
            model_people_rows=chunk_model_people_rows,
            organization_rows=payload.organization_rows,  # Include all organizations
            model_organization_rows=chunk_model_organization_rows,
            ids_to_delete=[],  # Only delete in first chunk
        )

    def _load_models_metadata(
        self,
        filenames_to_process: Sequence[str],
        files_by_name: Mapping[str, tuple[str, Path]],
        updated_entries: Mapping[str, str],
        *,
        allow_duplicate_synonyms: bool = False,
    ) -> tuple[list[tuple[FindingModelFull, str, str, str]], list[str]]:
        metadata: list[tuple[FindingModelFull, str, str, str]] = []
        embedding_payloads: list[str] = []

        for filename in filenames_to_process:
            if filename not in files_by_name:
                raise FileNotFoundError(f"File {filename} not found during directory ingestion")
            file_hash, file_path = files_by_name[filename]
            model = FindingModelFull.model_validate_json(file_path.read_text())
            # Only validate new models (not updates of existing models)
            if filename not in updated_entries and not allow_duplicate_synonyms:
                validation_errors = self._validate_model(model)
                if validation_errors:
                    joined = "; ".join(validation_errors)
                    raise ValueError(f"Model validation failed for {filename}: {joined}")
            search_text = self._build_search_text(model)
            metadata.append((model, filename, file_hash, search_text))
            embedding_payloads.append(self._build_embedding_text(model))

        return metadata, embedding_payloads

    async def _generate_embeddings(self, embedding_payloads: Sequence[str]) -> list[list[float]]:
        if not embedding_payloads:
            return []

        client = await self._ensure_openai_client()
        raw_embeddings = await batch_embeddings_for_duckdb(embedding_payloads, client=client)

        embeddings: list[list[float]] = []
        for embedding in raw_embeddings:
            if embedding is None:
                raise RuntimeError("Failed to generate embeddings for one or more models")
            embeddings.append(embedding)
        return embeddings

    def _build_row_data(
        self,
        metadata: Sequence[tuple[FindingModelFull, str, str, str]],
        embeddings: Sequence[list[float]],
    ) -> _RowData:
        model_rows: list[tuple[object, ...]] = []
        synonym_rows: list[tuple[str, str]] = []
        tag_rows: list[tuple[str, str]] = []
        attribute_rows: list[tuple[str, str, str, str, str]] = []
        people_rows_dict: dict[str, tuple[str, str, str, str, str | None]] = {}
        model_people_rows: list[tuple[str, str, str, int]] = []
        organization_rows_dict: dict[str, tuple[str, str, str | None]] = {}
        model_organization_rows: list[tuple[str, str, str, int]] = []

        for (model, filename, file_hash, search_text), embedding in zip(metadata, embeddings, strict=True):
            model_rows.append((
                model.oifm_id,
                normalize_name(model.name),
                model.name,
                filename,
                file_hash,
                model.description,
                search_text,
                embedding,
            ))

            # Deduplicate to avoid PRIMARY KEY violations
            unique_synonyms = list(dict.fromkeys(model.synonyms or []))
            unique_tags = list(dict.fromkeys(model.tags or []))
            synonym_rows.extend((model.oifm_id, synonym) for synonym in unique_synonyms)
            tag_rows.extend((model.oifm_id, tag) for tag in unique_tags)
            attribute_rows.extend(
                (
                    attribute.oifma_id,
                    model.oifm_id,
                    model.name,
                    attribute.name,
                    str(attribute.type),
                )
                for attribute in model.attributes
            )

            for order, contributor in enumerate(model.contributors or []):
                if isinstance(contributor, Person):
                    people_rows_dict[contributor.github_username] = (
                        contributor.github_username,
                        contributor.name,
                        str(contributor.email),
                        contributor.organization_code,
                        str(contributor.url) if contributor.url else None,
                    )
                    model_people_rows.append((
                        model.oifm_id,
                        contributor.github_username,
                        DEFAULT_CONTRIBUTOR_ROLE,
                        order,
                    ))
                elif isinstance(contributor, Organization):
                    organization_rows_dict[contributor.code] = (
                        contributor.code,
                        contributor.name,
                        str(contributor.url) if contributor.url else None,
                    )
                    model_organization_rows.append((
                        model.oifm_id,
                        contributor.code,
                        DEFAULT_CONTRIBUTOR_ROLE,
                        order,
                    ))

        return _RowData(
            model_rows=model_rows,
            synonym_rows=synonym_rows,
            tag_rows=tag_rows,
            attribute_rows=attribute_rows,
            people_rows=list(people_rows_dict.values()),
            model_people_rows=model_people_rows,
            organization_rows=list(organization_rows_dict.values()),
            model_organization_rows=model_organization_rows,
        )

    def _apply_batch_mutations(self, conn: duckdb.DuckDBPyConnection, payload: _BatchPayload) -> None:
        if payload.ids_to_delete:
            self._delete_denormalized_records(conn, payload.ids_to_delete)
            placeholders = ", ".join(["?"] * len(payload.ids_to_delete))
            conn.execute(
                f"DELETE FROM finding_models WHERE oifm_id IN ({placeholders})",
                payload.ids_to_delete,
            )
            logger.debug(
                "Deleted {} existing models during batch apply: {}",
                len(payload.ids_to_delete),
                sorted(payload.ids_to_delete),
            )

        statements: list[tuple[str, str, str, Sequence[tuple[object, ...]]]] = [
            (
                "finding_models",
                "inserted",
                """
                INSERT INTO finding_models (
                    oifm_id,
                    slug_name,
                    name,
                    filename,
                    file_hash_sha256,
                    description,
                    search_text,
                    embedding
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                payload.model_rows,
            ),
            (
                "synonyms",
                "inserted",
                "INSERT INTO synonyms (oifm_id, synonym) VALUES (?, ?)",
                payload.synonym_rows,
            ),
            (
                "tags",
                "inserted",
                "INSERT INTO tags (oifm_id, tag) VALUES (?, ?)",
                payload.tag_rows,
            ),
            (
                "attributes",
                "inserted",
                """
                INSERT INTO attributes (
                    attribute_id,
                    oifm_id,
                    model_name,
                    attribute_name,
                    attribute_type
                ) VALUES (?, ?, ?, ?, ?)
                """,
                payload.attribute_rows,
            ),
            (
                "people",
                "upserted",
                """
                INSERT INTO people (
                    github_username,
                    name,
                    email,
                    organization_code,
                    url
                ) VALUES (?, ?, ?, ?, ?)
                ON CONFLICT (github_username) DO UPDATE SET
                    name = EXCLUDED.name,
                    email = EXCLUDED.email,
                    organization_code = EXCLUDED.organization_code,
                    url = EXCLUDED.url,
                    updated_at = now()
                """,
                payload.people_rows,
            ),
            (
                "model_people",
                "upserted",
                """
                INSERT INTO model_people (oifm_id, person_id, role, display_order)
                VALUES (?, ?, ?, ?)
                ON CONFLICT (oifm_id, person_id, role) DO UPDATE SET display_order = EXCLUDED.display_order
                """,
                payload.model_people_rows,
            ),
            (
                "organizations",
                "upserted",
                """
                INSERT INTO organizations (
                    code,
                    name,
                    url
                ) VALUES (?, ?, ?)
                ON CONFLICT (code) DO UPDATE SET
                    name = EXCLUDED.name,
                    url = EXCLUDED.url,
                    updated_at = now()
                """,
                payload.organization_rows,
            ),
            (
                "model_organizations",
                "upserted",
                """
                INSERT INTO model_organizations (oifm_id, organization_id, role, display_order)
                VALUES (?, ?, ?, ?)
                ON CONFLICT (oifm_id, organization_id, role) DO UPDATE SET display_order = EXCLUDED.display_order
                """,
                payload.model_organization_rows,
            ),
        ]

        for table_name, action, statement, rows in statements:
            if rows:
                conn.executemany(statement, rows)
                logger.debug(
                    "Batch {} {} rows in {}",
                    action,
                    len(rows),
                    table_name,
                )

    async def update_from_directory(
        self,
        directory: str | Path,
        *,
        allow_duplicate_synonyms: bool = False,
        progress_callback: Callable[[str], None] | None = None,
    ) -> dict[str, int]:
        """Batch-update the index to match the contents of a directory.

        Args:
            directory: Path to directory containing .fm.json files
            allow_duplicate_synonyms: Allow models with duplicate synonyms
            progress_callback: Optional callback for progress updates (receives status messages)
        """

        directory_path = Path(directory).expanduser()
        if not directory_path.is_dir():
            raise ValueError(f"{directory_path} is not a valid directory.")

        if progress_callback:
            progress_callback("Scanning directory for .fm.json files...")
        files = self._collect_directory_files(directory_path)
        logger.info(
            "Refreshing DuckDB index from {} ({} files)",
            directory_path,
            len(files),
        )

        conn = self._ensure_writable_connection()
        await self.setup()

        conn.execute("DROP TABLE IF EXISTS tmp_directory_files")
        conn.execute("CREATE TEMP TABLE tmp_directory_files(filename TEXT, file_hash_sha256 TEXT)")

        try:
            if progress_callback:
                progress_callback(f"Analyzing {len(files)} files...")
            self._stage_directory_files(conn, files)
            added_filenames, updated_entries, removed_ids = self._classify_directory_changes(conn)
            logger.debug(
                "Directory diff computed for {}: added={} updated={} removed={}",
                directory_path,
                len(added_filenames),
                len(updated_entries),
                len(removed_ids),
            )
            if not added_filenames and not updated_entries and not removed_ids:
                logger.info("DuckDB index already in sync with {}", directory_path)
                if progress_callback:
                    progress_callback("Index already up to date")
                return {"added": 0, "updated": 0, "removed": 0}

            files_by_name = {filename: (file_hash, path) for filename, file_hash, path in files}
            filenames_to_process = sorted(added_filenames | set(updated_entries.keys()))

            if progress_callback:
                total = len(filenames_to_process)
                progress_callback(f"Processing {total} models (loading and generating embeddings)...")

            payload = await self._prepare_batch_payload(
                filenames_to_process,
                files_by_name,
                updated_entries,
                removed_ids,
                allow_duplicate_synonyms=allow_duplicate_synonyms,
            )

            self._execute_batch_directory_update(conn, payload, progress_callback)

            if progress_callback:
                progress_callback(
                    f"Complete: {len(added_filenames)} added, {len(updated_entries)} updated, {len(removed_ids)} removed"
                )

            logger.info(
                "DuckDB index refreshed: added={} updated={} removed={}",
                len(added_filenames),
                len(updated_entries),
                len(removed_ids),
            )
            return {
                "added": len(added_filenames),
                "updated": len(updated_entries),
                "removed": len(removed_ids),
            }
        except Exception:
            logger.exception("Failed to refresh DuckDB index from {}", directory_path)
            raise
        finally:
            conn.execute("DROP TABLE IF EXISTS tmp_directory_files")

    async def remove_entry(self, oifm_id: str) -> bool:
        """Remove a finding model by ID."""

        conn = self._ensure_writable_connection()
        await self.setup()

        conn.execute("BEGIN TRANSACTION")
        try:
            self._drop_search_indexes(conn)
            self._delete_denormalized_records(conn, [oifm_id])
            deleted = conn.execute(
                "DELETE FROM finding_models WHERE oifm_id = ? RETURNING oifm_id",
                (oifm_id,),
            ).fetchone()
            conn.execute("COMMIT")
        except Exception:  # pragma: no cover - rollback path
            conn.execute("ROLLBACK")
            self._create_search_indexes(conn)
            raise
        self._create_search_indexes(conn)
        return deleted is not None

    async def search(
        self,
        query: str,
        *,
        limit: int = 10,
        tags: Sequence[str] | None = None,
    ) -> list[IndexEntry]:
        """Search for finding models using hybrid search with RRF fusion.

        Uses Reciprocal Rank Fusion to combine FTS and semantic search results,
        returning exact matches immediately if found.

        Args:
            query: Search query string
            limit: Maximum number of results to return
            tags: Optional list of tags - models must have ALL specified tags
        """
        conn = self._ensure_connection()

        # Exact matches take priority - return immediately if found
        exact_matches = self._search_exact(conn, query, tags=tags)
        if exact_matches:
            return exact_matches[:limit]

        # Get both FTS and semantic results
        fts_matches = self._search_fts(conn, query, limit=limit, tags=tags)
        semantic_matches = await self._search_semantic(conn, query, limit=limit, tags=tags)

        # If no vector results, just return FTS results
        if not semantic_matches:
            return [entry for entry, _ in fts_matches[:limit]]

        # Apply RRF fusion
        fts_scores = [(entry.oifm_id, score) for entry, score in fts_matches]
        semantic_scores = [(entry.oifm_id, score) for entry, score in semantic_matches]
        fused_scores = rrf_fusion(fts_scores, semantic_scores)

        # Build result lookup by oifm_id
        entry_map: dict[str, IndexEntry] = {}
        for entry, _ in fts_matches + semantic_matches:
            if entry.oifm_id not in entry_map:
                entry_map[entry.oifm_id] = entry

        # Return entries in RRF-ranked order
        results: list[IndexEntry] = []
        for oifm_id, _ in fused_scores[:limit]:
            if oifm_id in entry_map:
                results.append(entry_map[oifm_id])

        return results

    async def search_batch(self, queries: list[str], *, limit: int = 10) -> dict[str, list[IndexEntry]]:
        """Search multiple queries efficiently with single embedding call and RRF fusion.

        Embeds ALL queries in a single OpenAI API call for efficiency,
        then performs hybrid search with RRF fusion for each query.

        Args:
            queries: List of search query strings
            limit: Maximum number of results per query

        Returns:
            Dictionary mapping each query string to its list of results
        """
        if not queries:
            return {}

        conn = self._ensure_connection()
        client = await self._ensure_openai_client()

        # Generate embeddings for all queries in a single batch API call
        embeddings = await batch_embeddings_for_duckdb(queries, client=client)

        results: dict[str, list[IndexEntry]] = {}
        for query, embedding in zip(queries, embeddings, strict=True):
            # Check for exact match first
            exact_matches = self._search_exact(conn, query, tags=None)
            if exact_matches:
                results[query] = exact_matches[:limit]
                continue

            # Perform FTS search
            fts_matches = self._search_fts(conn, query, limit=limit, tags=None)

            # Perform semantic search using pre-generated embedding
            semantic_matches: list[tuple[IndexEntry, float]] = []
            if embedding is not None:
                semantic_matches = self._search_semantic_with_embedding(conn, embedding, limit=limit, tags=None)

            # If no vector results, just return FTS results
            if not semantic_matches:
                results[query] = [entry for entry, _ in fts_matches[:limit]]
                continue

            # Apply RRF fusion
            fts_scores = [(entry.oifm_id, score) for entry, score in fts_matches]
            semantic_scores = [(entry.oifm_id, score) for entry, score in semantic_matches]
            fused_scores = rrf_fusion(fts_scores, semantic_scores)

            # Build result lookup by oifm_id
            entry_map: dict[str, IndexEntry] = {}
            for entry, _ in fts_matches + semantic_matches:
                if entry.oifm_id not in entry_map:
                    entry_map[entry.oifm_id] = entry

            # Return entries in RRF-ranked order
            query_results: list[IndexEntry] = []
            for oifm_id, _ in fused_scores[:limit]:
                if oifm_id in entry_map:
                    query_results.append(entry_map[oifm_id])

            results[query] = query_results

        return results

    def _ensure_connection(self) -> duckdb.DuckDBPyConnection:
        if self.conn is None:
            if not self.read_only:
                self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self.conn = setup_duckdb_connection(self.db_path, read_only=self.read_only)
        return self.conn

    def _ensure_writable_connection(self) -> duckdb.DuckDBPyConnection:
        if self.read_only:
            raise RuntimeError("DuckDBIndex is in read-only mode; write operation not permitted")
        return self._ensure_connection()

    async def _ensure_openai_client(self) -> AsyncOpenAI:
        if self._openai_client is None:
            settings.check_ready_for_openai()
            self._openai_client = AsyncOpenAI(api_key=settings.openai_api_key.get_secret_value())
        return self._openai_client

    def _fetch_index_entry(self, conn: duckdb.DuckDBPyConnection, oifm_id: str) -> IndexEntry | None:
        row = conn.execute(
            """
            SELECT oifm_id, name, slug_name, filename, file_hash_sha256, description
            FROM finding_models
            WHERE oifm_id = ?
            """,
            (oifm_id,),
        ).fetchone()
        if row is None:
            return None

        synonyms = [
            r[0]
            for r in conn.execute(
                "SELECT synonym FROM synonyms WHERE oifm_id = ? ORDER BY synonym", (oifm_id,)
            ).fetchall()
        ]
        tags = [
            r[0] for r in conn.execute("SELECT tag FROM tags WHERE oifm_id = ? ORDER BY tag", (oifm_id,)).fetchall()
        ]
        attribute_rows = conn.execute(
            """
            SELECT attribute_id, attribute_name, attribute_type
            FROM attributes
            WHERE oifm_id = ?
            ORDER BY attribute_name
            """,
            (oifm_id,),
        ).fetchall()
        attributes = [AttributeInfo(attribute_id=r[0], name=r[1], type=r[2]) for r in attribute_rows]

        contributors = self._collect_contributors(conn, oifm_id)

        return IndexEntry(
            oifm_id=row[0],
            name=row[1],
            slug_name=row[2],
            filename=row[3],
            file_hash_sha256=row[4],
            description=row[5],
            synonyms=synonyms or None,
            tags=tags or None,
            contributors=contributors or None,
            attributes=attributes,
        )

    def _collect_contributors(self, conn: duckdb.DuckDBPyConnection, oifm_id: str) -> list[str]:
        person_rows = conn.execute(
            "SELECT person_id, display_order FROM model_people WHERE oifm_id = ? ORDER BY display_order, person_id",
            (oifm_id,),
        ).fetchall()
        org_rows = conn.execute(
            "SELECT organization_id, display_order FROM model_organizations WHERE oifm_id = ? ORDER BY display_order, organization_id",
            (oifm_id,),
        ).fetchall()

        combined: list[tuple[int, str]] = []
        combined.extend((row[1] if row[1] is not None else idx, row[0]) for idx, row in enumerate(person_rows))
        base = len(combined)
        combined.extend((row[1] if row[1] is not None else base + idx, row[0]) for idx, row in enumerate(org_rows))
        combined.sort(key=lambda item: item[0])
        return [identifier for _, identifier in combined]

    def _resolve_oifm_id(self, conn: duckdb.DuckDBPyConnection, identifier: str) -> str | None:
        row = conn.execute("SELECT oifm_id FROM finding_models WHERE oifm_id = ?", (identifier,)).fetchone()
        if row is not None:
            return str(row[0])

        row = conn.execute(
            "SELECT oifm_id FROM finding_models WHERE LOWER(name) = LOWER(?)",
            (identifier,),
        ).fetchone()
        if row is not None:
            return str(row[0])

        slug = None
        if len(identifier) >= 3:
            try:
                slug = normalize_name(identifier)
            except (TypeError, ValueError):
                slug = None
        if slug:
            row = conn.execute(
                "SELECT oifm_id FROM finding_models WHERE slug_name = ?",
                (slug,),
            ).fetchone()
            if row is not None:
                return str(row[0])

        row = conn.execute(
            "SELECT oifm_id FROM synonyms WHERE LOWER(synonym) = LOWER(?) LIMIT 1",
            (identifier,),
        ).fetchone()
        if row is not None:
            return str(row[0])

        return None

    def _upsert_contributors(self, conn: duckdb.DuckDBPyConnection, model: FindingModelFull) -> None:
        contributors = list(model.contributors or [])
        for order, contributor in enumerate(contributors):
            if isinstance(contributor, Person):
                conn.execute(
                    """
                    INSERT INTO people (github_username, name, email, organization_code, url)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT (github_username) DO UPDATE SET
                        name = EXCLUDED.name,
                        email = EXCLUDED.email,
                        organization_code = EXCLUDED.organization_code,
                        url = EXCLUDED.url,
                        updated_at = now()
                    """,
                    (
                        contributor.github_username,
                        contributor.name,
                        str(contributor.email),
                        contributor.organization_code,
                        str(contributor.url) if contributor.url else None,
                    ),
                )
                conn.execute(
                    """
                    INSERT INTO model_people (oifm_id, person_id, role, display_order)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT (oifm_id, person_id, role) DO UPDATE SET display_order = EXCLUDED.display_order
                    """,
                    (model.oifm_id, contributor.github_username, DEFAULT_CONTRIBUTOR_ROLE, order),
                )
            elif isinstance(contributor, Organization):
                conn.execute(
                    """
                    INSERT INTO organizations (code, name, url)
                    VALUES (?, ?, ?)
                    ON CONFLICT (code) DO UPDATE SET
                        name = EXCLUDED.name,
                        url = EXCLUDED.url,
                        updated_at = now()
                    """,
                    (
                        contributor.code,
                        contributor.name,
                        str(contributor.url) if contributor.url else None,
                    ),
                )
                conn.execute(
                    """
                    INSERT INTO model_organizations (oifm_id, organization_id, role, display_order)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT (oifm_id, organization_id, role) DO UPDATE SET display_order = EXCLUDED.display_order
                    """,
                    (model.oifm_id, contributor.code, DEFAULT_CONTRIBUTOR_ROLE, order),
                )

    def _replace_synonyms(
        self,
        conn: duckdb.DuckDBPyConnection,
        oifm_id: str,
        synonyms: Sequence[str] | None,
    ) -> None:
        conn.execute("DELETE FROM synonyms WHERE oifm_id = ?", (oifm_id,))
        if synonyms:
            # Deduplicate synonyms to avoid PRIMARY KEY violations
            unique_synonyms = list(dict.fromkeys(synonyms))
            conn.executemany(
                "INSERT INTO synonyms (oifm_id, synonym) VALUES (?, ?)",
                [(oifm_id, synonym) for synonym in unique_synonyms],
            )

    def _replace_tags(
        self,
        conn: duckdb.DuckDBPyConnection,
        oifm_id: str,
        tags: Sequence[str] | None,
    ) -> None:
        conn.execute("DELETE FROM tags WHERE oifm_id = ?", (oifm_id,))
        if tags:
            # Deduplicate tags to avoid PRIMARY KEY violations
            unique_tags = list(dict.fromkeys(tags))
            conn.executemany(
                "INSERT INTO tags (oifm_id, tag) VALUES (?, ?)",
                [(oifm_id, tag) for tag in unique_tags],
            )

    def _replace_attributes(self, conn: duckdb.DuckDBPyConnection, model: FindingModelFull) -> None:
        conn.execute("DELETE FROM attributes WHERE oifm_id = ?", (model.oifm_id,))
        attribute_rows = [
            (
                attribute.oifma_id,
                model.oifm_id,
                model.name,
                attribute.name,
                str(attribute.type),
            )
            for attribute in model.attributes
        ]
        conn.executemany(
            """
            INSERT INTO attributes (
                attribute_id,
                oifm_id,
                model_name,
                attribute_name,
                attribute_type
            ) VALUES (?, ?, ?, ?, ?)
            """,
            attribute_rows,
        )

    def _build_search_text(self, model: FindingModelFull) -> str:
        parts: list[str] = [model.name]
        if model.description:
            parts.append(model.description)
        if model.synonyms:
            parts.extend(model.synonyms)
        if model.tags:
            parts.extend(model.tags)
        parts.extend(attribute.name for attribute in model.attributes)
        return "\n".join(part for part in parts if part)

    def _build_embedding_text(self, model: FindingModelFull) -> str:
        parts: list[str] = [model.name]
        if model.description:
            parts.append(model.description)
        if model.synonyms:
            parts.append("Synonyms: " + ", ".join(model.synonyms))
        if model.tags:
            parts.append("Tags: " + ", ".join(model.tags))
        attribute_lines = [
            f"Attribute {attribute.name}: {attribute.description or attribute.type}" for attribute in model.attributes
        ]
        parts.extend(attribute_lines)
        return "\n".join(part for part in parts if part)

    def _validate_model(self, model: FindingModelFull) -> list[str]:
        """Validate that a model can be added without conflicts.

        Checks for uniqueness of OIFM ID, name, slug_name, and attribute IDs.
        Returns a list of error messages (empty if valid).

        Args:
            model: The finding model to validate

        Returns:
            List of validation error messages (empty list means valid)
        """
        errors: list[str] = []
        conn = self._ensure_connection()

        # Check OIFM ID uniqueness
        row = conn.execute(
            "SELECT oifm_id FROM finding_models WHERE oifm_id = ?",
            (model.oifm_id,),
        ).fetchone()
        if row is not None:
            errors.append(f"OIFM ID '{model.oifm_id}' already exists")

        # Check name uniqueness (case-insensitive)
        row = conn.execute(
            "SELECT name FROM finding_models WHERE LOWER(name) = LOWER(?) AND oifm_id != ?",
            (model.name, model.oifm_id),
        ).fetchone()
        if row is not None:
            errors.append(f"Name '{model.name}' already in use")

        # Check slug_name uniqueness
        slug_name = normalize_name(model.name)
        row = conn.execute(
            "SELECT slug_name FROM finding_models WHERE slug_name = ? AND oifm_id != ?",
            (slug_name, model.oifm_id),
        ).fetchone()
        if row is not None:
            errors.append(f"Slug name '{slug_name}' already in use")

        # Check attribute ID conflicts (any attribute IDs already used by OTHER models)
        if model.attributes:
            attribute_ids = [attr.oifma_id for attr in model.attributes]
            if attribute_ids:
                placeholders = ", ".join("?" for _ in attribute_ids)
                conflicting_rows = conn.execute(
                    f"""
                    SELECT attribute_id, model_name
                    FROM attributes
                    WHERE attribute_id IN ({placeholders})
                      AND oifm_id != ?
                    """,
                    [*attribute_ids, model.oifm_id],
                ).fetchall()
                for attr_id, model_name in conflicting_rows:
                    errors.append(f"Attribute ID '{attr_id}' already used by model '{model_name}'")

        return errors

    def _calculate_file_hash(self, filename: Path) -> str:
        if not filename.exists() or not filename.is_file():
            raise FileNotFoundError(f"File {filename} not found")
        return hashlib.sha256(filename.read_bytes()).hexdigest()

    def _search_exact(
        self,
        conn: duckdb.DuckDBPyConnection,
        query: str,
        *,
        tags: Sequence[str] | None = None,
    ) -> list[IndexEntry]:
        oifm_id = self._resolve_oifm_id(conn, query)
        if oifm_id is None:
            return []

        entry = self._fetch_index_entry(conn, oifm_id)
        if entry is None:
            return []

        if tags and not self._entry_has_tags(entry, tags):
            return []

        return [entry]

    def _entry_has_tags(self, entry: IndexEntry, tags: Sequence[str]) -> bool:
        entry_tags = set(entry.tags or [])
        return all(tag in entry_tags for tag in tags)

    def _search_fts(
        self,
        conn: duckdb.DuckDBPyConnection,
        query: str,
        *,
        limit: int,
        tags: Sequence[str] | None = None,
    ) -> list[tuple[IndexEntry, float]]:
        rows = conn.execute(
            """
            WITH candidates AS (
                SELECT
                    f.oifm_id,
                    fts_main_finding_models.match_bm25(f.oifm_id, ?) AS bm25_score
                FROM finding_models AS f
            )
            SELECT oifm_id, bm25_score
            FROM candidates
            WHERE bm25_score IS NOT NULL
            ORDER BY bm25_score DESC
            LIMIT ?
            """,
            (query, limit * 3),
        ).fetchall()

        if not rows:
            return []

        entries: list[IndexEntry] = []
        scores: list[float] = []
        for oifm_id, score in rows:
            entry = self._fetch_index_entry(conn, str(oifm_id))
            if entry is None:
                continue
            if tags and not self._entry_has_tags(entry, tags):
                continue
            entries.append(entry)
            scores.append(float(score))
            if len(entries) >= limit:
                break

        if not entries:
            return []

        normalized_scores = normalize_scores(scores)
        paired = list(zip(entries, normalized_scores, strict=True))
        paired.sort(key=lambda item: item[1], reverse=True)
        return [(entry, score) for entry, score in paired]

    def _delete_denormalized_records(
        self,
        conn: duckdb.DuckDBPyConnection,
        oifm_ids: Sequence[str],
    ) -> None:
        unique_ids = list(dict.fromkeys(oifm_ids))
        if not unique_ids:
            return

        tables = ("model_people", "model_organizations", "synonyms", "attributes", "tags")
        placeholders = ", ".join("?" for _ in unique_ids)
        for table in tables:
            conn.execute(
                f"DELETE FROM {table} WHERE oifm_id IN ({placeholders})",
                unique_ids,
            )

    def _create_search_indexes(self, conn: duckdb.DuckDBPyConnection) -> None:
        create_hnsw_index(
            conn,
            table="finding_models",
            column="embedding",
            index_name="finding_models_embedding_hnsw",
            metric="l2sq",
        )
        create_fts_index(
            conn,
            "finding_models",
            "oifm_id",
            "search_text",
            stemmer="porter",
            stopwords="english",
            lower=1,
            overwrite=True,
        )

    def _load_base_contributors(self, conn: duckdb.DuckDBPyConnection) -> None:
        """Load base organizations and people if the tables are empty."""
        import json
        from importlib.resources import files

        # Check if organizations table is empty
        org_result = conn.execute("SELECT COUNT(*) FROM organizations").fetchone()
        org_count = org_result[0] if org_result else 0
        if org_count == 0:
            # Load base organizations from package data
            base_orgs_file = files("findingmodel") / "data" / "base_organizations.jsonl"
            with base_orgs_file.open("r") as f:
                for line in f:
                    if line.strip():
                        org_data = json.loads(line)
                        conn.execute(
                            """
                            INSERT INTO organizations (code, name, url)
                            VALUES (?, ?, ?)
                            """,
                            (org_data["code"], org_data["name"], org_data.get("url")),
                        )

        # Check if people table is empty
        people_result = conn.execute("SELECT COUNT(*) FROM people").fetchone()
        people_count = people_result[0] if people_result else 0
        if people_count == 0:
            # Load base people from package data
            base_people_file = files("findingmodel") / "data" / "base_people.jsonl"
            with base_people_file.open("r") as f:
                for line in f:
                    if line.strip():
                        person_data = json.loads(line)
                        conn.execute(
                            """
                            INSERT INTO people (github_username, name, email, organization_code, url)
                            VALUES (?, ?, ?, ?, ?)
                            """,
                            (
                                person_data["github_username"],
                                person_data["name"],
                                person_data["email"],
                                person_data.get("organization_code"),
                                person_data.get("url"),
                            ),
                        )

    def _drop_search_indexes(self, conn: duckdb.DuckDBPyConnection) -> None:
        drop_search_indexes(conn, table="finding_models", hnsw_index_name="finding_models_embedding_hnsw")

    async def _search_semantic(
        self,
        conn: duckdb.DuckDBPyConnection,
        query: str,
        *,
        limit: int,
        tags: Sequence[str] | None = None,
    ) -> list[tuple[IndexEntry, float]]:
        """Perform semantic search by generating embedding for query text."""

        if limit <= 0:
            return []

        trimmed_query = query.strip()
        if not trimmed_query:
            return []

        embedding = await get_embedding_for_duckdb(
            trimmed_query,
            client=await self._ensure_openai_client(),
        )
        if embedding is None:
            return []

        return self._search_semantic_with_embedding(conn, embedding, limit=limit, tags=tags)

    def _search_semantic_with_embedding(
        self,
        conn: duckdb.DuckDBPyConnection,
        embedding: list[float],
        *,
        limit: int,
        tags: Sequence[str] | None = None,
    ) -> list[tuple[IndexEntry, float]]:
        """Perform semantic search using a pre-computed embedding.

        This is used by search_batch() to avoid redundant embedding generation.

        Args:
            conn: Active database connection
            embedding: Pre-computed embedding vector
            limit: Maximum number of results to return
            tags: Optional list of tags - models must have ALL specified tags

        Returns:
            List of (IndexEntry, score) tuples sorted by descending similarity
        """
        if limit <= 0:
            return []

        dimensions = settings.openai_embedding_dimensions
        rows = conn.execute(
            f"""
            SELECT oifm_id, array_distance(embedding, CAST(? AS FLOAT[{dimensions}])) AS l2_distance
            FROM finding_models
            ORDER BY array_distance(embedding, CAST(? AS FLOAT[{dimensions}]))
            LIMIT ?
            """,
            (embedding, embedding, limit * 3),
        ).fetchall()

        if not rows:
            return []

        entries: list[IndexEntry] = []
        scores: list[float] = []
        for oifm_id, l2_distance in rows:
            entry = self._fetch_index_entry(conn, str(oifm_id))
            if entry is None:
                continue
            if tags and not self._entry_has_tags(entry, tags):
                continue
            scores.append(l2_to_cosine_similarity(float(l2_distance)))
            entries.append(entry)
            if len(entries) >= limit:
                break

        paired = list(zip(entries, scores, strict=True))
        paired.sort(key=lambda item: item[1], reverse=True)
        return [(entry, score) for entry, score in paired]


__all__ = [
    "AttributeInfo",
    "DuckDBIndex",
    "IndexEntry",
    "IndexReturnType",
]
