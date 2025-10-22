import geopandas as gpd
import pytest
import shapely.affinity
from shapely.geometry import MultiPolygon, Polygon


@pytest.fixture
def gdf() -> gpd.GeoDataFrame:
    polygon_east = Polygon([(170, 60), (180, 60), (180, 68), (170, 65)])
    polygon_west = Polygon([(-170, 60), (-166, 63), (-160, 64), (-170, 66)])
    gdf = gpd.GeoDataFrame(
        {
            'name': [
                'East',
                'West',
                'EW',
                'EW touch',
            ],
            'geometry': [
                polygon_east,
                shapely.affinity.translate(polygon_west, yoff=-10),
                shapely.affinity.translate(
                    MultiPolygon([polygon_east, polygon_west]), yoff=-20
                ),
                shapely.affinity.translate(
                    MultiPolygon(
                        [
                            polygon_east,
                            shapely.affinity.translate(polygon_west, xoff=-10),
                        ]
                    ),
                    yoff=-30,
                ),
            ],
        }
    )
    return gdf.set_geometry('geometry').set_crs(epsg=4326)
