"""
Image processing utilities for diff generation and visualization.
"""

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import io
import base64
import logging
import numpy as np
from PIL import Image
import cv2
from pathlib import Path
from typing import Tuple, Optional, Dict, List, TYPE_CHECKING
import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend

if TYPE_CHECKING:
    from config import Config, HistogramConfig

logger = logging.getLogger("ImageComparison")


class ImageProcessor:
    """Handles image diff generation and visualization."""

    def __init__(self, config: Optional["Config"] = None) -> None:
        """
        Initialize image processor.

        Args:
            config: Configuration object with processing settings
        """
        self.config = config
        logger.debug("ImageProcessor initialized")

    @staticmethod
    def equalize_histogram(
        img: np.ndarray, use_clahe: bool = True, to_grayscale: bool = False
    ) -> np.ndarray:
        """
        Apply histogram equalization to normalize tonal variations.

        Uses CLAHE (Contrast Limited Adaptive Histogram Equalization) which is
        less aggressive than standard histogram equalization and preserves
        local contrast better.

        Args:
            img: Input image array
            use_clahe: If True, use CLAHE instead of standard equalization
            to_grayscale: If True, convert to grayscale before equalization

        Returns:
            Histogram equalized image
        """
        logger.debug(f"Applying histogram equalization to image shape {img.shape}")

        # Convert to grayscale if requested or if it's color and we want better tonal neutralization
        if to_grayscale and len(img.shape) == 3:
            # Convert BGR to grayscale
            img_work = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            is_grayscale = True
        else:
            img_work = img
            is_grayscale = len(img.shape) == 2

        if is_grayscale:
            # Grayscale - apply equalization directly
            if use_clahe:
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                result = clahe.apply(img_work.astype(np.uint8))
            else:
                result = cv2.equalizeHist(img_work.astype(np.uint8))
            logger.debug("Histogram equalization complete (grayscale)")
            return result
        else:
            # Color image - equalize in LAB color space (better for perceptual tonal normalization)
            # Convert RGB to LAB
            img_lab = cv2.cvtColor(img_work.astype(np.uint8), cv2.COLOR_RGB2LAB)

            # Equalize only the L (lightness) channel
            l_channel = img_lab[:, :, 0]
            if use_clahe:
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                l_channel_eq = clahe.apply(l_channel)
            else:
                l_channel_eq = cv2.equalizeHist(l_channel)

            # Replace L channel with equalized version
            img_lab[:, :, 0] = l_channel_eq

            # Convert back to RGB
            result = cv2.cvtColor(img_lab, cv2.COLOR_LAB2RGB)
            logger.debug("Histogram equalization complete (color in LAB space)")
            return result

    @staticmethod
    def generate_histogram_image(
        img1: np.ndarray,
        img2: np.ndarray,
        hist_config: Optional["HistogramConfig"] = None,
    ) -> str:
        """
        Generate a histogram comparison image as base64 encoded PNG.
        Shows both grayscale (luminance) and RGB channel histograms for comparison.

        Args:
            img1: First image
            img2: Second image
            hist_config: HistogramConfig object for visualization settings

        Returns:
            Base64 encoded PNG image
        """
        # Use defaults if no config provided
        if hist_config is None:
            from config import HistogramConfig

            hist_config = HistogramConfig()

        fig, axes = plt.subplots(
            2,
            4,
            figsize=(hist_config.figure_width, hist_config.figure_height),
            dpi=hist_config.dpi,
        )
        fig.suptitle(hist_config.title, fontsize=14, fontweight="bold")

        # Convert to grayscale for luminance histograms
        if len(img1.shape) == 3:
            gray1 = cv2.cvtColor(img1.astype(np.uint8), cv2.COLOR_RGB2GRAY)
            gray2 = cv2.cvtColor(img2.astype(np.uint8), cv2.COLOR_RGB2GRAY)
        else:
            gray1 = img1.astype(np.uint8)
            gray2 = img2.astype(np.uint8)

        # Plot grayscale histograms in column 0 (if enabled)
        if hist_config.show_grayscale:
            hist_gray1, bins = np.histogram(
                gray1, bins=hist_config.bins, range=(0, 256)
            )
            axes[0, 0].plot(
                bins[:-1],
                hist_gray1,
                color=hist_config.grayscale_color,
                alpha=hist_config.grayscale_alpha,
                linewidth=hist_config.grayscale_linewidth,
            )
            axes[0, 0].set_title("Grayscale (Known Good)", fontweight="bold")
            axes[0, 0].set_xlim([0, 255])
            axes[0, 0].grid(True, alpha=hist_config.grid_alpha)
            axes[0, 0].legend(["Luminance"], loc="upper right")

            hist_gray2, _ = np.histogram(gray2, bins=hist_config.bins, range=(0, 256))
            axes[1, 0].plot(
                bins[:-1],
                hist_gray2,
                color=hist_config.grayscale_color,
                alpha=hist_config.grayscale_alpha,
                linewidth=hist_config.grayscale_linewidth,
            )
            axes[1, 0].set_title("Grayscale (New Image)", fontweight="bold")
            axes[1, 0].set_xlim([0, 255])
            axes[1, 0].grid(True, alpha=hist_config.grid_alpha)
            axes[1, 0].legend(["Luminance"], loc="upper right")
        else:
            axes[0, 0].axis("off")
            axes[1, 0].axis("off")

        # Plot RGB channel histograms in columns 1-3 (if enabled)
        if hist_config.show_rgb and len(img1.shape) == 3:
            for i, color in enumerate(hist_config.rgb_colors):
                col = i + 1

                # Image 1 histograms
                hist1, bins = np.histogram(
                    img1[:, :, i], bins=hist_config.bins, range=(0, 256)
                )
                axes[0, col].plot(
                    bins[:-1],
                    hist1,
                    color=color,
                    alpha=hist_config.rgb_alpha,
                    linewidth=hist_config.rgb_linewidth,
                )
                axes[0, col].set_title(
                    f"{color.capitalize()} Channel (Known Good)", fontweight="bold"
                )
                axes[0, col].set_xlim([0, 255])
                axes[0, col].grid(True, alpha=hist_config.grid_alpha)
                axes[0, col].legend([color.capitalize()], loc="upper right")

                # Image 2 histograms
                hist2, _ = np.histogram(
                    img2[:, :, i], bins=hist_config.bins, range=(0, 256)
                )
                axes[1, col].plot(
                    bins[:-1],
                    hist2,
                    color=color,
                    alpha=hist_config.rgb_alpha,
                    linewidth=hist_config.rgb_linewidth,
                )
                axes[1, col].set_title(
                    f"{color.capitalize()} Channel (New Image)", fontweight="bold"
                )
                axes[1, col].set_xlim([0, 255])
                axes[1, col].grid(True, alpha=hist_config.grid_alpha)
                axes[1, col].legend([color.capitalize()], loc="upper right")
        else:
            # Hide RGB columns for grayscale images or if disabled
            for i in range(1, 4):
                axes[0, i].axis("off")
                axes[1, i].axis("off")

        plt.tight_layout()

        # Convert to base64
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=100, bbox_inches="tight")
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode("utf-8")
        plt.close(fig)

        return img_base64

    @staticmethod
    def load_images(
        path1: Path,
        path2: Path,
        equalize: bool = False,
        use_clahe: bool = True,
        to_grayscale: bool = False,
        return_both: bool = False,
    ) -> Tuple[np.ndarray, ...]:
        """
        Load two images and ensure they're the same size.

        PERFORMANCE FIX: Now supports returning both original and equalized versions
        in a single load operation to eliminate duplicate I/O.

        Args:
            path1: Path to first image
            path2: Path to second image
            equalize: Whether to apply histogram equalization
            use_clahe: Whether to use CLAHE instead of standard equalization
            to_grayscale: Whether to convert to grayscale before equalization
            return_both: If True, returns 4-tuple (orig1, orig2, eq1, eq2).
                        If False, returns 2-tuple (img1, img2) for backward compatibility.

        Returns:
            If return_both=True: Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]
                (img1_original, img2_original, img1_equalized, img2_equalized)
            If return_both=False: Tuple[np.ndarray, np.ndarray]
                (img1, img2) - equalized if equalize=True, otherwise original
        """
        img1 = Image.open(path1)
        img2 = Image.open(path2)

        # Convert to RGB if needed
        if img1.mode != "RGB":
            img1 = img1.convert("RGB")
        if img2.mode != "RGB":
            img2 = img2.convert("RGB")

        # Resize if dimensions don't match
        if img1.size != img2.size:
            # Resize to the larger dimensions
            max_width = max(img1.width, img2.width)
            max_height = max(img1.height, img2.height)

            if img1.size != (max_width, max_height):
                img1 = img1.resize((max_width, max_height), Image.LANCZOS)
            if img2.size != (max_width, max_height):
                img2 = img2.resize((max_width, max_height), Image.LANCZOS)

        # Convert to numpy - keep originals
        img1_orig = np.array(img1)
        img2_orig = np.array(img2)

        # Handle different return modes
        if return_both:
            # Return both original and equalized versions
            if equalize:
                logger.debug("Applying histogram equalization (return_both mode)")
                img1_eq = ImageProcessor.equalize_histogram(
                    img1_orig.copy(),  # Important: copy to preserve original
                    use_clahe=use_clahe,
                    to_grayscale=to_grayscale,
                )
                img2_eq = ImageProcessor.equalize_histogram(
                    img2_orig.copy(), use_clahe=use_clahe, to_grayscale=to_grayscale
                )
            else:
                # If not equalizing, equalized versions are same as originals
                img1_eq, img2_eq = img1_orig, img2_orig

            logger.info(
                f"Images loaded successfully with shape {img1_orig.shape} (return_both=True)"
            )
            return img1_orig, img2_orig, img1_eq, img2_eq
        else:
            # Backward compatibility mode: return 2-tuple
            if equalize:
                logger.debug("Applying histogram equalization")
                img1_orig = ImageProcessor.equalize_histogram(
                    img1_orig, use_clahe=use_clahe, to_grayscale=to_grayscale
                )
                img2_orig = ImageProcessor.equalize_histogram(
                    img2_orig, use_clahe=use_clahe, to_grayscale=to_grayscale
                )

            logger.info(f"Images loaded successfully with shape {img1_orig.shape}")
            return img1_orig, img2_orig

    @staticmethod
    def create_diff_image(
        img1: np.ndarray, img2: np.ndarray, enhancement_factor: float = 5.0
    ) -> np.ndarray:
        """
        Create a difference image between two images.

        Args:
            img1: First image array
            img2: Second image array
            enhancement_factor: Contrast enhancement multiplier

        Returns:
            Diff image as numpy array
        """
        # Calculate absolute difference
        diff = np.abs(img1.astype(float) - img2.astype(float))

        # Enhance contrast to make differences more visible
        if enhancement_factor > 1.0:
            diff = ImageProcessor._enhance_diff_contrast(diff, enhancement_factor)

        return diff.astype(np.uint8)

    @staticmethod
    def _enhance_diff_contrast(diff: np.ndarray, factor: float = 5.0) -> np.ndarray:
        """
        Enhance contrast of difference image.

        Args:
            diff: Difference array
            factor: Multiplication factor for enhancement

        Returns:
            Enhanced difference array
        """
        # Scale up differences
        enhanced = diff * factor

        # Clip to valid range
        enhanced = np.clip(enhanced, 0, 255)

        return enhanced

    @staticmethod
    def create_annotated_image(
        img: np.ndarray,
        diff: np.ndarray,
        threshold: float = 10.0,
        min_area: int = 50,
        color: Tuple[int, int, int] = (255, 0, 0),
    ) -> np.ndarray:
        """
        Create annotated image with bounding boxes around differences.

        Args:
            img: Original image
            diff: Difference image
            threshold: Minimum difference to consider significant
            min_area: Minimum contour area for bounding boxes
            color: RGB color for bounding boxes

        Returns:
            Annotated image as numpy array
        """
        annotated = img.copy()

        # Convert diff to grayscale for processing
        if len(diff.shape) == 3:
            diff_gray = np.mean(diff, axis=2)
        else:
            diff_gray = diff

        # Threshold the difference
        _, thresh = cv2.threshold(
            diff_gray.astype(np.uint8), threshold, 255, cv2.THRESH_BINARY
        )

        # Find contours of differences
        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        # Draw bounding boxes around significant differences
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > min_area:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 2)

        return annotated

    @staticmethod
    def save_image(img: np.ndarray, path: Path):
        """
        Save numpy array as image file.

        Args:
            img: Image array
            path: Output path
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(img.astype(np.uint8)).save(path)

    @staticmethod
    def create_side_by_side(
        img1: np.ndarray, img2: np.ndarray, diff: np.ndarray
    ) -> np.ndarray:
        """
        Create side-by-side comparison image.

        Args:
            img1: First image
            img2: Second image
            diff: Difference image

        Returns:
            Combined image
        """
        # Ensure all images are the same height
        height = max(img1.shape[0], img2.shape[0], diff.shape[0])

        def pad_to_height(img, target_height):
            if img.shape[0] < target_height:
                padding = target_height - img.shape[0]
                return np.pad(
                    img,
                    ((0, padding), (0, 0), (0, 0)),
                    mode="constant",
                    constant_values=255,
                )
            return img

        img1 = pad_to_height(img1, height)
        img2 = pad_to_height(img2, height)
        diff = pad_to_height(diff, height)

        # Concatenate horizontally
        combined = np.hstack([img1, img2, diff])

        return combined

    @staticmethod
    def create_flip_heatmap(
        flip_map: np.ndarray,
        colormap: str = "viridis",
        normalize: bool = True
    ) -> np.ndarray:
        """
        Create heatmap visualization from FLIP error map.

        Converts FLIP error map (grayscale) to color heatmap using matplotlib colormaps.
        Useful for visualizing perceptual differences with intuitive color gradients.

        Args:
            flip_map: FLIP error map (H x W) with values in [0, 1]
                where 0 = identical, 1 = maximum perceptual difference
            colormap: Matplotlib colormap name. Options:
                - "viridis": Perceptually uniform, good for general use
                - "jet": High contrast, rainbow colors
                - "turbo": Smooth rainbow, improved version of jet
                - "magma": Dark to bright, good for dark backgrounds
            normalize: Whether to normalize map to full colormap range.
                If True, maps min->max to colormap's full range.
                If False, uses absolute [0, 1] scale.

        Returns:
            RGB heatmap image as uint8 numpy array (H x W x 3)

        Example:
            >>> flip_map = np.random.uniform(0, 0.3, (100, 100))
            >>> heatmap = ImageProcessor.create_flip_heatmap(flip_map, "viridis")
            >>> assert heatmap.shape == (100, 100, 3)
        """
        logger.debug(f"Creating FLIP heatmap with colormap={colormap}, normalize={normalize}")

        # Get the colormap
        try:
            cmap = cm.get_cmap(colormap)
        except ValueError:
            logger.warning(f"Invalid colormap '{colormap}', falling back to 'viridis'")
            cmap = cm.get_cmap("viridis")

        # Normalize if requested
        if normalize and flip_map.max() > flip_map.min():
            flip_normalized = (flip_map - flip_map.min()) / (flip_map.max() - flip_map.min())
            logger.debug(f"Normalized FLIP map: range [{flip_map.min():.6f}, {flip_map.max():.6f}] -> [0, 1]")
        else:
            flip_normalized = flip_map

        # Apply colormap (returns RGBA with values in [0, 1])
        heatmap_rgba = cmap(flip_normalized)

        # Convert to RGB uint8 (drop alpha channel)
        heatmap_rgb = (heatmap_rgba[:, :, :3] * 255).astype(np.uint8)

        logger.debug(f"FLIP heatmap created: shape={heatmap_rgb.shape}, dtype={heatmap_rgb.dtype}")
        return heatmap_rgb

    @staticmethod
    def create_flip_heatmaps_multi_colormap(
        flip_map: np.ndarray,
        colormaps: List[str],
        output_dir: Path,
        base_filename: str
    ) -> Dict[str, Path]:
        """
        Generate multiple heatmap versions with different colormaps.

        Creates and saves FLIP heatmaps using multiple color schemes, allowing
        users to choose their preferred visualization style.

        Args:
            flip_map: FLIP error map (H x W) with values in [0, 1]
            colormaps: List of colormap names (e.g., ["viridis", "jet", "turbo"])
            output_dir: Directory to save heatmap images
            base_filename: Base filename (e.g., "image.png" -> "flip_viridis_image.png")

        Returns:
            Dictionary mapping colormap name to saved file path

        Example:
            >>> flip_map = np.random.uniform(0, 0.3, (100, 100))
            >>> paths = ImageProcessor.create_flip_heatmaps_multi_colormap(
            ...     flip_map, ["viridis", "jet"], Path("./output"), "test.png"
            ... )
            >>> assert "viridis" in paths
            >>> assert paths["viridis"].exists()
        """
        logger.debug(f"Generating {len(colormaps)} FLIP heatmap versions for {base_filename}")

        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        heatmap_paths = {}

        for colormap in colormaps:
            # Generate heatmap
            heatmap = ImageProcessor.create_flip_heatmap(flip_map, colormap, normalize=True)

            # Create filename
            output_path = output_dir / f"flip_{colormap}_{base_filename}"

            # Save heatmap
            Image.fromarray(heatmap).save(output_path)
            heatmap_paths[colormap] = output_path

            logger.debug(f"Saved FLIP heatmap: {colormap} -> {output_path}")

        logger.info(f"Generated {len(heatmap_paths)} FLIP heatmap(s) for {base_filename}")
        return heatmap_paths

    @staticmethod
    def generate_flip_comparison_image(
        img1: np.ndarray,
        img2: np.ndarray,
        flip_map: np.ndarray,
        colormap: str = "viridis"
    ) -> str:
        """
        Generate side-by-side comparison with FLIP heatmap for HTML embedding.

        Creates a 4-panel visualization:
        1. Known Good image
        2. New Image
        3. FLIP Error Map (heatmap)
        4. FLIP Overlay (error map overlaid on known good)

        Args:
            img1: Known good image as numpy array (uint8, RGB)
            img2: New image as numpy array (uint8, RGB)
            flip_map: FLIP error map (H x W) with values in [0, 1]
            colormap: Matplotlib colormap for error visualization

        Returns:
            Base64 encoded PNG image string for HTML <img> tag embedding

        Example:
            >>> img1 = np.ones((100, 100, 3), dtype=np.uint8) * 128
            >>> img2 = np.ones((100, 100, 3), dtype=np.uint8) * 130
            >>> flip_map = np.random.uniform(0, 0.1, (100, 100))
            >>> b64_img = ImageProcessor.generate_flip_comparison_image(
            ...     img1, img2, flip_map, "viridis"
            ... )
            >>> assert b64_img.startswith("iVBOR")  # PNG signature in base64
        """
        logger.debug(f"Generating FLIP comparison image with colormap={colormap}")

        # Create figure with 4 subplots
        fig, axes = plt.subplots(1, 4, figsize=(20, 5))

        # Panel 1: Known Good
        axes[0].imshow(img1)
        axes[0].set_title("Known Good", fontweight="bold", fontsize=12)
        axes[0].axis("off")

        # Panel 2: New Image
        axes[1].imshow(img2)
        axes[1].set_title("New Image", fontweight="bold", fontsize=12)
        axes[1].axis("off")

        # Panel 3: FLIP Error Map
        flip_display = axes[2].imshow(flip_map, cmap=colormap, vmin=0, vmax=1)
        axes[2].set_title(f"FLIP Error Map ({colormap})", fontweight="bold", fontsize=12)
        axes[2].axis("off")

        # Panel 4: FLIP Overlay
        axes[3].imshow(img1)
        axes[3].imshow(flip_map, cmap=colormap, alpha=0.6, vmin=0, vmax=1)
        axes[3].set_title("FLIP Overlay", fontweight="bold", fontsize=12)
        axes[3].axis("off")

        # Add colorbar
        cbar = plt.colorbar(
            flip_display,
            ax=axes,
            orientation='horizontal',
            fraction=0.05,
            pad=0.05,
            shrink=0.8
        )
        cbar.set_label(
            "FLIP Error (0 = identical, 1 = max perceptual difference)",
            fontsize=10
        )

        plt.tight_layout()

        # Convert to base64
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=100, bbox_inches="tight")
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode("utf-8")
        plt.close(fig)

        logger.debug("FLIP comparison image generated successfully")
        return img_base64
