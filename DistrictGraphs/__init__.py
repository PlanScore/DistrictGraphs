import logging, time
import networkx
import shapely.geometry
import geopandas

# DE-9IM pattern for shared boundary between two blocks
CONTIGUOUS = 'F***1****'

# Magic name for the node representing outside a graph
OUTSIDE = 'outside'

def blocks_frame_graph(blocks, geoid):
    ''' Return graph representation of frame.
    
    Include one extra node representing outside the graph.
    '''
    graph = networkx.DiGraph()
    _start_time = time.time()

    # Add a node for each block with full geometry and a representative point
    for (_, block) in blocks.iterrows():
        graph.add_node(block[geoid], geom=block.geometry,
            pos=block.geometry.representative_point().coords[0])

    # Find all pairs of possibly-contiguous blocks
    intersections = geopandas.sjoin(blocks, blocks, how="inner", op='intersects')
    _possibles, _candidates, _connections = blocks.shape[0]**2, 0, 0

    for (id1, block1) in intersections.iterrows():
        _candidates += 1
        geom1, block2 = block1.geometry, blocks.loc[block1.index_right]
        geom2 = block2.geometry
        if geom1.relate_pattern(geom2, CONTIGUOUS):
            # Add an edge for this contiguous pair
            _connections += 1
            graph.add_edge(block1[f'{geoid}_left'], block2[geoid],
                line=shared_linear_boundary(geom1, geom2))
    
    _elapsed, _start_time = time.time() - _start_time, time.time()
    logging.debug(f'Out of {_possibles} possible connections,'
        f' reduced {_candidates} candidates to {_connections} contiguous pairs'
        f' in {_elapsed:.3f} seconds.')

    # Find all nodes that touch the outside
    node_ids = list(graph.nodes)

    for node1_id in node_ids:
        # Start with the complete boundary perimeter
        node1_perimeter = graph.nodes[node1_id]['geom'].boundary
        
        # Subtract portions of the perimeters accounted for by neighbors
        for node2_id in graph.neighbors(node1_id):
            edge_geom = graph.edges[(node1_id, node2_id)]['line']
            node1_perimeter = node1_perimeter.difference(edge_geom)
        
        # If any perimeter remains, it must connect to the outside
        if node1_perimeter.type in ('LineString', 'MultiLineString'):
            graph.add_edge(node1_id, OUTSIDE, line=node1_perimeter)
            graph.add_edge(OUTSIDE, node1_id, line=node1_perimeter)
    
    _elapsed = time.time() - _start_time
    logging.debug(f'Found outside blocks in {_elapsed:.3f} seconds.')

    return graph

def shared_linear_boundary(geom1, geom2):
    ''' Return just the linear parts of a shared boundary.
    '''
    intersection = geom1.intersection(geom2)

    if intersection.type in ('LineString', 'MultiLineString'):
        return intersection

    if intersection.type in ('Point', 'MultiPoint', 'Polygon', 'MultiPolygon'):
        raise ValueError('Bad type {}'.format(intersection.type))

    if intersection.type == 'GeometryCollection':
        types = {geom.type for geom in intersection.geoms}

        if 'Polygon' in types or 'MultiPolygon' in types:
            raise Exception('Type has polygon {}'.format(repr(types)))

        if types == {'Point', 'LineString'}:
            lines = [g for g in intersection.geoms if g.type == 'LineString']
            return shapely.geometry.MultiLineString(lines)

        raise Exception('Bad type {}'.format(intersection.type))
