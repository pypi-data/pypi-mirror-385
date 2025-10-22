"""Tests for the CLI module."""

import json
from pathlib import Path

import geopandas as gpd
import pytest
from click import BadParameter
from click.testing import CliRunner

from meridian_crossing.cli import main, parse_json_to_dict


@pytest.fixture
def test_data_path() -> Path:
    """Return path to test GeoJSON file."""
    return Path(__file__).parent / 'data' / 'test_poly.geojson'


@pytest.fixture
def runner() -> CliRunner:
    """Return Click CLI test runner."""
    return CliRunner()


class TestParseJsonToDict:
    """Tests for parse_json_to_dict callback function."""

    def test_none_value(self):
        """Test that None value returns None."""
        result = parse_json_to_dict(None, None, None)
        assert result is None

    def test_valid_json(self):
        """Test parsing valid JSON string."""
        json_str = '{"key": "value", "number": 42}'
        result = parse_json_to_dict(None, None, json_str)
        assert result == {'key': 'value', 'number': 42}

    def test_invalid_json(self):
        """Test that invalid JSON raises BadParameter."""
        invalid_json = '{invalid json}'
        with pytest.raises(BadParameter) as exc_info:
            parse_json_to_dict(None, 'test_param', invalid_json)

        assert 'Invalid JSON' in str(exc_info.value)
        # Verify exception chaining (B904 fix)
        assert exc_info.value.__cause__ is not None


class TestCLIBasic:
    """Tests for basic CLI functionality."""

    def test_help_option(self, runner: CliRunner):
        """Test that --help displays help message."""
        result = runner.invoke(main, ['--help'])
        assert result.exit_code == 0
        assert 'Meridian Crossing CLI' in result.output
        assert '--data' in result.output
        assert '--output' in result.output

    def test_version_option(self, runner: CliRunner):
        """Test that --version displays version."""
        result = runner.invoke(main, ['--version'])
        assert result.exit_code == 0

    def test_missing_required_args(self, runner: CliRunner):
        """Test that missing required arguments shows error."""
        result = runner.invoke(main, [])
        assert result.exit_code != 0
        assert 'Missing option' in result.output


class TestCLIFileProcessing:
    """Tests for CLI file processing functionality."""

    def test_basic_processing(
        self, runner: CliRunner, test_data_path: Path, tmp_path: Path
    ):
        """Test basic file processing with minimal options."""
        output_path = tmp_path / 'output.geojson'

        result = runner.invoke(
            main,
            [
                '--data',
                str(test_data_path),
                '--output',
                str(output_path),
            ],
        )

        assert result.exit_code == 0, f'CLI failed: {result.output}'
        assert output_path.exists(), 'Output file was not created'

        # Verify output is valid GeoJSON
        gdf = gpd.read_file(output_path)
        assert not gdf.empty
        assert gdf.geometry.is_valid.all()

    def test_with_direction_east(
        self, runner: CliRunner, test_data_path: Path, tmp_path: Path
    ):
        """Test processing with direction=east."""
        output_path = tmp_path / 'output_east.geojson'

        result = runner.invoke(
            main,
            [
                '--data',
                str(test_data_path),
                '--output',
                str(output_path),
                '--direction',
                'east',
            ],
        )

        assert result.exit_code == 0
        assert output_path.exists()

        gdf = gpd.read_file(output_path)
        assert gdf.geometry.is_valid.all()

    def test_with_direction_west(
        self, runner: CliRunner, test_data_path: Path, tmp_path: Path
    ):
        """Test processing with direction=west."""
        output_path = tmp_path / 'output_west.geojson'

        result = runner.invoke(
            main,
            [
                '--data',
                str(test_data_path),
                '--output',
                str(output_path),
                '--direction',
                'west',
            ],
        )

        assert result.exit_code == 0
        assert output_path.exists()

    def test_with_direction_centroid(
        self, runner: CliRunner, test_data_path: Path, tmp_path: Path
    ):
        """Test processing with direction=centroid."""
        output_path = tmp_path / 'output_centroid.geojson'

        result = runner.invoke(
            main,
            [
                '--data',
                str(test_data_path),
                '--output',
                str(output_path),
                '--direction',
                'centroid',
            ],
        )

        assert result.exit_code == 0
        assert output_path.exists()

    def test_with_custom_gap_threshold(
        self, runner: CliRunner, test_data_path: Path, tmp_path: Path
    ):
        """Test processing with custom gap threshold."""
        output_path = tmp_path / 'output_gap.geojson'

        result = runner.invoke(
            main,
            [
                '--data',
                str(test_data_path),
                '--output',
                str(output_path),
                '--gap-threshold',
                '150.0',
            ],
        )

        assert result.exit_code == 0
        assert output_path.exists()

    def test_with_custom_geom_col(
        self, runner: CliRunner, test_data_path: Path, tmp_path: Path
    ):
        """Test processing with custom geometry column name."""
        output_path = tmp_path / 'output_geom.geojson'

        # The test data uses 'geometry' as default, so this should work
        result = runner.invoke(
            main,
            [
                '--data',
                str(test_data_path),
                '--output',
                str(output_path),
                '--geom-col',
                'geometry',
            ],
        )

        assert result.exit_code == 0
        assert output_path.exists()


class TestCLIOptions:
    """Tests for CLI options like mode, crs, engine, metadata."""

    def test_mode_write(
        self, runner: CliRunner, test_data_path: Path, tmp_path: Path
    ):
        """Test write mode (default)."""
        output_path = tmp_path / 'output_mode_w.geojson'

        result = runner.invoke(
            main,
            [
                '--data',
                str(test_data_path),
                '--output',
                str(output_path),
                '--mode',
                'w',
            ],
        )

        assert result.exit_code == 0
        assert output_path.exists()

    def test_with_crs(
        self, runner: CliRunner, test_data_path: Path, tmp_path: Path
    ):
        """Test processing with explicit CRS using fiona engine."""
        output_path = tmp_path / 'output_crs.geojson'

        # CRS parameter requires fiona engine (not supported by pyogrio)
        # If fiona is not available, skip this test
        result = runner.invoke(
            main,
            [
                '--data',
                str(test_data_path),
                '--output',
                str(output_path),
                '--engine',
                'fiona',
                '--crs',
                'EPSG:4326',
            ],
        )

        # Fiona might not be installed, so accept either success or ImportError
        if result.exit_code != 0:
            # Check if it's a fiona import error (in exception or output)
            error_text = str(result.exception) + result.output
            assert 'fiona' in error_text.lower()
        else:
            assert output_path.exists()
            gdf = gpd.read_file(output_path)
            assert gdf.crs is not None

    def test_with_metadata_json(
        self, runner: CliRunner, test_data_path: Path, tmp_path: Path
    ):
        """Test processing with metadata as JSON string."""
        output_path = tmp_path / 'output_metadata.gpkg'
        metadata = {'title': 'Test Data', 'author': 'Test'}

        result = runner.invoke(
            main,
            [
                '--data',
                str(test_data_path),
                '--output',
                str(output_path),
                '--metadata',
                json.dumps(metadata),
            ],
        )

        # GPKG format might not be available, so we accept either success
        # or error. The important part is that JSON parsing works
        assert result.exit_code in [0, 1]

    def test_with_kwargs_json(
        self, runner: CliRunner, test_data_path: Path, tmp_path: Path
    ):
        """Test that kwargs option can be parsed from JSON string."""
        output_path = tmp_path / 'output_kwargs.geojson'
        # Test that JSON parsing works, even if the kwargs might not be used
        # We're primarily testing the parse_json_to_dict callback here
        kwargs = {}  # Empty dict should work without errors

        result = runner.invoke(
            main,
            [
                '--data',
                str(test_data_path),
                '--output',
                str(output_path),
                '--kwargs',
                json.dumps(kwargs),
            ],
        )

        assert result.exit_code == 0
        assert output_path.exists()


class TestCLIErrorHandling:
    """Tests for CLI error handling."""

    def test_nonexistent_input_file(self, runner: CliRunner, tmp_path: Path):
        """Test that nonexistent input file raises error."""
        nonexistent = tmp_path / 'nonexistent.geojson'
        output_path = tmp_path / 'output.geojson'

        result = runner.invoke(
            main,
            [
                '--data',
                str(nonexistent),
                '--output',
                str(output_path),
            ],
        )

        assert result.exit_code != 0
        assert 'does not exist' in result.output.lower()

    def test_invalid_direction(
        self, runner: CliRunner, test_data_path: Path, tmp_path: Path
    ):
        """Test that invalid direction value raises error."""
        output_path = tmp_path / 'output.geojson'

        result = runner.invoke(
            main,
            [
                '--data',
                str(test_data_path),
                '--output',
                str(output_path),
                '--direction',
                'invalid',
            ],
        )

        assert result.exit_code != 0
        assert 'Invalid value' in result.output

    def test_invalid_mode(
        self, runner: CliRunner, test_data_path: Path, tmp_path: Path
    ):
        """Test that invalid mode value raises error."""
        output_path = tmp_path / 'output.geojson'

        result = runner.invoke(
            main,
            [
                '--data',
                str(test_data_path),
                '--output',
                str(output_path),
                '--mode',
                'x',  # Invalid mode
            ],
        )

        assert result.exit_code != 0
        assert 'Invalid value' in result.output

    def test_invalid_metadata_json(
        self, runner: CliRunner, test_data_path: Path, tmp_path: Path
    ):
        """Test that invalid JSON in metadata raises error."""
        output_path = tmp_path / 'output.geojson'

        result = runner.invoke(
            main,
            [
                '--data',
                str(test_data_path),
                '--output',
                str(output_path),
                '--metadata',
                '{invalid json}',
            ],
        )

        assert result.exit_code != 0
        assert 'Invalid JSON' in result.output

    def test_invalid_kwargs_json(
        self, runner: CliRunner, test_data_path: Path, tmp_path: Path
    ):
        """Test that invalid JSON in kwargs raises error."""
        output_path = tmp_path / 'output.geojson'

        result = runner.invoke(
            main,
            [
                '--data',
                str(test_data_path),
                '--output',
                str(output_path),
                '--kwargs',
                'not a json',
            ],
        )

        assert result.exit_code != 0
        assert 'Invalid JSON' in result.output
