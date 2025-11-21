"""
UI module for image comparison configuration.
Uses tkinter for a simple GUI interface.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Optional
from config import Config


class ComparisonUI:
    """GUI for configuring image comparison settings."""
    
    def __init__(self):
        self.config: Optional[Config] = None
        self.root = tk.Tk()
        self.root.title("Image Comparison Configuration")
        self.root.geometry("750x700")
        self.root.resizable(True, True)
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create and layout UI widgets."""
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title = ttk.Label(
            main_frame, 
            text="Image Comparison Configuration",
            font=('Arial', 16, 'bold')
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
        ttk.Button(
            main_frame, text="Browse...", command=self._browse_base_dir
        ).grid(row=row, column=2)
        
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
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=15
        )
        
        row += 1
        ttk.Label(
            main_frame, 
            text="Tolerances & Thresholds",
            font=('Arial', 12, 'bold')
        ).grid(row=row, column=0, columnspan=3, sticky=tk.W)
        
        # Pixel Difference Threshold
        row += 1
        ttk.Label(main_frame, text="Pixel Diff Threshold (%):").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.pixel_diff_threshold_var = tk.StringVar(value="0.01")
        ttk.Entry(main_frame, textvariable=self.pixel_diff_threshold_var, width=50).grid(
            row=row, column=1, sticky=(tk.W, tk.E), padx=5
        )
        
        # Pixel Change Threshold
        row += 1
        ttk.Label(main_frame, text="Min Pixel Change:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.pixel_change_threshold_var = tk.StringVar(value="1")
        ttk.Entry(main_frame, textvariable=self.pixel_change_threshold_var, width=50).grid(
            row=row, column=1, sticky=(tk.W, tk.E), padx=5
        )
        
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
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=15
        )
        
        row += 1
        ttk.Label(
            main_frame, 
            text="Visual Settings",
            font=('Arial', 12, 'bold')
        ).grid(row=row, column=0, columnspan=3, sticky=tk.W)
        
        # Histogram Equalization
        row += 1
        self.use_histogram_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            main_frame,
            text="Use Histogram Equalization (normalize tonal variations)",
            variable=self.use_histogram_var
        ).grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        # Highlight Color
        row += 1
        ttk.Label(main_frame, text="Highlight Color (R,G,B):").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.highlight_color_var = tk.StringVar(value="255,0,0")
        color_frame = ttk.Frame(main_frame)
        color_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Entry(color_frame, textvariable=self.highlight_color_var, width=20).pack(side=tk.LEFT)
        self.color_preview = tk.Canvas(color_frame, width=30, height=20, bg='red', relief=tk.SUNKEN)
        self.color_preview.pack(side=tk.LEFT, padx=5)
        self.highlight_color_var.trace('w', self._update_color_preview)
        
        # Diff Enhancement Factor
        row += 1
        ttk.Label(main_frame, text="Diff Enhancement Factor:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.diff_enhancement_var = tk.StringVar(value="5.0")
        ttk.Entry(main_frame, textvariable=self.diff_enhancement_var, width=50).grid(
            row=row, column=1, sticky=(tk.W, tk.E), padx=5
        )
        
        # Info text
        row += 1
        info_text = (
            "Note: New Images and Known Good directories should contain "
            "matching image filenames.\nDiff and HTML directories will be "
            "created automatically."
        )
        info_label = ttk.Label(
            main_frame, 
            text=info_text,
            foreground="gray",
            wraplength=600
        )
        info_label.grid(
            row=row, column=0, columnspan=3, pady=(20, 10), sticky=tk.W
        )
        
        # Buttons
        row += 1
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=3, pady=(20, 0))
        
        ttk.Button(
            button_frame, 
            text="Start Comparison", 
            command=self._on_start,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, 
            text="Cancel", 
            command=self._on_cancel,
            width=20
        ).pack(side=tk.LEFT, padx=5)
    
    def _update_color_preview(self, *args):
        """Update the color preview box."""
        try:
            color_str = self.highlight_color_var.get()
            parts = [int(x.strip()) for x in color_str.split(',')]
            if len(parts) == 3 and all(0 <= p <= 255 for p in parts):
                hex_color = f'#{parts[0]:02x}{parts[1]:02x}{parts[2]:02x}'
                self.color_preview.configure(bg=hex_color)
        except:
            pass
    
    def _browse_base_dir(self):
        """Open directory browser for base directory."""
        directory = filedialog.askdirectory(title="Select Base Directory")
        if directory:
            self.base_dir_var.set(directory)
    
    def _on_start(self):
        """Validate inputs and create config."""
        try:
            # Validate inputs
            if not self.base_dir_var.get():
                messagebox.showerror("Error", "Please select a base directory")
                return
            
            if not self.new_dir_var.get():
                messagebox.showerror("Error", "Please specify new images directory")
                return
            
            if not self.known_good_var.get():
                messagebox.showerror(
                    "Error", 
                    "Please specify known good directory"
                )
                return
            
            # Create config
            pixel_diff_threshold = float(self.pixel_diff_threshold_var.get())
            pixel_change_threshold = int(self.pixel_change_threshold_var.get())
            ssim_threshold = float(self.ssim_threshold_var.get())
            color_distance = float(self.color_distance_var.get())
            min_contour = int(self.min_contour_var.get())
            diff_enhancement = float(self.diff_enhancement_var.get())
            
            # Parse highlight color
            color_parts = [int(x.strip()) for x in self.highlight_color_var.get().split(',')]
            if len(color_parts) != 3 or not all(0 <= p <= 255 for p in color_parts):
                raise ValueError("Invalid color format")
            highlight_color = tuple(color_parts)
            
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
                diff_enhancement_factor=diff_enhancement
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
