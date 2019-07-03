import urllib.parse
import networkx

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

def combine_digraphs(graph1, graph2):
    '''
    '''
    graph3 = networkx.DiGraph()
    
    for (node_id, _) in graph1.edges.keys():
        graph3.add_node(node_id, **graph1.nodes[node_id])
    
    for (node_id, _) in graph2.edges.keys():
        graph3.add_node(node_id, **graph2.nodes[node_id])
    
    for ((node1_id, node2_id), edge) in graph1.edges.items():
        graph3.add_edge(node1_id, node2_id, **edge)
    
    for ((node1_id, node2_id), edge) in graph2.edges.items():
        graph3.add_edge(node1_id, node2_id, **edge)
    
    return graph3
