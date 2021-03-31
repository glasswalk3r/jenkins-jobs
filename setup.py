#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['python-jenkins>=1.7.0', 'xmltodict>=0.12.0']

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest>=3', ]

setup(
    author="Alceu Rodrigues de Freitas Junior",
    author_email='glasswalk3r@yahoo.com.br',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    description="Listing all jobs on a Jenkins server with more information than jenkins-cli.jar",
    entry_points={
        'console_scripts': [
            'jenkins_jobs=jenkins_jobs.reporter:main',
            'jenkins_exporter=jenkins_jobs.exporter:main'
        ],
    },
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='jenkins jobs',
    name='jenkins_jobs',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/glasswalk3r/jenkins_jobs',
    version='0.0.1',
    zip_safe=False,
)
