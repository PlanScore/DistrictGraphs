import csv, io, os
import boto3
import networkx
import itsdangerous
from . import constants, polygonize

def lambda_handler(event, context):
    '''
    '''
    signature = event['queryStringParameters']['signature']
    id = itsdangerous.Signer(constants.SECRET).unsign(signature).decode('utf8')
    
    s3 = boto3.client('s3', endpoint_url=constants.S3_ENDPOINT_URL)
    object = s3.get_object(Bucket='districtgraphs', Key=id)
    assignments = polygonize.parse_assignments(object['Body'])
    
    path = os.path.join(os.path.dirname(__file__), 'tests/data/madison3.pickle')
    graph = networkx.read_gpickle(path)
    districts = polygonize.polygonize_assignment(assignments, graph)
    geojson = polygonize.districts_geojson(districts)
    
    return {
        'statusCode': '200',
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json',
            },
        'body': geojson
        }
