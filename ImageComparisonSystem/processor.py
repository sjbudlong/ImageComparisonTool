"""
Image processing utilities for diff generation and visualization.
"""

import logging
import numpy as np
from PIL import Image, ImageDraw
import cv2
from pathlib import Path
from typing import Tuple, Optional
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import io
import base64

logger = logging.getLogger("ImageComparison")


class ImageProcessor:
    """Handles image diff generation and visualization."""
    
    def __init__(self, config=None):
        """
        Args:
            config: Configuration object with processing settings
        """
        self.config = config
        logger.debug("ImageProcessor initialized")
    
    @staticmethod
    def equalize_histogram(img: np.ndarray) -> np.ndarray:
        """
        Apply histogram equalization to normalize tonal variations.
        
        Args:
            img: Input image array
            
        Returns:
            Histogram equalized image
        """
        logger.debug(f"Applying histogram equalization to image shape {img.shape}")
        if len(img.shape) == 3:
            # Color image - equalize each channel
            result = np.zeros_like(img)
            for i in range(img.shape[2]):
                result[:, :, i] = cv2.equalizeHist(img[:, :, i])
        logger.debug("Histogram equalization complete")
            return result
        else:
            # Grayscale
            return cv2.equalizeHist(img)
    
    @staticmethod
    def generate_histogram_image(img1: np.ndarray, img2: np.ndarray) -> str:
        """
        Generate a histogram comparison image as base64 encoded PNG.
        
        Args:
            img1: First image
            img2: Second image
            
        Returns:
            Base64 encoded PNG image
        """
        fig, axes = plt.subplots(2, 3, figsize=(12, 6))
        fig.suptitle('Histogram Comparison', fontsize=14, fontweight='bold')
        
        if len(img1.shape) == 3:
            # Color histograms
            colors = ['red', 'green', 'blue']
            for i, color in enumerate(colors):
                # Image 1 histograms
                hist1, bins = np.histogram(img1[:, :, i], bins=256, range=(0, 256))
                axes[0, i].plot(bins[:-1], hist1, color=color, alpha=0.7, label='Known Good')
                axes[0, i].set_title(f'{color.capitalize()} Channel')
                axes[0, i].set_xlim([0, 255])
                axes[0, i].grid(True, alpha=0.3)
                
                # Image 2 histograms
                hist2, _ = np.histogram(img2[:, :, i], bins=256, range=(0, 256))
                axes[1, i].plot(bins[:-1], hist2, color=color, alpha=0.7, label='New Image')
                axes[1, i].set_xlim([0, 255])
                axes[1, i].grid(True, alpha=0.3)
                
                # Add legend
                if i == 0:
                    axes[0, i].legend(loc='upper right')
                    axes[1, i].legend(loc='upper right')
        else:
            # Grayscale histogram
            hist1, bins = np.histogram(img1, bins=256, range=(0, 256))
            axes[0, 0].plot(bins[:-1], hist1, color='black', alpha=0.7)
            axes[0, 0].set_title('Known Good')
            axes[0, 0].set_xlim([0, 255])
            axes[0, 0].grid(True, alpha=0.3)
            
            hist2, _ = np.histogram(img2, bins=256, range=(0, 256))
            axes[1, 0].plot(bins[:-1], hist2, color='black', alpha=0.7)
            axes[1, 0].set_title('New Image')
            axes[1, 0].set_xlim([0, 255])
            axes[1, 0].grid(True, alpha=0.3)
            
            # Hide unused subplots
            for i in range(1, 3):
                axes[0, i].axis('off')
                axes[1, i].axis('off')
        
        plt.tight_layout()
        
        # Convert to base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        return img_base64
    
    @staticmethod
    def load_images(path1: Path, path2: Path, 
                   equalize: bool = False) -> Tuple[np.ndarray, np.ndarray]:
        """
        Load two images and ensure they're the same size.
        
        Args:
            path1: Path to first image
            path2: Path to second image
            equalize: Whether to apply histogram equalization
            
        Returns:
            Tuple of numpy arrays (img1, img2)
        """
        img1 = Image.open(path1)
        img2 = Image.open(path2)
        
        # Convert to RGB if needed
        if img1.mode != 'RGB':
            img1 = img1.convert('RGB')
        if img2.mode != 'RGB':
            img2 = img2.convert('RGB')
        
        # Resize if dimensions don't match
        if img1.size != img2.size:
            # Resize to the larger dimensions
            max_width = max(img1.width, img2.width)
            max_height = max(img1.height, img2.height)
            
            if img1.size != (max_width, max_height):
                img1 = img1.resize((max_width, max_height), Image.LANCZOS)
            if img2.size != (max_width, max_height):
                img2 = img2.resize((max_width, max_height), Image.LANCZOS)
        
        # Convert to numpy
        img1_np = np.array(img1)
        img2_np = np.array(img2)
        
        # Apply histogram equalization if requested
        if equalize:
            logger.debug("Applying histogram equalization")
            img1_np = ImageProcessor.equalize_histogram(img1_np)
            img2_np = ImageProcessor.equalize_histogram(img2_np)
        
        logger.info(f"Images loaded successfully with shape {img1_np.shape}")
        return img1_np, img2_np
    
    @staticmethod
    def create_diff_image(img1: np.ndarray, img2: np.ndarray, 
                         enhancement_factor: float = 5.0) -> np.ndarray:
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
    def create_annotated_image(img: np.ndarray, diff: np.ndarray, 
                              threshold: float = 10.0,
                              min_area: int = 50,
                              color: tuple = (255, 0, 0)) -> np.ndarray:
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
            diff_gray.astype(np.uint8), 
            threshold, 
            255, 
            cv2.THRESH_BINARY
        )
        
        # Find contours of differences
        contours, _ = cv2.findContours(
            thresh, 
            cv2.RETR_EXTERNAL, 
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Draw bounding boxes around significant differences
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > min_area:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(
                    annotated, 
                    (x, y), 
                    (x + w, y + h), 
                    color,
                    2
                )
        
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
    def create_side_by_side(img1: np.ndarray, img2: np.ndarray, 
                           diff: np.ndarray) -> np.ndarray:
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
                return np.pad(img, ((0, padding), (0, 0), (0, 0)), 
                            mode='constant', constant_values=255)
            return img
        
        img1 = pad_to_height(img1, height)
        img2 = pad_to_height(img2, height)
        diff = pad_to_height(diff, height)
        
        # Concatenate horizontally
        combined = np.hstack([img1, img2, diff])
        
        return combined
