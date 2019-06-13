import logging
import argparse
import geopandas
import networkx
from . import blocks_frame_graph

logger = logging.getLogger(__name__)

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

    logger.info(f'Loading {args.shapefile}...')
    frame = geopandas.read_file(args.shapefile)

    logger.info(f'Converting to graph...')
    graph = blocks_frame_graph(frame, 'GEOID10')

    logger.info(f'Writing {args.graphfile}...')
    networkx.write_gpickle(graph, args.graphfile)
