import logging
import io
import csv
import collections
import networkx
import shapely

logger = logging.getLogger(__name__)

Assignment = collections.namedtuple('Assignment', ('block', 'district'))

def parse_assignments(file):
    '''
    '''
    rows = csv.reader(io.StringIO(file.read().decode('utf8')))
    head = next(rows)

    block_i, district_i = None, None

    for (index, value) in enumerate(head):
        if value.lower() in ('id', 'geoid', 'geoid10'):
            block_i = index
        if value.lower() in ('district', 'district_id'):
            district_i = index
    
    if block_i is not None and district_i is not None:
        return [Assignment(row[block_i], row[district_i]) for row in rows]
    
    if block_i is None and district_i is None:
        return [Assignment(head[0], head[1])] \
             + [Assignment(row[0], row[1]) for row in rows]
    
    raise ValueError('Mixed signals in assignments file')

def districts_geojson(districts):
    '''
    '''
    features = [{
        'type': 'Feature',
        'properties': {'district': district_id},
        'geometry': shapely.geometry.mapping(geometry),
        } for (district_id, geometry) in districts.items()]
    geojson = {
        'type': 'FeatureCollection',
        'features': features,
        }
    return geojson

def get_county_graph_paths(layer, assignments):
    '''
    '''
    paths = set()
    
    for assignment in assignments:
        state_fips, county_fips = assignment.block[:2], assignment.block[:5]
        paths.add(f'{state_fips}/{county_fips}-{layer}.pickle')
    
    return paths

def polygonize_assignment(assignments, graph):
    '''
    '''
    district_nodes = collections.defaultdict(list)
    district_polys = dict()
    
    for assignment in assignments:
        district_nodes[assignment.district].append(assignment.block)
    
    for (district_id, node_ids) in district_nodes.items():
        multipoint = shapely.geometry.MultiPoint([graph.node[id]['pos'] for id in node_ids])
        logger.debug(f'{district_id} multipoint: {multipoint}')
    
        boundary = list(networkx.algorithms.boundary.edge_boundary(graph, node_ids))
        logger.debug(f'{district_id} boundary: {boundary}')
    
        lines = [graph.edges[(node1, node2)]['line'] for (node1, node2) in boundary]
        logger.debug(f'{district_id} lines: {lines}')
    
        district_polygons = list(shapely.ops.polygonize(lines))
        logger.debug(f'{district_id} district_polygons: {district_polygons}')
    
        polys = [poly for poly in district_polygons
            if poly.relate_pattern(multipoint, '0********')]
        logger.debug(f'{district_id} polys: {polys}')
    
        multipolygon = shapely.ops.cascaded_union(polys)
        logger.debug(f'{district_id} multipolygon: {multipolygon}')
        
        district_polys[district_id] = multipolygon

    return district_polys
