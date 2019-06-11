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
        },
    install_requires = [
        'Shapely == 1.6.4.post2',
        ],
    extras_require = {
        #'GDAL': ['GDAL == 2.1.3'],
        },
    entry_points = dict(
        console_scripts = [
            ]
        ),
)
