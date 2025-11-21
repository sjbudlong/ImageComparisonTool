"""
Main comparator module that orchestrates image comparison workflow.
"""

from pathlib import Path
from typing import List, Dict, Any
import json
from config import Config
from analyzers import AnalyzerRegistry
from processor import ImageProcessor
from report_generator import ReportGenerator
from models import ComparisonResult


class ImageComparator:
    """Orchestrates the image comparison process."""
    
    # Supported image extensions
    IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif'}
    
    def __init__(self, config: Config):
        self.config = config
        self.analyzer_registry = AnalyzerRegistry(config)
        self.processor = ImageProcessor(config)
        self.report_generator = ReportGenerator(config)
        
        # Ensure output directories exist
        self.config.diff_path.mkdir(parents=True, exist_ok=True)
        self.config.html_path.mkdir(parents=True, exist_ok=True)
    
    def _clean_output_directories(self):
        """Clean reports and diffs folders before running comparison."""
        import shutil
        
        # Clean diffs directory
        if self.config.diff_path.exists():
            try:
                shutil.rmtree(self.config.diff_path)
                self.config.diff_path.mkdir(parents=True, exist_ok=True)
                print("Cleaned diffs directory")
            except Exception as e:
                print(f"Warning: Could not clean diffs directory: {e}")
        
        # Clean reports directory
        if self.config.html_path.exists():
            try:
                shutil.rmtree(self.config.html_path)
                self.config.html_path.mkdir(parents=True, exist_ok=True)
                print("Cleaned reports directory")
            except Exception as e:
                print(f"Warning: Could not clean reports directory: {e}")
    
    def compare_all(self) -> List[ComparisonResult]:
        """
        Compare all matching images in the configured directories.
        
        Returns:
            List of comparison results, sorted by difference percentage
        """
        # Clean output directories before starting
        self._clean_output_directories()
        
        # Find all images in new directory
        new_images = self._find_images(self.config.new_path)
        
        if not new_images:
            print("No images found in new directory")
            return []
        
        results = []
        total = len(new_images)
        
        print(f"Found {total} images to compare\n")
        
        for idx, new_img_path in enumerate(new_images, 1):
            print(f"[{idx}/{total}] Processing: {new_img_path.name}")
            
            # Find corresponding known good image
            known_good_path = self.config.known_good_path / new_img_path.name
            
            if not known_good_path.exists():
                print(f"  ! Warning: No matching known good image found")
                continue
            
            try:
                result = self._compare_single_pair(new_img_path, known_good_path)
                results.append(result)
                print(f"  + Difference: {result.percent_different:.2f}%")
            except Exception as e:
                print(f"  - Error: {str(e)}")
                continue
        
        # Sort by percent difference (descending)
        results.sort(key=lambda x: x.percent_different, reverse=True)
        
        # Generate reports
        print("\nGenerating reports...")
        self._generate_reports(results)
        
        return results
    
    def _find_images(self, directory: Path) -> List[Path]:
        """Find all image files in a directory."""
        images = set()  # Use set to avoid duplicates
        for ext in self.IMAGE_EXTENSIONS:
            images.update(directory.glob(f"*{ext}"))
            images.update(directory.glob(f"*{ext.upper()}"))
        return sorted(list(images))
    
    def _compare_single_pair(self, new_path: Path, 
                            known_good_path: Path) -> ComparisonResult:
        """
        Compare a single pair of images.
        
        Args:
            new_path: Path to new image
            known_good_path: Path to known good image
            
        Returns:
            ComparisonResult object
        """
        # Load images with optional histogram equalization
        img_new, img_known = self.processor.load_images(
            new_path, 
            known_good_path,
            equalize=self.config.use_histogram_equalization
        )
        
        # Generate histogram visualization (using original images, not equalized)
        img_new_orig, img_known_orig = self.processor.load_images(
            new_path, known_good_path, equalize=False
        )
        histogram_data = self.processor.generate_histogram_image(
            img_known_orig, img_new_orig
        )
        
        # Run all analyzers
        metrics = self.analyzer_registry.analyze_all(img_known, img_new)
        
        # Extract primary difference percentage
        percent_diff = metrics.get('Pixel Difference', {}).get('percent_different', 0)
        
        # Generate diff images
        diff_img = self.processor.create_diff_image(
            img_known, img_new, 
            enhancement_factor=self.config.diff_enhancement_factor
        )
        annotated_img = self.processor.create_annotated_image(
            img_new, diff_img, 
            threshold=10.0,
            min_area=self.config.min_contour_area,
            color=self.config.highlight_color
        )
        
        # Save diff images
        diff_path = self.config.diff_path / f"diff_{new_path.name}"
        annotated_path = self.config.diff_path / f"annotated_{new_path.name}"
        
        self.processor.save_image(diff_img, diff_path)
        self.processor.save_image(annotated_img, annotated_path)
        
        return ComparisonResult(
            filename=new_path.name,
            new_image_path=new_path,
            known_good_path=known_good_path,
            diff_image_path=diff_path,
            annotated_image_path=annotated_path,
            metrics=metrics,
            percent_different=percent_diff,
            histogram_data=histogram_data
        )
    
    def _generate_reports(self, results: List[ComparisonResult]):
        """Generate HTML reports for all results."""
        print("\nGenerating reports...")
        
        # Generate individual reports with full results list for navigation
        for result in results:
            self.report_generator.generate_detail_report(result, results)
        
        # Generate summary report
        self.report_generator.generate_summary_report(results)
        
        # Save results as JSON for potential later use
        json_path = self.config.html_path / 'results.json'
        try:
            with open(json_path, 'w') as f:
                json.dump([r.to_dict() for r in results], f, indent=2)
            print(f"  + Saved results JSON: results.json")
        except Exception as e:
            print(f"  - Error saving JSON results: {e}")
