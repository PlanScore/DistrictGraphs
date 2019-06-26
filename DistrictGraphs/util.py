import urllib.parse

def event_url(event):
    '''
    '''
    scheme = event['headers'].get('X-Forwarded-Proto') or 'http'
    host = event['headers']['Host']
    query = urllib.parse.urlencode(event['queryStringParameters'])
    
    # only seems true running at *.execute-api.us-east-1.amazonaws.com
    is_raw_gateway = (event['requestContext'].get('path') != event.get('path'))
    
    if is_raw_gateway:
        path = event['requestContext']['path']
    else:
        path = urllib.parse.urlparse(event.get('resource')).path
    
    return urllib.parse.urlunparse((scheme, host, path, None, query, None))
