#!/usr/bin/env python
import re
import os
import sys
import time
import unittest
import ConfigParser
from setuptools import setup, Command


class SQLiteTest(Command):
    """
    Run the tests on SQLite
    """
    description = "Run tests on SQLite"

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        if self.distribution.tests_require:
            self.distribution.fetch_build_eggs(self.distribution.tests_require)

        os.environ['TRYTOND_DATABASE_URI'] = 'sqlite://'
        os.environ['DB_NAME'] = ':memory:'

        from tests import suite
        test_result = unittest.TextTestRunner(verbosity=3).run(suite())

        if test_result.wasSuccessful():
            sys.exit(0)
        sys.exit(-1)


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def get_required_version(name):
    return '%s >= %s.%s, < %s.%s' % (
        name, major_version, minor_version,
        major_version, minor_version + 1
    )


class PostgresTest(Command):
    """
    Run the tests on Postgres.
    """
    description = "Run tests on Postgresql"

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        # Set timezone in environment.
        os.environ['TZ'] = 'UTC'

        def set_config():
            os.environ['TRYTOND_DATABASE_URI'] = 'postgresql://'

        from trytond.backend.postgresql import Database
        import trytond.tests.test_tryton

        # Needed for the database loader to load correctly
        set_config()

        trytond.tests.test_tryton.DB_NAME = 'test_' + str(int(time.time()))
        from trytond.tests.test_tryton import DB_NAME
        trytond.tests.test_tryton.DB = Database(DB_NAME)
        from trytond.pool import Pool
        Pool.test = True
        trytond.tests.test_tryton.POOL = Pool(DB_NAME)

        from tests import suite
        test_result = unittest.TextTestRunner(verbosity=3).run(suite())

        if test_result.wasSuccessful():
            sys.exit(0)
        sys.exit(-1)


config = ConfigParser.ConfigParser()
config.readfp(open('tryton.cfg'))
info = dict(config.items('tryton'))
for key in ('depends', 'extras_depend', 'xml'):
    if key in info:
        info[key] = info[key].strip().splitlines()
major_version, minor_version, _ = info.get('version', '0.0.1').split('.', 2)
major_version = int(major_version)
minor_version = int(minor_version)

requires = []

MODULE = "nereid_payment_gateway"
PREFIX = "openlabs"

MODULE2PREFIX = {
    'payment_gateway': 'openlabs',
}
for dep in info.get('depends', []):
    if not re.match(r'(ir|res|webdav)(\W|$)', dep):
        requires.append(
            get_required_version('%s_%s' % (
                MODULE2PREFIX.get(dep, 'trytond'), dep
            ))
        )
requires.append(get_required_version('trytond'))
setup(
    name='%s_%s' % (PREFIX, MODULE),
    version=info.get('version', '0.0.1'),
    description="",
    author="Openlabs Technologies and Consulting (P) Ltd.",
    author_email='info@openlabs.co.in',
    url='http://www.openlabs.co.in/',
    package_dir={'trytond.modules.%s' % MODULE: '.'},
    packages=[
        'trytond.modules.%s' % MODULE,
        'trytond.modules.%s.tests' % MODULE,
    ],
    package_data={
        'trytond.modules.%s' % MODULE: info.get('xml', [])
        + info.get('translation', [])
        + ['tryton.cfg', 'locale/*.po', 'tests/*.rst', 'reports/*.odt']
        + ['view/*.xml'],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Tryton',
        'Topic :: Office/Business',
    ],
    license='GPL-3',
    install_requires=requires,
    zip_safe=False,
    entry_points="""
    [trytond.modules]
    %s = trytond.modules.%s
    """ % (MODULE, MODULE),
    test_suite='tests',
    test_loader='trytond.test_loader:Loader',
    cmdclass={
        'test_on_postgres': PostgresTest,
        'test': SQLiteTest,
    },
    tests_require=[
        'pycountry',
    ],
)
