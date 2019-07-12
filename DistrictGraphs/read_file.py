import os, json
import boto3, itsdangerous
from . import constants, polygonize, build_plan

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

    # get assignments unique token
    # get current status
    # when status token matches unique token and:
    #   ...status is "started": update progress, write status, respond
    #   ...status is "finished": respond with redirect to status results
    # otherwise:
    #   - start building districts
    #   - set status to "started", write status
    
    s3 = boto3.client('s3', endpoint_url=constants.S3_ENDPOINT_URL)
    lam = boto3.client('lambda', endpoint_url=constants.LAMBDA_ENDPOINT_URL)
    token = build_plan.get_token(s3, 'districtgraphs', assignments_path, layer)
    status = build_plan.get_status(s3, 'districtgraphs', assignments_dir)
    
    if status.token != token and token is not None:
        object = s3.get_object(Bucket='districtgraphs', Key=assignments_path)
        assignments = polygonize.parse_assignments(object['Body'])
        
        status = build_plan.Status(token, build_plan.STATUS_STARTED,
            list({a.district for a in assignments}), None)

        build_plan.fan_out_build_district(lam, assignments_path, status.district_ids, layer)
        build_plan.put_status(s3, 'districtgraphs', assignments_dir, status)
    
    if status.state == build_plan.STATUS_STARTED:
        expected = len(status.district_ids)
        finished = build_plan.count_finished_districts(s3,
            'districtgraphs', assignments_dir, status.district_ids)

        if finished != expected:
            return {
                'statusCode': '200',
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(status.to_dict())
                }
        
        geojson_path = build_plan.put_plan_geojson(s3,
            'districtgraphs', assignments_dir, status.district_ids)
        
        status.state = build_plan.STATUS_COMPLETE
        status.geojson_url = constants.S3_URL_PATTERN.format(b='districtgraphs', k=geojson_path)
        build_plan.put_status(s3, 'districtgraphs', assignments_dir, status)

    if status.state == build_plan.STATUS_COMPLETE:
        return {
            'statusCode': '200',
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(status.to_dict())
            }

    return {
        'statusCode': '500',
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(dict(error=True))
        }
