"""
Retention policy management for historical data cleanup.

Provides configurable retention policies to manage database growth while
preserving important data like anomalies and annotated results.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple

logger = logging.getLogger(__name__)

# Try to import Database
try:
    from .database import Database
except ImportError:
    from database import Database  # type: ignore


class RetentionPolicy:
    """
    Manages retention policies for historical comparison data.

    Provides flexible cleanup strategies to control database size while
    ensuring important data (anomalies, annotations) is preserved.
    """

    def __init__(
        self,
        database: Database,
        keep_all_runs: bool = True,
        max_runs_to_keep: Optional[int] = None,
        max_age_days: Optional[int] = None,
        keep_annotated: bool = True,
        keep_anomalies: bool = True,
    ):
        """
        Initialize retention policy.

        Args:
            database: Database instance for executing queries
            keep_all_runs: If True, never delete any runs (default)
            max_runs_to_keep: Maximum number of runs to retain (oldest deleted first)
            max_age_days: Maximum age in days for runs (older runs deleted)
            keep_annotated: Always preserve runs with annotated results
            keep_anomalies: Always preserve runs with detected anomalies

        Example:
            >>> db = Database("history.db")
            >>> # Keep last 30 days, preserve anomalies
            >>> policy = RetentionPolicy(db, keep_all_runs=False, max_age_days=30)
            >>> deleted = policy.apply_retention()
        """
        self.database = database
        self.keep_all_runs = keep_all_runs
        self.max_runs_to_keep = max_runs_to_keep
        self.max_age_days = max_age_days
        self.keep_annotated = keep_annotated
        self.keep_anomalies = keep_anomalies

        logger.debug(
            f"RetentionPolicy initialized: keep_all={keep_all_runs}, "
            f"max_runs={max_runs_to_keep}, max_age_days={max_age_days}"
        )

    def apply_retention(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Apply retention policy and delete old runs.

        Args:
            dry_run: If True, only report what would be deleted without actually deleting

        Returns:
            Dictionary with statistics:
                - runs_evaluated: Total number of runs in database
                - runs_eligible: Runs eligible for deletion
                - runs_protected: Runs protected by policy
                - runs_deleted: Number of runs actually deleted
                - run_ids_deleted: List of deleted run IDs

        Example:
            >>> # See what would be deleted
            >>> stats = policy.apply_retention(dry_run=True)
            >>> print(f"Would delete {stats['runs_eligible']} runs")
            >>> # Actually delete
            >>> stats = policy.apply_retention(dry_run=False)
        """
        if self.keep_all_runs:
            logger.info("Retention policy: keep_all_runs=True, skipping cleanup")
            return {
                "runs_evaluated": self._count_total_runs(),
                "runs_eligible": 0,
                "runs_protected": self._count_total_runs(),
                "runs_deleted": 0,
                "run_ids_deleted": [],
            }

        # Get all runs ordered by timestamp (oldest first)
        runs = self._get_all_runs()
        total_runs = len(runs)
        logger.info(f"Evaluating {total_runs} runs for retention cleanup")

        # Identify runs eligible for deletion
        eligible_run_ids = self._identify_eligible_runs(runs)

        # Filter out protected runs
        protected_run_ids = self._identify_protected_runs(eligible_run_ids)
        deletable_run_ids = [rid for rid in eligible_run_ids if rid not in protected_run_ids]

        logger.info(
            f"Retention analysis: {len(eligible_run_ids)} eligible, "
            f"{len(protected_run_ids)} protected, {len(deletable_run_ids)} will be deleted"
        )

        # Log protected runs
        if protected_run_ids:
            for run_id in protected_run_ids:
                reason = self._get_protection_reason(run_id)
                logger.info(f"  Protected run {run_id}: {reason}")

        # Delete runs (unless dry run)
        deleted_count = 0
        deleted_ids = []

        if not dry_run and deletable_run_ids:
            deleted_count, deleted_ids = self._delete_runs(deletable_run_ids)
            logger.info(f"Deleted {deleted_count} runs from database")
        elif dry_run and deletable_run_ids:
            logger.info(f"DRY RUN: Would delete {len(deletable_run_ids)} runs")
            deleted_ids = deletable_run_ids

        return {
            "runs_evaluated": total_runs,
            "runs_eligible": len(eligible_run_ids),
            "runs_protected": len(protected_run_ids),
            "runs_deleted": deleted_count,
            "run_ids_deleted": deleted_ids,
        }

    def _count_total_runs(self) -> int:
        """Count total number of runs in database."""
        try:
            rows = self.database.execute_query("SELECT COUNT(*) as count FROM runs")
            return rows[0]["count"] if rows else 0
        except Exception as e:
            logger.error(f"Failed to count runs: {e}")
            return 0

    def _get_all_runs(self) -> List[Dict[str, Any]]:
        """Get all runs ordered by timestamp (oldest first)."""
        try:
            return self.database.execute_query(
                "SELECT run_id, timestamp, build_number FROM runs ORDER BY timestamp ASC"
            )
        except Exception as e:
            logger.error(f"Failed to fetch runs: {e}")
            return []

    def _identify_eligible_runs(self, runs: List[Dict[str, Any]]) -> List[int]:
        """
        Identify runs eligible for deletion based on age and count limits.

        Args:
            runs: List of all runs (oldest first)

        Returns:
            List of run IDs eligible for deletion
        """
        eligible = []

        # Apply max_runs_to_keep limit
        if self.max_runs_to_keep is not None and len(runs) > self.max_runs_to_keep:
            # Delete oldest runs beyond the limit
            runs_to_delete = len(runs) - self.max_runs_to_keep
            for run in runs[:runs_to_delete]:
                eligible.append(run["run_id"])
            logger.debug(f"max_runs_to_keep: {runs_to_delete} runs eligible")

        # Apply max_age_days limit
        if self.max_age_days is not None:
            cutoff_date = datetime.now() - timedelta(days=self.max_age_days)
            age_eligible = 0

            for run in runs:
                try:
                    # Parse timestamp (ISO format)
                    run_timestamp = datetime.fromisoformat(
                        run["timestamp"].replace("Z", "+00:00")
                    )

                    if run_timestamp < cutoff_date:
                        if run["run_id"] not in eligible:
                            eligible.append(run["run_id"])
                            age_eligible += 1
                except (ValueError, AttributeError) as e:
                    logger.warning(f"Failed to parse timestamp for run {run['run_id']}: {e}")
                    continue

            logger.debug(f"max_age_days: {age_eligible} runs eligible")

        return eligible

    def _identify_protected_runs(self, eligible_run_ids: List[int]) -> List[int]:
        """
        Identify runs that should be protected from deletion.

        Args:
            eligible_run_ids: List of run IDs eligible for deletion

        Returns:
            List of run IDs that should be protected
        """
        if not eligible_run_ids:
            return []

        protected = []

        # Protect runs with annotations
        if self.keep_annotated:
            annotated_runs = self._get_runs_with_annotations(eligible_run_ids)
            protected.extend(annotated_runs)
            if annotated_runs:
                logger.debug(f"Protected {len(annotated_runs)} runs with annotations")

        # Protect runs with anomalies
        if self.keep_anomalies:
            anomaly_runs = self._get_runs_with_anomalies(eligible_run_ids)
            protected.extend(anomaly_runs)
            if anomaly_runs:
                logger.debug(f"Protected {len(anomaly_runs)} runs with anomalies")

        return list(set(protected))  # Remove duplicates

    def _get_runs_with_annotations(self, run_ids: List[int]) -> List[int]:
        """Get run IDs that have annotated results."""
        if not run_ids:
            return []

        try:
            placeholders = ",".join("?" * len(run_ids))
            query = f"""
                SELECT DISTINCT r.run_id
                FROM results r
                JOIN annotations a ON r.result_id = a.result_id
                WHERE r.run_id IN ({placeholders})
            """
            rows = self.database.execute_query(query, tuple(run_ids))
            return [row["run_id"] for row in rows]
        except Exception as e:
            logger.error(f"Failed to query annotated runs: {e}")
            return []

    def _get_runs_with_anomalies(self, run_ids: List[int]) -> List[int]:
        """Get run IDs that have anomalous results."""
        if not run_ids:
            return []

        try:
            placeholders = ",".join("?" * len(run_ids))
            query = f"""
                SELECT DISTINCT run_id
                FROM results
                WHERE run_id IN ({placeholders}) AND is_anomaly = 1
            """
            rows = self.database.execute_query(query, tuple(run_ids))
            return [row["run_id"] for row in rows]
        except Exception as e:
            logger.error(f"Failed to query anomalous runs: {e}")
            return []

    def _get_protection_reason(self, run_id: int) -> str:
        """Get reason why a run is protected from deletion."""
        reasons = []

        # Check for annotations
        try:
            query = """
                SELECT COUNT(*) as count
                FROM results r
                JOIN annotations a ON r.result_id = a.result_id
                WHERE r.run_id = ?
            """
            rows = self.database.execute_query(query, (run_id,))
            if rows and rows[0]["count"] > 0:
                reasons.append(f"{rows[0]['count']} annotations")
        except Exception:
            pass

        # Check for anomalies
        try:
            query = """
                SELECT COUNT(*) as count
                FROM results
                WHERE run_id = ? AND is_anomaly = 1
            """
            rows = self.database.execute_query(query, (run_id,))
            if rows and rows[0]["count"] > 0:
                reasons.append(f"{rows[0]['count']} anomalies")
        except Exception:
            pass

        return ", ".join(reasons) if reasons else "unknown"

    def _delete_runs(self, run_ids: List[int]) -> Tuple[int, List[int]]:
        """
        Delete runs from database.

        Args:
            run_ids: List of run IDs to delete

        Returns:
            Tuple of (number deleted, list of deleted IDs)
        """
        if not run_ids:
            return (0, [])

        deleted_count = 0
        deleted_ids = []

        try:
            with self.database.get_connection() as conn:
                cursor = conn.cursor()

                for run_id in run_ids:
                    try:
                        # Delete run (CASCADE will delete related results)
                        cursor.execute("DELETE FROM runs WHERE run_id = ?", (run_id,))

                        if cursor.rowcount > 0:
                            deleted_count += 1
                            deleted_ids.append(run_id)
                            logger.debug(f"Deleted run {run_id}")

                    except Exception as e:
                        logger.error(f"Failed to delete run {run_id}: {e}")
                        continue

                conn.commit()

        except Exception as e:
            logger.error(f"Failed to delete runs: {e}")
            return (0, [])

        return (deleted_count, deleted_ids)

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics for retention analysis.

        Returns:
            Dictionary with database statistics:
                - total_runs: Total number of runs
                - total_results: Total number of results
                - annotated_runs: Number of runs with annotations
                - anomalous_runs: Number of runs with anomalies
                - oldest_run: Timestamp of oldest run
                - newest_run: Timestamp of newest run
        """
        stats = {
            "total_runs": 0,
            "total_results": 0,
            "annotated_runs": 0,
            "anomalous_runs": 0,
            "oldest_run": None,
            "newest_run": None,
        }

        try:
            # Total runs
            rows = self.database.execute_query("SELECT COUNT(*) as count FROM runs")
            stats["total_runs"] = rows[0]["count"] if rows else 0

            # Total results
            rows = self.database.execute_query("SELECT COUNT(*) as count FROM results")
            stats["total_results"] = rows[0]["count"] if rows else 0

            # Annotated runs
            rows = self.database.execute_query("""
                SELECT COUNT(DISTINCT r.run_id) as count
                FROM results r
                JOIN annotations a ON r.result_id = a.result_id
            """)
            stats["annotated_runs"] = rows[0]["count"] if rows else 0

            # Anomalous runs
            rows = self.database.execute_query("""
                SELECT COUNT(DISTINCT run_id) as count
                FROM results
                WHERE is_anomaly = 1
            """)
            stats["anomalous_runs"] = rows[0]["count"] if rows else 0

            # Date range
            rows = self.database.execute_query("""
                SELECT MIN(timestamp) as oldest, MAX(timestamp) as newest
                FROM runs
            """)
            if rows and rows[0]["oldest"]:
                stats["oldest_run"] = rows[0]["oldest"]
                stats["newest_run"] = rows[0]["newest"]

        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")

        return stats
