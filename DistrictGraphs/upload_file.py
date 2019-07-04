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
    filename = event['queryStringParameters']['filename']
    key = 'assignments/{0}/{1}'.format(identifier, filename)

    signer = itsdangerous.Signer(constants.SECRET)
    filepath_signed = signer.sign(key.encode('utf8')).decode('utf8')
    query = urllib.parse.urlencode({'filepath': filepath_signed})
    
    url1 = s3.generate_presigned_url(ClientMethod='put_object', HttpMethod='PUT',
            Params={'Bucket': 'districtgraphs', 'Key': key})
    
    url2 = urllib.parse.urljoin(util.event_url(event), f'read_file?{query}{{&layer}}')
    
    body = {
        'put_file_url': url1,
        'read_file_url': url2,
        'event': event,
        }

    return {
        'statusCode': '200',
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': json.dumps(body, indent=2)
        }
