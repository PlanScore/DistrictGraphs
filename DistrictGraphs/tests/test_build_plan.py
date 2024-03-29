import os, unittest, unittest.mock, json, io, uuid
import botocore

from .. import build_plan, build_district

class TestBuildPlan (unittest.TestCase):
    
    def test_get_token_good(self):
        s3 = unittest.mock.Mock()
        s3.head_object.return_value = {'ETag': '0xdeadbeef'}
        token = build_plan.get_token(s3, 'dgraphs', 'stuff/assignments', 'vtd')
        self.assertIsNotNone(token)
    
    def test_get_token_bad(self):
        def raises():
            raise RuntimeError()
    
        s3 = unittest.mock.Mock()
        s3.head_object.side_effect = raises
        token = build_plan.get_token(s3, 'dgraphs', 'stuff/assignments', 'vtd')
        self.assertIsNone(token)
    
    def test_get_status_good(self):
        s3 = unittest.mock.Mock()
        s3.get_object.return_value = {'Body': unittest.mock.Mock()}
        s3.get_object.return_value['Body'].read.return_value = '''
            {
                "token": "T", "state": "S",
                "district_ids": ["1","2","3"], "geojson_url": "U"
            }
            '''
        status = build_plan.get_status(s3, 'dgraphs', 'stuff/assignments')
        
        self.assertEqual(status.token, 'T')
        self.assertEqual(status.state, 'S')
        self.assertEqual(status.district_ids, ['1','2','3'])
        self.assertEqual(status.geojson_url, 'U')
    
    def test_get_status_bad(self):
        def raises():
            raise RuntimeError()
    
        s3 = unittest.mock.Mock()
        s3.get_object.side_effect = raises
        status = build_plan.get_status(s3, 'dgraphs', 'stuff/assignments')
        
        self.assertIsNone(status.token)
        self.assertIsNone(status.state)
        self.assertIsNone(status.district_ids)
        self.assertIsNone(status.geojson_url)
    
    def test_put_status(self):
        s3, status = unittest.mock.Mock(), unittest.mock.Mock()
        status.to_dict.return_value = {'status': 'mock'}
        build_plan.put_status(s3, 'dgraphs', 'stuff/assignments', status)
        
        s3.put_object.assert_called_once_with(
            Bucket='dgraphs', Key='stuff/assignments/status',
            Body=b'{"status": "mock"}', ContentType='application/json')
    
    @unittest.mock.patch('networkx.read_gpickle')
    def test_load_graph(self, read_gpickle):
        s3 = unittest.mock.Mock()
        s3.get_object.return_value = {'Body': unittest.mock.Mock()}
        s3.get_object.return_value['Body'].read.return_value = b'fake'
        build_plan.load_graph(s3, 'dgraphs', 'G.pickle')

        s3.get_object.assert_called_once_with(Bucket='dgraphs', Key='graphs/G.pickle')
        temp_path = read_gpickle.mock_calls[0][1][0]
        self.assertFalse(os.path.exists(temp_path))
    
    def test_fan_out_build_district(self):
        lam = unittest.mock.Mock()
        
        build_plan.fan_out_build_district(lam,
            'stuff/assignments', ['1','2','3'], 'vtd')
        
        self.assertEqual(len(lam.invoke.mock_calls), 3)
        call1, call2, call3 = lam.invoke.mock_calls
        payload1, payload2, payload3 = [json.loads(call[2]['Payload'])
            for call in (call1, call2, call3)]
        
        self.assertEqual(call1[2]['FunctionName'], build_district.FUNCTION_NAME)
        self.assertEqual(payload1['key'], 'stuff/assignments')
        self.assertEqual(payload1['district'], '1')
        self.assertEqual(payload1['layer'], 'vtd')
        
        self.assertEqual(call2[2]['FunctionName'], build_district.FUNCTION_NAME)
        self.assertEqual(payload2['key'], 'stuff/assignments')
        self.assertEqual(payload2['district'], '2')
        self.assertEqual(payload2['layer'], 'vtd')
        
        self.assertEqual(call3[2]['FunctionName'], build_district.FUNCTION_NAME)
        self.assertEqual(payload3['key'], 'stuff/assignments')
        self.assertEqual(payload3['district'], '3')
        self.assertEqual(payload3['layer'], 'vtd')
    
    def test_count_finished_districts_complete(self):
        s3 = unittest.mock.Mock()
        
        finished = build_plan.count_finished_districts(s3, 'dgraphs', 'S', ['1','2','3'])
        self.assertEqual(finished, 3)

        self.assertEqual(len(s3.head_object.mock_calls), 3)
        call1, call2, call3 = s3.head_object.mock_calls
        
        self.assertEqual(call1[2], dict(Bucket='dgraphs', Key='S/district-1.wkt'))
        self.assertEqual(call2[2], dict(Bucket='dgraphs', Key='S/district-2.wkt'))
        self.assertEqual(call3[2], dict(Bucket='dgraphs', Key='S/district-3.wkt'))
    
    def test_count_finished_districts_incomplete(self):
        def raises_oddly(Bucket, Key):
            if '2' not in Key:
                raise botocore.exceptions.ClientError({'': ''}, '')
        
        s3 = unittest.mock.Mock()
        s3.head_object.side_effect = raises_oddly
        
        finished = build_plan.count_finished_districts(s3, 'dgraphs', 'S', ['1','2','3'])
        self.assertEqual(finished, 1)

        self.assertEqual(len(s3.head_object.mock_calls), 3)
        call1, call2, call3 = s3.head_object.mock_calls
        
        self.assertEqual(call1[2], dict(Bucket='dgraphs', Key='S/district-1.wkt'))
        self.assertEqual(call2[2], dict(Bucket='dgraphs', Key='S/district-2.wkt'))
        self.assertEqual(call3[2], dict(Bucket='dgraphs', Key='S/district-3.wkt'))
    
    def test_put_plan_geojson(self):
        s3 = unittest.mock.Mock()
        s3.get_object.return_value = {'Body': unittest.mock.Mock()}
        s3.get_object.return_value['Body'].read.return_value = b'POINT(0 0)'
        
        geojson_path = build_plan.put_plan_geojson(s3, 'dgraphs', 'S', ['1','2','3'])

        self.assertEqual(len(s3.get_object.mock_calls), 3)
        get_call1, get_call2, get_call3 = s3.get_object.mock_calls

        self.assertEqual(get_call1[2], dict(Bucket='dgraphs', Key='S/district-1.wkt'))
        self.assertEqual(get_call2[2], dict(Bucket='dgraphs', Key='S/district-2.wkt'))
        self.assertEqual(get_call3[2], dict(Bucket='dgraphs', Key='S/district-3.wkt'))
        
        self.assertEqual(len(s3.put_object.mock_calls), 1)
        put_call = s3.put_object.mock_calls[0]
        self.assertEqual(put_call[2]['Bucket'], 'dgraphs')
        self.assertEqual(put_call[2]['Key'], geojson_path)
        self.assertEqual(put_call[2]['ACL'], 'public-read')
        self.assertEqual(put_call[2]['ContentType'], 'application/json')
        
        geojson = json.loads(put_call[2]['Body'])

        self.assertEqual(geojson['type'], 'FeatureCollection')
        self.assertEqual(len(geojson['features']), 3)
        
        feature1, feature2, feature3 = geojson['features']

        self.assertEqual(feature1['properties']['district'], '1')
        self.assertEqual(feature1['geometry']['type'], 'Point')
        self.assertEqual(feature1['geometry']['coordinates'], [0, 0])

        self.assertEqual(feature2['properties']['district'], '2')
        self.assertEqual(feature2['geometry']['type'], 'Point')
        self.assertEqual(feature2['geometry']['coordinates'], [0, 0])

        self.assertEqual(feature3['properties']['district'], '3')
        self.assertEqual(feature3['geometry']['type'], 'Point')
        self.assertEqual(feature3['geometry']['coordinates'], [0, 0])
    
    @unittest.mock.patch('DistrictGraphs.build_plan.count_finished_districts')
    @unittest.mock.patch('DistrictGraphs.build_plan.fan_out_build_district')
    @unittest.mock.patch('DistrictGraphs.build_plan.put_status')
    def test_read_file_start(self, put_status, fan_out_build_district, count_finished_districts):
        assignments = b'060011234,1\n060015678,1\n060751234,2\n060755678,2'
        s3, lam = unittest.mock.Mock(), unittest.mock.Mock()
        s3.get_object.return_value = {'Body': io.BytesIO(assignments)}
        token = str(uuid.uuid4())
        status = build_plan.Status(None, None, None, None)
        count_finished_districts.return_value = 0
        
        new_status = build_plan.read_file(s3, lam, 'dgraphs',
            status, token, 'tract', 'stuff/assignments')

        self.assertEqual(new_status.token, token)
        self.assertEqual(new_status.state, build_plan.STATUS_STARTED)
        self.assertEqual(new_status.district_ids, ['1', '2'])
        self.assertIsNone(new_status.geojson_url)
        
        self.assertEqual(len(fan_out_build_district.mock_calls), 1)
        self.assertEqual(len(put_status.mock_calls), 1)
        
        self.assertEqual(fan_out_build_district.mock_calls[0][1],
            (lam, 'stuff/assignments', ['1', '2'], 'tract'))
        
        self.assertEqual(put_status.mock_calls[0][1][:3], (s3, 'dgraphs', 'stuff'))
    
    @unittest.mock.patch('DistrictGraphs.build_plan.count_finished_districts')
    @unittest.mock.patch('DistrictGraphs.build_plan.put_plan_geojson')
    @unittest.mock.patch('DistrictGraphs.build_plan.put_status')
    def test_read_file_continue(self, put_status, put_plan_geojson, count_finished_districts):
        s3, lam = unittest.mock.Mock(), unittest.mock.Mock()
        token = str(uuid.uuid4())
        status = build_plan.Status(token, build_plan.STATUS_STARTED, ['1', '2'], None)
        count_finished_districts.return_value = 1
        
        new_status = build_plan.read_file(s3, lam, 'dgraphs',
            status, token, 'tract', 'stuff/assignments')

        self.assertEqual(new_status.token, token)
        self.assertEqual(new_status.state, build_plan.STATUS_STARTED)
        self.assertEqual(new_status.district_ids, ['1', '2'])
        self.assertIsNone(new_status.geojson_url)
        
        self.assertEqual(len(put_plan_geojson.mock_calls), 0)
        self.assertEqual(len(put_status.mock_calls), 0)
    
    @unittest.mock.patch('DistrictGraphs.build_plan.count_finished_districts')
    @unittest.mock.patch('DistrictGraphs.build_plan.put_plan_geojson')
    @unittest.mock.patch('DistrictGraphs.build_plan.put_status')
    def test_read_file_complete(self, put_status, put_plan_geojson, count_finished_districts):
        s3, lam = unittest.mock.Mock(), unittest.mock.Mock()
        token = str(uuid.uuid4())
        status = build_plan.Status(token, build_plan.STATUS_STARTED, ['1', '2'], None)
        count_finished_districts.return_value = 2
        put_plan_geojson.return_value = 'stuff/districts.geojson'
        
        new_status = build_plan.read_file(s3, lam, 'dgraphs',
            status, token, 'tract', 'stuff/assignments')

        self.assertEqual(new_status.token, token)
        self.assertEqual(new_status.state, build_plan.STATUS_COMPLETE)
        self.assertEqual(new_status.district_ids, ['1', '2'])
        self.assertIn('dgraphs/stuff/districts.geojson', new_status.geojson_url)
        
        self.assertEqual(len(put_plan_geojson.mock_calls), 1)
        self.assertEqual(len(put_status.mock_calls), 1)
        
        self.assertEqual(put_plan_geojson.mock_calls[0][1],
            (s3, 'dgraphs', 'stuff', ['1', '2']))
        
        self.assertEqual(put_status.mock_calls[0][1][:3], (s3, 'dgraphs', 'stuff'))
    
    @unittest.mock.patch('DistrictGraphs.build_plan.count_finished_districts')
    @unittest.mock.patch('DistrictGraphs.build_plan.put_plan_geojson')
    @unittest.mock.patch('DistrictGraphs.build_plan.put_status')
    def test_read_file_completed(self, put_status, put_plan_geojson, count_finished_districts):
        s3, lam = unittest.mock.Mock(), unittest.mock.Mock()
        token = str(uuid.uuid4())
        status = build_plan.Status(token, build_plan.STATUS_COMPLETE, ['1', '2'],
            'https://example.com/dgraphs/stuff/districts.geojson')
        
        new_status = build_plan.read_file(s3, lam, 'dgraphs',
            status, token, 'tract', 'stuff/assignments')

        self.assertEqual(new_status.token, token)
        self.assertEqual(new_status.state, build_plan.STATUS_COMPLETE)
        self.assertEqual(new_status.district_ids, ['1', '2'])
        self.assertIn('dgraphs/stuff/districts.geojson', new_status.geojson_url)
        
        self.assertEqual(len(count_finished_districts.mock_calls), 0)
        self.assertEqual(len(put_plan_geojson.mock_calls), 0)
        self.assertEqual(len(put_status.mock_calls), 0)
    
    @unittest.mock.patch('DistrictGraphs.build_plan.count_finished_districts')
    @unittest.mock.patch('DistrictGraphs.build_plan.fan_out_build_district')
    @unittest.mock.patch('DistrictGraphs.build_plan.put_plan_geojson')
    @unittest.mock.patch('DistrictGraphs.build_plan.put_status')
    def test_read_file_instant(self, put_status, put_plan_geojson, fan_out_build_district, count_finished_districts):
        assignments = b'060011234,1\n060015678,1\n060751234,2\n060755678,2'
        s3, lam = unittest.mock.Mock(), unittest.mock.Mock()
        s3.get_object.return_value = {'Body': io.BytesIO(assignments)}
        token = str(uuid.uuid4())
        status = build_plan.Status(None, None, None, None)
        count_finished_districts.return_value = 2
        put_plan_geojson.return_value = 'stuff/districts.geojson'
        
        new_status = build_plan.read_file(s3, lam, 'dgraphs',
            status, token, 'tract', 'stuff/assignments')

        self.assertEqual(new_status.token, token)
        self.assertEqual(new_status.state, build_plan.STATUS_COMPLETE)
        self.assertEqual(new_status.district_ids, ['1', '2'])
        self.assertIn('dgraphs/stuff/districts.geojson', new_status.geojson_url)
        
        self.assertEqual(len(fan_out_build_district.mock_calls), 1)
        self.assertEqual(len(put_plan_geojson.mock_calls), 1)
        self.assertEqual(len(put_status.mock_calls), 2)
        
        self.assertEqual(fan_out_build_district.mock_calls[0][1],
            (lam, 'stuff/assignments', ['1', '2'], 'tract'))
        
        self.assertEqual(put_plan_geojson.mock_calls[0][1],
            (s3, 'dgraphs', 'stuff', ['1', '2']))
        
        self.assertEqual(put_status.mock_calls[0][1][:3], (s3, 'dgraphs', 'stuff'))
        self.assertEqual(put_status.mock_calls[1][1][:3], (s3, 'dgraphs', 'stuff'))
    
    def test_read_file_nonsense(self):
        s3, lam = unittest.mock.Mock(), unittest.mock.Mock()
        token = str(uuid.uuid4())
        status = build_plan.Status(token, 'Unknown', ['1', '2'],
            'https://example.com/dgraphs/stuff/districts.geojson')
        
        new_status = build_plan.read_file(s3, lam, 'dgraphs',
            status, token, 'tract', 'stuff/assignments')

        self.assertIsNone(new_status)
