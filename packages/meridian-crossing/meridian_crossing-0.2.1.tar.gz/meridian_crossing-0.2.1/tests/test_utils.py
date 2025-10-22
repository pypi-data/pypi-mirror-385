from typing import ClassVar

from geopandas import GeoDataFrame
from shapely.geometry import MultiPolygon, Polygon

from meridian_crossing import utils


class TestUnwrapLongitude:
    def test_to_centroid(self, gdf: GeoDataFrame):
        gdf_unwrapped = utils.unwrap_longitude(
            data=gdf,
            geom_col='geometry',
            direction='centroid',
            gap_threshold=180,
        )
        assert gdf_unwrapped.geometry.is_valid.all()

        e_unwrapped = gdf_unwrapped[
            gdf_unwrapped['name'] == 'East'
        ].geometry.iloc[0]
        e_expected = Polygon([(170, 60), (180, 60), (180, 68), (170, 65)])
        assert e_unwrapped.equals(e_expected)

        w_unwrapped = gdf_unwrapped[
            gdf_unwrapped['name'] == 'West'
        ].geometry.iloc[0]
        w_expected = Polygon([(-170, 50), (-166, 53), (-160, 54), (-170, 56)])
        assert w_unwrapped.equals(w_expected)

        ew_unwrapped = gdf_unwrapped[
            gdf_unwrapped['name'] == 'EW'
        ].geometry.iloc[0]
        ew_expected = MultiPolygon(
            [
                Polygon([(170, 40), (180, 40), (180, 48), (170, 45)]),
                Polygon([(190, 40), (194, 43), (200, 44), (190, 46)]),
            ]
        )
        assert ew_unwrapped.equals(ew_expected)

        ew_touch_unwrapped = gdf_unwrapped[
            gdf_unwrapped['name'] == 'EW touch'
        ].geometry.iloc[0]
        ew_touch_expected = (
            Polygon(
                [
                    (170.0, 30.0),
                    (180.0, 30.0),
                    (184.0, 33.0),
                    (190.0, 34.0),
                    (180.0, 36.0),
                    (180.0, 38.0),
                    (170.0, 35.0),
                ]
            ),
        )
        assert ew_touch_unwrapped.equals(ew_touch_expected)


class TestFindGeometriesGap:
    polygons: ClassVar[list[Polygon]] = [
        Polygon([(-170, 0), (-90, 0), (-90, 10), (-170, 10)]),
        Polygon([(20, 0), (30, 0), (30, 10), (20, 10)]),
        Polygon([(-50, 0), (-20, 0), (-20, 10), (-50, 10)]),
        Polygon([(40, 0), (150, 0), (150, 10), (40, 10)]),
        Polygon([(-110, 0), (-50, 0), (-50, 10), (-110, 10)]),
    ]

    def test_non_cyclic(self):
        gap = utils._find_geometries_gap(
            geoms=self.polygons, coord_limits=(-180, 180), cyclic_coords=False
        )
        assert gap == (-20, 20)

    def test_cyclic(self):
        gap = utils._find_geometries_gap(
            geoms=self.polygons, coord_limits=(-180, 180), cyclic_coords=True
        )
        assert gap == (150, -170)


class TestUnwrapMultipolygon:
    multipolygon: ClassVar[MultiPolygon] = MultiPolygon(
        [
            Polygon([(-170, 0), (-90, 0), (-90, 10), (-170, 10)]),
            Polygon([(20, 0), (30, 0), (30, 10), (20, 10)]),
            Polygon([(40, 0), (150, 0), (150, 10), (40, 10)]),
        ]
    )

    def test_unwrap(self):
        unwrapped = utils._unwrap_multipolygon(
            multipolygon=self.multipolygon,
            direction='east',
            coord_limits=(-180, 180),
            gap_threshold=100,
        )
        expected = MultiPolygon(
            [
                Polygon([(190, 0), (270, 0), (270, 10), (190, 10)]),
                Polygon([(20, 0), (30, 0), (30, 10), (20, 10)]),
                Polygon([(40, 0), (150, 0), (150, 10), (40, 10)]),
            ]
        )
        assert unwrapped.equals(expected)
        unwrapped = utils._unwrap_multipolygon(
            multipolygon=self.multipolygon,
            direction='centroid',
            coord_limits=(-180, 180),
            gap_threshold=100,
        )
        expected = MultiPolygon(
            [
                Polygon([(190, 0), (270, 0), (270, 10), (190, 10)]),
                Polygon([(20, 0), (30, 0), (30, 10), (20, 10)]),
                Polygon([(40, 0), (150, 0), (150, 10), (40, 10)]),
            ]
        )
        assert unwrapped.equals(expected)

        unwrapped = utils._unwrap_multipolygon(
            multipolygon=self.multipolygon,
            direction='west',
            coord_limits=(-180, 180),
            gap_threshold=100,
        )
        expected = MultiPolygon(
            [
                Polygon([(-170, 0), (-90, 0), (-90, 10), (-170, 10)]),
                Polygon([(-340, 0), (-330, 0), (-330, 10), (-340, 10)]),
                Polygon([(-320, 0), (-210, 0), (-210, 10), (-320, 10)]),
            ]
        )
        assert unwrapped.equals(expected)

    def test_large_threshold(self):
        unwrapped = utils._unwrap_multipolygon(
            multipolygon=self.multipolygon,
            direction='east',
            coord_limits=(-180, 180),
            gap_threshold=200,
        )
        assert unwrapped.equals(self.multipolygon)
