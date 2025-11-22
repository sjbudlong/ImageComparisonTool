"""
Modular image analysis components.
Each analyzer extracts specific metrics from image comparisons.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict
import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity as ssim

logger = logging.getLogger("ImageComparison")


class ImageAnalyzer(ABC):
    """Base class for image analysis components."""
    
    @abstractmethod
    def analyze(self, img1: np.ndarray, img2: np.ndarray) -> Dict[str, Any]:
        """
        Analyze two images and return metrics.
        
        Args:
            img1: First image as numpy array
            img2: Second image as numpy array
            
        Returns:
            Dictionary of metric name to value
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the analyzer name."""
        pass


class PixelDifferenceAnalyzer(ImageAnalyzer):
    """Analyzes pixel-level differences between images."""
    
    def __init__(self, threshold: int = 1):
        """
        Args:
            threshold: Minimum pixel value change to count as different
        """
        self.threshold = threshold
    
    @property
    def name(self) -> str:
        return "Pixel Difference"
    
    def analyze(self, img1: np.ndarray, img2: np.ndarray) -> Dict[str, Any]:
        """Calculate pixel difference metrics."""
        logger.debug(f"Analyzing pixel differences with threshold={self.threshold}")
        # Calculate absolute difference
        diff = np.abs(img1.astype(float) - img2.astype(float))
        
        # Calculate percentage of pixels that differ
        changed_pixels = np.sum(diff > self.threshold)
        total_pixels = diff.size
        percent_different = (changed_pixels / total_pixels) * 100
        
        # Calculate mean absolute error
        mae = np.mean(diff)
        
        # Calculate max difference
        max_diff = np.max(diff)
        
        logger.info(f"Pixel analysis complete: {percent_different:.2f}% different, MAE={mae:.4f}")
        return {
            'percent_different': round(percent_different, 4),
            'changed_pixels': int(changed_pixels),
            'total_pixels': int(total_pixels),
            'mean_absolute_error': round(float(mae), 4),
            'max_difference': float(max_diff),
            'threshold_used': self.threshold
        }


class StructuralSimilarityAnalyzer(ImageAnalyzer):
    """Analyzes structural similarity between images using SSIM."""
    
    @property
    def name(self) -> str:
        return "Structural Similarity"
    
    def analyze(self, img1: np.ndarray, img2: np.ndarray) -> Dict[str, Any]:
        """Calculate SSIM and related metrics."""
        logger.debug("Analyzing structural similarity")
        # Convert to grayscale if color
        if len(img1.shape) == 3:
            img1_gray = np.mean(img1, axis=2).astype(np.uint8)
            img2_gray = np.mean(img2, axis=2).astype(np.uint8)
        else:
            img1_gray = img1
            img2_gray = img2
        
        # Calculate SSIM
        ssim_value, ssim_map = ssim(
            img1_gray, 
            img2_gray, 
            full=True,
            data_range=255
        )
        logger.info(f"SSIM analysis complete: score={ssim_value:.6f}")
        
        return {
            'ssim_score': round(float(ssim_value), 6),
            'ssim_percentage': round((1 - float(ssim_value)) * 100, 4),
            'ssim_description': self._describe_ssim(ssim_value)
        }
    
    def _describe_ssim(self, ssim_value: float) -> str:
        """Provide human-readable description of SSIM score."""
        if ssim_value >= 0.99:
            return "Nearly identical"
        elif ssim_value >= 0.95:
            return "Very similar"
        elif ssim_value >= 0.90:
            return "Similar"
        elif ssim_value >= 0.80:
            return "Somewhat similar"
        elif ssim_value >= 0.70:
            return "Moderately different"
        else:
            return "Very different"


class ColorDifferenceAnalyzer(ImageAnalyzer):
    """Analyzes color-specific differences between images."""
    
    def __init__(self, distance_threshold: float = 10.0):
        """
        Args:
            distance_threshold: Threshold for significant color distance
        """
        self.distance_threshold = distance_threshold
    
    @property
    def name(self) -> str:
        return "Color Difference"
    
    def analyze(self, img1: np.ndarray, img2: np.ndarray) -> Dict[str, Any]:
        """Calculate color-based metrics."""
        if len(img1.shape) < 3:
            return {
                'grayscale': True,
                'message': 'Images are grayscale'
            }
        
        # Calculate per-channel differences
        channel_names = ['red', 'green', 'blue'] if img1.shape[2] == 3 else ['r', 'g', 'b', 'a']
        
        results = {'grayscale': False}
        
        for i, name in enumerate(channel_names[:img1.shape[2]]):
            diff = np.abs(img1[:, :, i].astype(float) - img2[:, :, i].astype(float))
            results[f'{name}_mean_diff'] = round(float(np.mean(diff)), 4)
            results[f'{name}_max_diff'] = float(np.max(diff))
        
        # Calculate overall color distance (Euclidean in RGB space)
        color_distance = np.sqrt(np.sum((img1.astype(float) - img2.astype(float)) ** 2, axis=2))
        results['mean_color_distance'] = round(float(np.mean(color_distance)), 4)
        results['max_color_distance'] = round(float(np.max(color_distance)), 4)
        
        # Count pixels exceeding threshold
        significant_changes = np.sum(color_distance > self.distance_threshold)
        results['significant_color_changes'] = int(significant_changes)
        results['significant_change_percent'] = round(
            (significant_changes / color_distance.size) * 100, 4
        )
        results['threshold_used'] = self.distance_threshold
        
        return results


class DimensionAnalyzer(ImageAnalyzer):
    """Analyzes image dimensions and size differences."""
    
    @property
    def name(self) -> str:
        return "Dimensions"
    
    def analyze(self, img1: np.ndarray, img2: np.ndarray) -> Dict[str, Any]:
        """Calculate dimension-related metrics."""
        return {
            'img1_shape': img1.shape,
            'img2_shape': img2.shape,
            'shapes_match': img1.shape == img2.shape,
            'img1_size': f"{img1.shape[1]}x{img1.shape[0]}",
            'img2_size': f"{img2.shape[1]}x{img2.shape[0]}"
        }


class HistogramAnalyzer(ImageAnalyzer):
    """Analyzes and compares image histograms."""
    
    @property
    def name(self) -> str:
        return "Histogram Analysis"
    
    def analyze(self, img1: np.ndarray, img2: np.ndarray) -> Dict[str, Any]:
        """Calculate histogram-based metrics."""
        results = {}
        
        if len(img1.shape) == 3:
            # Color image - analyze each channel
            channel_names = ['red', 'green', 'blue']
            for i, name in enumerate(channel_names):
                hist1, _ = np.histogram(img1[:, :, i], bins=256, range=(0, 256))
                hist2, _ = np.histogram(img2[:, :, i], bins=256, range=(0, 256))
                
                # Normalize histograms
                hist1 = hist1.astype(float) / hist1.sum()
                hist2 = hist2.astype(float) / hist2.sum()
                
                # Calculate correlation
                correlation = np.corrcoef(hist1, hist2)[0, 1]
                
                # Calculate chi-square distance
                epsilon = 1e-10
                chi_square = np.sum(((hist1 - hist2) ** 2) / (hist1 + hist2 + epsilon))
                
                results[f'{name}_histogram_correlation'] = round(float(correlation), 6)
                results[f'{name}_histogram_chi_square'] = round(float(chi_square), 6)
        else:
            # Grayscale image
            hist1, _ = np.histogram(img1, bins=256, range=(0, 256))
            hist2, _ = np.histogram(img2, bins=256, range=(0, 256))
            
            hist1 = hist1.astype(float) / hist1.sum()
            hist2 = hist2.astype(float) / hist2.sum()
            
            correlation = np.corrcoef(hist1, hist2)[0, 1]
            epsilon = 1e-10
            chi_square = np.sum(((hist1 - hist2) ** 2) / (hist1 + hist2 + epsilon))
            
            results['histogram_correlation'] = round(float(correlation), 6)
            results['histogram_chi_square'] = round(float(chi_square), 6)
        
        return results


class AnalyzerRegistry:
    """Registry for managing image analyzers."""
    
    def __init__(self, config=None):
        self.analyzers: list[ImageAnalyzer] = []
        self.config = config
        self._register_default_analyzers()
    
    def _register_default_analyzers(self):
        """Register default set of analyzers."""
        self.register(DimensionAnalyzer())
        self.register(HistogramAnalyzer())
        
        if self.config:
            self.register(PixelDifferenceAnalyzer(
                threshold=self.config.pixel_change_threshold
            ))
            self.register(ColorDifferenceAnalyzer(
                distance_threshold=self.config.color_distance_threshold
            ))
        else:
            self.register(PixelDifferenceAnalyzer())
            self.register(ColorDifferenceAnalyzer())
        
        self.register(StructuralSimilarityAnalyzer())
    
    def register(self, analyzer: ImageAnalyzer):
        """Add an analyzer to the registry."""
        self.analyzers.append(analyzer)
    
    def analyze_all(self, img1: np.ndarray, img2: np.ndarray) -> Dict[str, Dict[str, Any]]:
        """Run all registered analyzers on the image pair."""
        results = {}
        for analyzer in self.analyzers:
            try:
                results[analyzer.name] = analyzer.analyze(img1, img2)
            except Exception as e:
                results[analyzer.name] = {'error': str(e)}
        return results
