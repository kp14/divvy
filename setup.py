from setuptools import setup, find_packages
from divvy.version import __version__

setup(
    name='Divvy',
    version=__version__,
    description='For divvying up the QA work',
    long_description='Have to add this',
    url='...',
    author='kp14',
    author_email='kp14@ebi',
    license='public domain',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(exclude=['docs']),
    install_requires=['flask',
                      'flask-admin',
                      'apscheduler',
                      'flask-apscheduler',
                      'peewee==2.10.2',
                      'wtf-peewee==0.2.6',
                      'jira',
                      'pbr',
                      'waitress',
                      ],
    package_data={'divvy': ['static/favicon.ico',
                            'templates/base.html',
                            'templates/index.html',
                            'templates/admin/index.html',
                            ],
                  },
    entry_points = {'console_scripts': ['up2pmid=divvy.up2pmid:main']},
    scripts=['run_divvy.py'],
)