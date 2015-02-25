import os
import sys
from setuptools import setup

this_dir = os.path.dirname(__file__)
long_description = "\n" + open(os.path.join(this_dir, 'README.rst')).read()

setup(
    name='teamcity_cli',
    version='0.0.0',
    description='CLI for TeamCity CI server, built on pyteamcity',
    long_description=long_description,
    keywords='TeamCity',
    author='Marc Abramowitz',
    author_email='marca@surveymonkey.com',
    url='https://github.com/SurveyMonkey/teamcity_cli',
    py_modules=['teamcitycli'],
    zip_safe=False,
    install_requires=['click', 'pyteamcity'],
    entry_points = """\
      [console_scripts]
      teamcity_cli = teamcitycli:cli
    """,
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Testing',
        'Natural Language :: English',
        'Intended Audience :: Developers',
    ],
)
