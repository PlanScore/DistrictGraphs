import logging
import argparse
import geopandas
import networkx
from . import blocks_frame_graph

parser = argparse.ArgumentParser(description='Convert geographic blocks to graph format.')
parser.add_argument('shapefile',  help='Input geography file (SHP, GeoJSON, etc.)')
parser.add_argument('graphfile', help='Output graph file in pickle format')
parser.add_argument('--quiet', '-q', dest='loglevel', action='store_const',
    const=logging.WARNING, default=logging.INFO, help='Less output')
parser.add_argument('--verbose', '-v', dest='loglevel', action='store_const',
    const=logging.DEBUG, default=logging.INFO, help='More output')

def main():
    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel)
    frame = geopandas.read_file(args.shapefile)
    graph = blocks_frame_graph(frame, 'GEOID10')
    networkx.write_gpickle(graph, args.graphfile)
