"""
Data models for image comparison results.

Provides dataclasses for storing and serializing image comparison results
and related metadata.
"""

from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict, field


@dataclass
class ComparisonResult:
    """Results from comparing a single image pair.

    Stores comprehensive results from comparing two images, including
    file paths, metrics, and generated visualization data.
    """

    filename: str
    """Name of the compared image files."""
    new_image_path: Path
    """Path to the new image."""
    known_good_path: Path
    """Path to the reference (known good) image."""
    diff_image_path: Path
    """Path to the generated difference image."""
    annotated_image_path: Path
    """Path to the generated annotated image."""
    metrics: Dict[str, Any]
    """Dictionary of analysis metrics from all analyzers."""
    percent_different: float
    """Overall percentage difference between images."""
    histogram_data: str
    """Base64 encoded histogram comparison image."""

    # Historical tracking fields (optional, populated by history system)
    composite_score: Optional[float] = field(default=None)
    """Composite score from weighted combination of all metrics (0-100 scale)."""
    historical_mean: Optional[float] = field(default=None)
    """Historical mean of composite scores for this image."""
    historical_std_dev: Optional[float] = field(default=None)
    """Historical standard deviation of composite scores for this image."""
    std_dev_from_mean: Optional[float] = field(default=None)
    """Number of standard deviations current score is from historical mean."""
    is_anomaly: Optional[bool] = field(default=False)
    """Whether this result is flagged as a statistical anomaly."""
    run_id: Optional[int] = field(default=None)
    """Database run ID if result was saved to history."""

    def get_subdirectory(self, base_path: Path) -> str:
        """Get subdirectory relative to base path.

        Extracts the subdirectory component from the new_image_path relative
        to the specified base path. This is used for organizing reports by
        directory structure.

        Args:
            base_path: Base directory (e.g., config.new_path)

        Returns:
            Subdirectory path as string with forward slashes, or empty string
            for root-level images

        Example:
            If new_image_path is /base/new/renders/scene1/image.png
            and base_path is /base/new
            Returns: "renders/scene1"
        """
        try:
            rel_path = self.new_image_path.relative_to(base_path)
            parent = rel_path.parent
            if parent == Path("."):
                return ""  # Root level
            return str(parent).replace("\\", "/")
        except ValueError:
            return ""

    def to_dict(self, base_path: Path = None) -> Dict[str, Any]:
        """Convert to dictionary for serialization.

        Converts the dataclass to a dictionary suitable for JSON serialization,
        converting Path objects to strings. Optionally includes subdirectory
        information if base_path is provided.

        Args:
            base_path: Optional base path for computing subdirectory

        Returns:
            Dictionary representation with Path objects converted to strings
        """
        data: Dict[str, Any] = asdict(self)
        # Convert Path objects to strings
        data["new_image_path"] = str(data["new_image_path"])
        data["known_good_path"] = str(data["known_good_path"])
        data["diff_image_path"] = str(data["diff_image_path"])
        data["annotated_image_path"] = str(data["annotated_image_path"])

        # Include subdirectory if base_path provided
        if base_path:
            data["subdirectory"] = self.get_subdirectory(base_path)

        # Include historical tracking fields if present
        # (these are optional and may be None)
        if self.composite_score is not None:
            data["composite_score"] = self.composite_score
        if self.historical_mean is not None:
            data["historical_mean"] = self.historical_mean
        if self.historical_std_dev is not None:
            data["historical_std_dev"] = self.historical_std_dev
        if self.std_dev_from_mean is not None:
            data["std_dev_from_mean"] = self.std_dev_from_mean
        if self.is_anomaly is not None:
            data["is_anomaly"] = self.is_anomaly
        if self.run_id is not None:
            data["run_id"] = self.run_id

        return data
