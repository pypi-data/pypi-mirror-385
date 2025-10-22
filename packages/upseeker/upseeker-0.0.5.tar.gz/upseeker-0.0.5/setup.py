#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages, Extension

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [ ]

test_requirements = [ ]

setup(
    author="Meinolf Sellmann",
    author_email='info@insideopt.com',
    python_requires='>=3.9.0',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.9',
        'Operating System :: POSIX :: Linux'
    ],
    description="InsideOpt Seeker Linux 39 Distribution",
    install_requires=requirements,
    long_description=readme, 
    keywords='insideopt, seeker, optimization',
    name='upseeker',
    test_suite='tests',
    version='0.0.5',
    packages=find_packages(include=['upseeker', 'upseeker.*', '*.so']),
    package_data={'upseeker': ['*.so', 'upseeker.py', 'bin/*', 'scripts/*']},
    zip_safe=False,
)
