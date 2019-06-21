#!/usr/bin/env python
import sys, argparse, boto3, glob, socket, posixpath as pp
import os, time, copy
import botocore.exceptions

common = dict(
    Runtime='python3.6', Environment=dict(Variables={})
    )

if 'AWS_LAMBDA_DLQ_ARN' in os.environ:
    common.update(DeadLetterConfig=dict(TargetArn=os.environ['AWS_LAMBDA_DLQ_ARN']))

functions = {
    'DistrictGraphs-dwim': dict(Handler='lambda.dwim', Timeout=300, MemorySize=2048, **common),
    'DistrictGraphs-upload_url': dict(Handler='lambda.upload_url', Timeout=300, MemorySize=2048, **common),
    }

def publish_function(lam, name, path, env, role):
    ''' Create or update the named function to Lambda, return its ARN.
    '''
    start_time = time.time()
    function_kwargs = copy.deepcopy(functions[name])
    function_kwargs['Environment']['Variables'].update(env)
    
    if role is not None:
        function_kwargs.update(Role=role)

    with open(path, 'rb') as code_file:
        code_bytes = code_file.read()

    try:
        print('    * get function', name, file=sys.stderr)
        lam.get_function(FunctionName=name)
    except botocore.exceptions.ClientError:
        # Function does not exist, create it
        print('    * create function', name, file=sys.stderr)
        lam.create_function(FunctionName=name, Code=dict(ZipFile=code_bytes), **function_kwargs)
    else:
        # Function exists, update it
        print('    * update function code', name, file=sys.stderr)
        lam.update_function_code(FunctionName=name, ZipFile=code_bytes)
        print('    * update function configuration', name, file=sys.stderr)
        lam.update_function_configuration(FunctionName=name, **function_kwargs)
    
    arn = lam.get_function_configuration(FunctionName=name).get('FunctionArn')
    print('      done with {} in {:.1f} seconds'.format(arn, time.time() - start_time), file=sys.stderr)
    
    return arn

parser = argparse.ArgumentParser(description='Set up localstack environment.')
parser.add_argument('code_path', help='Path to Lambda code zip file')
arguments = parser.parse_args()

# Names of things

host_address = socket.gethostbyname(socket.gethostname())

BUCKETNAME = 'districtgraphs' # 'planscore'
ENDPOINT_S3 = 'http://{}:4572'.format(host_address)
ENDPOINT_LAM = 'http://{}:4574'.format(host_address)
ENDPOINT_API = 'http://{}:4567'.format(host_address)
AWS_CREDS = dict(aws_access_key_id='nobody', aws_secret_access_key='nothing')
CODE_PATH = arguments.code_path

# Lambda function setup

print('--> Set up Lambda', ENDPOINT_LAM)
lam = boto3.client('lambda', endpoint_url=ENDPOINT_LAM, region_name='us-east-1', **AWS_CREDS)

env = {
    'S3_ENDPOINT_URL': ENDPOINT_S3,
    'LAMBDA_ENDPOINT_URL': ENDPOINT_LAM,
    }

print('    Environment:', ' '.join(['='.join(kv) for kv in env.items()]))

function_arn = publish_function(lam, 'DistrictGraphs-upload_url', CODE_PATH, env, 'nobody')

# API Gateway setup

print('--> Set up API Gateway', ENDPOINT_API)
api = boto3.client('apigateway', endpoint_url=ENDPOINT_API, region_name='us-east-1', **AWS_CREDS)

rest_api_id = api.create_rest_api(name='DistrictGraphs')['id']
parent_id = api.get_resources(restApiId=rest_api_id)['items'][0]['id']
api_kwargs = dict(restApiId=rest_api_id, parentId=parent_id)

resource_id = api.create_resource(pathPart='upload_url', **api_kwargs)['id']
api_kwargs = dict(restApiId=rest_api_id, resourceId=resource_id)
print('    Args:', api_kwargs)

api.put_method(httpMethod='GET', authorizationType='NONE', 
    requestParameters={'method.request.querystring.filename': True},
    **api_kwargs)
api.put_integration(httpMethod='GET', type='AWS_PROXY',
    integrationHttpMethod='POST', passthroughBehavior='WHEN_NO_MATCH',
    uri=f'arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{function_arn}/invocations',
    #requestParameters={'integration.request.querystring.filename': 'method.request.querystring.filename'},
    **api_kwargs)
api.create_deployment(stageName='test', restApiId=rest_api_id)

print('    URL:', f'http://localhost:4567/restapis/{rest_api_id}/test/_user_request_/upload_url')

# S3 Bucket setup

print('--> Set up S3', ENDPOINT_S3)
s3 = boto3.client('s3', endpoint_url=ENDPOINT_S3, **AWS_CREDS)

print('    Create bucket', BUCKETNAME)
s3.create_bucket(Bucket=BUCKETNAME)

with open('madison3.pickle', 'rb') as file:
    print(f'    Put object graphs/{file.name}')
    data = file.read()
    s3.put_object(Bucket=BUCKETNAME, Key=f'graphs/{file.name}',
        ACL='public-read', Body=data, ContentType='application/binary')

exit()

with open('tl_2018_55_tabblock10.shp.pickle.gz', 'rb') as file:
    print(f'    Put object graphs/{file.name}')
    data = file.read()
    s3.put_object(Bucket=BUCKETNAME, Key=f'graphs/{file.name}',
        ACL='public-read', Body=data, ContentType='application/binary',
        ContentEncoding='gzip')

exit()

prefix1 = pp.join('data', 'XX', '001')
basedir1 = pp.join(pp.dirname(__file__), 'planscore', 'tests', 'data', 'XX')

upload(prefix1, basedir1, pp.join(basedir1, '12', '*', '*.geojson'))

prefix2 = pp.join('uploads', 'sample-NC-1-992')
basedir2 = pp.join(pp.dirname(__file__), 'data', 'sample-NC-1-992')

upload(prefix2, basedir2, pp.join(basedir2, '*.*'))
upload(prefix2, basedir2, pp.join(basedir2, '*', '*.*'))

prefix3 = pp.join('uploads', 'sample-NC-1-992-simple')
basedir3 = pp.join(pp.dirname(__file__), 'data', 'sample-NC-1-992-simple')

upload(prefix3, basedir3, pp.join(basedir3, '*.*'))
upload(prefix3, basedir3, pp.join(basedir3, '*', '*.*'))

prefix4 = pp.join('uploads', 'sample-NC-1-992-incomplete')
basedir4 = pp.join(pp.dirname(__file__), 'data', 'sample-NC-1-992-incomplete')

upload(prefix4, basedir4, pp.join(basedir4, '*.*'))

prefix5 = pp.join('data', 'XX', '003')
basedir5 = pp.join(pp.dirname(__file__), 'planscore', 'tests', 'data', 'XX-sim')

upload(prefix5, basedir5, pp.join(basedir5, '12', '*', '*.geojson'))

prefix6 = pp.join('uploads', 'sample-NC5.1')
basedir6 = pp.join(pp.dirname(__file__), 'data', 'sample-NC5.1')

upload(prefix6, basedir6, pp.join(basedir6, '*.*'))
upload(prefix6, basedir6, pp.join(basedir6, '*', '*.*'))

# Lambda function setup

print('--> Set up Lambda', ENDPOINT_LAM)
lam = boto3.client('lambda', endpoint_url=ENDPOINT_LAM, region_name='us-east-1', **AWS_CREDS)

env = {
    'PLANSCORE_SECRET': 'localstack',
    'WEBSITE_BASE': 'http://127.0.0.1:5000/',
    'S3_ENDPOINT_URL': ENDPOINT_S3,
    'LAMBDA_ENDPOINT_URL': ENDPOINT_LAM,
    }

print('    Environment:', ' '.join(['='.join(kv) for kv in env.items()]))

for function_name in deploy.functions.keys():
    deploy.publish_function(lam, function_name, CODE_PATH, env, 'nobody')
