"""
Configuration module for Image Comparison Tool.

Provides centralized configuration management for image comparison operations,
including paths, tolerances, and visual settings.
"""

from pathlib import Path
from dataclasses import dataclass
from typing import Tuple, Optional, Dict


@dataclass
class HistogramConfig:
    """Configuration settings for histogram visualization.

    Controls the visual appearance and data representation of histogram comparisons.
    """

    # Data representation
    bins: int = 256
    """Number of histogram bins for intensity distribution (64-512)."""

    # Visual layout
    figure_width: float = 16
    """Histogram figure width in inches."""
    figure_height: float = 6
    """Histogram figure height in inches."""
    dpi: int = 100
    """Resolution for histogram rendering (dots per inch)."""

    # Line styling
    grayscale_alpha: float = 0.7
    """Transparency for grayscale histogram line (0-1)."""
    rgb_alpha: float = 0.7
    """Transparency for RGB channel lines (0-1)."""
    grayscale_linewidth: float = 2.0
    """Line width for grayscale histogram."""
    rgb_linewidth: float = 1.5
    """Line width for RGB channel histograms."""
    grid_alpha: float = 0.3
    """Grid transparency (0-1)."""

    # Title and labels
    title: str = "Histogram Comparison - Grayscale & RGB Channels"
    """Histogram display title."""

    # Colors
    grayscale_color: str = "black"
    """Color for grayscale histogram (named color or hex)."""
    rgb_colors: Tuple[str, str, str] = ("red", "green", "blue")
    """Colors for RGB channels."""

    # Feature toggles
    show_grayscale: bool = True
    """Whether to display grayscale histogram."""
    show_rgb: bool = True
    """Whether to display RGB channel histograms."""


@dataclass
class Config:
    """Configuration settings for image comparison.

    Manages all configuration parameters for the image comparison process,
    including directory paths, tolerance thresholds, and visual settings.
    """

    base_dir: Path
    """Base directory for all operations."""
    new_dir: str
    """Directory containing new images (relative to base_dir)."""
    known_good_dir: str
    """Directory containing reference images (relative to base_dir)."""
    diff_dir: str = "diffs"
    """Directory for diff outputs (relative to base_dir)."""
    html_dir: str = "reports"
    """Directory for HTML reports (relative to base_dir)."""

    # Tolerances for different metrics
    pixel_diff_threshold: float = 0.01
    """Minimum % difference to flag image as different."""
    pixel_change_threshold: int = 1
    """Minimum pixel value change to count as different."""
    ssim_threshold: float = 0.95
    """Minimum SSIM to consider images similar (0-1)."""
    color_distance_threshold: float = 10.0
    """RGB color distance threshold for significant changes."""
    min_contour_area: int = 50
    """Minimum area for bounding boxes."""

    # Histogram equalization
    use_histogram_equalization: bool = True
    """Whether to apply histogram equalization during processing."""
    use_clahe: bool = True
    """Whether to use CLAHE (Contrast Limited Adaptive Histogram Equalization) instead of standard equalization."""
    equalize_to_grayscale: bool = False
    """Whether to convert to grayscale before equalization for more aggressive tonal normalization."""

    # Visual settings
    highlight_color: Tuple[int, int, int] = (255, 0, 0)
    """RGB color for bounding boxes highlighting differences."""
    diff_enhancement_factor: float = 5.0
    """Contrast enhancement multiplier for difference visualization."""

    # Histogram visualization
    histogram_config: Optional[HistogramConfig] = None
    """Configuration for histogram visualization."""

    # Parallel processing settings
    enable_parallel: bool = False
    """Whether to use parallel processing for image comparisons."""
    max_workers: Optional[int] = None
    """Maximum number of worker processes. None = use CPU count."""

    # Historical tracking settings
    enable_history: bool = True
    """Whether to enable historical metrics tracking."""
    build_number: Optional[str] = None
    """Build number or identifier for this comparison run."""
    history_db_path: Optional[Path] = None
    """Custom path to history database. None = use default (<base_dir>/.imgcomp_history/comparison_history.db)."""

    # Composite metric configuration
    composite_metric_weights: Optional[Dict[str, float]] = None
    """Custom weights for composite metric calculation. None = use equal weights (0.25 each)."""
    anomaly_threshold: float = 2.0
    """Standard deviation threshold for anomaly detection (default: 2.0 = 95% confidence)."""

    # Retention policy settings
    retention_keep_all: bool = True
    """Whether to keep all historical runs (True = unlimited retention)."""
    retention_max_runs: Optional[int] = None
    """Maximum number of runs to keep. None = unlimited."""
    retention_max_age_days: Optional[int] = None
    """Maximum age of runs in days. None = unlimited."""
    retention_keep_annotated: bool = True
    """Whether to always preserve runs with annotations during cleanup."""
    retention_keep_anomalies: bool = True
    """Whether to always preserve runs with detected anomalies during cleanup."""

    # Source code tracking
    commit_hash: Optional[str] = None
    """Git commit hash for reproducibility. Allows recreating the exact environment that generated this run."""

    def __post_init__(self) -> None:
        """Convert string paths to Path objects and validate.

        Called after dataclass initialization to ensure paths are Path objects
        and that the base directory exists.
        """
        if isinstance(self.base_dir, str):
            self.base_dir = Path(self.base_dir)

        # Initialize default histogram config if not provided
        if self.histogram_config is None:
            self.histogram_config = HistogramConfig()

        # Ensure base directory exists
        self.base_dir.mkdir(parents=True, exist_ok=True)

        # Convert history_db_path to Path if it's a string
        if isinstance(self.history_db_path, str):
            self.history_db_path = Path(self.history_db_path)

    @property
    def new_path(self) -> Path:
        """Return full path to new images directory.

        Returns:
            Path object for new images directory
        """
        return self.base_dir / self.new_dir

    @property
    def known_good_path(self) -> Path:
        """Return full path to known good images directory.

        Returns:
            Path object for known good images directory
        """
        return self.base_dir / self.known_good_dir

    @property
    def diff_path(self) -> Path:
        """Return full path to diff outputs directory.

        Returns:
            Path object for diff outputs directory
        """
        return self.base_dir / self.diff_dir

    @property
    def html_path(self) -> Path:
        """Return full path to HTML reports directory.

        Returns:
            Path object for HTML reports directory
        """
        return self.base_dir / self.html_dir

    def validate(self) -> Tuple[bool, str]:
        """Validate configuration settings.

        Checks that all required directories exist and are not empty.

        Returns:
            Tuple of (is_valid: bool, error_message: str)
                - is_valid: True if all checks pass, False otherwise
                - error_message: Descriptive message if validation fails, empty string if valid
        """
        if not self.new_path.exists():
            return False, f"New images directory does not exist: {self.new_path}"

        if not self.known_good_path.exists():
            return False, f"Known good directory does not exist: {self.known_good_path}"

        # Ensure there is at least one file somewhere under the directories (recursive)
        try:
            has_new_files = any(p.is_file() for p in self.new_path.rglob("*"))
        except Exception:
            has_new_files = False

        try:
            has_known_files = any(p.is_file() for p in self.known_good_path.rglob("*"))
        except Exception:
            has_known_files = False

        if not has_new_files:
            return (
                False,
                f"New images directory is empty (no files found): {self.new_path}",
            )

        if not has_known_files:
            return (
                False,
                f"Known good directory is empty (no files found): {self.known_good_path}",
            )

        return True, ""
