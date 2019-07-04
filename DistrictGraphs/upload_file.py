import urllib.parse, json, datetime, random
import boto3, itsdangerous
from . import constants, util

def generate_signed_id(secret):
    ''' Generate a unique ID with a signature.
    
        We want this to include date for sorting, be a valid ISO-8601 datetime,
        and to use a big random number for fake nanosecond accuracy to increase
        likelihood of uniqueness.
    '''
    now, nsec = datetime.datetime.utcnow(), random.randint(0, 999999999)
    identifier = '{}.{:09d}Z'.format(now.strftime('%Y%m%dT%H%M%S'), nsec)
    signer = itsdangerous.Signer(secret)
    return identifier, signer.sign(identifier.encode('utf8')).decode('utf8')

def lambda_handler(event, context):
    '''
    '''
    s3 = boto3.client('s3', endpoint_url=constants.S3_ENDPOINT_URL)
    
    identifier, _ = generate_signed_id(constants.SECRET)
    filepath = f'assignments/{identifier}/assignments'
    query = urllib.parse.urlencode({'filepath': filepath})
    
    put_url = s3.generate_presigned_url(ClientMethod='put_object', HttpMethod='PUT',
        Params={'Bucket': 'districtgraphs', 'Key': filepath})
    
    read_url = urllib.parse.urljoin(util.event_url(event), f'read_file?{query}{{&layer}}')
    
    body = {
        'assignments_url': put_url,
        'districts_url': read_url,
        'event': event,
        }

    return {
        'statusCode': '200',
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': json.dumps(body, indent=2)
        }
