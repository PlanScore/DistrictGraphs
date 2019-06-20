import os, networkx, shapely.geometry, shapely.ops, boto3, io, time, gzip

def lambda_handler(event, context):
    '''
    '''
    start_time = time.time()
    ENDPOINT_S3 = os.environ.get('S3_ENDPOINT_URL')
    s3 = boto3.client('s3', endpoint_url=ENDPOINT_S3)
    
    #obj = s3.get_object(Bucket='districtgraphs', Key='graphs/tl_2018_55_tabblock10.shp.pickle.gz')
    #body = io.BytesIO(gzip.decompress(obj['Body'].read()))
    obj = s3.get_object(Bucket='districtgraphs', Key='graphs/madison3.pickle')
    body = io.BytesIO(obj['Body'].read())
    graph = networkx.read_gpickle(body)
    graph_read_time = time.time() - start_time
    
    return {
        'statusCode': '200',
        'headers': {
            'X-Remaining-Time': str(context and context.get_remaining_time_in_millis()),
            'X-Memory-Limit': str(context and context.memory_limit_in_mb),
            'X-Graph-File-Size': str(obj['ContentLength']),
            'X-Graph-Read-Time': f'{graph_read_time:.3f} seconds',
            'X-Graph-Node-Count': str(len(graph.nodes)),
            'X-Graph-Edge-Count': str(len(graph.edges)),
            },
        'body': {
            'event': event,
            'graph': {
                'file_size': obj['ContentLength'],
                'read_time': round(graph_read_time, 3),
                'node_count': len(graph.nodes),
                'edge_count': len(graph.edges),
                }
            }
        }
    
    dirpath = os.path.join(os.path.dirname(__file__), 'tests', 'data')
    G = networkx.read_gpickle(os.path.join(dirpath, 'madison3.pickle'))

    assignments = [
        '550250016062005', # <-- inside
        '550250016063000', '550250016062004', '550250016063003',
        '550250016062003', '550250016062002', '550250016051003', '550250016051004',
        '550250012001003', # <-- hole
        '550250032001014', '550250011022006' # <-- corner-touch pair
        ]

    boundary = list(networkx.algorithms.boundary.edge_boundary(G, assignments))
    
    print(boundary)
    
    boundary_nodes = {geoid for (geoid, _) in boundary if geoid in G.nodes}
    
    print(boundary_nodes)
    
    multipoint = shapely.geometry.MultiPoint([(G.nodes[geoid]['pos'])
        for geoid in boundary_nodes])
    
    print(multipoint)
    
    lines = [G.edges[(g1, g2)]['line'] for (g1, g2) in boundary]
    
    print(lines)
    
    district_polygons = [poly for poly in shapely.ops.polygonize(lines)
        if poly.relate_pattern(multipoint, '0********')]
    
    print(district_polygons)
    
    return {
        'statusCode': '200',
        'headers': {
            'X-Remaining-Time': str(context and context.get_remaining_time_in_millis()),
            'X-Memory-Limit': str(context and context.memory_limit_in_mb),
            },
        'body': {
            'type': 'FeatureCollection',
            'features': [{
                    'type': 'Feature', 'properties': {},
                    'geometry': shapely.geometry.mapping(poly),
                    }
                for poly in district_polygons
                ]
            }
        }

def main():
    return lambda_handler(None, None)