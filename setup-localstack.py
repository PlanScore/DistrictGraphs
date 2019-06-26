#!/usr/bin/env python
import sys, argparse, boto3, glob, socket, posixpath as pp
import os, time, copy
import botocore.exceptions
import deploy

common = dict(
    Runtime='python3.6', Environment=dict(Variables={})
    )

if 'AWS_LAMBDA_DLQ_ARN' in os.environ:
    common.update(DeadLetterConfig=dict(TargetArn=os.environ['AWS_LAMBDA_DLQ_ARN']))

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

function_arn1 = deploy.publish_function(lam, 'DistrictGraphs-upload_file', CODE_PATH, env, 'nobody')
function_arn2 = deploy.publish_function(lam, 'DistrictGraphs-read_file', CODE_PATH, env, 'nobody')

# API Gateway setup

print('--> Set up API Gateway', ENDPOINT_API)
api = boto3.client('apigateway', endpoint_url=ENDPOINT_API, region_name='us-east-1', **AWS_CREDS)

deploy.publish_api(api, 'DistrictGraphs', function_arn1, 'DistrictGraphs-upload_file', 'Nobody')
deploy.publish_api(api, 'DistrictGraphs', function_arn2, 'DistrictGraphs-read_file', 'Nobody')

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
