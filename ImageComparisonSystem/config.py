"""
Configuration module for Image Comparison Tool.

Provides centralized configuration management for image comparison operations,
including paths, tolerances, and visual settings.
"""

from pathlib import Path
from dataclasses import dataclass
from typing import Tuple


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
    diff_dir: str = 'diffs'
    """Directory for diff outputs (relative to base_dir)."""
    html_dir: str = 'reports'
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
    
    def __post_init__(self) -> None:
        """Convert string paths to Path objects and validate.
        
        Called after dataclass initialization to ensure paths are Path objects
        and that the base directory exists.
        """
        if isinstance(self.base_dir, str):
            self.base_dir = Path(self.base_dir)
        
        # Ensure base directory exists
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
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
            has_new_files = any(p.is_file() for p in self.new_path.rglob('*'))
        except Exception:
            has_new_files = False

        try:
            has_known_files = any(p.is_file() for p in self.known_good_path.rglob('*'))
        except Exception:
            has_known_files = False

        if not has_new_files:
            return False, f"New images directory is empty (no files found): {self.new_path}"

        if not has_known_files:
            return False, f"Known good directory is empty (no files found): {self.known_good_path}"
        
        return True, ""

