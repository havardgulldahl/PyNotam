import unittest
from shapely.geometry import shape, Polygon

# Import geo helpers from the actual module name (_geo). Original tests referenced
# a non-existent notam_geo module; adjust to current implementation file.
from _geo import (
    parse_latlon_pair,
    parse_multi_latlon_seq,
    m_from_text,
    build_circle,
    build_line_corridor,
    build_sector,
    build_ellipse,
    build_polygon,
    parse_notam_block,
    parse_notam_file_text,
)


class GeoParsingTests(unittest.TestCase):
    def test_parse_latlon_pair(self):
        lon, lat = parse_latlon_pair("595835N0301229E")
        self.assertGreater(lat, 0)
        self.assertGreater(lon, 0)
        self.assertAlmostEqual(lat, 59.9764, places=3)
        self.assertAlmostEqual(lon, 30.2081, places=3)

    def test_parse_multi_latlon_seq(self):
        coords = parse_multi_latlon_seq(
            "595835N0301229E-595811N0301228E-595809N0301307E"
        )
        self.assertEqual(len(coords), 3)
        for lon, lat in coords:
            self.assertTrue(-180 <= lon <= 180)
            self.assertTrue(-90 <= lat <= 90)

    def test_m_from_text(self):
        self.assertEqual(m_from_text("5KM"), 5000)
        self.assertEqual(m_from_text("0.5KM"), 500)
        self.assertEqual(m_from_text("150M"), 150)

    def test_build_circle_area(self):
        center = (30.0, 60.0)
        poly = build_circle(center, 5000)
        self.assertTrue(poly.is_valid)
        cx, cy = poly.centroid.x, poly.centroid.y
        self.assertLess(abs(cx - center[0]), 0.01)
        self.assertLess(abs(cy - center[1]), 0.01)

    def test_build_line_corridor(self):
        pts = [(30.0, 60.0), (30.1, 60.1)]
        poly = build_line_corridor(pts, 1000)
        self.assertTrue(poly.is_valid)
        self.assertGreater(poly.area, 0)

    def test_build_sector(self):
        center = (30.0, 60.0)
        poly = build_sector(center, 4000, 300, 60)  # wrap-around supported
        self.assertTrue(poly.is_valid)
        self.assertGreater(poly.area, 0)

    def test_build_ellipse(self):
        center = (30.0, 60.0)
        poly = build_ellipse(center, major_km=2.8, minor_km=1.3, azm_deg=141)
        self.assertTrue(poly.is_valid)
        self.assertGreater(poly.area, 0)

    def test_build_polygon(self):
        coords = [(30, 60), (30.1, 60), (30.1, 60.1), (30, 60.1)]
        poly = build_polygon(coords)
        self.assertTrue(poly.is_valid)
        self.assertGreater(poly.area, 0)

    def test_parse_notam_circle(self):
        block = """(Q1762/25 NOTAMN
E) AIRSPACE CLSD WI CIRCLE RADIUS 1KM CENTRE 585106N0304315E.
F) SFC  G) 150M AMSL)"""
        nf = parse_notam_block(block)
        self.assertIsNotNone(nf)
        self.assertTrue(nf.parts)
        p = nf.parts[0]
        self.assertEqual(p.kind, "CIRCLE")
        self.assertEqual(p.altitude_to.get("unit"), "M")

    def test_parse_notam_sector(self):
        block = """(Q1507/25 NOTAMN
E) AIRSPACE CLSD AS FLW:
WI SECTOR CENTRE 610424N0331023E AZM 321-144 DEG RADIUS 8KM.
F) SFC  G) 1500M AMSL)"""
        nf = parse_notam_block(block)
        self.assertIsNotNone(nf)
        self.assertTrue(nf.parts)
        self.assertTrue(any(prt.kind == "SECTOR" for prt in nf.parts))

    def test_parse_notam_ellipse(self):
        block = """(Q1760/25 NOTAMN
E) AIRSPACE CLSD AS FLW:
ELLIPSE CENTRE 584622N0304438E WITH AXES DIMENSIONS 2.8X1.3KM AZM OF MAJOR AXIS 141DEG
F) SFC  G) 150M AMSL)"""
        nf = parse_notam_block(block)
        self.assertIsNotNone(nf)
        self.assertTrue(nf.parts)
        self.assertEqual(nf.parts[0].kind, "ELLIPSE")

    def test_parse_notam_line_corridor(self):
        block = """(Q1624/25 NOTAMN
E) AIRSPACE CLSD WI 0.75KM EITHER SIDE OF LINE JOINING POINTS:
595217N0304217E-594911N0305154E.
F) SFC  G) 300M AMSL)"""
        nf = parse_notam_block(block)
        self.assertIsNotNone(nf)
        self.assertTrue(nf.parts)
        self.assertEqual(nf.parts[0].kind, "LINE_CORRIDOR")

    def test_parse_notam_area_polygon(self):
        block = """(Q0338/25 NOTAMN
E) AIRSPACE CLSD WI AREA:
595835N0301229E-595811N0301228E-595809N0301307E-595811N0301313E-595835N0301229E.
F) SFC  G) 100M AMSL)"""
        nf = parse_notam_block(block)
        self.assertIsNotNone(nf)
        self.assertTrue(nf.parts)
        self.assertEqual(nf.parts[0].kind, "POLYGON")
        geom = nf.parts[0].geom
        self.assertIsInstance(geom, Polygon)
        self.assertTrue(geom.exterior.is_ring)

    def test_full_file_parsing_smoke(self):
        content = """(Q1762/25 NOTAMN
A) ULLL B)2509100700 C)2509111400
E) AIRSPACE CLSD WI CIRCLE RADIUS 1KM CENTRE 585106N0304315E.
F) SFC  G) 150M AMSL)"""
        fc = parse_notam_file_text(content)
        self.assertEqual(fc.get("type"), "FeatureCollection")
        self.assertEqual(len(fc.get("features", [])), 1)
        geom = shape(fc["features"][0]["geometry"])
        self.assertTrue(geom.is_valid)


if __name__ == "__main__":  # pragma: no cover
    unittest.main(verbosity=2)
