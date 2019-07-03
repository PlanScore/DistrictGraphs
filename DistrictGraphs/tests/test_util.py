from .. import util

import unittest
import networkx
import json

class TestUtil (unittest.TestCase):
    
    def test_event_url_localstack(self):
        '''
        '''
        event = '''{ "path": "/upload_file", "headers": { "Host": "192.168.42.70:4567", "Connection": "keep-alive", "Cache-Control": "max-age=0", "Upgrade-Insecure-Requests": "1", "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8", "Accept-Encoding": "gzip, deflate", "Accept-Language": "en-US,en;q=0.9", "X-Forwarded-For": "192.168.42.70, 0.0.0.0:4567" }, "pathParameters": {}, "body": null, "isBase64Encoded": false, "resource": "/restapis/0A-Z28229327/test/_user_request_/upload_file?filename=floof", "httpMethod": "GET", "queryStringParameters": { "filename": "floof" }, "requestContext": { "path": "/upload_file", "accountId": "000000000000", "resourceId": "482678141A-Z", "stage": "test", "identity": { "accountId": "000000000000", "sourceIp": "192.168.42.70", "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36" } }, "stageVariables": {} }'''
        url = util.event_url(json.loads(event))
        self.assertEqual(url, 'http://192.168.42.70:4567/restapis/0A-Z28229327/test/_user_request_/upload_file?filename=floof')
    
    def test_event_url_teststage(self):
        '''
        '''
        event = '''{ "resource": "/upload_file", "path": "/upload_file", "httpMethod": "GET", "headers": { "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8", "Accept-Encoding": "gzip, deflate, br", "Accept-Language": "en-US,en;q=0.9", "cache-control": "max-age=0", "CloudFront-Forwarded-Proto": "https", "CloudFront-Is-Desktop-Viewer": "true", "CloudFront-Is-Mobile-Viewer": "false", "CloudFront-Is-SmartTV-Viewer": "false", "CloudFront-Is-Tablet-Viewer": "false", "CloudFront-Viewer-Country": "US", "Host": "ad3b4lkfdc.execute-api.us-east-1.amazonaws.com", "upgrade-insecure-requests": "1", "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36", "Via": "2.0 2cd1423c218193e9646892449fb7844a.cloudfront.net (CloudFront)", "X-Amz-Cf-Id": "SO6oEj_7kLOuK7AhgtM9wLOL6bshyiWtBe9U6Y1SQppRiqPQb7uwWQ==", "X-Amzn-Trace-Id": "Root=1-5d130bdb-c0af7027feb0e5b94f62cc21", "X-Forwarded-For": "70.36.235.225, 70.132.18.144", "X-Forwarded-Port": "443", "X-Forwarded-Proto": "https" }, "multiValueHeaders": { "Accept": [ "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8" ], "Accept-Encoding": [ "gzip, deflate, br" ], "Accept-Language": [ "en-US,en;q=0.9" ], "cache-control": [ "max-age=0" ], "CloudFront-Forwarded-Proto": [ "https" ], "CloudFront-Is-Desktop-Viewer": [ "true" ], "CloudFront-Is-Mobile-Viewer": [ "false" ], "CloudFront-Is-SmartTV-Viewer": [ "false" ], "CloudFront-Is-Tablet-Viewer": [ "false" ], "CloudFront-Viewer-Country": [ "US" ], "Host": [ "ad3b4lkfdc.execute-api.us-east-1.amazonaws.com" ], "upgrade-insecure-requests": [ "1" ], "User-Agent": [ "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36" ], "Via": [ "2.0 2cd1423c218193e9646892449fb7844a.cloudfront.net (CloudFront)" ], "X-Amz-Cf-Id": [ "SO6oEj_7kLOuK7AhgtM9wLOL6bshyiWtBe9U6Y1SQppRiqPQb7uwWQ==" ], "X-Amzn-Trace-Id": [ "Root=1-5d130bdb-c0af7027feb0e5b94f62cc21" ], "X-Forwarded-For": [ "70.36.235.225, 70.132.18.144" ], "X-Forwarded-Port": [ "443" ], "X-Forwarded-Proto": [ "https" ] }, "queryStringParameters": { "filename": "floof" }, "multiValueQueryStringParameters": { "filename": [ "floof" ] }, "pathParameters": null, "stageVariables": null, "requestContext": { "resourceId": "905w5w", "resourcePath": "/upload_file", "httpMethod": "GET", "extendedRequestId": "b37KWE-qoAMF9oA=", "requestTime": "26/Jun/2019:06:08:27 +0000", "path": "/test/upload_file", "accountId": "101696101272", "protocol": "HTTP/1.1", "stage": "test", "domainPrefix": "ad3b4lkfdc", "requestTimeEpoch": 1561529307873, "requestId": "d0868ed0-97d8-11e9-bfac-97a2bc660746", "identity": { "cognitoIdentityPoolId": null, "accountId": null, "cognitoIdentityId": null, "caller": null, "sourceIp": "70.36.235.225", "principalOrgId": null, "accessKey": null, "cognitoAuthenticationType": null, "cognitoAuthenticationProvider": null, "userArn": null, "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36", "user": null }, "domainName": "ad3b4lkfdc.execute-api.us-east-1.amazonaws.com", "apiId": "ad3b4lkfdc" }, "body": null, "isBase64Encoded": false }'''
        url = util.event_url(json.loads(event))
        self.assertEqual(url, 'https://ad3b4lkfdc.execute-api.us-east-1.amazonaws.com/test/upload_file?filename=floof')
    
    def test_event_url_livedomain(self):
        '''
        '''
        event = '''{ "resource": "/upload_file", "path": "/upload_file", "httpMethod": "GET", "headers": { "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8", "Accept-Encoding": "gzip, deflate, br", "Accept-Language": "en-US,en;q=0.9", "cache-control": "max-age=0", "CloudFront-Forwarded-Proto": "https", "CloudFront-Is-Desktop-Viewer": "true", "CloudFront-Is-Mobile-Viewer": "false", "CloudFront-Is-SmartTV-Viewer": "false", "CloudFront-Is-Tablet-Viewer": "false", "CloudFront-Viewer-Country": "US", "Cookie": "_ga=GA1.2.476562506.1508302986", "Host": "dgraphs.example.com", "upgrade-insecure-requests": "1", "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36", "Via": "2.0 05aec04162b0fed6e9762cd1edd66a72.cloudfront.net (CloudFront)", "X-Amz-Cf-Id": "0WIyvSNpjbRatxNZyMLlRHavJLf8FACh5XCUbWtsaKSuw97T4LmO4g==", "X-Amzn-Trace-Id": "Root=1-5d145415-104877631845dde42c69f241", "X-Forwarded-For": "70.36.235.225, 70.132.18.149", "X-Forwarded-Port": "443", "X-Forwarded-Proto": "https" }, "multiValueHeaders": { "Accept": [ "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8" ], "Accept-Encoding": [ "gzip, deflate, br" ], "Accept-Language": [ "en-US,en;q=0.9" ], "cache-control": [ "max-age=0" ], "CloudFront-Forwarded-Proto": [ "https" ], "CloudFront-Is-Desktop-Viewer": [ "true" ], "CloudFront-Is-Mobile-Viewer": [ "false" ], "CloudFront-Is-SmartTV-Viewer": [ "false" ], "CloudFront-Is-Tablet-Viewer": [ "false" ], "CloudFront-Viewer-Country": [ "US" ], "Cookie": [ "_ga=GA1.2.476562506.1508302986" ], "Host": [ "dgraphs.example.com" ], "upgrade-insecure-requests": [ "1" ], "User-Agent": [ "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36" ], "Via": [ "2.0 05aec04162b0fed6e9762cd1edd66a72.cloudfront.net (CloudFront)" ], "X-Amz-Cf-Id": [ "0WIyvSNpjbRatxNZyMLlRHavJLf8FACh5XCUbWtsaKSuw97T4LmO4g==" ], "X-Amzn-Trace-Id": [ "Root=1-5d145415-104877631845dde42c69f241" ], "X-Forwarded-For": [ "70.36.235.225, 70.132.18.149" ], "X-Forwarded-Port": [ "443" ], "X-Forwarded-Proto": [ "https" ] }, "queryStringParameters": { "filename": "floof" }, "multiValueQueryStringParameters": { "filename": [ "floof" ] }, "pathParameters": null, "stageVariables": null, "requestContext": { "resourceId": "905w5w", "resourcePath": "/upload_file", "httpMethod": "GET", "extendedRequestId": "b7ITYEmsoAMFu7g=", "requestTime": "27/Jun/2019:05:28:53 +0000", "path": "/upload_file", "accountId": "101696101272", "protocol": "HTTP/1.1", "stage": "test", "domainPrefix": "dgraphs", "requestTimeEpoch": 1561613333649, "requestId": "73caa021-989c-11e9-9045-8baf1b843611", "identity": { "cognitoIdentityPoolId": null, "accountId": null, "cognitoIdentityId": null, "caller": null, "sourceIp": "70.36.235.225", "principalOrgId": null, "accessKey": null, "cognitoAuthenticationType": null, "cognitoAuthenticationProvider": null, "userArn": null, "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36", "user": null }, "domainName": "dgraphs.example.com", "apiId": "ad3b4lkfdc" }, "body": null, "isBase64Encoded": false }'''
        url = util.event_url(json.loads(event))
        self.assertEqual(url, 'https://dgraphs.example.com/upload_file?filename=floof')
    
    def test_combine_digraphs(self):
        '''
        '''
        graph1, graph2 = networkx.DiGraph(), networkx.DiGraph()
        
        graph1.add_node('A', pos='yes')
        graph1.add_node('B', pos='nope') # to be overriden by graph2[B]
        graph2.add_node('B', pos='yup')
        graph1.add_edge('A', 'B', line='yes')
        graph1.add_edge('B', 'A', line='nope') # to be overriden by graph2[B,A]
        graph2.add_edge('B', 'A', line='yup')
        
        graph3 = util.combine_digraphs(graph1, graph2)
        self.assertEqual(len(graph3.nodes), 2)
        self.assertEqual(len(graph3.edges), 2)
        self.assertEqual(graph3.nodes['A']['pos'], 'yes')
        self.assertEqual(graph3.nodes['B']['pos'], 'yup')
        self.assertEqual(graph3.edges[('A', 'B')]['line'], 'yes')
        self.assertEqual(graph3.edges[('B', 'A')]['line'], 'yup')

