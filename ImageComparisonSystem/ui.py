"""
UI module for image comparison configuration.
Uses tkinter for a simple GUI interface.
"""

import logging
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Optional, Tuple

# Handle both package and direct module imports
try:
    from .config import Config
except ImportError:
    from config import Config  # type: ignore

logger = logging.getLogger("ImageComparison")


class ComparisonUI:
    """GUI for configuring image comparison settings."""

    def __init__(self) -> None:
        logger.debug("Initializing ComparisonUI")
        self.config: Optional[Config] = None
        self.root = tk.Tk()
        self.root.title("Image Comparison Configuration")
        self.root.geometry("1400x1000")  # Expanded width for historical tracking panel
        self.root.resizable(True, True)

        self._create_widgets()

    def _create_widgets(self):
        """Create and layout UI widgets."""
        # Main container frame
        container = ttk.Frame(self.root, padding="20")
        container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)

        # Left panel - Main settings
        main_frame = ttk.Frame(container, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        main_frame.columnconfigure(1, weight=1)

        # Right panel - Historical tracking
        history_frame = ttk.Frame(
            container, padding="10", relief="groove", borderwidth=2
        )
        history_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        history_frame.columnconfigure(1, weight=1)

        # Title - spans both panels
        title = ttk.Label(
            main_frame,
            text="Image Comparison Configuration",
            font=("Arial", 16, "bold"),
        )
        title.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # Base Directory
        row = 1
        ttk.Label(main_frame, text="Base Directory:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.base_dir_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.base_dir_var, width=50).grid(
            row=row, column=1, sticky=(tk.W, tk.E), padx=5
        )
        ttk.Button(main_frame, text="Browse...", command=self._browse_base_dir).grid(
            row=row, column=2
        )

        # New Images Directory
        row += 1
        ttk.Label(main_frame, text="New Images (relative):").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.new_dir_var = tk.StringVar(value="new")
        ttk.Entry(main_frame, textvariable=self.new_dir_var, width=50).grid(
            row=row, column=1, sticky=(tk.W, tk.E), padx=5
        )

        # Known Good Directory
        row += 1
        ttk.Label(main_frame, text="Known Good (relative):").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.known_good_var = tk.StringVar(value="known_good")
        ttk.Entry(main_frame, textvariable=self.known_good_var, width=50).grid(
            row=row, column=1, sticky=(tk.W, tk.E), padx=5
        )

        # Diff Directory
        row += 1
        ttk.Label(main_frame, text="Diff Output (relative):").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.diff_dir_var = tk.StringVar(value="diffs")
        ttk.Entry(main_frame, textvariable=self.diff_dir_var, width=50).grid(
            row=row, column=1, sticky=(tk.W, tk.E), padx=5
        )

        # HTML Directory
        row += 1
        ttk.Label(main_frame, text="HTML Reports (relative):").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.html_dir_var = tk.StringVar(value="reports")
        ttk.Entry(main_frame, textvariable=self.html_dir_var, width=50).grid(
            row=row, column=1, sticky=(tk.W, tk.E), padx=5
        )

        # Separator for tolerances
        row += 1
        ttk.Separator(main_frame, orient="horizontal").grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=15
        )

        row += 1
        ttk.Label(
            main_frame, text="Tolerances & Thresholds", font=("Arial", 12, "bold")
        ).grid(row=row, column=0, columnspan=3, sticky=tk.W)

        # Pixel Difference Threshold
        row += 1
        ttk.Label(main_frame, text="Pixel Diff Threshold (%):").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.pixel_diff_threshold_var = tk.StringVar(value="0.01")
        ttk.Entry(
            main_frame, textvariable=self.pixel_diff_threshold_var, width=50
        ).grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5)

        # Pixel Change Threshold
        row += 1
        ttk.Label(main_frame, text="Min Pixel Change:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.pixel_change_threshold_var = tk.StringVar(value="1")
        ttk.Entry(
            main_frame, textvariable=self.pixel_change_threshold_var, width=50
        ).grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5)

        # SSIM Threshold
        row += 1
        ttk.Label(main_frame, text="SSIM Threshold (0-1):").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.ssim_threshold_var = tk.StringVar(value="0.95")
        ttk.Entry(main_frame, textvariable=self.ssim_threshold_var, width=50).grid(
            row=row, column=1, sticky=(tk.W, tk.E), padx=5
        )

        # Color Distance Threshold
        row += 1
        ttk.Label(main_frame, text="Color Distance Threshold:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.color_distance_var = tk.StringVar(value="10.0")
        ttk.Entry(main_frame, textvariable=self.color_distance_var, width=50).grid(
            row=row, column=1, sticky=(tk.W, tk.E), padx=5
        )

        # Min Contour Area
        row += 1
        ttk.Label(main_frame, text="Min Bounding Box Area:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.min_contour_var = tk.StringVar(value="50")
        ttk.Entry(main_frame, textvariable=self.min_contour_var, width=50).grid(
            row=row, column=1, sticky=(tk.W, tk.E), padx=5
        )

        # Separator for visual settings
        row += 1
        ttk.Separator(main_frame, orient="horizontal").grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=15
        )

        row += 1
        ttk.Label(main_frame, text="Visual Settings", font=("Arial", 12, "bold")).grid(
            row=row, column=0, columnspan=3, sticky=tk.W
        )

        # Histogram Equalization
        row += 1
        self.use_histogram_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            main_frame,
            text="Use Histogram Equalization (normalize tonal variations)",
            variable=self.use_histogram_var,
        ).grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=5)

        # Highlight Color
        row += 1
        ttk.Label(main_frame, text="Highlight Color (R,G,B):").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.highlight_color_var = tk.StringVar(value="255,0,0")
        color_frame = ttk.Frame(main_frame)
        color_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Entry(color_frame, textvariable=self.highlight_color_var, width=20).pack(
            side=tk.LEFT
        )
        self.color_preview = tk.Canvas(
            color_frame, width=30, height=20, bg="red", relief=tk.SUNKEN
        )
        self.color_preview.pack(side=tk.LEFT, padx=5)
        self.highlight_color_var.trace("w", self._update_color_preview)

        # Diff Enhancement Factor
        row += 1
        ttk.Label(main_frame, text="Diff Enhancement Factor:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.diff_enhancement_var = tk.StringVar(value="5.0")
        ttk.Entry(main_frame, textvariable=self.diff_enhancement_var, width=50).grid(
            row=row, column=1, sticky=(tk.W, tk.E), padx=5
        )

        # Separator for histogram settings
        row += 1
        ttk.Separator(main_frame, orient="horizontal").grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=15
        )

        row += 1
        ttk.Label(
            main_frame, text="Histogram Visualization", font=("Arial", 12, "bold")
        ).grid(row=row, column=0, columnspan=3, sticky=tk.W)

        # Histogram Bins
        row += 1
        ttk.Label(main_frame, text="Histogram Bins (64-512):").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.hist_bins_var = tk.StringVar(value="256")
        ttk.Entry(main_frame, textvariable=self.hist_bins_var, width=50).grid(
            row=row, column=1, sticky=(tk.W, tk.E), padx=5
        )

        # Figure Width
        row += 1
        ttk.Label(main_frame, text="Figure Width (inches):").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.hist_width_var = tk.StringVar(value="16")
        ttk.Entry(main_frame, textvariable=self.hist_width_var, width=50).grid(
            row=row, column=1, sticky=(tk.W, tk.E), padx=5
        )

        # Figure Height
        row += 1
        ttk.Label(main_frame, text="Figure Height (inches):").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.hist_height_var = tk.StringVar(value="6")
        ttk.Entry(main_frame, textvariable=self.hist_height_var, width=50).grid(
            row=row, column=1, sticky=(tk.W, tk.E), padx=5
        )

        # Grayscale Alpha
        row += 1
        ttk.Label(main_frame, text="Grayscale Transparency (0-1):").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.hist_gray_alpha_var = tk.StringVar(value="0.7")
        ttk.Entry(main_frame, textvariable=self.hist_gray_alpha_var, width=50).grid(
            row=row, column=1, sticky=(tk.W, tk.E), padx=5
        )

        # RGB Alpha
        row += 1
        ttk.Label(main_frame, text="RGB Transparency (0-1):").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.hist_rgb_alpha_var = tk.StringVar(value="0.7")
        ttk.Entry(main_frame, textvariable=self.hist_rgb_alpha_var, width=50).grid(
            row=row, column=1, sticky=(tk.W, tk.E), padx=5
        )

        # Grayscale Line Width
        row += 1
        ttk.Label(main_frame, text="Grayscale Line Width:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.hist_gray_lw_var = tk.StringVar(value="2.0")
        ttk.Entry(main_frame, textvariable=self.hist_gray_lw_var, width=50).grid(
            row=row, column=1, sticky=(tk.W, tk.E), padx=5
        )

        # RGB Line Width
        row += 1
        ttk.Label(main_frame, text="RGB Line Width:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.hist_rgb_lw_var = tk.StringVar(value="1.5")
        ttk.Entry(main_frame, textvariable=self.hist_rgb_lw_var, width=50).grid(
            row=row, column=1, sticky=(tk.W, tk.E), padx=5
        )

        # Show Grayscale
        row += 1
        self.hist_show_gray_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            main_frame,
            text="Show Grayscale Histogram",
            variable=self.hist_show_gray_var,
        ).grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=5)

        # Show RGB
        row += 1
        self.hist_show_rgb_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            main_frame,
            text="Show RGB Channel Histograms",
            variable=self.hist_show_rgb_var,
        ).grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=5)

        # Info text
        row += 1
        info_text = (
            "Note: New Images and Known Good directories should contain "
            "matching image filenames.\nDiff and HTML directories will be "
            "created automatically."
        )
        info_label = ttk.Label(
            main_frame, text=info_text, foreground="gray", wraplength=600
        )
        info_label.grid(row=row, column=0, columnspan=3, pady=(20, 10), sticky=tk.W)

        # === HISTORICAL TRACKING PANEL (RIGHT SIDE) ===
        self._create_history_widgets(history_frame)

        # Buttons (in container, spanning both columns)
        button_frame = ttk.Frame(container)
        button_frame.grid(row=1, column=0, columnspan=2, pady=(20, 0))

        ttk.Button(
            button_frame, text="Start Comparison", command=self._on_start, width=20
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="Cancel", command=self._on_cancel, width=20).pack(
            side=tk.LEFT, padx=5
        )

    def _create_history_widgets(self, parent_frame):
        """Create historical tracking configuration widgets."""
        row = 0

        # Title
        ttk.Label(
            parent_frame, text="Historical Metrics Tracking", font=("Arial", 14, "bold")
        ).grid(row=row, column=0, columnspan=3, pady=(0, 15), sticky=tk.W)

        # Enable History
        row += 1
        self.enable_history_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            parent_frame,
            text="Enable historical metrics tracking",
            variable=self.enable_history_var,
            command=self._toggle_history_fields,
        ).grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=5)

        # Build Number
        row += 1
        ttk.Label(parent_frame, text="Build Number/ID:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.build_number_var = tk.StringVar()
        self.build_number_entry = ttk.Entry(
            parent_frame, textvariable=self.build_number_var, width=30
        )
        self.build_number_entry.grid(
            row=row, column=1, sticky=(tk.W, tk.E), padx=5, columnspan=2
        )

        # Commit Hash (for reproducibility)
        row += 1
        ttk.Label(parent_frame, text="Commit Hash:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.commit_hash_var = tk.StringVar()
        self.commit_hash_entry = ttk.Entry(
            parent_frame, textvariable=self.commit_hash_var, width=30
        )
        self.commit_hash_entry.grid(
            row=row, column=1, sticky=(tk.W, tk.E), padx=5, columnspan=2
        )

        ttk.Label(
            parent_frame,
            text="(Optional - Git commit SHA for exact reproducibility)",
            foreground="gray",
            font=("Arial", 8),
        ).grid(row=row + 1, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))

        # History Database Path
        row += 2
        ttk.Label(parent_frame, text="History DB Path:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.history_db_var = tk.StringVar()
        self.history_db_entry = ttk.Entry(
            parent_frame, textvariable=self.history_db_var, width=30
        )
        self.history_db_entry.grid(
            row=row, column=1, sticky=(tk.W, tk.E), padx=5, columnspan=2
        )

        ttk.Label(
            parent_frame,
            text="(Optional - default: <base-dir>/.imgcomp_history/)",
            foreground="gray",
            font=("Arial", 8),
        ).grid(row=row + 1, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))

        # Separator
        row += 2
        ttk.Separator(parent_frame, orient="horizontal").grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=15
        )

        # Anomaly Detection
        row += 1
        ttk.Label(
            parent_frame, text="Anomaly Detection", font=("Arial", 12, "bold")
        ).grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))

        row += 1
        ttk.Label(parent_frame, text="Anomaly Threshold (σ):").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.anomaly_threshold_var = tk.StringVar(value="2.0")
        self.anomaly_threshold_entry = ttk.Entry(
            parent_frame, textvariable=self.anomaly_threshold_var, width=10
        )
        self.anomaly_threshold_entry.grid(row=row, column=1, sticky=tk.W, padx=5)

        ttk.Label(
            parent_frame,
            text="(standard deviations)",
            foreground="gray",
            font=("Arial", 8),
        ).grid(row=row, column=2, sticky=tk.W)

        # Separator
        row += 1
        ttk.Separator(parent_frame, orient="horizontal").grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=15
        )

        # Data Retention
        row += 1
        ttk.Label(
            parent_frame, text="Data Retention (Cleanup)", font=("Arial", 12, "bold")
        ).grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))

        # Keep all runs
        row += 1
        self.keep_all_runs_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            parent_frame,
            text="Keep all historical runs",
            variable=self.keep_all_runs_var,
            command=self._toggle_retention_fields,
        ).grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=5)

        # Max runs to keep
        row += 1
        ttk.Label(parent_frame, text="Max Runs to Keep:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.max_runs_var = tk.StringVar()
        self.max_runs_entry = ttk.Entry(
            parent_frame, textvariable=self.max_runs_var, width=10, state="disabled"
        )
        self.max_runs_entry.grid(row=row, column=1, sticky=tk.W, padx=5)

        # Max age in days
        row += 1
        ttk.Label(parent_frame, text="Max Age (days):").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.max_age_days_var = tk.StringVar()
        self.max_age_days_entry = ttk.Entry(
            parent_frame, textvariable=self.max_age_days_var, width=10, state="disabled"
        )
        self.max_age_days_entry.grid(row=row, column=1, sticky=tk.W, padx=5)

        # Keep annotated
        row += 1
        self.keep_annotated_var = tk.BooleanVar(value=True)
        self.keep_annotated_check = ttk.Checkbutton(
            parent_frame,
            text="Always keep annotated results",
            variable=self.keep_annotated_var,
            state="disabled",
        )
        self.keep_annotated_check.grid(
            row=row, column=0, columnspan=3, sticky=tk.W, pady=5
        )

        # Keep anomalies
        row += 1
        self.keep_anomalies_var = tk.BooleanVar(value=True)
        self.keep_anomalies_check = ttk.Checkbutton(
            parent_frame,
            text="Always keep anomalous results",
            variable=self.keep_anomalies_var,
            state="disabled",
        )
        self.keep_anomalies_check.grid(
            row=row, column=0, columnspan=3, sticky=tk.W, pady=5
        )

        # Info text
        row += 1
        info_text = (
            "Historical tracking stores metrics in a SQLite database for "
            "trend analysis and anomaly detection. Build number helps identify runs."
        )
        info_label = ttk.Label(
            parent_frame, text=info_text, foreground="gray", wraplength=400
        )
        info_label.grid(row=row, column=0, columnspan=3, pady=(20, 10), sticky=tk.W)

    def _toggle_parallel_fields(self):
        """Enable/disable parallel processing fields based on checkbox."""
        state = "normal" if self.enable_parallel_var.get() else "disabled"
        self.max_workers_entry.config(state=state)

    def _toggle_history_fields(self):
        """Enable/disable history fields based on checkbox."""
        state = "normal" if self.enable_history_var.get() else "disabled"
        self.build_number_entry.config(state=state)
        self.history_db_entry.config(state=state)
        self.anomaly_threshold_entry.config(state=state)
        # Don't disable retention fields here - they have their own toggle

    def _toggle_retention_fields(self):
        """Enable/disable retention fields based on keep_all_runs checkbox."""
        state = "disabled" if self.keep_all_runs_var.get() else "normal"
        self.max_runs_entry.config(state=state)
        self.max_age_days_entry.config(state=state)
        self.keep_annotated_check.config(state=state)
        self.keep_anomalies_check.config(state=state)

    def _update_color_preview(self, *args):
        """Update the color preview box."""
        try:
            color_str = self.highlight_color_var.get()
            parts = [int(x.strip()) for x in color_str.split(",")]
            if len(parts) == 3 and all(0 <= p <= 255 for p in parts):
                hex_color = f"#{parts[0]:02x}{parts[1]:02x}{parts[2]:02x}"
                self.color_preview.configure(bg=hex_color)
        except (ValueError, AttributeError):
            logger.debug(f"Invalid color format provided: {color_str}")
            pass

    def _browse_base_dir(self) -> None:
        """Open directory browser for base directory."""
        directory = filedialog.askdirectory(title="Select Base Directory")
        if directory:
            self.base_dir_var.set(directory)

    def _on_start(self) -> None:
        """Validate inputs and create config."""
        logger.debug("Starting comparison from UI")
        try:
            # Validate inputs
            if not self.base_dir_var.get():
                logger.warning("Base directory not selected")
                messagebox.showerror("Error", "Please select a base directory")
                return

            if not self.new_dir_var.get():
                logger.warning("New images directory not specified")
                messagebox.showerror("Error", "Please specify new images directory")
                return

            if not self.known_good_var.get():
                messagebox.showerror("Error", "Please specify known good directory")
                return

            # Create config
            pixel_diff_threshold: float = float(self.pixel_diff_threshold_var.get())
            pixel_change_threshold: int = int(self.pixel_change_threshold_var.get())
            ssim_threshold: float = float(self.ssim_threshold_var.get())
            color_distance: float = float(self.color_distance_var.get())
            min_contour: int = int(self.min_contour_var.get())
            diff_enhancement: float = float(self.diff_enhancement_var.get())

            # Parse highlight color
            color_parts: list = [
                int(x.strip()) for x in self.highlight_color_var.get().split(",")
            ]
            if len(color_parts) != 3 or not all(0 <= p <= 255 for p in color_parts):
                raise ValueError("Invalid color format")
            highlight_color: Tuple[int, int, int] = tuple(color_parts)

            # Create histogram config
            from config import HistogramConfig

            hist_config = HistogramConfig(
                bins=int(self.hist_bins_var.get()),
                figure_width=float(self.hist_width_var.get()),
                figure_height=float(self.hist_height_var.get()),
                grayscale_alpha=float(self.hist_gray_alpha_var.get()),
                rgb_alpha=float(self.hist_rgb_alpha_var.get()),
                grayscale_linewidth=float(self.hist_gray_lw_var.get()),
                rgb_linewidth=float(self.hist_rgb_lw_var.get()),
                show_grayscale=self.hist_show_gray_var.get(),
                show_rgb=self.hist_show_rgb_var.get(),
            )

            # Parse parallel processing settings
            enable_parallel = self.enable_parallel_var.get()
            max_workers = (
                int(self.max_workers_var.get()) if self.max_workers_var.get() else None
            )

            # Parse historical tracking settings
            enable_history = self.enable_history_var.get()
            build_number = (
                self.build_number_var.get() if self.build_number_var.get() else None
            )
            history_db_path = (
                Path(self.history_db_var.get()) if self.history_db_var.get() else None
            )
            anomaly_threshold = (
                float(self.anomaly_threshold_var.get())
                if self.anomaly_threshold_var.get()
                else 2.0
            )

            # Parse retention settings
            retention_keep_all = self.keep_all_runs_var.get()
            retention_max_runs = (
                int(self.max_runs_var.get()) if self.max_runs_var.get() else None
            )
            retention_max_age = (
                int(self.max_age_days_var.get())
                if self.max_age_days_var.get()
                else None
            )
            retention_keep_annotated = self.keep_annotated_var.get()
            retention_keep_anomalies = self.keep_anomalies_var.get()

            # Get commit hash (optional)
            commit_hash = self.commit_hash_var.get().strip() or None

            self.config = Config(
                base_dir=Path(self.base_dir_var.get()),
                new_dir=self.new_dir_var.get(),
                known_good_dir=self.known_good_var.get(),
                diff_dir=self.diff_dir_var.get(),
                html_dir=self.html_dir_var.get(),
                pixel_diff_threshold=pixel_diff_threshold,
                pixel_change_threshold=pixel_change_threshold,
                ssim_threshold=ssim_threshold,
                color_distance_threshold=color_distance,
                min_contour_area=min_contour,
                use_histogram_equalization=self.use_histogram_var.get(),
                highlight_color=highlight_color,
                diff_enhancement_factor=diff_enhancement,
                histogram_config=hist_config,
                # Parallel processing settings
                enable_parallel=enable_parallel,
                max_workers=max_workers,
                # Historical tracking settings
                enable_history=enable_history,
                build_number=build_number,
                commit_hash=commit_hash,
                history_db_path=history_db_path,
                anomaly_threshold=anomaly_threshold,
                # Retention policy settings
                retention_keep_all=retention_keep_all,
                retention_max_runs=retention_max_runs,
                retention_max_age_days=retention_max_age,
                retention_keep_annotated=retention_keep_annotated,
                retention_keep_anomalies=retention_keep_anomalies,
            )

            # Validate config
            is_valid, error_msg = self.config.validate()
            if not is_valid:
                messagebox.showerror("Validation Error", error_msg)
                return

            self.root.quit()

        except ValueError as e:
            messagebox.showerror("Error", f"Invalid value: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def _on_cancel(self):
        """Cancel and close UI."""
        self.config = None
        self.root.quit()

    def run(self) -> Optional[Config]:
        """Run the UI and return the configuration."""
        self.root.mainloop()
        self.root.destroy()
        return self.config
