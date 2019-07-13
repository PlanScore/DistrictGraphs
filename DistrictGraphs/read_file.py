import os, json
import boto3, itsdangerous
from . import constants, build_plan

def extract_signed_upload(secret, upload_signed):
    ''' 
    '''
    signer = itsdangerous.Signer(secret)
    upload_path = signer.unsign(upload_signed).decode('utf8')
    layer, assignments_path = upload_path.split(':', 1)

    return layer, assignments_path

def lambda_handler(event, context):
    '''
    '''
    upload_signed = event['queryStringParameters']['upload']
    layer, assignments_path = extract_signed_upload(constants.SECRET, upload_signed)
    assignments_dir = os.path.dirname(assignments_path)

    s3 = boto3.client('s3', endpoint_url=constants.S3_ENDPOINT_URL)
    lam = boto3.client('lambda', endpoint_url=constants.LAMBDA_ENDPOINT_URL)
    token = build_plan.get_token(s3, 'districtgraphs', assignments_path, layer)

    old_status = build_plan.get_status(s3, 'districtgraphs', assignments_dir)
    new_status = build_plan.read_file(s3, lam, 'districtgraphs',
        old_status, token, layer, assignments_path)
    
    if new_status is None:
        return {
            'statusCode': '500',
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(dict(error=True))
            }

    return {
        'statusCode': '200',
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(new_status.to_dict())
        }
