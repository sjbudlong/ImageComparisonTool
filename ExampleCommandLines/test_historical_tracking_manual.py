"""
Manual integration test for historical tracking feature (Phases 1-5).

This script tests the complete pipeline:
1. Database creation
2. History manager operations
3. Configuration
4. Composite metric calculation
5. Statistical analysis

Run this to verify Phases 1-5 are working correctly before continuing.
"""

import sys
import tempfile
from pathlib import Path
from datetime import datetime
from ImageComparisonSystem.config import Config
from ImageComparisonSystem.history import Database, HistoryManager
from ImageComparisonSystem.history.composite_metric import CompositeMetricCalculator
from ImageComparisonSystem.history.statistics import StatisticsCalculator
from ImageComparisonSystem.models import ComparisonResult

# Add ImageComparisonSystem to path
sys.path.insert(0, str(Path(__file__).parent))


def create_mock_result(filename, pixel_diff, ssim_score, color_dist, hist_chi):
    """Create a mock ComparisonResult for testing."""
    return ComparisonResult(
        filename=filename,
        new_image_path=Path(f"/test/new/{filename}"),
        known_good_path=Path(f"/test/known/{filename}"),
        diff_image_path=Path(f"/test/diff/{filename}"),
        annotated_image_path=Path(f"/test/annotated/{filename}"),
        metrics={
            "Pixel Difference": {
                "percent_different": pixel_diff,
                "changed_pixels": int(pixel_diff * 100),
                "mean_absolute_error": pixel_diff / 10,
                "max_difference": 255,
            },
            "Structural Similarity": {
                "ssim_score": ssim_score,
                "ssim_percentage": (1 - ssim_score) * 100,
            },
            "Color Difference": {
                "mean_color_distance": color_dist,
                "max_color_distance": color_dist * 2,
                "significant_color_changes": int(color_dist * 5),
            },
            "Histogram Analysis": {
                "red_histogram_correlation": 0.95,
                "green_histogram_correlation": 0.94,
                "blue_histogram_correlation": 0.96,
                "red_histogram_chi_square": hist_chi,
                "green_histogram_chi_square": hist_chi * 1.1,
                "blue_histogram_chi_square": hist_chi * 0.9,
            },
        },
        percent_different=pixel_diff,
        histogram_data="mock_base64_data",
    )


def test_phase_1_database():
    """Test Phase 1: Database Foundation."""
    print("\n" + "="*70)
    print("PHASE 1: DATABASE FOUNDATION")
    print("="*70)

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_history.db"

        print(f"✓ Creating database at: {db_path}")
        db = Database(db_path)

        # Test table creation
        tables = db.get_table_names()
        expected_tables = ["runs", "results", "composite_metric_config",
                           "annotations", "reviewer_metadata", "retention_policy"]

        for table in expected_tables:
            if table in tables:
                print(f"  ✓ Table '{table}' exists")
            else:
                print(f"  ✗ Table '{table}' MISSING!")
                return False

        # Test insert/query
        run_id = db.execute_insert(
            "INSERT INTO runs (build_number, base_dir, new_dir, known_good_dir) VALUES (?, ?, ?, ?)",
            ("test-001", "/test", "new", "known")
        )
        print(f"  ✓ Inserted test run (ID: {run_id})")

        rows = db.execute_query("SELECT * FROM runs WHERE run_id = ?", (run_id,))
        if rows and rows[0]["build_number"] == "test-001":
            print("  ✓ Query successful")
        else:
            print("  ✗ Query failed!")
            return False

        db.close()
        print("✅ Phase 1: PASSED\n")
        return True


def test_phase_2_history_manager():
    """Test Phase 2: History Manager Core."""
    print("="*70)
    print("PHASE 2: HISTORY MANAGER CORE")
    print("="*70)

    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)
        config = Config(
            base_dir=base_dir,
            new_dir="new",
            known_good_dir="known_good",
            build_number="build-001"
        )

        print("✓ Creating HistoryManager")
        manager = HistoryManager(config)

        # Create mock results
        results = [
            create_mock_result("image1.png", 10.5, 0.95, 15.0, 0.3),
            create_mock_result("image2.png", 25.0, 0.80, 50.0, 0.8),
            create_mock_result("image3.png", 5.2, 0.98, 8.0, 0.1),
        ]

        # Test save_run
        print("✓ Saving run with 3 results")
        run_id = manager.save_run(results, config, notes="Integration test")
        print(f"  ✓ Run saved (ID: {run_id})")

        # Test query
        retrieved_run = manager.get_run(run_id)
        if retrieved_run and retrieved_run["build_number"] == "build-001":
            print("  ✓ Run retrieved successfully")
        else:
            print("  ✗ Failed to retrieve run!")
            return False

        # Test get_results_for_run
        saved_results = manager.get_results_for_run(run_id)
        if len(saved_results) == 3:
            print("  ✓ All 3 results retrieved")
        else:
            print(f"  ✗ Expected 3 results, got {len(saved_results)}!")
            return False

        # Test historical query
        history = manager.get_history_for_image("image1.png")
        if len(history) == 1:
            print("  ✓ Historical query works")
        else:
            print("  ✗ Historical query failed!")
            return False

        manager.close()
        print("✅ Phase 2: PASSED\n")
        return True


def test_phase_3_configuration():
    """Test Phase 3: Configuration Integration."""
    print("="*70)
    print("PHASE 3: CONFIGURATION INTEGRATION")
    print("="*70)

    with tempfile.TemporaryDirectory() as tmpdir:
        # Test config with history fields
        config = Config(
            base_dir=Path(tmpdir),
            new_dir="new",
            known_good_dir="known_good",
            enable_history=True,
            build_number="build-002",
            history_db_path=Path(tmpdir) / "custom.db",
            composite_metric_weights={"pixel_diff": 0.3, "ssim": 0.3, "color_distance": 0.2, "histogram": 0.2},
            anomaly_threshold=2.5,
            retention_keep_all=False,
            retention_max_runs=100,
        )

        print("✓ Config created with history fields")
        print(f"  ✓ enable_history: {config.enable_history}")
        print(f"  ✓ build_number: {config.build_number}")
        print(f"  ✓ anomaly_threshold: {config.anomaly_threshold}")
        print(f"  ✓ Custom weights: {config.composite_metric_weights is not None}")

        # Test backward compatibility
        config_no_history = Config(
            base_dir=Path(tmpdir),
            new_dir="new",
            known_good_dir="known_good"
        )

        if config_no_history.enable_history is True:  # Default
            print("  ✓ Backward compatibility maintained")
        else:
            print("  ✗ Backward compatibility broken!")
            return False

        print("✅ Phase 3: PASSED\n")
        return True


def test_phase_4_composite_metric():
    """Test Phase 4: Composite Metric Calculator."""
    print("="*70)
    print("PHASE 4: COMPOSITE METRIC CALCULATOR")
    print("="*70)

    calculator = CompositeMetricCalculator()
    print("✓ CompositeMetricCalculator created")

    # Test with identical images (should be low score)
    result_identical = create_mock_result("identical.png", 0.0, 1.0, 0.0, 0.0)
    score_identical = calculator.calculate_composite_score(result_identical)
    print(f"  ✓ Identical images score: {score_identical:.2f} (expected: ~0)")

    if score_identical > 5.0:
        print("  ✗ Score too high for identical images!")
        return False

    # Test with very different images (should be high score)
    result_different = create_mock_result("different.png", 100.0, 0.0, 441.67, 2.0)
    score_different = calculator.calculate_composite_score(result_different)
    print(f"  ✓ Different images score: {score_different:.2f} (expected: ~100)")

    if score_different < 95.0:
        print("  ✗ Score too low for very different images!")
        return False

    # Test with moderate difference
    result_moderate = create_mock_result("moderate.png", 50.0, 0.5, 100.0, 1.0)
    score_moderate = calculator.calculate_composite_score(result_moderate)
    print(f"  ✓ Moderate difference score: {score_moderate:.2f} (expected: 30-70)")

    if not (30.0 < score_moderate < 70.0):
        print("  ✗ Score out of expected range!")
        return False

    # Test batch enrichment
    results = [result_identical, result_moderate, result_different]
    enriched = calculator.enrich_results_with_scores(results)

    if all(hasattr(r, 'composite_score') and r.composite_score is not None for r in enriched):
        print("  ✓ Batch enrichment works")
    else:
        print("  ✗ Batch enrichment failed!")
        return False

    print("✅ Phase 4: PASSED\n")
    return True


def test_phase_5_statistics():
    """Test Phase 5: Statistical Analysis Engine."""
    print("="*70)
    print("PHASE 5: STATISTICAL ANALYSIS ENGINE")
    print("="*70)

    calculator = StatisticsCalculator(anomaly_threshold=2.0, min_runs_for_stats=3)
    print("✓ StatisticsCalculator created")

    # Test stats calculation with sufficient data
    historical_scores = [10.0, 12.0, 11.0, 13.0, 10.5]
    stats = calculator.calculate_historical_stats(historical_scores)

    if stats:
        mean, std_dev = stats
        print(f"  ✓ Stats calculated: mean={mean:.2f}, std_dev={std_dev:.2f}")
    else:
        print("  ✗ Stats calculation failed!")
        return False

    # Test anomaly detection - normal value
    is_anomaly, deviation = calculator.detect_anomaly(11.5, mean, std_dev)
    print(f"  ✓ Normal value (11.5): anomaly={is_anomaly}, deviation={deviation:.2f}σ")

    if is_anomaly:
        print("  ✗ False positive: normal value flagged as anomaly!")
        return False

    # Test anomaly detection - outlier
    is_anomaly_outlier, deviation_outlier = calculator.detect_anomaly(50.0, mean, std_dev)
    print(f"  ✓ Outlier (50.0): anomaly={is_anomaly_outlier}, deviation={deviation_outlier:.2f}σ")

    if not is_anomaly_outlier:
        print("  ✗ False negative: outlier not detected!")
        return False

    # Test result enrichment
    result = create_mock_result("test.png", 50.0, 0.5, 100.0, 1.0)
    result.composite_score = 50.0

    enriched = calculator.enrich_result_with_statistics(result, historical_scores)

    if (hasattr(enriched, 'historical_mean') and
            enriched.historical_mean is not None and
            hasattr(enriched, 'is_anomaly')):
        print(f"  ✓ Result enrichment works: is_anomaly={enriched.is_anomaly}")
    else:
        print("  ✗ Result enrichment failed!")
        return False

    # Test trend detection
    increasing_scores = [10.0, 15.0, 20.0, 25.0, 30.0]
    trend = calculator.get_trend_direction(increasing_scores)
    print(f"  ✓ Trend detection: {trend} (expected: increasing)")

    if trend != "increasing":
        print("  ✗ Trend detection wrong!")
        return False

    print("✅ Phase 5: PASSED\n")
    return True


def test_integration_end_to_end():
    """Test complete integration of Phases 1-5."""
    print("="*70)
    print("END-TO-END INTEGRATION TEST (Phases 1-5)")
    print("="*70)

    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)

        # Create config
        config = Config(
            base_dir=base_dir,
            new_dir="new",
            known_good_dir="known_good",
            enable_history=True,
            build_number="integration-test",
            anomaly_threshold=2.0
        )
        print("✓ Config created")

        # Initialize history manager
        manager = HistoryManager(config)
        print("✓ HistoryManager initialized")

        # Simulate 5 historical runs with consistent scores
        print("\n✓ Creating historical baseline (5 runs)...")
        for i in range(5):
            results = [
                create_mock_result("stable_image.png", 10.0 + i*0.5, 0.95, 15.0, 0.3),
                create_mock_result("variable_image.png", 20.0 + i*2.0, 0.85, 30.0, 0.6),
            ]
            run_id = manager.save_run(results, config, notes=f"Historical run {i+1}")
            print(f"  ✓ Run {i+1} saved (ID: {run_id})")

        # Create current run with one anomaly
        print("\n✓ Creating current run with anomaly...")
        current_results = [
            create_mock_result("stable_image.png", 11.0, 0.95, 15.0, 0.3),  # Normal
            create_mock_result("variable_image.png", 80.0, 0.30, 200.0, 1.8),  # ANOMALY!
        ]

        # Enrich with history
        print("✓ Enriching results with historical statistics...")
        enriched_results = manager.enrich_with_history(current_results)

        # Verify enrichment
        print("\n✓ Checking results:")
        for result in enriched_results:
            if hasattr(result, 'composite_score') and result.composite_score is not None:
                print(f"  • {result.filename}:")
                print(f"      Composite score: {result.composite_score:.2f}")

                if hasattr(result, 'historical_mean') and result.historical_mean is not None:
                    print(f"      Historical mean: {result.historical_mean:.2f}")
                    print(f"      Std deviation: {result.historical_std_dev:.2f}")
                    print(f"      Deviation: {result.std_dev_from_mean:.2f}σ")
                    print(f"      Anomaly: {'⚠️  YES' if result.is_anomaly else '✓  No'}")
                else:
                    print("      (Insufficient historical data)")
            else:
                print(f"  ✗ {result.filename}: No composite score!")
                return False

        # Verify anomaly detection worked
        anomalies = [r for r in enriched_results if hasattr(r, 'is_anomaly') and r.is_anomaly]
        if len(anomalies) > 0:
            print(f"\n✅ Detected {len(anomalies)} anomaly (expected: 1)")
            print(f"   Anomalous image: {anomalies[0].filename}")
        else:
            print("\n✗ No anomalies detected (expected 1)!")
            return False

        manager.close()
        print("\n✅ END-TO-END INTEGRATION: PASSED\n")
        return True


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("HISTORICAL TRACKING INTEGRATION TEST (Phases 1-5)")
    print("Testing all components before Phase 6 integration")
    print("="*70)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    tests = [
        ("Phase 1: Database Foundation", test_phase_1_database),
        ("Phase 2: History Manager Core", test_phase_2_history_manager),
        ("Phase 3: Configuration Integration", test_phase_3_configuration),
        ("Phase 4: Composite Metric Calculator", test_phase_4_composite_metric),
        ("Phase 5: Statistical Analysis Engine", test_phase_5_statistics),
        ("End-to-End Integration", test_integration_end_to_end),
    ]

    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n❌ {name} CRASHED: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {name}")

    total = len(results)
    passed_count = sum(1 for _, p in results if p)

    print(f"\nTotal: {passed_count}/{total} tests passed ({passed_count/total*100:.0f}%)")
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")

    if passed_count == total:
        print("🎉 ALL TESTS PASSED! Ready for Phase 6 integration.")
        return 0
    else:
        print("⚠️  SOME TESTS FAILED. Please review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
