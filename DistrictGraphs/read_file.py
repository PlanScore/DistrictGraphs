import csv, io, os, json, tempfile, time
import functools
import boto3
import botocore.exceptions
import networkx
from . import constants, polygonize, util, build_district

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
    layer = event['queryStringParameters'].get('layer', 'tabblock')
    assignments_path = event['queryStringParameters']['filepath']
    assignments_dir = os.path.dirname(assignments_path)
    
    s3 = boto3.client('s3', endpoint_url=constants.S3_ENDPOINT_URL)
    object = s3.get_object(Bucket='districtgraphs', Key=assignments_path)
    assignments = polygonize.parse_assignments(object['Body'])
    
    district_ids = {assignment.district for assignment in assignments}

    lam = boto3.client('lambda', endpoint_url=constants.LAMBDA_ENDPOINT_URL)
    for district_id in district_ids:
        print('Invoking', build_district.FUNCTION_NAME, 'for', district_id)
        lam.invoke(FunctionName=build_district.FUNCTION_NAME, InvocationType='Event',
            Payload=json.dumps({'key': assignments_path, 'district': district_id, 'layer': layer}))
    
    for district_id in district_ids:
        # Wait for one expected tile
        while True:
            expected_wkt = os.path.join(assignments_dir,
                build_district.WKT_FORMAT.format(id=district_id))
            
            try:
                object = s3.get_object(Bucket='districtgraphs', Key=expected_wkt)
            except botocore.exceptions.ClientError:
                # Did not find the expected wkt, wait a little before checking
                print('Did not find', expected_wkt)
                time.sleep(3)
            else:
                # Found the expected wkt, break out of this loop
                print('Found', expected_wkt)
                break

    geojson = {'type': 'Empty'}
    
    geojson_path = os.path.join(assignments_dir, 'districts.geojson')
    
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
