"""
Unit tests for history.database module.

Tests database initialization, CRUD operations, schema validation,
and transaction management.
"""

import pytest
import sqlite3
import tempfile
from pathlib import Path

from ImageComparisonSystem.history.database import Database


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_history.db"
        db = Database(db_path)
        yield db
        db.close()


class TestDatabaseInitialization:
    """Test database initialization and schema creation."""

    def test_database_creation(self, temp_db):
        """Test that database file is created."""
        assert temp_db.db_path.exists()

    def test_schema_tables_created(self, temp_db):
        """Test that all required tables are created."""
        expected_tables = [
            "runs",
            "results",
            "composite_metric_config",
            "image_storage",
            "annotations",
            "reviewer_metadata",
            "retention_policy",
        ]

        actual_tables = temp_db.get_table_names()

        for table in expected_tables:
            assert table in actual_tables, f"Table {table} not found"

    def test_indexes_created(self, temp_db):
        """Test that performance indexes are created."""
        query = "SELECT name FROM sqlite_master WHERE type='index'"
        rows = temp_db.execute_query(query)
        index_names = [row["name"] for row in rows]

        expected_indexes = [
            "idx_runs_build_number",
            "idx_runs_timestamp",
            "idx_results_run_id",
            "idx_results_filename",
            "idx_results_composite_score",
        ]

        for idx in expected_indexes:
            assert idx in index_names, f"Index {idx} not found"

    def test_wal_mode_enabled(self, temp_db):
        """Test that WAL mode is enabled for crash safety."""
        with temp_db.get_connection() as conn:
            cursor = conn.execute("PRAGMA journal_mode")
            mode = cursor.fetchone()[0]
            assert mode.lower() == "wal"

    def test_foreign_keys_enabled(self, temp_db):
        """Test that foreign keys are enforced."""
        with temp_db.get_connection() as conn:
            cursor = conn.execute("PRAGMA foreign_keys")
            enabled = cursor.fetchone()[0]
            assert enabled == 1

    def test_default_config_inserted(self, temp_db):
        """Test that default composite metric config is inserted."""
        query = "SELECT * FROM composite_metric_config WHERE version = 1"
        rows = temp_db.execute_query(query)

        assert len(rows) == 1
        config = rows[0]
        assert config["is_active"] == 1
        assert config["weight_pixel_diff"] == 0.25
        assert config["weight_ssim"] == 0.25
        assert config["weight_color_distance"] == 0.25
        assert config["weight_histogram"] == 0.25

    def test_default_retention_policy_inserted(self, temp_db):
        """Test that default retention policy is inserted."""
        query = "SELECT * FROM retention_policy WHERE is_active = 1"
        rows = temp_db.execute_query(query)

        assert len(rows) == 1
        policy = rows[0]
        assert policy["keep_all_runs"] == 1
        assert policy["keep_annotated"] == 1
        assert policy["keep_anomalies"] == 1


class TestDatabaseOperations:
    """Test CRUD operations."""

    def test_execute_insert(self, temp_db):
        """Test inserting a single row."""
        run_id = temp_db.execute_insert(
            "INSERT INTO runs (build_number, base_dir, new_dir, known_good_dir) VALUES (?, ?, ?, ?)",
            ("build-123", "/base", "new", "known_good"),
        )

        assert run_id > 0

        # Verify insertion
        rows = temp_db.execute_query("SELECT * FROM runs WHERE run_id = ?", (run_id,))
        assert len(rows) == 1
        assert rows[0]["build_number"] == "build-123"

    def test_execute_query(self, temp_db):
        """Test querying rows."""
        # Insert test data
        temp_db.execute_insert(
            "INSERT INTO runs (build_number, base_dir, new_dir, known_good_dir) VALUES (?, ?, ?, ?)",
            ("build-100", "/base", "new", "known_good"),
        )
        temp_db.execute_insert(
            "INSERT INTO runs (build_number, base_dir, new_dir, known_good_dir) VALUES (?, ?, ?, ?)",
            ("build-200", "/base", "new", "known_good"),
        )

        # Query all runs
        rows = temp_db.execute_query("SELECT * FROM runs ORDER BY build_number")
        assert len(rows) == 2
        assert rows[0]["build_number"] == "build-100"
        assert rows[1]["build_number"] == "build-200"

    def test_execute_many(self, temp_db):
        """Test batch insert operations."""
        # Insert a run first
        run_id = temp_db.execute_insert(
            "INSERT INTO runs (build_number, base_dir, new_dir, known_good_dir) VALUES (?, ?, ?, ?)",
            ("build-300", "/base", "new", "known_good"),
        )

        # Batch insert results
        results_data = [
            (run_id, "image1.png", "dir1", "/new/image1.png", "/good/image1.png", 45.2, 0),
            (run_id, "image2.png", "dir1", "/new/image2.png", "/good/image2.png", 12.8, 0),
            (run_id, "image3.png", "dir2", "/new/image3.png", "/good/image3.png", 89.5, 1),
        ]

        count = temp_db.execute_many(
            """INSERT INTO results
               (run_id, filename, subdirectory, new_image_path, known_good_path, composite_score, is_anomaly)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            results_data,
        )

        assert count == 3

        # Verify insertions
        rows = temp_db.execute_query("SELECT * FROM results WHERE run_id = ?", (run_id,))
        assert len(rows) == 3

    def test_execute_update(self, temp_db):
        """Test updating rows."""
        # Insert test run
        run_id = temp_db.execute_insert(
            "INSERT INTO runs (build_number, base_dir, new_dir, known_good_dir, total_images) VALUES (?, ?, ?, ?, ?)",
            ("build-400", "/base", "new", "known_good", 10),
        )

        # Update the run
        count = temp_db.execute_update(
            "UPDATE runs SET total_images = ? WHERE run_id = ?",
            (20, run_id),
        )

        assert count == 1

        # Verify update
        rows = temp_db.execute_query("SELECT * FROM runs WHERE run_id = ?", (run_id,))
        assert rows[0]["total_images"] == 20

    def test_foreign_key_cascade_delete(self, temp_db):
        """Test that deleting a run cascades to results."""
        # Insert run
        run_id = temp_db.execute_insert(
            "INSERT INTO runs (build_number, base_dir, new_dir, known_good_dir) VALUES (?, ?, ?, ?)",
            ("build-500", "/base", "new", "known_good"),
        )

        # Insert results
        temp_db.execute_insert(
            """INSERT INTO results
               (run_id, filename, subdirectory, new_image_path, known_good_path)
               VALUES (?, ?, ?, ?, ?)""",
            (run_id, "image1.png", "dir1", "/new/img1.png", "/good/img1.png"),
        )

        # Verify result exists
        rows = temp_db.execute_query("SELECT * FROM results WHERE run_id = ?", (run_id,))
        assert len(rows) == 1

        # Delete run
        temp_db.execute_update("DELETE FROM runs WHERE run_id = ?", (run_id,))

        # Verify results were cascade deleted
        rows = temp_db.execute_query("SELECT * FROM results WHERE run_id = ?", (run_id,))
        assert len(rows) == 0


class TestDatabaseUtilities:
    """Test utility methods."""

    def test_table_exists(self, temp_db):
        """Test checking if table exists."""
        assert temp_db.table_exists("runs") is True
        assert temp_db.table_exists("nonexistent_table") is False

    def test_get_row_count(self, temp_db):
        """Test getting row count."""
        # Insert some runs
        temp_db.execute_insert(
            "INSERT INTO runs (build_number, base_dir, new_dir, known_good_dir) VALUES (?, ?, ?, ?)",
            ("build-600", "/base", "new", "known_good"),
        )
        temp_db.execute_insert(
            "INSERT INTO runs (build_number, base_dir, new_dir, known_good_dir) VALUES (?, ?, ?, ?)",
            ("build-700", "/base", "new", "known_good"),
        )

        count = temp_db.get_row_count("runs")
        assert count == 2

    def test_backup(self, temp_db):
        """Test database backup."""
        # Insert some data
        temp_db.execute_insert(
            "INSERT INTO runs (build_number, base_dir, new_dir, known_good_dir) VALUES (?, ?, ?, ?)",
            ("build-800", "/base", "new", "known_good"),
        )

        # Backup database
        backup_path = temp_db.db_path.parent / "backup.db"
        temp_db.backup(backup_path)

        assert backup_path.exists()

        # Verify backup contains data
        backup_db = Database(backup_path)
        count = backup_db.get_row_count("runs")
        assert count == 1
        backup_db.close()

    def test_vacuum(self, temp_db):
        """Test database vacuum."""
        # Insert and delete data to create fragmentation
        run_id = temp_db.execute_insert(
            "INSERT INTO runs (build_number, base_dir, new_dir, known_good_dir) VALUES (?, ?, ?, ?)",
            ("build-900", "/base", "new", "known_good"),
        )
        temp_db.execute_update("DELETE FROM runs WHERE run_id = ?", (run_id,))

        # Vacuum should not raise exception
        temp_db.vacuum()


class TestTransactionManagement:
    """Test transaction handling."""

    def test_transaction_commit(self, temp_db):
        """Test successful transaction commit."""
        with temp_db.get_connection() as conn:
            conn.execute(
                "INSERT INTO runs (build_number, base_dir, new_dir, known_good_dir) VALUES (?, ?, ?, ?)",
                ("build-1000", "/base", "new", "known_good"),
            )
            conn.commit()

        # Verify data persisted
        rows = temp_db.execute_query("SELECT * FROM runs WHERE build_number = ?", ("build-1000",))
        assert len(rows) == 1

    def test_transaction_rollback_on_error(self, temp_db):
        """Test transaction rollback on error."""
        try:
            with temp_db.get_connection() as conn:
                conn.execute(
                    "INSERT INTO runs (build_number, base_dir, new_dir, known_good_dir) VALUES (?, ?, ?, ?)",
                    ("build-1100", "/base", "new", "known_good"),
                )
                # Intentionally cause an error (invalid SQL)
                conn.execute("INVALID SQL STATEMENT")
                conn.commit()
        except sqlite3.Error:
            pass  # Expected

        # Verify data was rolled back
        rows = temp_db.execute_query("SELECT * FROM runs WHERE build_number = ?", ("build-1100",))
        assert len(rows) == 0


class TestDataIntegrity:
    """Test data integrity constraints."""

    def test_check_constraint_annotation_type(self, temp_db):
        """Test CHECK constraint on annotation_type."""
        # Insert a run and result first
        run_id = temp_db.execute_insert(
            "INSERT INTO runs (build_number, base_dir, new_dir, known_good_dir) VALUES (?, ?, ?, ?)",
            ("build-1200", "/base", "new", "known_good"),
        )
        result_id = temp_db.execute_insert(
            """INSERT INTO results
               (run_id, filename, subdirectory, new_image_path, known_good_path)
               VALUES (?, ?, ?, ?, ?)""",
            (run_id, "image1.png", "dir1", "/new/img1.png", "/good/img1.png"),
        )

        # Valid annotation type should work
        temp_db.execute_insert(
            "INSERT INTO annotations (result_id, annotation_type, label) VALUES (?, ?, ?)",
            (result_id, "bounding_box", "test_label"),
        )

        # Invalid annotation type should fail
        with pytest.raises(sqlite3.IntegrityError):
            temp_db.execute_insert(
                "INSERT INTO annotations (result_id, annotation_type, label) VALUES (?, ?, ?)",
                (result_id, "invalid_type", "test_label"),
            )

    def test_check_constraint_review_status(self, temp_db):
        """Test CHECK constraint on review_status."""
        # Insert a run and result first
        run_id = temp_db.execute_insert(
            "INSERT INTO runs (build_number, base_dir, new_dir, known_good_dir) VALUES (?, ?, ?, ?)",
            ("build-1300", "/base", "new", "known_good"),
        )
        result_id = temp_db.execute_insert(
            """INSERT INTO results
               (run_id, filename, subdirectory, new_image_path, known_good_path)
               VALUES (?, ?, ?, ?, ?)""",
            (run_id, "image1.png", "dir1", "/new/img1.png", "/good/img1.png"),
        )

        # Valid review status should work
        temp_db.execute_insert(
            "INSERT INTO reviewer_metadata (result_id, review_status) VALUES (?, ?)",
            (result_id, "approved"),
        )

        # Invalid review status should fail
        with pytest.raises(sqlite3.IntegrityError):
            temp_db.execute_insert(
                "INSERT INTO reviewer_metadata (result_id, review_status) VALUES (?, ?)",
                (result_id, "invalid_status"),
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
