from setuptools import setup

setup(
    name = 'DistrictGraphs',
    url = '',
    author = '',
    description = '',
    packages = [
        'DistrictGraphs', 'DistrictGraphs.tests',
        ],
    test_suite = 'DistrictGraphs.tests',
    package_data = {
        'DistrictGraphs.tests': ['data/*.*'],
        },
    install_requires = [
        'Shapely == 1.6.4.post2',
        'geopandas == 0.5.0',
        'pandas == 0.24.2',
        'Rtree == 0.8.3',
        'networkx == 2.3',
        ],
    extras_require = {
        #'GDAL': ['GDAL == 2.1.3'],
        },
    entry_points = dict(
        console_scripts = [
            'geo2graph = DistrictGraphs.geo2graph:main',
            ]
        ),
)
