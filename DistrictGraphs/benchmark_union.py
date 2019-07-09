import boto3, argparse, functools, shapely.ops, os, time, sys, fcntl
from . import constants, polygonize, util, build_district

parser = argparse.ArgumentParser()
parser.add_argument('layer')
parser.add_argument('path')
parser.add_argument('out')

def main():

    times = [time.time()]
    args = parser.parse_args()
    s3 = boto3.client('s3', endpoint_url=constants.S3_ENDPOINT_URL)
    
    with open(args.path, 'rb') as file:
        all_assignments = polygonize.parse_assignments(file)
    
    district_ids = {a.district for a in all_assignments}
    times.append(time.time())
    
    for district_id in district_ids:
        times.append(time.time())
        district_assignments = [a for a in all_assignments if a.district == district_id]

        graph_paths = polygonize.get_county_graph_paths(args.layer, district_assignments)
        graphs = [build_district.load_graph(s3, 'districtgraphs', path) for path in graph_paths]
        graph = functools.reduce(util.combine_digraphs, graphs)
        times.append(time.time())
        
        geoms = [graph.node[a.block]['geom'] for a in district_assignments]
        geometry = shapely.ops.unary_union(geoms)
        geometry_wkt = shapely.wkt.dumps(geometry, rounding_precision=6)
        times.append(time.time())
        
        read_time = times[1] - times[0]
        graph_time = times[-2] - times[-3]
        polygon_time = times[-1] - times[-2]
        counties = len(graph_paths)
        report = f'{read_time:.6f}\t{graph_time:.6f}\t{polygon_time:.6f}\t{args.layer}\t"{args.path}"\t"{district_id}"\t{counties}'

        with open(args.out, 'a') as file:
            fcntl.lockf(file, fcntl.LOCK_EX)
            print(report, file=file)
            fcntl.lockf(file, fcntl.LOCK_UN)
