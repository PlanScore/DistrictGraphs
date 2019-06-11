import shapely.geometry

def shared_linear_boundary(geom1, geom2):
    ''' Return just the linear parts of a shared boundary.
    '''
    intersection = geom1.intersection(geom2)

    if intersection.type in ('LineString', 'MultiLineString'):
        return intersection

    if intersection.type in ('Point', 'MultiPoint', 'Polygon', 'MultiPolygon'):
        raise ValueError('Bad type {}'.format(intersection.type))

    if intersection.type == 'GeometryCollection':
        types = {geom.type for geom in intersection.geoms}

        if 'Polygon' in types or 'MultiPolygon' in types:
            raise Exception('Type has polygon {}'.format(repr(types)))

        if types == {'Point', 'LineString'}:
            lines = [g for g in intersection.geoms if g.type == 'LineString']
            return shapely.geometry.MultiLineString(lines)

        raise Exception('Bad type {}'.format(intersection.type))
