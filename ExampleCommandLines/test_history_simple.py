"""
Simple test for historical tracking database and composite metrics.
Tests only the modules that don't have complex dependencies.
"""

import sys
import tempfile
from pathlib import Path
from datetime import datetime

# Add to path
sys.path.insert(0, str(Path(__file__).parent / "ImageComparisonSystem"))


def test_database():
    """Test Phase 1: Database creation."""
    print("\n" + "="*60)
    print("PHASE 1: Database Foundation")
    print("="*60)

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"

        from history.database import Database

        db = Database(db_path)
        print(f"[OK] Database created at: {db_path}")

        # Verify tables
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

        expected = ['runs', 'results', 'composite_metric_config',
                    'image_storage', 'annotations', 'reviewer_metadata',
                    'retention_policy']

        for table in expected:
            assert table in tables, f"Missing: {table}"
            print(f"[OK] Table '{table}' exists")

        # Test insert
        run_id = db.execute_insert(
            """INSERT INTO runs (build_number, timestamp, base_dir, new_dir,
               known_good_dir, config_snapshot, total_images, avg_difference)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            ("test-build", datetime.now().isoformat(), "/test", "/test/new",
             "/test/known", "{}", 10, 5.5)
        )

        print(f"[OK] Inserted run ID: {run_id}")

        # Test query
        rows = db.execute_query(
            "SELECT * FROM runs WHERE run_id = ?",
            (run_id,)
        )

        assert len(rows) == 1
        assert rows[0]['build_number'] == 'test-build'
        print("[OK] Query successful")

    print("\n[PASS] Phase 1 Database Foundation")


def test_composite_metric():
    """Test Phase 4: Composite Metric Calculator."""
    print("\n" + "="*60)
    print("PHASE 4: Composite Metric Calculator")
    print("="*60)

    from history.composite_metric import CompositeMetricCalculator, normalize

    # Test normalize
    assert normalize(50, 0, 100) == 0.5
    assert normalize(0, 0, 100) == 0.0
    assert normalize(100, 0, 100) == 1.0
    print("[OK] normalize() working")

    # Test calculator
    calc = CompositeMetricCalculator()
    print("[OK] CompositeMetricCalculator initialized")

    # Create mock result
    from dataclasses import dataclass
    from typing import Optional, Dict, Any

    @dataclass
    class MockResult:
        filename: str
        metrics: Dict[str, Any]
        composite_score: Optional[float] = None

    # Test with identical images
    result_identical = MockResult(
        filename="identical.png",
        metrics={
            "Pixel Difference": {"percent_different": 0.0},
            "Structural Similarity": {"ssim_score": 1.0},
            "Color Difference": {"mean_color_distance": 0.0},
            "Histogram Analysis": {
                "red_histogram_chi_square": 0.0,
                "green_histogram_chi_square": 0.0,
                "blue_histogram_chi_square": 0.0
            }
        }
    )

    score = calc.calculate_composite_score(result_identical)
    print(f"[OK] Identical images score: {score:.2f} (expected < 1.0)")
    assert score < 1.0

    # Test with different images
    result_different = MockResult(
        filename="different.png",
        metrics={
            "Pixel Difference": {"percent_different": 100.0},
            "Structural Similarity": {"ssim_score": 0.0},
            "Color Difference": {"mean_color_distance": 441.67},
            "Histogram Analysis": {
                "red_histogram_chi_square": 2.0,
                "green_histogram_chi_square": 2.0,
                "blue_histogram_chi_square": 2.0
            }
        }
    )

    score = calc.calculate_composite_score(result_different)
    print(f"[OK] Different images score: {score:.2f} (expected > 99.0)")
    assert score > 99.0

    print("\n[PASS] Phase 4 Composite Metric Calculator")


def test_statistics():
    """Test Phase 5: Statistical Analysis."""
    print("\n" + "="*60)
    print("PHASE 5: Statistical Analysis Engine")
    print("="*60)

    from history.statistics import StatisticsCalculator

    calc = StatisticsCalculator(anomaly_threshold=2.0, min_runs_for_stats=3)
    print("[OK] StatisticsCalculator initialized")

    # Test stats calculation
    scores = [10.0, 12.0, 11.0, 13.0, 10.5]
    stats = calc.calculate_historical_stats(scores)
    assert stats is not None
    mean, std_dev = stats
    print(f"[OK] Stats calculated: mean={mean:.2f}, std_dev={std_dev:.2f}")
    assert abs(mean - 11.3) < 0.1

    # Test anomaly detection (not anomaly)
    is_anomaly, deviation = calc.detect_anomaly(11.0, 10.0, 1.0)
    assert not is_anomaly
    print(f"[OK] No anomaly for normal value (deviation={deviation:.2f})")

    # Test anomaly detection (is anomaly)
    is_anomaly, deviation = calc.detect_anomaly(15.0, 10.0, 1.0)
    assert is_anomaly
    print(f"[OK] Anomaly detected (deviation={deviation:.2f})")

    # Test trend detection
    increasing = [10.0, 15.0, 20.0, 25.0, 30.0]
    trend = calc.get_trend_direction(increasing)
    assert trend == "increasing"
    print(f"[OK] Trend detection: {trend}")

    print("\n[PASS] Phase 5 Statistical Analysis Engine")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("HISTORICAL TRACKING TEST SUITE")
    print("Testing Phases 1, 4, and 5 (without dependencies)")
    print("="*60)

    try:
        test_database()
        test_composite_metric()
        test_statistics()

        print("\n" + "="*60)
        print("[SUCCESS] All tests passed!")
        print("="*60)
        print("\nPhases 1, 4, and 5 are working correctly.")
        print("Phase 2 and 3 require full system integration to test.")

    except Exception as e:
        print("\n" + "="*60)
        print("[FAILED] Test error")
        print("="*60)
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
