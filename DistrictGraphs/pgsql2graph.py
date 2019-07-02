import logging
import argparse
import geopandas
import networkx
import psycopg2
import shapely.wkt
from . import convert

logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description='Convert geographic blocks to graph format.')
parser.add_argument('postgres',  help='Input Postgres connection string')
parser.add_argument('geoid',  help='GEOID of selected county')
parser.add_argument('layer',  help='Geographic unit layer', choices=('tract', 'vtd', 'bg', 'tabblock'))
parser.add_argument('graphfile', help='Output graph file in pickle format')
parser.add_argument('--quiet', '-q', dest='loglevel', action='store_const',
    const=logging.WARNING, default=logging.INFO, help='Less output')
parser.add_argument('--verbose', '-v', dest='loglevel', action='store_const',
    const=logging.DEBUG, default=logging.INFO, help='More output')

def main():
    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel)
    
    logger.info(f'Loading {args.geoid} {args.layer}s from {args.postgres}...')
    graph = networkx.DiGraph()
    
    with psycopg2.connect(args.postgres) as conn:
        with conn.cursor() as db:
            db.execute(f'''
                SELECT geoid10, ST_AsText(geom)
                FROM tl_2010_us_{args.layer}10
                WHERE geoid10 LIKE %s||'%%'
                ''',
                (args.geoid, ))
            
            for (geoid, geom_wkt) in db:
                geom = shapely.wkt.loads(geom_wkt)
                center = geom.representative_point()
                graph.add_node(geoid, geom=geom, pos=(center.x, center.y))
                logger.debug(f'Node: {geoid} {center.x} {center.y}')
                            
            db.execute(f'''
                SELECT geoid10a, geoid10b, same_state, same_county,
                    CASE WHEN geoid10b IS NULL THEN ST_AsText(ST_Intersection(g1.geom, ST_Boundary(us.geom)))
                    ELSE ST_AsText(ST_Intersection(g1.geom, g2.geom))
                    END AS line
                FROM edges_us_{args.layer}10 AS e
                LEFT JOIN tl_2010_us_{args.layer}10 AS g1
                    ON g1.geoid10 = geoid10a
                LEFT JOIN tl_2010_us_{args.layer}10 AS g2
                    ON g2.geoid10 = geoid10b
                LEFT JOIN tl_2010_us AS us
                    ON g1.is_border
                WHERE geoid10a LIKE %s||'%%'
                ''',
                (args.geoid, ))
            
            for (geoid1, geoid2, same_state, same_county, line_wkt) in db:
                line = shapely.wkt.loads(line_wkt)
                graph.add_edge(geoid1, geoid2, same_state=same_state,
                    same_county=same_county, line=line)
                logger.debug(f'Edge: {geoid1}-{geoid2} {line.type}')
            
    logger.info('Loaded graph with {} nodes and {} edges.'.format(len(graph.nodes), len(graph.edges)))

    logger.info(f'Writing {args.graphfile}...')
    networkx.write_gpickle(graph, args.graphfile)
