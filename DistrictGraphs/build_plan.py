import os
import json
import tempfile
import networkx
import botocore
import shapely.wkt

from . import build_district, polygonize, constants

STATUS_STARTED = 'started'
STATUS_COMPLETE = 'complete'

class Status:

    def __init__(self, token, state, district_ids, geojson_url):
        '''
        '''
        self.token = token
        self.state = state
        self.district_ids = district_ids
        self.geojson_url = geojson_url
    
    def to_dict(self):
        return dict(
            token = self.token,
            state = self.state,
            district_ids = self.district_ids,
            geojson_url = self.geojson_url,
            )

def get_token(s3, bucket, assignments_path, layer):
    '''
    '''
    try:
        assignments_obj = s3.head_object(Bucket=bucket, Key=assignments_path)
    except:
        token = None
    else:
        token = f'{assignments_obj["ETag"]}|{layer}'

    return token

def get_status(s3, bucket, assignments_dir):
    '''
    '''
    status_path = os.path.join(assignments_dir, 'status')
    
    try:
        status_obj = s3.get_object(Bucket=bucket, Key=status_path)
    except:
        status = Status(None, None, None, None)
    else:
        d = json.loads(status_obj['Body'].read())
        status = Status(d.get('token'), d.get('state'),
            d.get('district_ids'), d.get('geojson_url'))
    
    return status

def put_status(s3, bucket, assignments_dir, status):
    '''
    '''
    status_path = os.path.join(assignments_dir, 'status')

    s3.put_object(Bucket=bucket, Key=status_path,
        ContentType='application/json',
        Body=json.dumps(status.to_dict()).encode('utf8'),
        )

def load_graph(s3, bucket, path):
    '''
    '''
    print('Loading', bucket, f'graphs/{path}')
    
    object = s3.get_object(Bucket=bucket, Key=f'graphs/{path}')
    
    with tempfile.NamedTemporaryFile(prefix='graph-', suffix='.pickle') as file:
        file.write(object['Body'].read())
        file.seek(0)
        graph = networkx.read_gpickle(file.name)

    return graph

def fan_out_build_district(lam, assignments_path, district_ids, layer):
    '''
    '''
    for district_id in district_ids:
        print('Invoking', build_district.FUNCTION_NAME, 'for', district_id)
        lam.invoke(FunctionName=build_district.FUNCTION_NAME, InvocationType='Event',
            Payload=json.dumps({'key': assignments_path, 'district': district_id, 'layer': layer}))

def count_finished_districts(s3, bucket, assignments_dir, district_ids):
    '''
    '''
    finished = 0

    for district_id in district_ids:
        expected_wkt = os.path.join(assignments_dir,
            build_district.WKT_FORMAT.format(id=district_id))

        try:
            object = s3.head_object(Bucket=bucket, Key=expected_wkt)
        except botocore.exceptions.ClientError:
            # Did not find the expected wkt
            print('Did not find', expected_wkt)
        else:
            # Found the expected wkt
            print('Found', expected_wkt)
            finished += 1
    
    return finished

def put_plan_geojson(s3, bucket, assignments_dir, district_ids):
    '''
    '''
    # assemble geojson from WKT
    districts = dict()
    for district_id in district_ids:
        expected_wkt = os.path.join(assignments_dir,
            build_district.WKT_FORMAT.format(id=district_id))
        
        object = s3.get_object(Bucket=bucket, Key=expected_wkt)
        wkt_string = object['Body'].read().decode('ascii')
        districts[district_id] = shapely.wkt.loads(wkt_string)
    
    geojson = polygonize.districts_geojson(districts)
    geojson_path = os.path.join(assignments_dir, 'districts.geojson')

    s3.put_object(Bucket=bucket, Key=geojson_path,
        ACL='public-read', ContentType='application/json',
        Body=json.dumps(geojson).encode('utf8'),
        )
    
    return geojson_path

def read_file(s3, lam, bucket, status, token, layer, assignments_path):
    '''
        when status token matches unique token and:
          ...status is "started": update progress, write status, respond
          ...status is "finished": respond with redirect to status results
        otherwise:
          - start building districts
          - set status to "started", write status
    '''
    assignments_dir = os.path.dirname(assignments_path)
    
    if status.token != token and token is not None:
        object = s3.get_object(Bucket=bucket, Key=assignments_path)
        assignments = polygonize.parse_assignments(object['Body'])
        
        status = Status(token, STATUS_STARTED,
            sorted(list({a.district for a in assignments})), None)

        fan_out_build_district(lam, assignments_path, status.district_ids, layer)
        put_status(s3, bucket, assignments_dir, status)
    
    if status.state == STATUS_STARTED:
        expected = len(status.district_ids)
        finished = count_finished_districts(s3,
            bucket, assignments_dir, status.district_ids)

        if finished != expected:
            return status
        
        geojson_path = put_plan_geojson(s3,
            bucket, assignments_dir, status.district_ids)
        
        status.state = STATUS_COMPLETE
        status.geojson_url = constants.S3_URL_PATTERN.format(b=bucket, k=geojson_path)
        put_status(s3, bucket, assignments_dir, status)

    if status.state == STATUS_COMPLETE:
        return status
