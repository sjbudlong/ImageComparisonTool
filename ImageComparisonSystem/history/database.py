"""
Database module for historical metrics tracking.

Provides SQLite database connection management, schema creation,
and migration support for historical image comparison data.
"""

import sqlite3
import logging
from pathlib import Path
from typing import Optional, Any, List, Dict
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class Database:
    """
    SQLite database manager for historical metrics tracking.

    Handles connection management, schema creation, migrations,
    and provides context manager for transaction handling.
    """

    def __init__(self, db_path: Path):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection: Optional[sqlite3.Connection] = None

        # Initialize database on creation
        self._initialize_database()

    def _initialize_database(self) -> None:
        """
        Initialize database with schema if it doesn't exist.

        Creates tables, indexes, and default configurations using
        the v1 initial schema migration.
        """
        try:
            with self.get_connection() as conn:
                # Enable WAL mode for better concurrency and crash safety
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA foreign_keys=ON")

                # Run schema migration
                schema_path = (
                    Path(__file__).parent / "migrations" / "v1_initial_schema.sql"
                )
                if schema_path.exists():
                    with open(schema_path, "r", encoding="utf-8") as f:
                        schema_sql = f.read()
                    conn.executescript(schema_sql)
                    conn.commit()
                    logger.info(f"Database initialized at {self.db_path}")
                else:
                    logger.error(f"Schema file not found: {schema_path}")
                    raise FileNotFoundError(f"Schema file not found: {schema_path}")

                # Validate database integrity
                cursor = conn.execute("PRAGMA integrity_check")
                result = cursor.fetchone()
                if result[0] != "ok":
                    logger.error(f"Database integrity check failed: {result[0]}")
                    raise RuntimeError(f"Database integrity check failed: {result[0]}")

        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.

        Provides automatic transaction management with commit on success
        and rollback on error.

        Yields:
            sqlite3.Connection: Database connection

        Example:
            >>> with db.get_connection() as conn:
            ...     conn.execute("INSERT INTO runs ...")
            ...     conn.commit()
        """
        conn = None
        try:
            conn = sqlite3.connect(
                str(self.db_path),
                timeout=30.0,  # 30 second timeout for locks
                isolation_level="",  # Enable transaction mode (implicit BEGIN on first statement)
            )
            # Enable foreign keys
            conn.execute("PRAGMA foreign_keys=ON")
            # Use Row factory for dict-like access
            conn.row_factory = sqlite3.Row
            yield conn
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def execute_query(
        self, query: str, params: Optional[tuple] = None
    ) -> List[sqlite3.Row]:
        """
        Execute a SELECT query and return results.

        Args:
            query: SQL query string
            params: Optional query parameters (tuple)

        Returns:
            List of Row objects (dict-like access)

        Example:
            >>> rows = db.execute_query("SELECT * FROM runs WHERE build_number = ?", ("build-123",))
            >>> for row in rows:
            ...     print(row["run_id"], row["timestamp"])
        """
        with self.get_connection() as conn:
            cursor = conn.execute(query, params or ())
            return cursor.fetchall()

    def execute_insert(self, query: str, params: Optional[tuple] = None) -> int:
        """
        Execute an INSERT query and return the last inserted row ID.

        Args:
            query: SQL INSERT statement
            params: Optional query parameters (tuple)

        Returns:
            Last inserted row ID

        Example:
            >>> run_id = db.execute_insert(
            ...     "INSERT INTO runs (build_number, base_dir) VALUES (?, ?)",
            ...     ("build-123", "/path/to/project")
            ... )
        """
        with self.get_connection() as conn:
            cursor = conn.execute(query, params or ())
            conn.commit()
            return cursor.lastrowid

    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """
        Execute multiple INSERT/UPDATE queries in a single transaction.

        Args:
            query: SQL statement (INSERT or UPDATE)
            params_list: List of parameter tuples

        Returns:
            Number of rows affected

        Example:
            >>> db.execute_many(
            ...     "INSERT INTO results (run_id, filename, composite_score) VALUES (?, ?, ?)",
            ...     [(1, "img1.png", 45.2), (1, "img2.png", 12.8)]
            ... )
        """
        with self.get_connection() as conn:
            cursor = conn.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount

    def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """
        Execute an UPDATE or DELETE query.

        Args:
            query: SQL UPDATE or DELETE statement
            params: Optional query parameters (tuple)

        Returns:
            Number of rows affected

        Example:
            >>> count = db.execute_update(
            ...     "UPDATE results SET is_anomaly = 1 WHERE std_dev_from_mean > 2.0"
            ... )
        """
        with self.get_connection() as conn:
            cursor = conn.execute(query, params or ())
            conn.commit()
            return cursor.rowcount

    def get_table_names(self) -> List[str]:
        """
        Get list of all tables in the database.

        Returns:
            List of table names

        Example:
            >>> tables = db.get_table_names()
            >>> print(tables)
            ['runs', 'results', 'composite_metric_config', ...]
        """
        query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        rows = self.execute_query(query)
        return [row["name"] for row in rows]

    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists in the database.

        Args:
            table_name: Name of the table to check

        Returns:
            True if table exists, False otherwise

        Example:
            >>> if db.table_exists("runs"):
            ...     print("Table exists")
        """
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        rows = self.execute_query(query, (table_name,))
        return len(rows) > 0

    def get_row_count(self, table_name: str) -> int:
        """
        Get number of rows in a table.

        Args:
            table_name: Name of the table

        Returns:
            Number of rows

        Example:
            >>> count = db.get_row_count("runs")
            >>> print(f"Total runs: {count}")
        """
        query = f"SELECT COUNT(*) as count FROM {table_name}"
        rows = self.execute_query(query)
        return rows[0]["count"] if rows else 0

    def vacuum(self) -> None:
        """
        Vacuum database to reclaim space and optimize.

        Should be called periodically after deleting large amounts of data.

        Example:
            >>> db.vacuum()
        """
        with self.get_connection() as conn:
            conn.execute("VACUUM")
            logger.info("Database vacuumed successfully")

    def backup(self, backup_path: Path) -> None:
        """
        Create a backup of the database.

        Args:
            backup_path: Path to backup file

        Example:
            >>> db.backup(Path("backups/comparison_history_2025-12-03.db"))
        """
        backup_path = Path(backup_path)
        backup_path.parent.mkdir(parents=True, exist_ok=True)

        with self.get_connection() as conn:
            backup_conn = sqlite3.connect(str(backup_path))
            try:
                conn.backup(backup_conn)
                backup_conn.close()
                logger.info(f"Database backed up to {backup_path}")
            except Exception as e:
                backup_conn.close()
                logger.error(f"Backup failed: {e}")
                raise

    def close(self) -> None:
        """
        Close database connection.

        Note: Connections are automatically closed when using get_connection()
        context manager. This method is primarily for cleanup in long-running
        processes.
        """
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.debug("Database connection closed")
