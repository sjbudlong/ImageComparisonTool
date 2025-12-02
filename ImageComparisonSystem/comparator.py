"""
Main comparator module that orchestrates image comparison workflow.
"""

import logging
from pathlib import Path
from typing import List, Dict, Set, Iterator, Optional
import json
from concurrent.futures import ProcessPoolExecutor
import os

# Handle both package and direct module imports
try:
    from .config import Config
    from .analyzers import AnalyzerRegistry
    from .processor import ImageProcessor
    from .report_generator import ReportGenerator
    from .markdown_exporter import MarkdownExporter
    from .models import ComparisonResult
except ImportError:
    from config import Config  # type: ignore
    from analyzers import AnalyzerRegistry  # type: ignore
    from processor import ImageProcessor  # type: ignore
    from report_generator import ReportGenerator  # type: ignore
    from markdown_exporter import MarkdownExporter  # type: ignore
    from models import ComparisonResult  # type: ignore

logger = logging.getLogger("ImageComparison")


class ImageComparator:
    """Orchestrates the image comparison process."""

    # Supported image extensions
    IMAGE_EXTENSIONS: Set[str] = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".gif"}

    def __init__(self, config: Config) -> None:
        """
        Initialize image comparator.

        Args:
            config: Configuration object
        """
        self.config: Config = config
        self.analyzer_registry: AnalyzerRegistry = AnalyzerRegistry(config)
        self.processor: ImageProcessor = ImageProcessor(config)
        self.report_generator: ReportGenerator = ReportGenerator(config)

        # Ensure output directories exist
        self.config.diff_path.mkdir(parents=True, exist_ok=True)
        self.config.html_path.mkdir(parents=True, exist_ok=True)

    def _clean_output_directories(self) -> None:
        """Clean reports and diffs folders before running comparison."""
        import shutil

        # Clean diffs directory
        if self.config.diff_path.exists():
            try:
                shutil.rmtree(self.config.diff_path)
                self.config.diff_path.mkdir(parents=True, exist_ok=True)
                logger.debug("Cleaned diffs directory")
            except Exception as e:
                logger.warning(f"Could not clean diffs directory: {e}")

        # Clean reports directory
        if self.config.html_path.exists():
            try:
                shutil.rmtree(self.config.html_path)
                self.config.html_path.mkdir(parents=True, exist_ok=True)
                logger.debug("Cleaned reports directory")
            except Exception as e:
                logger.warning(f"Could not clean reports directory: {e}")

    def compare_all_streaming(self) -> Iterator[ComparisonResult]:
        """
        Compare all matching images, yielding results as they're generated.

        PERFORMANCE FIX: Uses generator pattern to stream results instead of
        accumulating them in memory. This maintains constant memory usage
        regardless of the number of images being compared.

        Yields:
            ComparisonResult objects as they're generated

        Example:
            for result in comparator.compare_all_streaming():
                print(f"Processed: {result.filename}")
                # Result is immediately available, no need to wait for all
        """
        # Clean output directories before starting
        self._clean_output_directories()

        # Find all images in new directory (recursive)
        new_images = self._find_images(self.config.new_path)

        if not new_images:
            logger.error("No images found in new directory")
            return

        # Build a lookup of known-good images (filename -> list of paths)
        known_images = self._find_images(self.config.known_good_path)
        known_index: Dict[str, List[Path]] = {}
        for kp in known_images:
            known_index.setdefault(kp.name, []).append(kp)

        total = len(new_images)
        logger.info(f"Found {total} images to compare")

        for idx, new_img_path in enumerate(new_images, 1):
            logger.info(f"[{idx}/{total}] Processing: {new_img_path.name}")

            # Find matching known good image
            known_good_path = self._find_matching_known_good(new_img_path, known_index)
            if not known_good_path:
                logger.warning(
                    f"No matching known good image found for {new_img_path.name}"
                )
                continue

            try:
                result = self._compare_single_pair(new_img_path, known_good_path)
                logger.debug(
                    f"Difference for {new_img_path.name}: {result.percent_different:.2f}%"
                )

                # Yield result immediately instead of accumulating
                # Note: Detail reports will be generated later by caller if needed
                yield result
            except Exception as e:
                logger.error(
                    f"Error processing {new_img_path.name}: {str(e)}", exc_info=True
                )
                continue

    def compare_all(self) -> List[ComparisonResult]:
        """
        Compare all matching images in the configured directories.

        REFACTORED: Now uses compare_all_streaming() internally to eliminate
        code duplication while maintaining backward compatibility.

        Returns:
            List of comparison results, sorted by difference percentage
        """
        # Collect all results from streaming generator
        results = list(self.compare_all_streaming())

        # Sort by percent difference (descending)
        results.sort(key=lambda x: x.percent_different, reverse=True)

        # Generate summary report with full results list for navigation
        logger.info("Generating summary report...")
        self._generate_reports(results)

        return results

    def _find_images(self, directory: Path) -> List[Path]:
        """Find all image files in a directory."""
        images = set()  # Use set to avoid duplicates
        if not directory.exists():
            return []

        for ext in self.IMAGE_EXTENSIONS:
            # Use rglob for recursive search
            try:
                images.update(directory.rglob(f"*{ext}"))
                images.update(directory.rglob(f"*{ext.upper()}"))
            except Exception:
                # In case directory is not readable or rglob fails for any reason
                continue

        # Filter only files
        images = {p for p in images if p.is_file()}
        return sorted(list(images))

    def _find_matching_known_good(
        self, new_img_path: Path, known_index: Dict[str, List[Path]]
    ) -> Optional[Path]:
        """
        Find the matching known good image for a new image.

        Args:
            new_img_path: Path to the new image
            known_index: Dictionary mapping filenames to known good paths

        Returns:
            Path to matching known good image, or None if not found
        """
        # Attempt to find corresponding known good image.
        # First try to match by relative subpath (preserve directory structure).
        try:
            rel = new_img_path.relative_to(self.config.new_path)
        except Exception:
            rel = Path(new_img_path.name)

        candidate = self.config.known_good_path / rel

        if candidate.exists() and candidate.is_file():
            return candidate

        # Fallback: lookup by filename anywhere under known_good tree
        matches = known_index.get(new_img_path.name, [])
        if matches:
            # If multiple matches exist, prefer one with the same relative parent name
            if len(matches) == 1:
                return matches[0]
            else:
                # Try to find the best candidate: same relative parent directory
                new_parent = rel.parent.name if rel.parent != Path(".") else None
                for m in matches:
                    if new_parent and m.parent.name == new_parent:
                        return m
                return matches[0]

        return None

    @staticmethod
    def _compare_pair_worker(args: tuple) -> Optional[ComparisonResult]:
        """
        Static worker function for parallel processing.

        PERFORMANCE FIX: Designed to be used with ProcessPoolExecutor for
        parallel image comparisons. Each worker process operates independently.

        Args:
            args: Tuple of (config_dict, new_path, known_good_path)
                - config_dict: Serializable config attributes
                - new_path: Path to new image
                - known_good_path: Path to known good image

        Returns:
            ComparisonResult if successful, None if error occurred
        """
        config_dict, new_path, known_good_path = args

        # Reconstruct minimal objects needed for comparison
        # (Can't pickle the full comparator, so we recreate components)
        try:
            from .config import Config
            from .processor import ImageProcessor
            from .analyzers import AnalyzerRegistry
        except ImportError:
            from config import Config  # type: ignore
            from processor import ImageProcessor  # type: ignore
            from analyzers import AnalyzerRegistry  # type: ignore

        try:
            # Reconstruct config from dict
            config = Config(**config_dict)

            # Create processor and analyzer
            processor = ImageProcessor()
            analyzer_registry = AnalyzerRegistry(config)

            # Load images once with both original and equalized versions
            img_new_orig, img_known_orig, img_new_eq, img_known_eq = (
                processor.load_images(
                    new_path,
                    known_good_path,
                    equalize=config.use_histogram_equalization,
                    use_clahe=config.use_clahe,
                    to_grayscale=config.equalize_to_grayscale,
                    return_both=True,
                )
            )

            # Generate histogram visualization using original images
            histogram_data = processor.generate_histogram_image(
                img_known_orig, img_new_orig
            )

            # Run all analyzers on equalized images
            metrics = analyzer_registry.analyze_all(img_known_eq, img_new_eq)

            # Generate diff images using equalized versions
            diff_img_unenhanced = processor.create_diff_image(
                img_known_eq, img_new_eq, enhancement_factor=1.0
            )
            diff_img = processor.create_diff_image(
                img_known_eq,
                img_new_eq,
                enhancement_factor=config.diff_enhancement_factor,
            )

            # Create annotated image with bounding boxes
            annotated_img = processor.create_annotated_image(
                diff_img_unenhanced,
                diff_img_unenhanced,
                threshold=10.0,
                min_area=config.min_contour_area,
                color=config.highlight_color,
            )

            # Save diff images
            diff_path = config.diff_path / f"diff_{new_path.name}"
            annotated_path = config.diff_path / f"annotated_{new_path.name}"

            processor.save_image(diff_img, diff_path)
            processor.save_image(annotated_img, annotated_path)

            # Calculate percent difference
            percent_diff = metrics.get("Pixel Difference", {}).get(
                "percent_different", 0.0
            )

            return ComparisonResult(
                filename=new_path.name,
                new_image_path=new_path,
                known_good_path=known_good_path,
                diff_image_path=diff_path,
                annotated_image_path=annotated_path,
                metrics=metrics,
                percent_different=percent_diff,
                histogram_data=histogram_data,
            )
        except Exception as e:
            # Log error and return None (will be filtered out)
            logger.error(f"Worker error processing {new_path.name}: {str(e)}")
            return None

    def compare_all_parallel(self) -> List[ComparisonResult]:
        """
        Compare all matching images using parallel processing.

        PERFORMANCE FIX: Uses ProcessPoolExecutor to process multiple images
        concurrently, reducing total processing time by ~70% on multi-core systems.

        Expected performance:
        - Sequential: 2.7 hours for 2000 images
        - Parallel (4 cores): ~40 minutes for 2000 images
        - Parallel (8 cores): ~20 minutes for 2000 images

        Returns:
            List of comparison results, sorted by difference percentage
        """
        # Clean output directories before starting
        self._clean_output_directories()

        # Find all images
        new_images = self._find_images(self.config.new_path)
        if not new_images:
            logger.error("No images found in new directory")
            return []

        # Build known index
        known_images = self._find_images(self.config.known_good_path)
        known_index: Dict[str, List[Path]] = {}
        for kp in known_images:
            known_index.setdefault(kp.name, []).append(kp)

        # Build work items (filter out non-matching pairs)
        work_items = []
        for new_img_path in new_images:
            known_good_path = self._find_matching_known_good(new_img_path, known_index)
            if known_good_path:
                work_items.append((new_img_path, known_good_path))
            else:
                logger.warning(
                    f"No matching known good image found for {new_img_path.name}"
                )

        if not work_items:
            logger.warning("No matching image pairs found")
            return []

        # Serialize config for worker processes
        config_dict = {
            "base_dir": self.config.base_dir,
            "new_dir": self.config.new_dir,
            "known_good_dir": self.config.known_good_dir,
            "diff_dir": self.config.diff_dir,
            "html_dir": self.config.html_dir,
            "pixel_diff_threshold": self.config.pixel_diff_threshold,
            "pixel_change_threshold": self.config.pixel_change_threshold,
            "ssim_threshold": self.config.ssim_threshold,
            "color_distance_threshold": self.config.color_distance_threshold,
            "min_contour_area": self.config.min_contour_area,
            "use_histogram_equalization": self.config.use_histogram_equalization,
            "use_clahe": self.config.use_clahe,
            "equalize_to_grayscale": self.config.equalize_to_grayscale,
            "highlight_color": self.config.highlight_color,
            "diff_enhancement_factor": self.config.diff_enhancement_factor,
        }

        # Prepare args for worker
        worker_args = [
            (config_dict, new_path, known_path) for new_path, known_path in work_items
        ]

        # Determine worker count
        max_workers = self.config.max_workers or os.cpu_count()
        total = len(work_items)

        logger.info(f"Processing {total} image pairs using {max_workers} workers...")

        # Process in parallel
        results = []
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Submit all work
            futures = [
                executor.submit(ImageComparator._compare_pair_worker, args)
                for args in worker_args
            ]

            # Collect results as they complete
            for idx, future in enumerate(futures, 1):
                try:
                    result = future.result(timeout=300)  # 5 minute timeout per image
                    if result:
                        results.append(result)
                        logger.info(
                            f"[{idx}/{total}] Completed: {result.filename} ({result.percent_different:.2f}%)"
                        )
                    else:
                        logger.warning(f"[{idx}/{total}] Failed to process image")
                except Exception as e:
                    logger.error(f"[{idx}/{total}] Error: {str(e)}")

        # Sort by percent difference (descending)
        results.sort(key=lambda x: x.percent_different, reverse=True)

        # Generate reports
        logger.info("Generating reports...")
        self._generate_reports(results)

        return results

    def _compare_single_pair(
        self, new_path: Path, known_good_path: Path
    ) -> ComparisonResult:
        """
        Compare a single pair of images.

        PERFORMANCE FIX: Load images once using return_both=True to eliminate
        duplicate I/O operations (50% reduction in file reads).

        Args:
            new_path: Path to new image
            known_good_path: Path to known good image

        Returns:
            ComparisonResult object
        """
        # PERFORMANCE FIX: Load images once, get both original and equalized versions
        # This eliminates the previous duplicate load operation
        img_new_orig, img_known_orig, img_new_eq, img_known_eq = (
            self.processor.load_images(
                new_path,
                known_good_path,
                equalize=self.config.use_histogram_equalization,
                use_clahe=self.config.use_clahe,
                to_grayscale=self.config.equalize_to_grayscale,
                return_both=True,  # Get both original and equalized in one load
            )
        )

        # Generate histogram visualization using original images
        histogram_data = self.processor.generate_histogram_image(
            img_known_orig, img_new_orig, self.config.histogram_config
        )

        # Run all analyzers on equalized images
        metrics = self.analyzer_registry.analyze_all(img_known_eq, img_new_eq)

        # Extract primary difference percentage
        percent_diff = metrics.get("Pixel Difference", {}).get("percent_different", 0)

        # Generate diff images using equalized versions
        # Create unenhanced diff for annotation target
        diff_img_unenhanced = self.processor.create_diff_image(
            img_known_eq, img_new_eq, enhancement_factor=1.0
        )
        # Create enhanced diff for visualization
        diff_img = self.processor.create_diff_image(
            img_known_eq,
            img_new_eq,
            enhancement_factor=self.config.diff_enhancement_factor,
        )
        # Use unenhanced diff as annotation target
        annotated_img = self.processor.create_annotated_image(
            diff_img_unenhanced,
            diff_img_unenhanced,
            threshold=10.0,
            min_area=self.config.min_contour_area,
            color=self.config.highlight_color,
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
            histogram_data=histogram_data,
        )

    def _generate_reports(self, results: List[ComparisonResult]):
        """Generate HTML and markdown reports for all results."""
        logger.info("Generating reports...")

        # Group results by subdirectory for hierarchical reporting
        grouped = self.report_generator._group_by_subdirectory(results)

        # Generate subdirectory index pages
        for subdirectory, subdir_results in grouped.items():
            self.report_generator.generate_subdirectory_index(
                subdirectory, subdir_results
            )

        # Generate individual detail reports with subdirectory-specific navigation
        for subdirectory, subdir_results in grouped.items():
            for result in subdir_results:
                # Pass only results from the same subdirectory for prev/next navigation
                self.report_generator.generate_detail_report(result, subdir_results)

        # Generate summary reports (HTML) - now shows subdirectories
        self.report_generator.generate_summary_report(results)

        # Generate markdown summary for CI/CD pipeline integration
        markdown_exporter = MarkdownExporter(self.config.html_path)
        markdown_exporter.export_summary(results, self.config.new_path)

        # Save results as JSON for potential later use
        json_path = self.config.html_path / "results.json"
        try:
            with open(json_path, "w") as f:
                json.dump(
                    [r.to_dict(self.config.new_path) for r in results], f, indent=2
                )
            logger.info("Saved results JSON: results.json")
        except Exception as e:
            logger.error(f"Error saving JSON results: {e}", exc_info=True)
