from distutils.core import setup

setup(
    name='serenity-pypeline',
    version='1.0',
    packages=['serenity_pypeline'],
    url='',
    license='Apache License 2.0',
    author='plotkaba, macromanowski, dejson',
    author_email='',
    description='Serenity Python Pipeline', requires=['influxdb', 'sqlbuilder', 'protobuf', 'numpy']
)
