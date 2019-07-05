import csv, io, os, json, tempfile
import functools
import boto3
import networkx
import shapely.wkt
from . import constants, polygonize, util

FUNCTION_NAME = 'DistrictGraphs-build_district'
WKT_FORMAT = 'district-{id}.wkt'

def load_graph(s3, bucket, path):
    '''
    '''
    print('Loading', bucket, f'graphs/{path}')

    obj2 = s3.get_object(Bucket=bucket, Key=f'graphs/{path}')
    
    handle, tmp_path = tempfile.mkstemp(prefix='graph-', suffix='.pickle')
    os.write(handle, obj2['Body'].read())
    os.close(handle)

    return networkx.read_gpickle(tmp_path)

def lambda_handler(event, context):
    '''
    '''
    import sys
    print('build district:', event, file=sys.stderr)
    print('build district...', event, file=sys.stdout)
    
    assignments_path, district_id, layer = event['key'], event['district'], event['layer']
    
    s3 = boto3.client('s3', endpoint_url=constants.S3_ENDPOINT_URL)
    object = s3.get_object(Bucket='districtgraphs', Key=assignments_path)
    all_assignments = polygonize.parse_assignments(object['Body'])
    
    district_assignments = [a for a in all_assignments if a.district == district_id]

    graph_paths = polygonize.get_county_graph_paths(layer, district_assignments)
    graphs = [load_graph(s3, 'districtgraphs', path) for path in graph_paths]
    graph = functools.reduce(util.combine_digraphs, graphs)

    districts = polygonize.polygonize_assignment(district_assignments, graph)
    wkt_path = os.path.join(os.path.dirname(assignments_path), WKT_FORMAT.format(id=district_id))
    geometry = districts[district_id]
    
    s3.put_object(Bucket='districtgraphs', Key=wkt_path,
        ACL='public-read', ContentType='text/plain',
        Body=shapely.wkt.dumps(geometry, rounding_precision=6),
        )
    
    geometry_url = constants.S3_URL_PATTERN.format(b='districtgraphs', k=wkt_path)
    
    return {
        'geometry_url': geometry_url,
        }
