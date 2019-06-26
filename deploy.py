#!/usr/bin/env python
import sys, argparse, boto3, os, copy, time
import botocore.exceptions

common = dict(
    Runtime='python3.6', Environment=dict(Variables={})
    )

if 'AWS_LAMBDA_DLQ_ARN' in os.environ:
    common.update(DeadLetterConfig=dict(TargetArn=os.environ['AWS_LAMBDA_DLQ_ARN']))

functions = {
    'DistrictGraphs-upload_file': dict(Handler='lambda.upload_file', Timeout=3, **common),
    'DistrictGraphs-read_file': dict(Handler='lambda.read_file', Timeout=300, MemorySize=2048, **common),
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
    print('    * done with {} in {:.1f} seconds'.format(arn, time.time() - start_time), file=sys.stderr)
    
    return arn

def publish_api(api, api_name, function_arn, path, role):
    '''
    '''
    try:
        print('    * get API', api_name, file=sys.stderr)
        rest_api = [item for item in api.get_rest_apis()['items']
            if item['name'] == api_name][0]
    except:
        print('    * create API', api_name, file=sys.stderr)
        rest_api = api.create_rest_api(name=api_name)
    finally:
        rest_api_id = rest_api['id']
        api_kwargs = dict(restApiId=rest_api_id,
            parentId=api.get_resources(restApiId=rest_api_id)['items'][0]['id'])

    try:
        print('    * get resource', rest_api_id, path, file=sys.stderr)
        resource = [item for item in api.get_resources(restApiId=rest_api_id)['items']
            if item['path'] == f'/{path}'][0]
    except:
        print('    * create resource', rest_api_id, path, file=sys.stderr)
        resource = api.create_resource(pathPart=path, **api_kwargs)
    finally:
        api_kwargs = dict(restApiId=rest_api_id, resourceId=resource['id'])
    
    try:
        print('    * put method', rest_api_id, 'GET', path, file=sys.stderr)
        api.put_method(httpMethod='GET', authorizationType='NONE', 
            requestParameters={'method.request.querystring.filename': True},
            **api_kwargs)
    except:
        print('    * method exists?', rest_api_id, 'GET', path, file=sys.stderr)

    print('    * put integration', rest_api_id, 'GET', path, file=sys.stderr)
    api.put_integration(httpMethod='GET', type='AWS_PROXY', credentials=role,
        integrationHttpMethod='POST', passthroughBehavior='WHEN_NO_MATCH',
        uri=f'arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{function_arn}/invocations',
        #requestParameters={'integration.request.querystring.filename': 'method.request.querystring.filename'},
        **api_kwargs)

    print('    * create deployment', rest_api_id, 'test', file=sys.stderr)
    api.create_deployment(stageName='test', restApiId=rest_api_id)

    print('    * done with', f'{api._endpoint.host}/restapis/{rest_api_id}/test/_user_request_/{path}')

parser = argparse.ArgumentParser(description='Update Lambda function.')
parser.add_argument('path', help='Function code path')
parser.add_argument('name', help='Function name')

if __name__ == '__main__':
    args = parser.parse_args()
    env = {k: os.environ[k]
        for k in ('DGRAPHS_SECRET', 'AWS')
        if k in os.environ}
    
    lam = boto3.client('lambda', region_name='us-east-1')
    api = boto3.client('apigateway', region_name='us-east-1')
    role = os.environ.get('AWS_IAM_ROLE')
    arn = publish_function(lam, args.name, args.path, env, role)
    publish_api(api, 'DistrictGraphs', arn, args.name.split('-')[-1], role)
