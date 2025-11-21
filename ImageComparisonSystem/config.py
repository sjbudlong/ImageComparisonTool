"""
Configuration module for Image Comparison Tool.
"""

from pathlib import Path
from dataclasses import dataclass


@dataclass
class Config:
    """Configuration settings for image comparison."""
    
    base_dir: Path
    new_dir: str
    known_good_dir: str
    diff_dir: str = 'diffs'
    html_dir: str = 'reports'
    
    # Tolerances for different metrics
    pixel_diff_threshold: float = 0.01  # Minimum % difference to flag
    pixel_change_threshold: int = 1  # Minimum pixel value change to count
    ssim_threshold: float = 0.95  # Minimum SSIM to consider similar
    color_distance_threshold: float = 10.0  # RGB distance threshold
    min_contour_area: int = 50  # Minimum area for bounding boxes
    
    # Histogram equalization
    use_histogram_equalization: bool = True
    
    # Visual settings
    highlight_color: tuple = (255, 0, 0)  # RGB for bounding boxes
    diff_enhancement_factor: float = 5.0  # Contrast enhancement multiplier
    
    def __post_init__(self):
        """Convert string paths to Path objects and validate."""
        if isinstance(self.base_dir, str):
            self.base_dir = Path(self.base_dir)
        
        # Ensure base directory exists
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    @property
    def new_path(self) -> Path:
        """Full path to new images directory."""
        return self.base_dir / self.new_dir
    
    @property
    def known_good_path(self) -> Path:
        """Full path to known good images directory."""
        return self.base_dir / self.known_good_dir
    
    @property
    def diff_path(self) -> Path:
        """Full path to diff outputs directory."""
        return self.base_dir / self.diff_dir
    
    @property
    def html_path(self) -> Path:
        """Full path to HTML reports directory."""
        return self.base_dir / self.html_dir
    
    def validate(self) -> tuple[bool, str]:
        """
        Validate configuration settings.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.new_path.exists():
            return False, f"New images directory does not exist: {self.new_path}"
        
        if not self.known_good_path.exists():
            return False, f"Known good directory does not exist: {self.known_good_path}"
        
        if not any(self.new_path.iterdir()):
            return False, f"New images directory is empty: {self.new_path}"
        
        if not any(self.known_good_path.iterdir()):
            return False, f"Known good directory is empty: {self.known_good_path}"
        
        return True, ""
