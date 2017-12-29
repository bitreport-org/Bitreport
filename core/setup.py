from setuptools import setup, find_packages

setup(
    name='core',
    version='1.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'altgraph==0.15',
        'aniso8601==1.3.0',
        'certifi==2017.11.5',
        'chardet==3.0.4',
        'click==6.7',
        'Flask==0.12.2',
        'Flask-RESTful==0.3.6',
        'future==0.16.0',
        'gevent==1.2.2',
        'greenlet==0.4.12',
        'idna==2.6',
        'influxdb==5.0.0',
        'iso8601==0.1.12',
        'itsdangerous==0.24',
        'Jinja2==2.10',
        'JsonForm==0.0.2',
        'jsonschema==2.6.0',
        'JsonSir==0.0.2',
        'macholib==1.9',
        'MarkupSafe==1.0',
        'numpy==1.13.3',
        'pefile==2017.11.5',
        'PyInstaller==3.3.1',
        'python-dateutil==2.6.1',
        'Python-EasyConfig==0.1.7',
        'pytz==2017.3',
        'PyYAML==3.12',
        'requests==2.18.4',
        'Resource==0.2.1',
        'six==1.11.0',
        'TA-Lib==0.4.10',
        'urllib3==1.22',
        'websocket==0.2.1',
        'websocket-client==0.45.0',
        'Werkzeug==0.13'
    ],
    author='Timmi',
    description='core application of bitReport.org'
)
