"""
Modular image analysis components.
Each analyzer extracts specific metrics from image comparisons.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TYPE_CHECKING
import numpy as np
from skimage.metrics import structural_similarity as ssim

# Optional FLIP import with graceful degradation
try:
    from flip_evaluator import evaluate as flip_evaluate
    FLIP_AVAILABLE = True
except ImportError:
    FLIP_AVAILABLE = False
    flip_evaluate = None
    logger_flip = logging.getLogger("ImageComparison")
    logger_flip.warning(
        "NVIDIA FLIP not installed. FLIP analysis disabled. "
        "Install with: pip install flip-evaluator"
    )

if TYPE_CHECKING:
    from config import Config

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

    def __init__(self, threshold: int = 1) -> None:
        """
        Initialize pixel difference analyzer.

        Args:
            threshold: Minimum pixel value change to count as different
        """
        self.threshold: int = threshold

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

        logger.info(
            f"Pixel analysis complete: {percent_different:.2f}% different, MAE={mae:.4f}"
        )
        return {
            "percent_different": round(percent_different, 4),
            "changed_pixels": int(changed_pixels),
            "total_pixels": int(total_pixels),
            "mean_absolute_error": round(float(mae), 4),
            "max_difference": float(max_diff),
            "threshold_used": self.threshold,
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
        ssim_value, ssim_map = ssim(img1_gray, img2_gray, full=True, data_range=255)
        logger.info(f"SSIM analysis complete: score={ssim_value:.6f}")

        return {
            "ssim_score": round(float(ssim_value), 6),
            "ssim_percentage": round((1 - float(ssim_value)) * 100, 4),
            "ssim_description": self._describe_ssim(ssim_value),
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
            return {"grayscale": True, "message": "Images are grayscale"}

        # Calculate per-channel differences
        channel_names = (
            ["red", "green", "blue"] if img1.shape[2] == 3 else ["r", "g", "b", "a"]
        )

        results = {"grayscale": False}

        for i, name in enumerate(channel_names[: img1.shape[2]]):
            diff = np.abs(img1[:, :, i].astype(float) - img2[:, :, i].astype(float))
            results[f"{name}_mean_diff"] = round(float(np.mean(diff)), 4)
            results[f"{name}_max_diff"] = float(np.max(diff))

        # Calculate overall color distance (Euclidean in RGB space)
        color_distance = np.sqrt(
            np.sum((img1.astype(float) - img2.astype(float)) ** 2, axis=2)
        )
        results["mean_color_distance"] = round(float(np.mean(color_distance)), 4)
        results["max_color_distance"] = round(float(np.max(color_distance)), 4)

        # Count pixels exceeding threshold
        significant_changes = np.sum(color_distance > self.distance_threshold)
        results["significant_color_changes"] = int(significant_changes)
        results["significant_change_percent"] = round(
            (significant_changes / color_distance.size) * 100, 4
        )
        results["threshold_used"] = self.distance_threshold

        return results


class DimensionAnalyzer(ImageAnalyzer):
    """Analyzes image dimensions and size differences."""

    @property
    def name(self) -> str:
        return "Dimensions"

    def analyze(self, img1: np.ndarray, img2: np.ndarray) -> Dict[str, Any]:
        """Calculate dimension-related metrics."""
        return {
            "img1_shape": img1.shape,
            "img2_shape": img2.shape,
            "shapes_match": img1.shape == img2.shape,
            "img1_size": f"{img1.shape[1]}x{img1.shape[0]}",
            "img2_size": f"{img2.shape[1]}x{img2.shape[0]}",
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
            channel_names = ["red", "green", "blue"]
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

                results[f"{name}_histogram_correlation"] = round(float(correlation), 6)
                results[f"{name}_histogram_chi_square"] = round(float(chi_square), 6)
        else:
            # Grayscale image
            hist1, _ = np.histogram(img1, bins=256, range=(0, 256))
            hist2, _ = np.histogram(img2, bins=256, range=(0, 256))

            hist1 = hist1.astype(float) / hist1.sum()
            hist2 = hist2.astype(float) / hist2.sum()

            correlation = np.corrcoef(hist1, hist2)[0, 1]
            epsilon = 1e-10
            chi_square = np.sum(((hist1 - hist2) ** 2) / (hist1 + hist2 + epsilon))

            results["histogram_correlation"] = round(float(correlation), 6)
            results["histogram_chi_square"] = round(float(chi_square), 6)

        return results


class FLIPAnalyzer(ImageAnalyzer):
    """
    Analyzes perceptual differences using NVIDIA FLIP metric.

    FLIP (FLaws in Luminance and Pixels) is a perceptual image comparison metric
    that accounts for:
    - Spatial frequency sensitivity (Contrast Sensitivity Function)
    - Viewing distance (pixels per degree)
    - Luminance adaptation
    - Chrominance handling

    Superior to SSIM for rendering quality assessment and perceptual analysis.
    Designed for VFX, gaming, and 3D rendering workflows.
    """

    def __init__(self, pixels_per_degree: float = 67.0) -> None:
        """
        Initialize FLIP analyzer.

        Args:
            pixels_per_degree: Viewing distance parameter. Default 67.0 corresponds
                to 0.7m viewing distance on a 24" 1080p display.

        Raises:
            ImportError: If NVIDIA FLIP package is not installed
        """
        if not FLIP_AVAILABLE:
            raise ImportError(
                "NVIDIA FLIP not installed. Install with: pip install flip-evaluator"
            )
        self.pixels_per_degree: float = pixels_per_degree

    @property
    def name(self) -> str:
        return "FLIP Perceptual Metric"

    def analyze(self, img1: np.ndarray, img2: np.ndarray) -> Dict[str, Any]:
        """
        Calculate FLIP perceptual metrics.

        Args:
            img1: First image as numpy array (uint8, RGB or grayscale)
            img2: Second image as numpy array (uint8, RGB or grayscale)

        Returns:
            Dictionary containing:
                - flip_mean: Mean FLIP error across all pixels
                - flip_max: Maximum FLIP error value
                - flip_weighted_median: Median of non-zero FLIP errors
                - flip_percentile_95: 95th percentile FLIP error
                - flip_percentile_99: 99th percentile FLIP error
                - flip_error_map_array: Full FLIP error map for visualization
                - pixels_per_degree: Viewing distance parameter used
                - flip_quality_description: Human-readable quality assessment
        """
        logger.debug(f"Analyzing FLIP with pixels_per_degree={self.pixels_per_degree}")

        # Convert to float32 [0, 1] range as required by FLIP
        img1_float = img1.astype(np.float32) / 255.0
        img2_float = img2.astype(np.float32) / 255.0

        # Handle grayscale images by converting to RGB
        if len(img1_float.shape) == 2:
            img1_float = np.stack([img1_float] * 3, axis=-1)
        if len(img2_float.shape) == 2:
            img2_float = np.stack([img2_float] * 3, axis=-1)

        # Calculate FLIP error map
        # Note: flip_evaluate returns (error_map, mean_error, parameters_used)
        # where error_map has values in [0, 1]: 0 = identical, 1 = maximum perceptual difference
        flip_result = flip_evaluate(
            reference=img1_float,
            test=img2_float,
            dynamicRangeString="LDR",  # Low Dynamic Range (images in [0, 1])
            inputsRGB=True,  # Images are in sRGB color space
            applyMagma=False,  # Don't apply colormap, we'll do that separately
            computeMeanError=True,  # Compute mean FLIP error
            parameters={"ppd": self.pixels_per_degree}  # Pixels per degree parameter
        )

        # Unpack results: (error_map, mean_error, parameters_dict)
        flip_map, flip_mean_computed, _ = flip_result

        # Error map is (H, W, 1), squeeze to (H, W)
        if len(flip_map.shape) == 3 and flip_map.shape[2] == 1:
            flip_map = np.squeeze(flip_map, axis=2)

        # Calculate statistics
        flip_mean = float(flip_mean_computed) if flip_mean_computed >= 0 else float(np.mean(flip_map))
        flip_max = float(np.max(flip_map))

        # Calculate weighted median (only considering non-zero errors)
        non_zero_errors = flip_map[flip_map > 0]
        flip_weighted_median = (
            float(np.median(non_zero_errors))
            if len(non_zero_errors) > 0
            else 0.0
        )

        # Calculate percentiles
        flip_percentile_95 = float(np.percentile(flip_map, 95))
        flip_percentile_99 = float(np.percentile(flip_map, 99))

        # Quality description
        quality_description = self._describe_flip(flip_mean)

        logger.info(
            f"FLIP analysis complete: mean={flip_mean:.6f}, max={flip_max:.6f}, "
            f"quality={quality_description}"
        )

        return {
            "flip_mean": round(flip_mean, 6),
            "flip_max": round(flip_max, 6),
            "flip_weighted_median": round(flip_weighted_median, 6),
            "flip_percentile_95": round(flip_percentile_95, 6),
            "flip_percentile_99": round(flip_percentile_99, 6),
            "flip_error_map_array": flip_map,  # Keep full precision for visualization
            "pixels_per_degree": self.pixels_per_degree,
            "flip_quality_description": quality_description,
        }

    def _describe_flip(self, flip_mean: float) -> str:
        """
        Provide human-readable description of FLIP score.

        FLIP values range from 0 (identical) to 1 (maximum perceptual difference).
        Thresholds based on perceptual research and industry standards.

        Args:
            flip_mean: Mean FLIP error value

        Returns:
            Human-readable quality description
        """
        if flip_mean <= 0.01:
            return "Imperceptible differences"
        elif flip_mean <= 0.05:
            return "Just noticeable differences"
        elif flip_mean <= 0.10:
            return "Slight perceptual differences"
        elif flip_mean <= 0.20:
            return "Moderate perceptual differences"
        elif flip_mean <= 0.40:
            return "Noticeable perceptual differences"
        else:
            return "Significant perceptual differences"


class AnalyzerRegistry:
    """Registry for managing image analyzers."""

    def __init__(self, config: Optional["Config"] = None) -> None:
        """
        Initialize analyzer registry.

        Args:
            config: Optional configuration object
        """
        self.analyzers: List[ImageAnalyzer] = []
        self.config: Optional["Config"] = config
        self._register_default_analyzers()

    def _register_default_analyzers(self) -> None:
        """Register default set of analyzers."""
        self.register(DimensionAnalyzer())
        self.register(HistogramAnalyzer())

        if self.config:
            self.register(
                PixelDifferenceAnalyzer(threshold=self.config.pixel_change_threshold)
            )
            self.register(
                ColorDifferenceAnalyzer(
                    distance_threshold=self.config.color_distance_threshold
                )
            )
        else:
            self.register(PixelDifferenceAnalyzer())
            self.register(ColorDifferenceAnalyzer())

        self.register(StructuralSimilarityAnalyzer())

        # Register FLIP analyzer if available and enabled
        if FLIP_AVAILABLE and self.config and self.config.enable_flip:
            try:
                flip_ppd = self.config.flip_pixels_per_degree
                self.register(FLIPAnalyzer(pixels_per_degree=flip_ppd))
                logger.info(f"FLIP analyzer registered (pixels_per_degree={flip_ppd})")
            except Exception as e:
                logger.warning(f"Failed to register FLIP analyzer: {e}")

    def register(self, analyzer: ImageAnalyzer) -> None:
        """
        Add an analyzer to the registry.

        Args:
            analyzer: Analyzer instance to register
        """
        self.analyzers.append(analyzer)

    def analyze_all(
        self, img1: np.ndarray, img2: np.ndarray
    ) -> Dict[str, Dict[str, Any]]:
        """
        Run all registered analyzers on the image pair.

        Args:
            img1: First image array
            img2: Second image array

        Returns:
            Dictionary mapping analyzer names to their results
        """
        results: Dict[str, Dict[str, Any]] = {}
        for analyzer in self.analyzers:
            try:
                results[analyzer.name] = analyzer.analyze(img1, img2)
            except Exception as e:
                logger.error(f"Error in {analyzer.name}: {e}", exc_info=True)
                results[analyzer.name] = {"error": str(e)}
        return results
