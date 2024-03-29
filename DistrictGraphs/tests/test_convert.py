from .. import convert

import unittest
import shapely.geometry, shapely.wkt
import geopandas
import os

TESTS_DATA = os.path.join(os.path.dirname(__file__), 'data')

# DE-9IM pattern for two identical lines
SAME_LINES = '1FFF0FFF2'

class TestConvert (unittest.TestCase):
    
    def test_load_block_graph(self):
        frame = geopandas.read_file(os.path.join(TESTS_DATA, 'kohl-center.geojson'))
        graph = convert.blocks_frame_graph(frame, 'GEOID10')
        
        self.assertEqual(len(graph.nodes), 11)
        self.assertEqual(len(graph.edges), 14 * 2 + 9 * 2)
        self.assertEqual(len(list(graph.neighbors(convert.OUTSIDE))), 9)

        self.assertNotIn(('550250012001004', convert.OUTSIDE), graph.edges)
        self.assertIn(('550250012001004', '550250012001003'), graph.edges)
        self.assertIn(('550250012001003', convert.OUTSIDE), graph.edges)
        self.assertIn(('550250012001003', '550250016063003'), graph.edges)
        self.assertIn(('550250016063003', convert.OUTSIDE), graph.edges)
        self.assertNotIn(('550250012001004', '550250016063003'), graph.edges)
        self.assertIn(('550250016063003', '550250016052009'), graph.edges)
        self.assertIn(('550250016052009', '550250016051004'), graph.edges)
        self.assertNotIn(('550250016051004', '550250016063003'), graph.edges)
        
        import networkx as nx
        nx.write_gpickle(graph, '/tmp/graph.pickle')

    def test_shared_linear_boundary_simple(self):
        # GEOIDs 550250011012019, 550250011012020 share a single edge
        geom1 = shapely.geometry.shape({ "type": "Polygon", "coordinates": [ [ [ -89.407346, 43.068485 ], [ -89.407342, 43.068729 ], [ -89.406568, 43.068722 ], [ -89.406569, 43.068474 ], [ -89.406573, 43.067729 ], [ -89.406994, 43.06774 ], [ -89.407326, 43.067739 ], [ -89.407343, 43.068211 ], [ -89.407346, 43.068485 ] ] ] })
        geom2 = shapely.geometry.shape({ "type": "Polygon", "coordinates": [ [ [ -89.406569, 43.068474 ], [ -89.406568, 43.068722 ], [ -89.405711, 43.068714 ], [ -89.405708, 43.068462 ], [ -89.405706, 43.068294 ], [ -89.405707, 43.068203 ], [ -89.405715, 43.067719 ], [ -89.40582, 43.067722 ], [ -89.406073, 43.067721 ], [ -89.406573, 43.067729 ], [ -89.406569, 43.068474 ] ] ] })
        actual = convert.shared_linear_boundary(geom1, geom2)
        expected = shapely.wkt.loads('MULTILINESTRING ((-89.406568 43.068722, -89.406569 43.068474), (-89.406569 43.068474, -89.406573 43.067729))')
        self.assertEqual(expected.relate(actual), SAME_LINES)

    def test_shared_linear_boundary_multi(self):
        # GEOIDs 550250011022016 550250011022005 share an interrupted edge
        geom1 = shapely.geometry.shape({ "type": "Polygon", "coordinates": [ [ [ -89.412767, 43.0745 ], [ -89.412767, 43.074574 ], [ -89.412736, 43.075146 ], [ -89.412431, 43.075141 ], [ -89.410414, 43.075126 ], [ -89.41042, 43.074789 ], [ -89.410429, 43.07428 ], [ -89.410146, 43.074275 ], [ -89.410133, 43.074779 ], [ -89.410125, 43.075109 ], [ -89.409963, 43.075101 ], [ -89.409596, 43.075097 ], [ -89.408612, 43.075091 ], [ -89.407804, 43.075085 ], [ -89.40771, 43.075088 ], [ -89.406413, 43.075074 ], [ -89.406216, 43.075076 ], [ -89.40622, 43.074969 ], [ -89.406209, 43.074836 ], [ -89.406207, 43.074317 ], [ -89.406203, 43.074166 ], [ -89.406205, 43.073758 ], [ -89.406159, 43.073347 ], [ -89.407361, 43.073359 ], [ -89.408988, 43.073369 ], [ -89.409595, 43.073377 ], [ -89.409715, 43.073378 ], [ -89.410165, 43.073406 ], [ -89.410443, 43.073419 ], [ -89.410625, 43.073427 ], [ -89.411203, 43.073525 ], [ -89.411523, 43.073646 ], [ -89.41224, 43.073874 ], [ -89.412607, 43.074005 ], [ -89.412671, 43.074051 ], [ -89.412696, 43.074075 ], [ -89.412726, 43.074118 ], [ -89.412753, 43.074178 ], [ -89.412767, 43.074366 ], [ -89.412767, 43.0745 ] ] ] })
        geom2 = shapely.geometry.shape({ "type": "Polygon", "coordinates": [ [ [ -89.412702, 43.076263 ], [ -89.412709, 43.076421 ], [ -89.412612, 43.076416 ], [ -89.412269, 43.076413 ], [ -89.412048, 43.076455 ], [ -89.412026, 43.076463 ], [ -89.411929, 43.0765 ], [ -89.411749, 43.076581 ], [ -89.411533, 43.076632 ], [ -89.41124, 43.076692 ], [ -89.410995, 43.076694 ], [ -89.410891, 43.076691 ], [ -89.410664, 43.07667 ], [ -89.409904, 43.076528 ], [ -89.40965, 43.0765 ], [ -89.409242, 43.076482 ], [ -89.409079, 43.076487 ], [ -89.408843, 43.076501 ], [ -89.408462, 43.076536 ], [ -89.408197, 43.076552 ], [ -89.40772, 43.076564 ], [ -89.40732, 43.076557 ], [ -89.407036, 43.076542 ], [ -89.406814, 43.076513 ], [ -89.406702, 43.076484 ], [ -89.406013, 43.076145 ], [ -89.405937, 43.076111 ], [ -89.405824, 43.076069 ], [ -89.405957, 43.075902 ], [ -89.406005, 43.075743 ], [ -89.406093, 43.075534 ], [ -89.406176, 43.075308 ], [ -89.406213, 43.075161 ], [ -89.406216, 43.075076 ], [ -89.406413, 43.075074 ], [ -89.40771, 43.075088 ], [ -89.407804, 43.075085 ], [ -89.408612, 43.075091 ], [ -89.409596, 43.075097 ], [ -89.409963, 43.075101 ], [ -89.410125, 43.075109 ], [ -89.410414, 43.075126 ], [ -89.412431, 43.075141 ], [ -89.412736, 43.075146 ], [ -89.412702, 43.076263 ] ] ] })
        actual = convert.shared_linear_boundary(geom1, geom2)
        expected = shapely.wkt.loads('MULTILINESTRING ((-89.412736 43.075146, -89.412431 43.075141), (-89.412431 43.075141, -89.410414 43.075126), (-89.410125 43.075109, -89.409963 43.075101), (-89.409963 43.075101, -89.409596 43.075097), (-89.409596 43.075097, -89.408612 43.075091), (-89.408612 43.075091, -89.407804 43.075085), (-89.407804 43.075085, -89.40771 43.075088), (-89.40771 43.075088, -89.406413 43.075074), (-89.406413 43.075074, -89.406216 43.075076))')
        self.assertEqual(expected.relate(actual), SAME_LINES)

    def test_shared_linear_boundary_cornertouch(self):
        # GEOIDs 550250011011014 550250011011016 touch only at a corner
        geom1 = shapely.geometry.shape({ "type": "Polygon", "coordinates": [ [ [ -89.404062, 43.069354 ], [ -89.403248, 43.069346 ], [ -89.402868, 43.069342 ], [ -89.402537, 43.069329 ], [ -89.40246, 43.069332 ], [ -89.402476, 43.069126 ], [ -89.40247, 43.068847 ], [ -89.402474, 43.068756 ], [ -89.403104, 43.068766 ], [ -89.403634, 43.068765 ], [ -89.404069, 43.068771 ], [ -89.404062, 43.069354 ] ] ] })
        geom2 = shapely.geometry.shape({ "type": "Polygon", "coordinates": [ [ [ -89.402474, 43.068756 ], [ -89.402243, 43.068757 ], [ -89.401417, 43.068741 ], [ -89.400944, 43.068749 ], [ -89.400953, 43.06822 ], [ -89.401195, 43.068223 ], [ -89.401315, 43.068221 ], [ -89.40234, 43.068243 ], [ -89.402469, 43.068243 ], [ -89.402477, 43.068674 ], [ -89.402474, 43.068756 ] ] ] })
        with self.assertRaises(ValueError) as e:
            actual = convert.shared_linear_boundary(geom1, geom2)

    def test_shared_linear_boundary_multitouch(self):
        # GEOIDs 550250011022006 550250032001014 touch at a corner and share an edge
        geom1 = shapely.geometry.shape({ "type": "Polygon", "coordinates": [ [ [ -89.424156, 43.074595 ], [ -89.423986, 43.074605 ], [ -89.423898, 43.074626 ], [ -89.423825, 43.074648 ], [ -89.423739, 43.074655 ], [ -89.423499, 43.074655 ], [ -89.423169, 43.074655 ], [ -89.422745, 43.074657 ], [ -89.422682, 43.074679 ], [ -89.422651, 43.074705 ], [ -89.422632, 43.074737 ], [ -89.422629, 43.074793 ], [ -89.422629, 43.074896 ], [ -89.422632, 43.075334 ], [ -89.422633, 43.07544 ], [ -89.423663, 43.075572 ], [ -89.423288, 43.07557 ], [ -89.423266, 43.076513 ], [ -89.421675, 43.076501 ], [ -89.421708, 43.076305 ], [ -89.421824, 43.075744 ], [ -89.421841, 43.075655 ], [ -89.421885, 43.075422 ], [ -89.421915, 43.075166 ], [ -89.421979, 43.074976 ], [ -89.422053, 43.074801 ], [ -89.422107, 43.074698 ], [ -89.422282, 43.074491 ], [ -89.422406, 43.074367 ], [ -89.422775, 43.074083 ], [ -89.422954, 43.073879 ], [ -89.422478, 43.074194 ], [ -89.422071, 43.074542 ], [ -89.421897, 43.074823 ], [ -89.421806, 43.075019 ], [ -89.421758, 43.07522 ], [ -89.421743, 43.075532 ], [ -89.421711, 43.075673 ], [ -89.421605, 43.076143 ], [ -89.421529, 43.0765 ], [ -89.421369, 43.076503 ], [ -89.421383, 43.07643 ], [ -89.421554, 43.075843 ], [ -89.421592, 43.07569 ], [ -89.421591, 43.075661 ], [ -89.421562, 43.075618 ], [ -89.42151, 43.075576 ], [ -89.421473, 43.075561 ], [ -89.421426, 43.075551 ], [ -89.420624, 43.075544 ], [ -89.419202, 43.075538 ], [ -89.418926, 43.075533 ], [ -89.418942, 43.075031 ], [ -89.418947, 43.074887 ], [ -89.418948, 43.07437 ], [ -89.418948, 43.074224 ], [ -89.419135, 43.074211 ], [ -89.420152, 43.074145 ], [ -89.420825, 43.074079 ], [ -89.421282, 43.074017 ], [ -89.42186, 43.073933 ], [ -89.423459, 43.073691 ], [ -89.424911, 43.074593 ], [ -89.424156, 43.074595 ] ] ] })
        geom2 = shapely.geometry.shape({ "type": "Polygon", "coordinates": [ [ [ -89.42163, 43.076766 ], [ -89.421501, 43.07743 ], [ -89.42141, 43.07775 ], [ -89.421374, 43.07786 ], [ -89.421203, 43.077881 ], [ -89.421195, 43.077845 ], [ -89.421181, 43.077758 ], [ -89.421248, 43.077591 ], [ -89.421311, 43.077282 ], [ -89.421404, 43.077061 ], [ -89.421514, 43.076577 ], [ -89.421369, 43.076503 ], [ -89.421529, 43.0765 ], [ -89.421675, 43.076501 ], [ -89.42163, 43.076766 ] ] ] })
        actual = convert.shared_linear_boundary(geom1, geom2)
        expected = shapely.wkt.loads('MULTILINESTRING ((-89.421529 43.0765, -89.421369 43.076503))')
        self.assertEqual(expected.relate(actual), SAME_LINES)
