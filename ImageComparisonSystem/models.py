"""
Data models for image comparison results.

Provides dataclasses for storing and serializing image comparison results
and related metadata.
"""

from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass, asdict


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
            if parent == Path('.'):
                return ''  # Root level
            return str(parent).replace('\\', '/')
        except ValueError:
            return ''

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
        data['new_image_path'] = str(data['new_image_path'])
        data['known_good_path'] = str(data['known_good_path'])
        data['diff_image_path'] = str(data['diff_image_path'])
        data['annotated_image_path'] = str(data['annotated_image_path'])

        # Include subdirectory if base_path provided
        if base_path:
            data['subdirectory'] = self.get_subdirectory(base_path)

        return data
