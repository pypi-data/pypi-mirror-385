#!/usr/bin/env python
"""Command-line interface for the Meridian Crossing application."""

import json
from pathlib import Path
from typing import Literal

import click
import geopandas as gpd

from meridian_crossing import utils


def parse_json_to_dict(ctx, param, value: str | None) -> dict | None:  # noqa: ANN001
    _ = ctx  # unused
    if value is None:
        return None

    try:
        return json.loads(value)
    except json.JSONDecodeError as e:
        msg = f'{param} has Invalid JSON: {e}'
        raise click.BadParameter(msg) from e


@click.command()
@click.option(
    '--data',
    'data_path',
    type=click.Path(exists=True, path_type=Path),
    help='Path to input geospatial data file.',
    required=True,
)
@click.option(
    '--geom-col',
    type=str,
    help='Name of the geometry column in the data.',
    default='geometry',
    show_default=True,
)
@click.option(
    '--direction',
    type=click.Choice(['east', 'west', 'centroid'], case_sensitive=False),
    help='Direction to unwrap geometries.',
    default='east',
    show_default=True,
)
@click.option(
    '--gap-threshold',
    type=float,
    help='Minimum gap size to trigger unwrapping (in degrees).',
    default=180.0,
    show_default=True,
)
@click.option(
    '--output',
    'output_path',
    type=click.Path(path_type=Path),
    help='Path to output geospatial data file.',
    required=True,
)
@click.option(
    '--mode',
    type=click.Choice(['w', 'a'], case_sensitive=True),
    help=(
        "The write mode, 'w' to overwrite the existing file and 'a' to "
        'append. Not all drivers support appending. The drivers that support '
        'appending are listed in fiona.supported_drivers or Toblerity/Fiona'
    ),
    default='w',
    show_default=True,
)
@click.option(
    '--crs',
    type=str,
    help=(
        'If specified, the CRS is passed to Fiona to better control how the '
        'file is written. If None, GeoPandas will determine the crs based on '
        'crs df attribute. The value can be anything accepted by '
        'pyproj.CRS.from_user_input(), such as an authority string '
        '(eg "EPSG:4326") or a WKT string. The keyword is not supported for '
        'the "pyogrio" engine.'
    ),
    default=None,
    show_default=True,
)
@click.option(
    '--engine',
    type=click.Choice(['fiona', 'pyogrio'], case_sensitive=False),
    help=(
        'The underlying library that is used to write the file. Currently, '
        'the supported options are "pyogrio" and "fiona". Defaults to '
        '"pyogrio" if installed, otherwise tries "fiona".'
    ),
    default=None,
    show_default=True,
)
@click.option(
    '--metadata',
    type=str,
    help=(
        'A JSON string representing a dictionary of metadata to be '
        'written to the file. Keys and values must be strings. '
        'Supported only for "GPKG" driver.'
    ),
    default=None,
    show_default=True,
    callback=parse_json_to_dict,
)
@click.option(
    '--kwargs',
    'extra_kwargs',
    type=str,
    help=(
        'Additional keyword arguments to be passed to the '
        'GeoDataFrame.to_file() method as a JSON string.'
    ),
    default=None,
    show_default=True,
    callback=parse_json_to_dict,
)
@click.version_option()
@click.help_option('-h', '--help')
def main(  # noqa: PLR0913
    data_path: Path,
    geom_col: str,
    direction: Literal['east', 'west', 'centroid'],
    gap_threshold: float,
    output_path: Path,
    mode: Literal['w', 'a'],
    crs: str | None = None,
    engine: Literal['fiona', 'pyogrio'] | None = None,
    metadata: dict | None = None,
    extra_kwargs: dict | None = None,
) -> None:
    """Meridian Crossing CLI."""
    gdf = gpd.read_file(filename=data_path)

    # Build kwargs for to_file
    to_file_kwargs = {
        'filename': output_path,
        'mode': mode,
    }
    if crs is not None:
        to_file_kwargs['crs'] = crs
    if engine is not None:
        to_file_kwargs['engine'] = engine
    if metadata is not None:
        to_file_kwargs['metadata'] = metadata
    if extra_kwargs is not None:
        to_file_kwargs.update(extra_kwargs)

    utils.unwrap_longitude(
        data=gdf,
        geom_col=geom_col,
        direction=direction,
        gap_threshold=gap_threshold,
    ).to_file(**to_file_kwargs)


if __name__ == '__main__':
    main()
