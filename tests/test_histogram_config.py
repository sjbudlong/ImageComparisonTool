"""
Unit tests for HistogramConfig dataclass.
"""

import pytest
import logging
from config import HistogramConfig

logger = logging.getLogger(__name__)


@pytest.mark.unit
class TestHistogramConfig:
    """Test HistogramConfig dataclass."""

    def test_histogram_config_defaults(self):
        """HistogramConfig should have sensible defaults."""
        logger.debug("Testing HistogramConfig default values")
        config = HistogramConfig()

        assert config.bins == 256
        assert config.figure_width == 16
        assert config.figure_height == 6
        assert config.dpi == 100
        assert config.grayscale_alpha == 0.7
        assert config.rgb_alpha == 0.7
        assert config.grayscale_linewidth == 2.0
        assert config.rgb_linewidth == 1.5
        assert config.grid_alpha == 0.3
        assert config.show_grayscale is True
        assert config.show_rgb is True
        assert config.grayscale_color == "black"
        assert config.rgb_colors == ("red", "green", "blue")
        assert "Histogram Comparison" in config.title

        logger.info("✓ HistogramConfig default values test passed")

    def test_histogram_config_custom_bins(self):
        """HistogramConfig should accept custom bin values."""
        logger.debug("Testing HistogramConfig custom bins")

        test_cases = [64, 128, 256, 384, 512]
        for bins in test_cases:
            config = HistogramConfig(bins=bins)
            assert config.bins == bins

        logger.info("✓ HistogramConfig custom bins test passed")

    def test_histogram_config_custom_figure_size(self):
        """HistogramConfig should accept custom figure dimensions."""
        logger.debug("Testing HistogramConfig custom figure size")
        config = HistogramConfig(figure_width=20, figure_height=8, dpi=150)

        assert config.figure_width == 20
        assert config.figure_height == 8
        assert config.dpi == 150

        logger.info("✓ HistogramConfig custom figure size test passed")

    def test_histogram_config_custom_alpha_values(self):
        """HistogramConfig should accept custom alpha (transparency) values."""
        logger.debug("Testing HistogramConfig custom alpha values")
        config = HistogramConfig(grayscale_alpha=0.9, rgb_alpha=0.85, grid_alpha=0.1)

        assert config.grayscale_alpha == 0.9
        assert config.rgb_alpha == 0.85
        assert config.grid_alpha == 0.1

        logger.info("✓ HistogramConfig custom alpha values test passed")

    def test_histogram_config_custom_linewidth(self):
        """HistogramConfig should accept custom line width values."""
        logger.debug("Testing HistogramConfig custom linewidth")
        config = HistogramConfig(grayscale_linewidth=2.5, rgb_linewidth=2.0)

        assert config.grayscale_linewidth == 2.5
        assert config.rgb_linewidth == 2.0

        logger.info("✓ HistogramConfig custom linewidth test passed")

    def test_histogram_config_custom_colors(self):
        """HistogramConfig should accept custom color values."""
        logger.debug("Testing HistogramConfig custom colors")
        config = HistogramConfig(
            grayscale_color="#333333", rgb_colors=("#FF6B6B", "#4ECDC4", "#45B7D1")
        )

        assert config.grayscale_color == "#333333"
        assert config.rgb_colors == ("#FF6B6B", "#4ECDC4", "#45B7D1")

        logger.info("✓ HistogramConfig custom colors test passed")

    def test_histogram_config_custom_title(self):
        """HistogramConfig should accept custom title."""
        logger.debug("Testing HistogramConfig custom title")
        custom_title = "My Custom Histogram"
        config = HistogramConfig(title=custom_title)

        assert config.title == custom_title

        logger.info("✓ HistogramConfig custom title test passed")

    def test_histogram_config_show_grayscale_only(self):
        """HistogramConfig should support showing only grayscale histogram."""
        logger.debug("Testing HistogramConfig show grayscale only")
        config = HistogramConfig(show_grayscale=True, show_rgb=False)

        assert config.show_grayscale is True
        assert config.show_rgb is False

        logger.info("✓ HistogramConfig show grayscale only test passed")

    def test_histogram_config_show_rgb_only(self):
        """HistogramConfig should support showing only RGB histograms."""
        logger.debug("Testing HistogramConfig show RGB only")
        config = HistogramConfig(show_grayscale=False, show_rgb=True)

        assert config.show_grayscale is False
        assert config.show_rgb is True

        logger.info("✓ HistogramConfig show RGB only test passed")

    def test_histogram_config_both_hidden(self):
        """HistogramConfig should allow both histograms to be hidden."""
        logger.debug("Testing HistogramConfig both histograms hidden")
        config = HistogramConfig(show_grayscale=False, show_rgb=False)

        assert config.show_grayscale is False
        assert config.show_rgb is False

        logger.info("✓ HistogramConfig both hidden test passed")

    def test_histogram_config_comprehensive_custom(self):
        """HistogramConfig should accept comprehensive custom configuration."""
        logger.debug("Testing HistogramConfig comprehensive custom setup")
        config = HistogramConfig(
            bins=512,
            figure_width=18,
            figure_height=7,
            dpi=120,
            grayscale_alpha=0.9,
            rgb_alpha=0.85,
            grayscale_linewidth=2.5,
            rgb_linewidth=2.0,
            grid_alpha=0.2,
            title="Advanced Histogram",
            grayscale_color="darkgray",
            rgb_colors=("red", "green", "blue"),
            show_grayscale=True,
            show_rgb=True,
        )

        assert config.bins == 512
        assert config.figure_width == 18
        assert config.figure_height == 7
        assert config.dpi == 120
        assert config.grayscale_alpha == 0.9
        assert config.rgb_alpha == 0.85
        assert config.grayscale_linewidth == 2.5
        assert config.rgb_linewidth == 2.0
        assert config.grid_alpha == 0.2
        assert config.title == "Advanced Histogram"
        assert config.grayscale_color == "darkgray"
        assert config.rgb_colors == ("red", "green", "blue")
        assert config.show_grayscale is True
        assert config.show_rgb is True

        logger.info("✓ HistogramConfig comprehensive custom test passed")

    def test_histogram_config_immutable_rgb_colors_tuple(self):
        """HistogramConfig should store rgb_colors as tuple (immutable)."""
        logger.debug("Testing HistogramConfig rgb_colors immutability")
        config = HistogramConfig()

        assert isinstance(config.rgb_colors, tuple)
        assert len(config.rgb_colors) == 3

        logger.info("✓ HistogramConfig rgb_colors tuple test passed")

    def test_histogram_config_realistic_scenarios(self):
        """HistogramConfig should support realistic usage scenarios."""
        logger.debug("Testing HistogramConfig realistic scenarios")

        # Scenario 1: Smooth overview (publication)
        overview = HistogramConfig(
            bins=64,
            figure_width=14,
            figure_height=5,
            grayscale_alpha=0.8,
            rgb_alpha=0.8,
        )
        assert overview.bins == 64
        assert overview.figure_width == 14

        # Scenario 2: Detailed analysis
        detailed = HistogramConfig(
            bins=512,
            figure_width=20,
            figure_height=8,
            grayscale_alpha=0.95,
            rgb_alpha=0.9,
        )
        assert detailed.bins == 512
        assert detailed.figure_width == 20

        # Scenario 3: Minimal (grayscale only)
        minimal = HistogramConfig(
            bins=128,
            figure_width=12,
            figure_height=4,
            show_grayscale=True,
            show_rgb=False,
        )
        assert minimal.show_grayscale is True
        assert minimal.show_rgb is False

        # Scenario 4: Presentation (large, high quality)
        presentation = HistogramConfig(
            bins=256,
            figure_width=20,
            figure_height=8,
            dpi=150,
            grayscale_linewidth=3.0,
            rgb_linewidth=2.5,
        )
        assert presentation.dpi == 150
        assert presentation.grayscale_linewidth == 3.0

        logger.info("✓ HistogramConfig realistic scenarios test passed")
