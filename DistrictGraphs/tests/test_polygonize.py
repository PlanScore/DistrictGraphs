from .. import polygonize

import unittest
import os
import networkx
import shapely

TESTS_DATA = os.path.join(os.path.dirname(__file__), 'data')

# DE-9IM pattern for two identical polygons
SAME_POLYS = '2FFF1FFF2'

class TestPolygonize (unittest.TestCase):
    
    def test_parse_assignments1(self):
        with open(os.path.join(TESTS_DATA, 'madison3-assignments1.csv'), 'rb') as file:
            assignments = polygonize.parse_assignments(file)
        
        self.assertEqual(len(assignments), 5)
        self.assertEqual(assignments[0], ('550250016063000', '1'))
        self.assertEqual(assignments[1], ('550250016063003', '1'))
        self.assertEqual(assignments[2], ('550250012001003', '1'))
        self.assertEqual(assignments[3], ('550250032001014', '1'))
        self.assertEqual(assignments[4], ('550250011022006', '1'))
    
    def test_parse_assignments2(self):
        with open(os.path.join(TESTS_DATA, 'madison3-assignments2.csv'), 'rb') as file:
            assignments = polygonize.parse_assignments(file)
        
        self.assertEqual(len(assignments), 6)
        self.assertEqual(assignments[0], ('550250011011015', '1'))
        self.assertEqual(assignments[1], ('550250011011014', '1'))
        self.assertEqual(assignments[2], ('550250011011017', '1'))
        self.assertEqual(assignments[3], ('550250011011018', '2'))
        self.assertEqual(assignments[4], ('550250011011019', '2'))
        self.assertEqual(assignments[5], ('550250011011016', '2'))
    
    def test_parse_assignments3(self):
        with open(os.path.join(TESTS_DATA, 'madison3-assignments3.csv'), 'rb') as file:
            assignments = polygonize.parse_assignments(file)
        
        self.assertEqual(len(assignments), 6)
        self.assertEqual(assignments[0], ('550250011011014', '1'))
        self.assertEqual(assignments[1], ('550250011011015', '1'))
        self.assertEqual(assignments[2], ('550250011011016', '2'))
        self.assertEqual(assignments[3], ('550250011011017', '2'))
        self.assertEqual(assignments[4], ('550250011011018', '3'))
        self.assertEqual(assignments[5], ('550250011011019', '3'))
    
    def test_parse_assignments4(self):
        with open(os.path.join(TESTS_DATA, 'DB-db1-census-tracts-export.csv'), 'rb') as file:
            assignments = polygonize.parse_assignments(file)
        
        self.assertEqual(len(assignments), 9)
        self.assertEqual(assignments[0], ('42047951000', '1'))
        self.assertEqual(assignments[1], ('42031160900', '1'))
        self.assertEqual(assignments[2], ('42031160400', '1'))
        self.assertEqual(assignments[3], ('42007603802', '2'))
        self.assertEqual(assignments[4], ('42003414102', '2'))
        self.assertEqual(assignments[5], ('42073010100', '2'))
        self.assertEqual(assignments[6], ('42003130300', '3'))
        self.assertEqual(assignments[7], ('42003070800', '3'))
        self.assertEqual(assignments[8], ('42003980000', '3'))
    
    def test_parse_assignments5(self):
        with open(os.path.join(TESTS_DATA, 'DRA-NC-2016-Contingent-Corrected-map.csv'), 'rb') as file:
            assignments = polygonize.parse_assignments(file)
        
        self.assertEqual(len(assignments), 9)
        self.assertEqual(assignments[0], ('370010205012023', '6'))
        self.assertEqual(assignments[1], ('370010205012019', '6'))
        self.assertEqual(assignments[2], ('370010205012038', '6'))
        self.assertEqual(assignments[3], ('370179501002090', '7'))
        self.assertEqual(assignments[4], ('370179501002084', '7'))
        self.assertEqual(assignments[5], ('370179501002100', '7'))
        self.assertEqual(assignments[6], ('370250424011031', '8'))
        self.assertEqual(assignments[7], ('370250412001027', '8'))
        self.assertEqual(assignments[8], ('370250407031003', '8'))
    
    def test_parse_assignments6(self):
        with open(os.path.join(TESTS_DATA, 'DRA-NC-Congress-2016BG.csv'), 'rb') as file:
            assignments = polygonize.parse_assignments(file)
        
        self.assertEqual(len(assignments), 9)
        self.assertEqual(assignments[0], ('370439501003', '13'))
        self.assertEqual(assignments[1], ('370439502003', '13'))
        self.assertEqual(assignments[2], ('370439502002', '13'))
        self.assertEqual(assignments[3], ('370459504004', '12'))
        self.assertEqual(assignments[4], ('370459505002', '12'))
        self.assertEqual(assignments[5], ('370459505003', '12'))
        self.assertEqual(assignments[6], ('371219502001', '11'))
        self.assertEqual(assignments[7], ('371219502003', '11'))
        self.assertEqual(assignments[8], ('371219503001', '11'))
    
    def test_get_county_graph_paths_tracts(self):
        assignments = [
            polygonize.Assignment('550250011011014', '1'),
            polygonize.Assignment('550250011011016', '2'),
            polygonize.Assignment('550250011011018', '3'),
            ]
        
        paths = polygonize.get_county_graph_paths('tract', assignments)
        self.assertEqual(paths, {'55/55025-tract.pickle'})
    
    def test_get_county_graph_paths_vtds(self):
        assignments = [
            polygonize.Assignment('550250011011014', '1'),
            polygonize.Assignment('550250011011016', '2'),
            polygonize.Assignment('550250011011018', '3'),
            ]
        
        paths = polygonize.get_county_graph_paths('vtd', assignments)
        self.assertEqual(paths, {'55/55025-vtd.pickle'})
    
    def test_get_county_graph_paths_bgs(self):
        assignments = [
            polygonize.Assignment('550250011011014', '1'),
            polygonize.Assignment('550250011011016', '2'),
            polygonize.Assignment('550250011011018', '3'),
            ]
        
        paths = polygonize.get_county_graph_paths('bg', assignments)
        self.assertEqual(paths, {'55/55025-bg.pickle'})
    
    def test_get_county_graph_paths_blocks(self):
        assignments = [
            polygonize.Assignment('550250011011014', '1'),
            polygonize.Assignment('550250011011016', '2'),
            polygonize.Assignment('550250011011018', '3'),
            ]
        
        paths = polygonize.get_county_graph_paths('tabblock', assignments)
        self.assertEqual(paths, {'55/55025-tabblock.pickle'})
    
    def test_polygonize_assignment1(self):
        graph = networkx.read_gpickle(os.path.join(TESTS_DATA, 'madison3.pickle'))
        
        assignments = [
            polygonize.Assignment('550250016063000', '1'),
            polygonize.Assignment('550250016063003', '1'),
            polygonize.Assignment('550250012001003', '1'), # <-- donut hole
            polygonize.Assignment('550250032001014', '1'), # <-- corner-touch pair
            polygonize.Assignment('550250011022006', '1'), # <-- corner-touch pair
            ]
        
        districts = polygonize.polygonize_assignment(assignments, graph)
        
        self.assertEqual(len(districts), 1)
        self.assertIn('1', districts)
        self.assertEqual(len(districts['1'].geoms), 2)
        
        expected = shapely.geometry.shape({ "type": "MultiPolygon", "coordinates": [ [ [ [ -89.400745, 43.064762 ], [ -89.400747, 43.065161 ], [ -89.400764, 43.065475 ], [ -89.400794, 43.065738 ], [ -89.400837, 43.066314 ], [ -89.400941, 43.06765 ], [ -89.400951, 43.067868 ], [ -89.400953, 43.06822 ], [ -89.400944, 43.068749 ], [ -89.400929, 43.069319 ], [ -89.400897, 43.069778 ], [ -89.400886, 43.069885 ], [ -89.399591, 43.069532 ], [ -89.399189, 43.0694 ], [ -89.398719, 43.069246 ], [ -89.397588, 43.068897 ], [ -89.397573, 43.068959 ], [ -89.397537, 43.069317 ], [ -89.397509, 43.070289 ], [ -89.397528, 43.070907 ], [ -89.396761, 43.070889 ], [ -89.395905, 43.070875 ], [ -89.395925, 43.070316 ], [ -89.395967, 43.06921 ], [ -89.395982, 43.068923 ], [ -89.395997, 43.068627 ], [ -89.395408, 43.068422 ], [ -89.393817, 43.06787 ], [ -89.393967, 43.067764 ], [ -89.394013, 43.067732 ], [ -89.394849, 43.06716 ], [ -89.395127, 43.066998 ], [ -89.395557, 43.066703 ], [ -89.396172, 43.066247 ], [ -89.396356, 43.066115 ], [ -89.397629, 43.06523 ], [ -89.398269, 43.064779 ], [ -89.399755, 43.064792 ], [ -89.400451, 43.064794 ], [ -89.400745, 43.064762 ] ], [ [ -89.397774, 43.066547 ], [ -89.397773, 43.066501 ], [ -89.397772, 43.066445 ], [ -89.39777, 43.066396 ], [ -89.397555, 43.0664 ], [ -89.397385, 43.066402 ], [ -89.397395, 43.066825 ], [ -89.397486, 43.066829 ], [ -89.397555, 43.066828 ], [ -89.39763, 43.066829 ], [ -89.397704, 43.066832 ], [ -89.397761, 43.066841 ], [ -89.397772, 43.066788 ], [ -89.397773, 43.066741 ], [ -89.397775, 43.066686 ], [ -89.397774, 43.066638 ], [ -89.397776, 43.066592 ], [ -89.397774, 43.066547 ] ] ], [ [ [ -89.421203, 43.077881 ], [ -89.421195, 43.077845 ], [ -89.421181, 43.077758 ], [ -89.421248, 43.077591 ], [ -89.421311, 43.077282 ], [ -89.421404, 43.077061 ], [ -89.421514, 43.076577 ], [ -89.421369, 43.076503 ], [ -89.421383, 43.07643 ], [ -89.421554, 43.075843 ], [ -89.421592, 43.07569 ], [ -89.421591, 43.075661 ], [ -89.421562, 43.075618 ], [ -89.42151, 43.075576 ], [ -89.421473, 43.075561 ], [ -89.421426, 43.075551 ], [ -89.420624, 43.075544 ], [ -89.419202, 43.075538 ], [ -89.418926, 43.075533 ], [ -89.418942, 43.075031 ], [ -89.418947, 43.074887 ], [ -89.418948, 43.07437 ], [ -89.418948, 43.074224 ], [ -89.419135, 43.074211 ], [ -89.420152, 43.074145 ], [ -89.420825, 43.074079 ], [ -89.421282, 43.074017 ], [ -89.42186, 43.073933 ], [ -89.423459, 43.073691 ], [ -89.424911, 43.074593 ], [ -89.424156, 43.074595 ], [ -89.423986, 43.074605 ], [ -89.423898, 43.074626 ], [ -89.423825, 43.074648 ], [ -89.423739, 43.074655 ], [ -89.423499, 43.074655 ], [ -89.423169, 43.074655 ], [ -89.422745, 43.074657 ], [ -89.422682, 43.074679 ], [ -89.422651, 43.074705 ], [ -89.422632, 43.074737 ], [ -89.422629, 43.074793 ], [ -89.422629, 43.074896 ], [ -89.422632, 43.075334 ], [ -89.422633, 43.07544 ], [ -89.423663, 43.075572 ], [ -89.423288, 43.07557 ], [ -89.423266, 43.076513 ], [ -89.421675, 43.076501 ], [ -89.42163, 43.076766 ], [ -89.421501, 43.07743 ], [ -89.42141, 43.07775 ], [ -89.421374, 43.07786 ], [ -89.421203, 43.077881 ] ], [ [ -89.421529, 43.0765 ], [ -89.421675, 43.076501 ], [ -89.421708, 43.076305 ], [ -89.421824, 43.075744 ], [ -89.421841, 43.075655 ], [ -89.421885, 43.075422 ], [ -89.421915, 43.075166 ], [ -89.421979, 43.074976 ], [ -89.422053, 43.074801 ], [ -89.422107, 43.074698 ], [ -89.422282, 43.074491 ], [ -89.422406, 43.074367 ], [ -89.422775, 43.074083 ], [ -89.422954, 43.073879 ], [ -89.422478, 43.074194 ], [ -89.422071, 43.074542 ], [ -89.421897, 43.074823 ], [ -89.421806, 43.075019 ], [ -89.421758, 43.07522 ], [ -89.421743, 43.075532 ], [ -89.421711, 43.075673 ], [ -89.421605, 43.076143 ], [ -89.421529, 43.0765 ] ] ] ] })
        self.assertEqual(expected.relate(districts['1']), SAME_POLYS)
        
        for assignment in assignments:
            actual = districts[assignment.district]
            center = shapely.geometry.Point(graph.nodes[assignment.block]['pos'])
            self.assertTrue(actual.contains(center))
    
    def test_districts_geojson(self):
        districts = {
            'a': shapely.geometry.Point(0, 1).buffer(1),
            'b': shapely.geometry.Point(1, 0).buffer(1),
            }
        
        geojson = polygonize.districts_geojson(districts)
        
        self.assertEqual(geojson['type'], 'FeatureCollection')
        self.assertEqual(len(geojson['features']), 2)
        self.assertEqual(geojson['features'][0]['properties']['district'], 'a')
        self.assertEqual(geojson['features'][1]['properties']['district'], 'b')
        self.assertEqual(geojson['features'][0]['geometry']['type'], 'Polygon')
        self.assertEqual(geojson['features'][1]['geometry']['type'], 'Polygon')
    
    def test_polygonize_assignment2(self):
        graph = networkx.read_gpickle(os.path.join(TESTS_DATA, 'madison3.pickle'))
        
        assignments = [
            polygonize.Assignment('550250011011015', '1'),
            polygonize.Assignment('550250011011014', '1'),
            polygonize.Assignment('550250011011017', '1'),
            polygonize.Assignment('550250011011018', '2'),
            polygonize.Assignment('550250011011019', '2'),
            polygonize.Assignment('550250011011016', '2'),
            ]
        
        districts = polygonize.polygonize_assignment(assignments, graph)
        
        self.assertEqual(len(districts), 2)
        self.assertIn('1', districts)
        self.assertIn('2', districts)
        self.assertEqual(len(districts['1'].interiors), 0)
        self.assertEqual(len(districts['2'].interiors), 0)
        self.assertTrue(districts['1'].touches(districts['2']))
        
        for assignment in assignments:
            actual = districts[assignment.district]
            center = shapely.geometry.Point(graph.nodes[assignment.block]['pos'])
            self.assertTrue(actual.contains(center))
    
    def test_polygonize_assignment3(self):
        graph = networkx.read_gpickle(os.path.join(TESTS_DATA, 'madison3.pickle'))
        
        assignments = [
            polygonize.Assignment('550250011011014', '1'),
            polygonize.Assignment('550250011011015', '1'),
            polygonize.Assignment('550250011011016', '2'),
            polygonize.Assignment('550250011011017', '2'),
            polygonize.Assignment('550250011011018', '3'),
            polygonize.Assignment('550250011011019', '3'),
            ]
        
        districts = polygonize.polygonize_assignment(assignments, graph)
        
        self.assertEqual(len(districts), 3)
        self.assertIn('1', districts)
        self.assertIn('2', districts)
        self.assertIn('3', districts)
        self.assertEqual(len(districts['1'].interiors), 0)
        self.assertEqual(len(districts['2'].interiors), 0)
        self.assertEqual(len(districts['3'].interiors), 0)
        self.assertTrue(districts['1'].touches(districts['2']))
        self.assertTrue(districts['2'].touches(districts['3']))
        self.assertFalse(districts['3'].touches(districts['1']))
        
        for assignment in assignments:
            actual = districts[assignment.district]
            center = shapely.geometry.Point(graph.nodes[assignment.block]['pos'])
            self.assertTrue(actual.contains(center))
