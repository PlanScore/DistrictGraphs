import logging
import collections
import networkx
import shapely

logger = logging.getLogger(__name__)

def polygonize_assignment(assignments, graph):
    '''
    '''
    district_nodes = collections.defaultdict(list)
    district_polys = dict()
    
    for (node_id, district_id) in assignments:
        district_nodes[district_id].append(node_id)
    
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
