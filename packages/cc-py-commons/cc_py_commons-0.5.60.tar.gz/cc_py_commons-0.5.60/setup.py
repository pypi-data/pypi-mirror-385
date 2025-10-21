from setuptools import setup, find_packages

setup(
    name='cc_py_commons',
    description='Common code for microservices',
    version='0.5.60',
    url='https://github.com/Cargo-Chief/py-commons',
    author='CargoChief',
    author_email='engineering@cargochief.com',
    packages=find_packages(),
    install_requires=['requests', 'googlemaps', 'marshmallow', 'boto3', 'inflection', 'pytz'],
    keywords=[]
    )
