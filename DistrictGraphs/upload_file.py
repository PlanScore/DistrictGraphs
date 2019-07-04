import urllib.parse, json
import boto3, itsdangerous
from . import constants, util

def lambda_handler(event, context):
    '''
    '''
    s3 = boto3.client('s3', endpoint_url=constants.S3_ENDPOINT_URL)
    
    key = 'uploads/{0}'.format(event['queryStringParameters']['filename'])
    signer = itsdangerous.Signer(constants.SECRET)
    signature = signer.sign(key.encode('utf8')).decode('utf8')
    query = urllib.parse.urlencode({'signature': signature})
    
    url1 = s3.generate_presigned_url(ClientMethod='put_object', HttpMethod='PUT',
            Params={'Bucket': 'districtgraphs', 'Key': key})
    
    url2 = urllib.parse.urljoin(util.event_url(event), f'read_file?{query}{{&layer}}')
    
    body = {
        'put_file_href': url1,
        'read_file_href': url2,
        'event': event,
        }

    return {
        'statusCode': '200',
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': json.dumps(body, indent=2)
        }
