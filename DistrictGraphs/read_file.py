import csv, io, os, json
import functools
import boto3
import networkx
import itsdangerous
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
    signed_filepath = event['queryStringParameters']['filepath']
    filepath = itsdangerous.Signer(constants.SECRET).unsign(signed_filepath).decode('utf8')
    
    s3 = boto3.client('s3', endpoint_url=constants.S3_ENDPOINT_URL)
    object = s3.get_object(Bucket='districtgraphs', Key=filepath)
    assignments = polygonize.parse_assignments(object['Body'])
    
    graph_paths = polygonize.get_county_graph_paths(layer, assignments)
    graphs = [load_graph(s3, 'districtgraphs', path) for path in graph_paths]
    graph = functools.reduce(util.combine_digraphs, graphs)
    districts = polygonize.polygonize_assignment(assignments, graph)
    geojson = polygonize.districts_geojson(districts)
    
    s3.put_object(Bucket='districtgraphs', Key=f'{filepath}.geojson',
        ACL='public-read', ContentType='application/json',
        Body=json.dumps(geojson).encode('utf8'),
        )
    
    url = constants.S3_URL_PATTERN.format(b='districtgraphs', k=f'{filepath}.geojson')
    
    return {
        'statusCode': '200',
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json',
            },
        'body': json.dumps({
            'url': url,
            })
        }
