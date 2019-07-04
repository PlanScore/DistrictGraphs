import csv, io, os, json
import functools
import boto3
import networkx
from . import constants, polygonize, util

def load_graph(s3, bucket, path):
    '''
    '''
    print('Loading', bucket, f'graphs/{path}')

    obj2 = s3.get_object(Bucket=bucket, Key=f'graphs/{path}')

    with open('/tmp/pickle.pickle', 'wb') as file:
        file.write(obj2['Body'].read())

    return networkx.read_gpickle('/tmp/pickle.pickle')

def lambda_handler(event, context):
    '''
    '''
    layer = event['queryStringParameters'].get('layer', 'tabblock')
    assignments_path = event['queryStringParameters']['filepath']
    
    s3 = boto3.client('s3', endpoint_url=constants.S3_ENDPOINT_URL)
    object = s3.get_object(Bucket='districtgraphs', Key=assignments_path)
    assignments = polygonize.parse_assignments(object['Body'])
    
    graph_paths = polygonize.get_county_graph_paths(layer, assignments)
    graphs = [load_graph(s3, 'districtgraphs', path) for path in graph_paths]
    graph = functools.reduce(util.combine_digraphs, graphs)
    districts = polygonize.polygonize_assignment(assignments, graph)
    geojson = polygonize.districts_geojson(districts)
    
    geojson_path = os.path.join(os.path.dirname(assignments_path), 'districts.geojson')
    
    s3.put_object(Bucket='districtgraphs', Key=geojson_path,
        ACL='public-read', ContentType='application/json',
        Body=json.dumps(geojson).encode('utf8'),
        )
    
    geojson_url = constants.S3_URL_PATTERN.format(b='districtgraphs', k=geojson_path)
    
    return {
        'statusCode': '200',
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json',
            },
        'body': json.dumps({
            'geojson_url': geojson_url,
            })
        }
