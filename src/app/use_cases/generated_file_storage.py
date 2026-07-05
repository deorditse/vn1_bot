from dataclasses import dataclass
import sqlite3
from pathlib import Path
from time import time
from uuid import uuid4

from common import env
from domain.services.converter import Converter


@dataclass(frozen=True)
class GeneratedFile:
    file_id: str
    owner_id: str
    file_name: str
    markdown: str
    expires_at: float


class GeneratedFileStorage:
    def __init__(
            self,
            db_path: str = env.generated_file_db_path(),
            ttl_seconds: int = env.generated_file_ttl_seconds(),
    ):
        self._db_path = Path(db_path)
        self._ttl_seconds = ttl_seconds
        self._init_db()

    def add(self, owner_id: str, file_name: str, markdown: str) -> GeneratedFile:
        self._prune_expired()

        file_id = uuid4().hex
        generated_file = GeneratedFile(
            file_id=file_id,
            owner_id=owner_id,
            file_name=file_name,
            markdown=markdown,
            expires_at=time() + self._ttl_seconds,
        )

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO generated_files (file_id, owner_id, file_name, markdown, expires_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(owner_id) DO UPDATE SET
                    file_id = excluded.file_id,
                    file_name = excluded.file_name,
                    markdown = excluded.markdown,
                    expires_at = excluded.expires_at
                """,
                (
                    generated_file.file_id,
                    generated_file.owner_id,
                    generated_file.file_name,
                    generated_file.markdown,
                    generated_file.expires_at,
                ),
            )

        return generated_file

    def get(self, file_id: str, owner_id: str) -> GeneratedFile | None:
        self._prune_expired()

        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT file_id, owner_id, file_name, markdown, expires_at
                FROM generated_files
                WHERE file_id = ? AND owner_id = ?
                """,
                (file_id, owner_id),
            ).fetchone()

        if row is None:
            return None

        return GeneratedFile(
            file_id=str(row["file_id"]),
            owner_id=str(row["owner_id"]),
            file_name=str(row["file_name"]),
            markdown=str(row["markdown"]),
            expires_at=float(row["expires_at"]),
        )

    def _init_db(self) -> None:
        self._db_path.parent.mkdir(parents=True, exist_ok=True)

        with self._connect() as connection:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute("PRAGMA busy_timeout=5000")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS generated_files (
                    file_id TEXT PRIMARY KEY,
                    owner_id TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    markdown TEXT NOT NULL,
                    expires_at REAL NOT NULL
                )
                """
            )
            columns = {
                str(row["name"])
                for row in connection.execute("PRAGMA table_info(generated_files)").fetchall()
            }
            if "owner_id" not in columns:
                connection.execute("ALTER TABLE generated_files ADD COLUMN owner_id TEXT")
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_generated_files_expires_at
                ON generated_files (expires_at)
                """
            )
            connection.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS idx_generated_files_owner_id
                ON generated_files (owner_id)
                """
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._db_path, timeout=5)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA busy_timeout=5000")

        return connection

    def _prune_expired(self) -> None:
        with self._connect() as connection:
            connection.execute(
                "DELETE FROM generated_files WHERE expires_at <= ?",
                (time(),),
            )


generated_file_storage = GeneratedFileStorage()


class UploadGeneratedFileUseCase:
    def __init__(
            self,
            converter: Converter,
            storage: GeneratedFileStorage = generated_file_storage,
    ):
        self._converter = converter
        self._storage = storage

    async def upload(self, owner_id: str, file_bytes: bytes, file_name: str) -> GeneratedFile:
        markdown = await self._converter.convert(file_bytes=file_bytes)

        return self._storage.add(
            owner_id=owner_id,
            file_name=file_name,
            markdown=markdown,
        )
