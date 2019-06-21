import os, boto3, urllib.parse

def lambda_handler(event, context):
    '''
    '''
    ENDPOINT_S3 = os.environ.get('S3_ENDPOINT_URL')
    s3 = boto3.client('s3', endpoint_url=ENDPOINT_S3)
    
    key = 'uploads/{filename}'.format(**event['queryStringParameters'])
    url1 = s3.generate_presigned_url(ClientMethod='put_object', HttpMethod='PUT',
            Params={'Bucket': 'districtgraphs', 'Key': key})
    
    url2 = urllib.parse.urljoin(event['resource'], 'do-the-next-thing')

    return {
        'statusCode': '200',
        'headers': {
            },
        'body': {
            'event': event,
            'url1': url1,
            'url2': url2,
            }
        }
