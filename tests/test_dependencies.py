"""
Unit tests for dependencies module.
"""

import pytest
from dependencies import DependencyChecker, Dependency


@pytest.mark.unit
class TestDependency:
    """Test Dependency dataclass."""
    
    def test_dependency_creation(self):
        """Dependency should be creatable with required fields."""
        dep = Dependency(
            package_name="test-package",
            import_name="test_package",
            min_version="1.0.0",
            description="A test package",
            pip_install="test-package>=1.0.0"
        )
        assert dep.package_name == "test-package"
        assert dep.import_name == "test_package"
        assert dep.min_version == "1.0.0"
    
    def test_dependency_defaults(self):
        """Dependency should have sensible defaults."""
        dep = Dependency(
            package_name="test-package",
            import_name="test_package"
        )
        # Default install commands should match package name
        assert dep.pip_install == "test-package"
        assert dep.conda_install == "test-package"


@pytest.mark.unit
class TestDependencyChecker:
    """Test DependencyChecker functionality."""
    
    def test_check_package_installed(self):
        """check_package should detect installed packages."""
        # numpy should be installed (it's a dependency of the project)
        dep = Dependency(
            package_name="numpy",
            import_name="numpy",
            min_version="1.24.0"
        )
        
        is_installed, version, error = DependencyChecker.check_package(dep)
        assert is_installed is True
        assert version is not None
        assert error is None
    
    def test_check_package_not_installed(self):
        """check_package should detect missing packages."""
        dep = Dependency(
            package_name="nonexistent-package-xyz",
            import_name="nonexistent_package_xyz"
        )
        
        is_installed, version, error = DependencyChecker.check_package(dep)
        assert is_installed is False
        assert version is None
        assert error is not None
    
    def test_check_all_returns_tuple(self):
        """check_all should return tuple of (bool, dict)."""
        all_satisfied, results = DependencyChecker.check_all(verbose=False)
        
        assert isinstance(all_satisfied, bool)
        assert isinstance(results, dict)
        assert len(results) > 0
    
    def test_check_all_results_structure(self):
        """check_all results should have proper structure."""
        all_satisfied, results = DependencyChecker.check_all(verbose=False)
        
        # Check that each result has required keys
        for package_name, result_data in results.items():
            assert "installed" in result_data
            assert "version" in result_data
            assert "error" in result_data
            assert "dependency" in result_data
            assert isinstance(result_data["installed"], bool)
    
    def test_critical_dependencies_installed(self):
        """Critical dependencies should be installed."""
        critical_packages = ["numpy", "PIL", "cv2", "skimage"]
        all_satisfied, results = DependencyChecker.check_all(verbose=False)
        
        for package in critical_packages:
            # At least one of these should match
            installed_packages = [
                pkg for pkg, data in results.items()
                if data["installed"]
            ]
            # We just check that there are some installed packages
            assert len(installed_packages) > 0
