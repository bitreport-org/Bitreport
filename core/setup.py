from setuptools import setup, find_packages

setup(
    name='core',
    version='1.1',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'aniso8601>=3.0.0',
        'certifi>=2018.4.16',
        'chardet>=3.0.4',
        'click>=6.7',
        'configparser>=3.5.0',
        'Flask>=0.12.2',
        'Flask-RESTful>=0.3.6',
        'idna>=2.6',
        'influxdb>=5.0.0',
        'itsdangerous==0.24',
        'Jinja2>=2.10',
        'MarkupSafe>=1.0',
        'numpy>=1.14.2',
        'pandas>=0.22.0',
        'python-dateutil>=2.7.2',
        'pytz>=2018.4',
        'requests>=2.18.4',
        'six>=1.11.0',
        'TA-Lib>=0.4.17',
        'urllib3>=1.22',
        'Werkzeug>=0.14.1',
     ],
    author='Timmi',
    description='core application of bitReport.org'
)
