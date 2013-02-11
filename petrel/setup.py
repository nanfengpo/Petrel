#!/usr/bin/env python
import os
from pkg_resources import Requirement, resource_filename
from setuptools import setup, find_packages
import shutil
import subprocess
import sys
import urllib2

README = os.path.join(os.path.dirname(__file__), 'README.txt')
long_description = open(README).read() + '\n\n'

PACKAGE = "petrel"

PETREL_VERSION = '0.1'

def get_storm_version():
    return subprocess.check_output(['storm', 'version']).strip()    

def get_version(argv):
    """ Dynamically calculate the version based on VERSION."""
    return '%s.%s' % (get_storm_version(), PETREL_VERSION)

def build_petrel():
    version = get_storm_version()
    
    # Generate Thrift Python wrappers.
    if os.path.isdir('petrel/generated'):
        shutil.rmtree('petrel/generated')
    os.mkdir('petrel/generated')
    f_url = urllib2.urlopen('https://raw.github.com/nathanmarz/storm/%s/src/storm.thrift' % version)
    with open('storm.thrift', 'w') as f:
        f.write(f_url.read())
    f_url.close()
    old_cwd = os.getcwd()
    os.chdir('petrel/generated')
    
    subprocess.check_call(['thrift', '-gen', 'py', '-out', '.', '../../storm.thrift'])    
    os.chdir(old_cwd)
    os.remove('storm.thrift')
    
    # Build JVMPetrel.
    os.chdir('../jvmpetrel')
    subprocess.check_call(['mvn', '-Dstorm_version=%s' % version, 'assembly:assembly'])
    os.chdir(old_cwd)
    shutil.copyfile(
        '../jvmpetrel/target/storm-petrel-%s-SNAPSHOT.jar' % version,
        'petrel/generated/storm-petrel-%s-SNAPSHOT.jar' % version)

if 'bdist_egg' in sys.argv or 'develop' in sys.argv:
    build_petrel()

setup(name=PACKAGE
    ,version=get_version(sys.argv)
    ,description=("Storm Topology Builder. AirSage, Inc")
    ,long_description=long_description
    ,classifiers=[
         "Programming Language :: Python"
        ,("Topic :: Software Development :: Libraries :: Python Modules")
    ]
    ,keywords='Storm Topology Builder'
    ,author='bhart'
    ,url='https://github.com/AirSage/Petrel'
    ,scripts=[
         'bin/petrel',
        ]
    ,packages=find_packages()
    ,package_data={'': ['*.jar']}
    ,license='Copyright AirSage, Inc'
    ,install_requires=[
        'simplejson>=2.6.0',
        # Request specific Thrift version. Storm is in Java and may be sensitive to version incompatibilities.
        'thrift==0.8.0',
        'PyYAML>=3.10',
    ]
    # Setting this flag makes Petrel easier to debug within a running topology.
    ,zip_safe=False)
