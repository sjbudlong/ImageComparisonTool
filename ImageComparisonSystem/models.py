"""
Data models for image comparison results.
"""

from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class ComparisonResult:
    """Results from comparing a single image pair."""
    
    filename: str
    new_image_path: Path
    known_good_path: Path
    diff_image_path: Path
    annotated_image_path: Path
    metrics: Dict[str, Any]
    percent_different: float
    histogram_data: str  # Base64 encoded histogram image
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        # Convert Path objects to strings
        data['new_image_path'] = str(data['new_image_path'])
        data['known_good_path'] = str(data['known_good_path'])
        data['diff_image_path'] = str(data['diff_image_path'])
        data['annotated_image_path'] = str(data['annotated_image_path'])
        return data
