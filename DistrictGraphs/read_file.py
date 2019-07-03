import csv, io, os, json
import urllib.parse
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
    obj2 = s3.get_object(Bucket='districtgraphs', Key='graphs/55/55025-tabblock.pickle')
    with open('/tmp/pickle.pickle', 'wb') as file:
        file.write(obj2['Body'].read())
    graph = networkx.read_gpickle('/tmp/pickle.pickle')
    districts = polygonize.polygonize_assignment(assignments, graph)
    geojson = polygonize.districts_geojson(districts)
    
    s3.put_object(Bucket='districtgraphs', Key=f'{id}.geojson',
        ACL='public-read', ContentType='application/json',
        Body=json.dumps(geojson).encode('utf8'),
        )
    
    url = urllib.parse.urljoin(constants.S3_ENDPOINT_URL, f'/districtgraphs/{id}.geojson')
    
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
