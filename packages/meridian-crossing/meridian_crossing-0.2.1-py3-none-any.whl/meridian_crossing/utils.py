"""Utilities for handling geometries crossing the antimeridian."""

from typing import Literal, TypeVar

from geopandas import GeoDataFrame
from shapely import MultiPolygon, Polygon, affinity

T = TypeVar('T', Polygon, MultiPolygon)


def _find_geometries_gap(
    *,
    geoms: list[Polygon],
    coord_limits: tuple[float, float] = (-180, 180),
    cyclic_coords: bool = True,
) -> tuple[float, float] | None:
    """Find longest gap in x-coordinates to divide geometries.

    Parameters
    ----------
    geoms : list[Polygon]
        List of shapely Polygons.
    coord_limits : tuple(float, float), optional
        The x-range to consider for dividing line. Default is (-180, 180).
    cyclic_coords : bool, optional
        Whether the x-coordinates are cyclic (e.g., longitude). Default is
        True. If True, the function will consider the wrap-around interval
        between x_range[1] and x_range[0].

    Returns
    -------
    tuple[float, float]
        The range (min, max) of the gap that best divides the polygons.

    """
    if not geoms:
        return coord_limits
    # Collect x-coordinate ranges from all geometries
    geom_bounds = [geom.bounds for geom in geoms]
    ranges = [(minx, maxx) for minx, _, maxx, _ in geom_bounds]

    # Sort ranges by start point
    ranges.sort(key=lambda r: r[0])

    gaps: list[tuple[float, float]] = []
    current_end = coord_limits[0]
    for start, end in ranges:
        if start > current_end:
            gaps.append((current_end, start))
        current_end = max(current_end, end)
    if current_end < coord_limits[1]:
        gaps.append((current_end, coord_limits[1]))
    if len(gaps) == 0:
        return None
    gap_widths = [(end - start, (start, end)) for start, end in gaps]
    if (
        cyclic_coords
        and gaps[0][0] == coord_limits[0]
        and gaps[-1][1] == coord_limits[1]
    ):
        gap_widths[0] = (
            gap_widths[0][0] + gap_widths[-1][0],
            (gaps[-1][0], gaps[0][1]),
        )
        gap_widths.pop()

    return max(gap_widths, key=lambda gw: gw[0])[1]


def _unwrap_multipolygon(
    multipolygon: MultiPolygon,
    direction: Literal['east', 'west', 'centroid'],
    coord_limits: tuple[float, float],
    gap_threshold: float,
) -> MultiPolygon:
    """Unwrap a MultiPolygon based on the specified direction."""
    if multipolygon.is_empty:
        return multipolygon
    minx, _, maxx, _ = multipolygon.bounds
    if minx < coord_limits[0] or maxx > coord_limits[1]:
        msg = (
            'Geometry bounds exceed coordinate limits.'
            f' Got bounds: ({minx}, {maxx}),'
            f' limits: {coord_limits}'
        )
        raise ValueError(msg)
    if maxx - minx < gap_threshold:
        return multipolygon

    polygons = list(multipolygon.geoms)
    gap = _find_geometries_gap(
        geoms=polygons,
        coord_limits=coord_limits,
        cyclic_coords=True,
    )
    if gap is None or gap[1] - gap[0] < gap_threshold or gap[1] < gap[0]:
        return multipolygon
    if direction == 'centroid':
        centroid_x = multipolygon.centroid.x
        direction = 'west' if centroid_x < (gap[0] + gap[1]) / 2 else 'east'
    shift = (
        coord_limits[1] - coord_limits[0]
        if direction == 'east'
        else (coord_limits[0] - coord_limits[1])
    )
    to_be_shifted = [
        (p.bounds[2] <= gap[0] and direction == 'east')
        or (p.bounds[0] >= gap[1] and direction == 'west')
        for p in polygons
    ]

    wrapped_polygons = [
        affinity.translate(p, xoff=shift) if t else p
        for p, t in zip(polygons, to_be_shifted, strict=False)
    ]
    return MultiPolygon(wrapped_polygons)


def unwrap_longitude(
    data: GeoDataFrame,
    geom_col: str = 'geometry',
    direction: Literal['east', 'west', 'centroid'] = 'east',
    gap_threshold: float = 180.0,
) -> GeoDataFrame:
    """Unwrap geometries crossing the antimeridian.

    Unwrap longitude values to produce a continuous sequence across the
    meridian.

    This function converts cyclic longitude values (ranging from -180° to 180°)
    into a continuous representation by adding or subtracting 360° when a jump
    larger than 180° is detected. Useful for handling features that cross the
    antimeridian in geographic datasets.

    Parameters
    ----------
    data : GeoDataFrame
        Input GeoDataFrame containing geometries to be unwrapped.
    geom_col : str, optional
        Name of the geometry column in the GeoDataFrame. Default is 'geometry'.
    direction: Literal['east', 'west', 'centroid'], optional
        Direction to unwrap the geometries. Options are:
        - 'east': Unwrap towards the east (default).
        - 'west': Unwrap towards the west.
        - 'centroid': Shift toward the side with the larger total polygon area.
          The area is calculated based on the current coordinate system.
    gap_threshold: float
        Minimum gap size (in degrees) to consider for unwrapping. Default is
        180.0 degrees.

    Returns
    -------
    GeoDataFrame
        A new GeoDataFrame with unwrapped geometries.

    """
    # Create a copy to avoid modifying the original
    result = data.copy()

    # Apply unwrapping to each geometry if geometry type is MultiPolygon
    result[geom_col] = result[geom_col].apply(
        lambda geom: _unwrap_multipolygon(
            multipolygon=geom,
            direction=direction,
            coord_limits=(-180, 180),
            gap_threshold=gap_threshold,
        )
        if isinstance(geom, MultiPolygon)
        else geom
    )

    # Fix any invalid geometries that may result from unwrapping
    # (e.g., MultiPolygons with touching edges at the antimeridian)
    result[geom_col] = result[geom_col].apply(
        lambda geom: geom.buffer(0) if not geom.is_valid else geom
    )

    return result
