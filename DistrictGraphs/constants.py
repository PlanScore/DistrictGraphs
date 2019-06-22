import os, socket, urllib.parse

def _local_url(port):
    ''' Generate a local URL with a given port number.
        
        Host addresses will be different from localhost or 127.0.0.1, so that
        localstack S3 can be accessible from localstack Lambda in Docker.
    '''
    host_address = socket.gethostbyname(socket.gethostname())
    return 'http://{}:{}'.format(host_address, port)

# Signing secret for securing redirects between front-end and back-end.
SECRET = os.environ.get('DGRAPHS_SECRET', 'fake')

# AWS endpoint URLs, used when running under localstack.
#
# Set AWS='amazonaws.com' so that these are set to None: in production,
# boto3 will use its own values for endpoint URLs. When developing locally,
# these might be set to values like 'http://127.0.0.1:4572/' for use with
# localstack mock services. See also setup-localstack.py.

S3_ENDPOINT_URL = os.environ.get('S3_ENDPOINT_URL', _local_url(4572))
GATEWAY_ENDPOINT_URL = os.environ.get('GATEWAY_ENDPOINT_URL', _local_url(4567))
LAMBDA_ENDPOINT_URL = os.environ.get('LAMBDA_ENDPOINT_URL', _local_url(4574))
S3_URL_PATTERN = urllib.parse.urljoin(S3_ENDPOINT_URL, '/{b}/{k}')

if os.environ.get('AWS') == 'amazonaws.com':
    S3_ENDPOINT_URL, GATEWAY_ENDPOINT_URL, LAMBDA_ENDPOINT_URL = None, None, None
    S3_URL_PATTERN = 'https://{b}.s3.amazonaws.com/{k}'
