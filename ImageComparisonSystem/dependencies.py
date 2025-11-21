"""
Dependency checker for Image Comparison Tool.
Validates all required packages are installed before running.
"""

import sys
import importlib.util
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Dependency:
    """Represents a package dependency."""
    package_name: str
    import_name: str
    min_version: Optional[str] = None
    description: str = ""
    pip_install: str = ""
    conda_install: str = ""
    
    def __post_init__(self):
        if not self.pip_install:
            self.pip_install = self.package_name
        if not self.conda_install:
            self.conda_install = self.package_name


class DependencyChecker:
    """Checks for required Python package dependencies."""
    
    # Define all dependencies
    DEPENDENCIES = [
        Dependency(
            package_name="Pillow",
            import_name="PIL",
            min_version="10.0.0",
            description="Image loading and manipulation",
            pip_install="Pillow>=10.0.0"
        ),
        Dependency(
            package_name="numpy",
            import_name="numpy",
            min_version="1.24.0",
            description="Array operations and numerical computing",
            pip_install="numpy>=1.24.0"
        ),
        Dependency(
            package_name="opencv-python",
            import_name="cv2",
            min_version="4.8.0",
            description="Computer vision and image processing",
            pip_install="opencv-python>=4.8.0"
        ),
        Dependency(
            package_name="scikit-image",
            import_name="skimage",
            min_version="0.21.0",
            description="Image analysis and SSIM calculation",
            pip_install="scikit-image>=0.21.0"
        ),
        Dependency(
            package_name="matplotlib",
            import_name="matplotlib",
            min_version="3.7.0",
            description="Histogram visualization",
            pip_install="matplotlib>=3.7.0"
        ),
        Dependency(
            package_name="tkinter",
            import_name="tkinter",
            description="GUI interface (usually included with Python)",
            pip_install="python3-tk (system package manager)",
            conda_install="tk"
        )
    ]
    
    @staticmethod
    def check_package(dep: Dependency) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Check if a package is installed and get its version.
        
        Args:
            dep: Dependency to check
            
        Returns:
            Tuple of (is_installed, version, error_message)
        """
        try:
            # Check if package can be imported
            spec = importlib.util.find_spec(dep.import_name)
            if spec is None:
                return False, None, f"{dep.package_name} is not installed"
            
            # Import and get version
            module = importlib.import_module(dep.import_name)
            
            # Try different ways to get version
            version = None
            for version_attr in ['__version__', 'VERSION', 'version']:
                if hasattr(module, version_attr):
                    version = getattr(module, version_attr)
                    if isinstance(version, tuple):
                        version = '.'.join(map(str, version))
                    elif not isinstance(version, str):
                        version = str(version)
                    break
            
            return True, version, None
            
        except ImportError as e:
            return False, None, str(e)
        except Exception as e:
            return False, None, f"Error checking {dep.package_name}: {str(e)}"
    
    @classmethod
    def check_all(cls, verbose: bool = True) -> Tuple[bool, Dict[str, dict]]:
        """
        Check all dependencies.
        
        Args:
            verbose: Whether to print detailed information
            
        Returns:
            Tuple of (all_satisfied, results_dict)
        """
        results = {}
        all_satisfied = True
        
        if verbose:
            print("=" * 70)
            print("DEPENDENCY CHECK")
            print("=" * 70)
            print()
        
        for dep in cls.DEPENDENCIES:
            is_installed, version, error = cls.check_package(dep)
            
            results[dep.package_name] = {
                'installed': is_installed,
                'version': version,
                'error': error,
                'dependency': dep
            }
            
            if not is_installed:
                all_satisfied = False
            
            if verbose:
                status = "✓" if is_installed else "✗"
                print(f"[{status}] {dep.package_name:20s}", end="")
                
                if is_installed:
                    version_str = f"v{version}" if version else "version unknown"
                    print(f" {version_str:15s} - {dep.description}")
                else:
                    print(f" MISSING - {dep.description}")
        
        if verbose:
            print()
            print("=" * 70)
            
            if all_satisfied:
                print("✓ All dependencies are installed!")
            else:
                print("✗ Some dependencies are missing. See installation instructions below.")
            
            print("=" * 70)
        
        return all_satisfied, results
    
    @classmethod
    def generate_install_instructions(cls, results: Dict[str, dict]) -> str:
        """
        Generate installation instructions for missing packages.
        
        Args:
            results: Results from check_all()
            
        Returns:
            Installation instructions as string
        """
        missing = [
            results[pkg]['dependency'] 
            for pkg in results 
            if not results[pkg]['installed']
        ]
        
        if not missing:
            return "All dependencies are installed!"
        
        instructions = []
        instructions.append("\n" + "=" * 70)
        instructions.append("INSTALLATION INSTRUCTIONS")
        instructions.append("=" * 70)
        instructions.append("\nMissing packages need to be installed:\n")
        
        # Pip instructions
        instructions.append("Using pip:")
        instructions.append("-" * 70)
        pip_packages = [dep.pip_install for dep in missing]
        instructions.append("pip install " + " ".join(pip_packages))
        instructions.append("")
        
        # Conda instructions
        instructions.append("OR using conda:")
        instructions.append("-" * 70)
        conda_packages = [dep.conda_install for dep in missing]
        instructions.append("conda install " + " ".join(conda_packages))
        instructions.append("")
        
        # Offline installation
        instructions.append("For OFFLINE installation:")
        instructions.append("-" * 70)
        instructions.append("1. On a machine with internet, download wheels:")
        instructions.append("   pip download " + " ".join([d.pip_install for d in missing]) + " -d packages/")
        instructions.append("")
        instructions.append("2. Transfer the 'packages/' directory to offline machine")
        instructions.append("")
        instructions.append("3. On offline machine, install from downloaded wheels:")
        instructions.append("   pip install --no-index --find-links=packages/ " + " ".join([d.package_name for d in missing]))
        instructions.append("")
        
        # Special notes
        if any(dep.package_name == "tkinter" for dep in missing):
            instructions.append("NOTE: tkinter requires system-level installation:")
            instructions.append("-" * 70)
            instructions.append("  Ubuntu/Debian: sudo apt-get install python3-tk")
            instructions.append("  Fedora/RHEL:   sudo dnf install python3-tkinter")
            instructions.append("  macOS:         Usually included with Python")
            instructions.append("  Windows:       Usually included with Python")
            instructions.append("")
        
        instructions.append("=" * 70)
        
        return "\n".join(instructions)
    
    @classmethod
    def check_and_exit_if_missing(cls, skip_tkinter: bool = False):
        """
        Check dependencies and exit with error if any are missing.
        
        Args:
            skip_tkinter: Whether to skip tkinter check (for CLI-only usage)
        """
        # Filter out tkinter if skip requested
        original_deps = cls.DEPENDENCIES
        if skip_tkinter:
            cls.DEPENDENCIES = [d for d in cls.DEPENDENCIES if d.package_name != "tkinter"]
        
        all_satisfied, results = cls.check_all(verbose=True)
        
        if not all_satisfied:
            print(cls.generate_install_instructions(results))
            sys.exit(1)
        
        # Restore original dependencies
        cls.DEPENDENCIES = original_deps
    
    @classmethod
    def save_requirements_freeze(cls, output_file: str = "requirements-freeze.txt"):
        """
        Save exact versions of all installed dependencies.
        Useful for creating reproducible environments.
        
        Args:
            output_file: Path to output file
        """
        all_satisfied, results = cls.check_all(verbose=False)
        
        lines = ["# Exact dependencies for Image Comparison Tool"]
        lines.append("# Generated by dependency checker")
        lines.append("")
        
        for dep in cls.DEPENDENCIES:
            if dep.package_name in results and results[dep.package_name]['installed']:
                version = results[dep.package_name]['version']
                if version and dep.package_name != "tkinter":
                    lines.append(f"{dep.package_name}=={version}")
                elif dep.package_name != "tkinter":
                    lines.append(f"{dep.package_name}  # version unknown")
        
        try:
            with open(output_file, 'w') as f:
                f.write('\n'.join(lines))
            print(f"\n✓ Requirements saved to: {output_file}")
            print("  Use 'pip install -r requirements-freeze.txt' to install exact versions")
        except Exception as e:
            print(f"\n✗ Error saving requirements: {e}")


def main():
    """Run dependency check as standalone script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Check dependencies for Image Comparison Tool"
    )
    parser.add_argument(
        '--save-freeze',
        action='store_true',
        help='Save exact versions to requirements-freeze.txt'
    )
    parser.add_argument(
        '--skip-tkinter',
        action='store_true',
        help='Skip tkinter check (for CLI-only usage)'
    )
    
    args = parser.parse_args()
    
    if args.save_freeze:
        all_satisfied, _ = DependencyChecker.check_all(verbose=True)
        if all_satisfied:
            DependencyChecker.save_requirements_freeze()
    else:
        DependencyChecker.check_and_exit_if_missing(skip_tkinter=args.skip_tkinter)


if __name__ == '__main__':
    exit_code = main()
    
    # Keep console window open on Windows
    if sys.platform == 'win32':
        input("\nPress Enter to close this window...")
    
    sys.exit(exit_code)
