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
        'networkx == 2.3',
        'boto3 == 1.9.169',
        'botocore == 1.12.174',
        'itsdangerous == 0.24',
        'progressbar2 == 3.42.0',
        ],
    extras_require = {
        'convert': [
            'geopandas == 0.5.0',
            'pandas == 0.24.2',
            'Rtree == 0.8.3',
            'psycopg2 == 2.8.3',
            ],
        },
    entry_points = dict(
        console_scripts = [
            'geo2graph = DistrictGraphs.geo2graph:main',
            'pgsql2graph = DistrictGraphs.pgsql2graph:main',
            'dwim = DistrictGraphs.dwim:main',
            ]
        ),
)
