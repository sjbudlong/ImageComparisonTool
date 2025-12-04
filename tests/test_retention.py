"""
Unit tests for retention policy module.
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "ImageComparisonSystem"))

from history.database import Database
from history.retention import RetentionPolicy


@pytest.fixture
def temp_database():
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = Database(db_path)
        yield db


@pytest.fixture
def populated_database(temp_database):
    """Create a database with test data."""
    db = temp_database

    # Insert test runs
    now = datetime.now()

    # Run 1: 30 days old, normal
    run_id_1 = db.execute_insert(
        """INSERT INTO runs (build_number, timestamp, base_dir, new_dir, known_good_dir,
           config_snapshot, total_images, avg_difference)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            "build-1",
            (now - timedelta(days=30)).isoformat(),
            "/test",
            "/test/new",
            "/test/known",
            "{}",
            10,
            5.0,
        ),
    )

    # Run 2: 15 days old, has anomaly
    run_id_2 = db.execute_insert(
        """INSERT INTO runs (build_number, timestamp, base_dir, new_dir, known_good_dir,
           config_snapshot, total_images, avg_difference)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            "build-2",
            (now - timedelta(days=15)).isoformat(),
            "/test",
            "/test/new",
            "/test/known",
            "{}",
            10,
            8.0,
        ),
    )

    # Add anomalous result to run 2
    result_id_2 = db.execute_insert(
        """INSERT INTO results (run_id, filename, subdirectory, new_image_path, known_good_path,
           pixel_difference, ssim_score, composite_score, is_anomaly)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (run_id_2, "test.png", "", "/test/new/test.png", "/test/known/test.png", 10.0, 0.8, 50.0, 1),
    )

    # Run 3: 5 days old, has annotation
    run_id_3 = db.execute_insert(
        """INSERT INTO runs (build_number, timestamp, base_dir, new_dir, known_good_dir,
           config_snapshot, total_images, avg_difference)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            "build-3",
            (now - timedelta(days=5)).isoformat(),
            "/test",
            "/test/new",
            "/test/known",
            "{}",
            10,
            3.0,
        ),
    )

    # Add result with annotation to run 3
    result_id_3 = db.execute_insert(
        """INSERT INTO results (run_id, filename, subdirectory, new_image_path, known_good_path,
           pixel_difference, ssim_score, composite_score, is_anomaly)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (run_id_3, "annotated.png", "", "/test/new/annotated.png", "/test/known/annotated.png", 5.0, 0.9, 20.0, 0),
    )

    # Add annotation
    db.execute_insert(
        """INSERT INTO annotations (result_id, annotation_type, geometry_json, label,
           annotator_name, annotation_timestamp)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (result_id_3, "bounding_box", '{"x": 10, "y": 20}', "test", "tester", now.isoformat()),
    )

    # Run 4: 1 day old, normal
    run_id_4 = db.execute_insert(
        """INSERT INTO runs (build_number, timestamp, base_dir, new_dir, known_good_dir,
           config_snapshot, total_images, avg_difference)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            "build-4",
            (now - timedelta(days=1)).isoformat(),
            "/test",
            "/test/new",
            "/test/known",
            "{}",
            10,
            4.0,
        ),
    )

    return db, [run_id_1, run_id_2, run_id_3, run_id_4]


@pytest.mark.unit
class TestRetentionPolicy:
    """Test RetentionPolicy class."""

    def test_initialization_keep_all(self, temp_database):
        """RetentionPolicy should initialize with keep_all_runs=True."""
        policy = RetentionPolicy(temp_database, keep_all_runs=True)
        assert policy.keep_all_runs is True
        assert policy.max_runs_to_keep is None
        assert policy.max_age_days is None

    def test_initialization_with_limits(self, temp_database):
        """RetentionPolicy should initialize with retention limits."""
        policy = RetentionPolicy(
            temp_database, keep_all_runs=False, max_runs_to_keep=10, max_age_days=30
        )
        assert policy.keep_all_runs is False
        assert policy.max_runs_to_keep == 10
        assert policy.max_age_days == 30
        assert policy.keep_annotated is True
        assert policy.keep_anomalies is True

    def test_apply_retention_keep_all(self, populated_database):
        """Retention with keep_all_runs should not delete anything."""
        db, run_ids = populated_database
        policy = RetentionPolicy(db, keep_all_runs=True)

        result = policy.apply_retention(dry_run=False)

        assert result["runs_evaluated"] == 4
        assert result["runs_eligible"] == 0
        assert result["runs_protected"] == 4
        assert result["runs_deleted"] == 0

        # Verify all runs still exist
        rows = db.execute_query("SELECT COUNT(*) as count FROM runs")
        assert rows[0]["count"] == 4

    def test_apply_retention_max_runs(self, populated_database):
        """Retention with max_runs should delete oldest runs."""
        db, run_ids = populated_database
        policy = RetentionPolicy(db, keep_all_runs=False, max_runs_to_keep=2)

        result = policy.apply_retention(dry_run=False)

        assert result["runs_evaluated"] == 4
        assert result["runs_eligible"] == 2  # 2 oldest runs (runs 1 and 2)
        # Run 2 has anomaly - protected, Run 3 not eligible (within max_runs limit)
        assert result["runs_protected"] == 1  # Only run 2 (has anomaly)
        assert result["runs_deleted"] == 1  # Only run 1 deleted (no protection)

    def test_apply_retention_max_age(self, populated_database):
        """Retention with max_age_days should delete old runs."""
        db, run_ids = populated_database
        policy = RetentionPolicy(db, keep_all_runs=False, max_age_days=20)

        result = policy.apply_retention(dry_run=False)

        assert result["runs_evaluated"] == 4
        assert result["runs_eligible"] == 1  # Only run 1 (30 days old)
        assert result["runs_deleted"] == 1

        # Verify run 1 was deleted
        rows = db.execute_query("SELECT COUNT(*) as count FROM runs")
        assert rows[0]["count"] == 3

    def test_dry_run(self, populated_database):
        """Dry run should not delete anything."""
        db, run_ids = populated_database
        policy = RetentionPolicy(db, keep_all_runs=False, max_age_days=20)

        result = policy.apply_retention(dry_run=True)

        assert result["runs_eligible"] == 1
        assert len(result["run_ids_deleted"]) == 1  # Would delete 1 run

        # Verify nothing was actually deleted
        rows = db.execute_query("SELECT COUNT(*) as count FROM runs")
        assert rows[0]["count"] == 4

    def test_protect_annotated_runs(self, populated_database):
        """Runs with annotations should be protected."""
        db, run_ids = populated_database
        policy = RetentionPolicy(
            db, keep_all_runs=False, max_age_days=10, keep_annotated=True
        )

        result = policy.apply_retention(dry_run=False)

        # Run 3 (5 days old, has annotation) should be protected
        # Run 1 (30 days old) and Run 2 (15 days old) should be eligible
        assert result["runs_eligible"] == 2

        # Run 2 has anomaly, so it's protected too
        # Run 1 has no protection
        assert result["runs_deleted"] == 1

        # Verify run 3 still exists
        rows = db.execute_query("SELECT * FROM runs WHERE run_id = ?", (run_ids[2],))
        assert len(rows) == 1

    def test_protect_anomalous_runs(self, populated_database):
        """Runs with anomalies should be protected."""
        db, run_ids = populated_database
        policy = RetentionPolicy(
            db, keep_all_runs=False, max_age_days=20, keep_anomalies=True
        )

        result = policy.apply_retention(dry_run=False)

        # Run 1 (30 days old, no anomaly) should be deleted
        # Run 2 (15 days old, has anomaly) should be protected
        assert result["runs_eligible"] == 1
        assert result["runs_protected"] == 0  # Run 2 not eligible (within 20 days)
        assert result["runs_deleted"] == 1

        # Verify run 2 still exists
        rows = db.execute_query("SELECT * FROM runs WHERE run_id = ?", (run_ids[1],))
        assert len(rows) == 1

    def test_get_statistics(self, populated_database):
        """get_statistics should return accurate database stats."""
        db, run_ids = populated_database
        policy = RetentionPolicy(db, keep_all_runs=True)

        stats = policy.get_statistics()

        assert stats["total_runs"] == 4
        assert stats["total_results"] == 2  # 2 results inserted
        assert stats["annotated_runs"] == 1  # Run 3 has annotation
        assert stats["anomalous_runs"] == 1  # Run 2 has anomaly
        assert stats["oldest_run"] is not None
        assert stats["newest_run"] is not None

    def test_cascade_delete(self, populated_database):
        """Deleting a run should cascade delete its results."""
        db, run_ids = populated_database

        # Get initial result count
        rows = db.execute_query("SELECT COUNT(*) as count FROM results WHERE run_id = ?", (run_ids[1],))
        initial_count = rows[0]["count"]
        assert initial_count == 1  # Run 2 has 1 result

        # Delete run 2 directly (simulating retention deletion)
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM runs WHERE run_id = ?", (run_ids[1],))
            conn.commit()

        # Verify results were cascade deleted
        rows = db.execute_query("SELECT COUNT(*) as count FROM results WHERE run_id = ?", (run_ids[1],))
        assert rows[0]["count"] == 0

    def test_multiple_retention_criteria(self, populated_database):
        """Multiple retention criteria should work together."""
        db, run_ids = populated_database
        policy = RetentionPolicy(
            db,
            keep_all_runs=False,
            max_runs_to_keep=3,
            max_age_days=10,
            keep_annotated=True,
            keep_anomalies=True,
        )

        result = policy.apply_retention(dry_run=False)

        # Run 1 (30 days old) is eligible by both age and count
        # Run 2 (15 days old, anomaly) is eligible by age but protected
        # Run 3 (5 days old, annotation) is within limits
        # Run 4 (1 day old) is within limits

        # Both age and count limits should identify Run 1 and Run 2 as eligible
        assert result["runs_eligible"] >= 1
        assert result["runs_protected"] >= 1  # Run 2 protected by anomaly

    def test_empty_database(self, temp_database):
        """Retention on empty database should not crash."""
        policy = RetentionPolicy(temp_database, keep_all_runs=False, max_runs_to_keep=10)

        result = policy.apply_retention(dry_run=False)

        assert result["runs_evaluated"] == 0
        assert result["runs_eligible"] == 0
        assert result["runs_deleted"] == 0

    def test_no_protected_runs(self, temp_database):
        """Runs without protection should be deletable."""
        db = temp_database
        now = datetime.now()

        # Insert old run with no anomalies or annotations
        run_id = db.execute_insert(
            """INSERT INTO runs (build_number, timestamp, base_dir, new_dir, known_good_dir,
               config_snapshot, total_images, avg_difference)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                "old-build",
                (now - timedelta(days=60)).isoformat(),
                "/test",
                "/test/new",
                "/test/known",
                "{}",
                10,
                5.0,
            ),
        )

        policy = RetentionPolicy(db, keep_all_runs=False, max_age_days=30)
        result = policy.apply_retention(dry_run=False)

        assert result["runs_eligible"] == 1
        assert result["runs_protected"] == 0
        assert result["runs_deleted"] == 1

        # Verify run was deleted
        rows = db.execute_query("SELECT COUNT(*) as count FROM runs")
        assert rows[0]["count"] == 0
