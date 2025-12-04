"""
Trend chart generator for historical metrics visualization.

Generates matplotlib charts showing composite score trends over time and anomaly detection.
"""

import logging
import base64
from io import BytesIO
from typing import List, Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import matplotlib, but don't fail if not available
try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logger.warning("matplotlib not available - chart generation disabled")


class TrendChartGenerator:
    """
    Generates trend charts for historical metrics data.

    Creates line charts for composite scores over time and scatter plots
    for anomaly visualization. Charts are returned as base64-encoded PNG images.
    """

    def __init__(self, figsize: tuple = (10, 6), dpi: int = 100):
        """
        Initialize chart generator.

        Args:
            figsize: Figure size in inches (width, height)
            dpi: Dots per inch for rasterization

        Example:
            >>> generator = TrendChartGenerator(figsize=(12, 8))
        """
        self.figsize = figsize
        self.dpi = dpi

        if not MATPLOTLIB_AVAILABLE:
            logger.warning("TrendChartGenerator initialized but matplotlib not available")

    def generate_trend_chart(
        self,
        historical_data: List[Dict[str, Any]],
        filename: str,
        title: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate line chart showing composite score trend over time.

        Args:
            historical_data: List of dicts with 'timestamp', 'composite_score', 'is_anomaly'
            filename: Image filename for chart title
            title: Optional custom title

        Returns:
            Base64-encoded PNG image string, or None if generation fails

        Example:
            >>> data = [
            ...     {'timestamp': '2025-01-01T10:00:00', 'composite_score': 10.5, 'is_anomaly': False},
            ...     {'timestamp': '2025-01-02T10:00:00', 'composite_score': 45.2, 'is_anomaly': True}
            ... ]
            >>> chart = generator.generate_trend_chart(data, "test.png")
        """
        if not MATPLOTLIB_AVAILABLE:
            logger.debug("Skipping chart generation - matplotlib not available")
            return None

        if not historical_data or len(historical_data) < 2:
            logger.debug(f"Insufficient data for trend chart: {len(historical_data) if historical_data else 0} points")
            return None

        try:
            # Extract data
            timestamps = []
            scores = []
            anomalies = []

            for entry in historical_data:
                try:
                    # Parse timestamp
                    ts_str = entry.get('timestamp')
                    if ts_str:
                        # Handle both ISO format and datetime objects
                        if isinstance(ts_str, str):
                            ts = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                        else:
                            ts = ts_str
                        timestamps.append(ts)
                        scores.append(entry.get('composite_score', 0))
                        anomalies.append(entry.get('is_anomaly', False))
                except (ValueError, AttributeError) as e:
                    logger.debug(f"Skipping invalid entry: {e}")
                    continue

            if len(timestamps) < 2:
                logger.debug("Not enough valid data points after parsing")
                return None

            # Create figure
            fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)

            # Plot trend line
            ax.plot(timestamps, scores, marker='o', linestyle='-', linewidth=2,
                   markersize=6, color='#2E86AB', label='Composite Score')

            # Highlight anomalies
            anomaly_timestamps = [ts for ts, is_anom in zip(timestamps, anomalies) if is_anom]
            anomaly_scores = [score for score, is_anom in zip(scores, anomalies) if is_anom]

            if anomaly_timestamps:
                ax.scatter(anomaly_timestamps, anomaly_scores, color='#E63946',
                          s=150, marker='X', zorder=5, label='Anomalies', edgecolors='black')

            # Calculate mean line
            if scores:
                mean_score = sum(scores) / len(scores)
                ax.axhline(y=mean_score, color='#06A77D', linestyle='--',
                          linewidth=1.5, alpha=0.7, label=f'Mean: {mean_score:.1f}')

            # Formatting
            ax.set_xlabel('Date', fontsize=11, fontweight='bold')
            ax.set_ylabel('Composite Score', fontsize=11, fontweight='bold')

            if title:
                ax.set_title(title, fontsize=13, fontweight='bold', pad=15)
            else:
                ax.set_title(f'Historical Trend: {filename}', fontsize=13, fontweight='bold', pad=15)

            # Format x-axis dates
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            fig.autofmt_xdate()  # Rotate labels

            # Grid and legend
            ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.5)
            ax.legend(loc='best', framealpha=0.9)

            # Tight layout
            plt.tight_layout()

            # Convert to base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=self.dpi, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            plt.close(fig)

            logger.debug(f"Generated trend chart for {filename}: {len(timestamps)} data points")
            return image_base64

        except Exception as e:
            logger.error(f"Failed to generate trend chart: {e}")
            return None

    def generate_anomaly_scatter(
        self,
        results: List[Any],
        title: str = "Anomaly Detection Overview"
    ) -> Optional[str]:
        """
        Generate scatter plot showing all results with anomalies highlighted.

        Args:
            results: List of ComparisonResult objects with composite_score and is_anomaly
            title: Chart title

        Returns:
            Base64-encoded PNG image string, or None if generation fails

        Example:
            >>> chart = generator.generate_anomaly_scatter(results, "Current Run Anomalies")
        """
        if not MATPLOTLIB_AVAILABLE:
            logger.debug("Skipping scatter plot - matplotlib not available")
            return None

        if not results:
            logger.debug("No results for scatter plot")
            return None

        try:
            # Extract data
            normal_scores = []
            normal_names = []
            anomaly_scores = []
            anomaly_names = []

            for idx, result in enumerate(results):
                if not hasattr(result, 'composite_score') or result.composite_score is None:
                    continue

                score = result.composite_score
                name = result.filename if hasattr(result, 'filename') else f"Image {idx}"
                is_anom = getattr(result, 'is_anomaly', False)

                if is_anom:
                    anomaly_scores.append((idx, score))
                    anomaly_names.append(name)
                else:
                    normal_scores.append((idx, score))
                    normal_names.append(name)

            if not normal_scores and not anomaly_scores:
                logger.debug("No valid data for scatter plot")
                return None

            # Create figure
            fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)

            # Plot normal results
            if normal_scores:
                indices, scores = zip(*normal_scores)
                ax.scatter(indices, scores, color='#2E86AB', s=60, alpha=0.6,
                          label=f'Normal ({len(normal_scores)})', edgecolors='black', linewidth=0.5)

            # Plot anomalies
            if anomaly_scores:
                indices, scores = zip(*anomaly_scores)
                ax.scatter(indices, scores, color='#E63946', s=150, marker='X',
                          label=f'Anomalies ({len(anomaly_scores)})', edgecolors='black', linewidth=1.5, zorder=5)

            # Calculate thresholds if we have anomalies with historical data
            all_with_stats = [r for r in results
                            if hasattr(r, 'historical_mean') and r.historical_mean is not None]

            if all_with_stats:
                # Use first result's historical stats (same for all images from same run)
                sample = all_with_stats[0]
                mean = sample.historical_mean
                std = sample.historical_std_dev

                if mean is not None and std is not None:
                    threshold = 2.0  # Default anomaly threshold
                    upper_bound = mean + (threshold * std)
                    lower_bound = mean - (threshold * std)

                    ax.axhline(y=upper_bound, color='#FF6B6B', linestyle='--',
                              linewidth=1.5, alpha=0.5, label=f'+2σ threshold')
                    ax.axhline(y=mean, color='#06A77D', linestyle='-',
                              linewidth=2, alpha=0.7, label=f'Historical mean')
                    if lower_bound > 0:
                        ax.axhline(y=lower_bound, color='#FF6B6B', linestyle='--',
                                  linewidth=1.5, alpha=0.5, label=f'-2σ threshold')

            # Formatting
            ax.set_xlabel('Image Index', fontsize=11, fontweight='bold')
            ax.set_ylabel('Composite Score', fontsize=11, fontweight='bold')
            ax.set_title(title, fontsize=13, fontweight='bold', pad=15)

            # Grid and legend
            ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.5)
            ax.legend(loc='best', framealpha=0.9, fontsize=9)

            # Tight layout
            plt.tight_layout()

            # Convert to base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=self.dpi, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            plt.close(fig)

            logger.debug(f"Generated anomaly scatter plot: {len(results)} results")
            return image_base64

        except Exception as e:
            logger.error(f"Failed to generate anomaly scatter: {e}")
            return None

    def generate_summary_histogram(
        self,
        results: List[Any],
        title: str = "Composite Score Distribution"
    ) -> Optional[str]:
        """
        Generate histogram showing distribution of composite scores.

        Args:
            results: List of ComparisonResult objects with composite_score
            title: Chart title

        Returns:
            Base64-encoded PNG image string, or None if generation fails
        """
        if not MATPLOTLIB_AVAILABLE:
            logger.debug("Skipping histogram - matplotlib not available")
            return None

        if not results:
            logger.debug("No results for histogram")
            return None

        try:
            # Extract scores
            scores = [r.composite_score for r in results
                     if hasattr(r, 'composite_score') and r.composite_score is not None]

            if len(scores) < 3:
                logger.debug("Not enough scores for histogram")
                return None

            # Create figure
            fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)

            # Create histogram
            n, bins, patches = ax.hist(scores, bins=20, color='#2E86AB',
                                      alpha=0.7, edgecolor='black', linewidth=1)

            # Color anomalies differently
            anomaly_threshold = 2.0
            for result in results:
                if (hasattr(result, 'is_anomaly') and result.is_anomaly and
                    hasattr(result, 'composite_score') and result.composite_score is not None):
                    score = result.composite_score
                    # Find which bin this falls into
                    for i, (bin_start, bin_end) in enumerate(zip(bins[:-1], bins[1:])):
                        if bin_start <= score < bin_end:
                            patches[i].set_facecolor('#E63946')
                            break

            # Add mean line
            mean_score = sum(scores) / len(scores)
            ax.axvline(x=mean_score, color='#06A77D', linestyle='--',
                      linewidth=2, label=f'Mean: {mean_score:.1f}')

            # Formatting
            ax.set_xlabel('Composite Score', fontsize=11, fontweight='bold')
            ax.set_ylabel('Frequency', fontsize=11, fontweight='bold')
            ax.set_title(title, fontsize=13, fontweight='bold', pad=15)

            # Grid and legend
            ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.5, axis='y')
            ax.legend(loc='best', framealpha=0.9)

            # Tight layout
            plt.tight_layout()

            # Convert to base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=self.dpi, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            plt.close(fig)

            logger.debug(f"Generated histogram: {len(scores)} scores")
            return image_base64

        except Exception as e:
            logger.error(f"Failed to generate histogram: {e}")
            return None
