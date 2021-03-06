try:
    from unittest import mock
except ImportError:
    import mock
import unittest
from sqlalchemy import create_engine
from pyramid_sqlalchemy import init_sqlalchemy
from pyramid_sqlalchemy import metadata
from pyramid_sqlalchemy import Session
import transaction


def enable_sql_two_phase_commit_test(config, enable=True):
    """Fake enable_sql_two_phase_commit function used in the tests."""


def includeme_test(config):
    """Fake includeme function that replaces the real one in the tests."""
    config.add_directive('enable_sql_two_phase_commit', enable_sql_two_phase_commit_test)


class DatabaseTestCase(unittest.TestCase):
    """Base class for tests which require a database connection.

    This class provides makes sure a SQL connection to a database is available
    for tests. Each test is run in a separate transaction, and all tables are
    recreated for each test to guarantee a clean slate.
    """

    #: FLag indicating if SQL tables should be created. This is normally
    #: set to `True`, but you may want to disabled table creation when writing
    #: tests for migration code.
    create_tables = True

    #: :ref:`Database URL <sqlalchemy:database_urls>` for the test database.
    #: Normally a private in-memory SQLite database is used.
    db_uri = 'sqlite://'

    def setUp(self):
        self.engine = create_engine(self.db_uri)
        if self.engine.dialect.name == 'sqlite':
            self.engine.execute('PRAGMA foreign_keys = ON')
        init_sqlalchemy(self.engine)
        if self.create_tables:
            metadata.create_all()
        super(DatabaseTestCase, self).setUp()
        self._sqlalchemy_patcher = mock.patch('pyramid_sqlalchemy.includeme', includeme_test)
        self._sqlalchemy_patcher.start()

    def tearDown(self):
        transaction.abort()
        Session.remove()
        if self.create_tables:
            metadata.drop_all()
        Session.configure(bind=None)
        metadata.bind = None
        self.engine.dispose()
        self._sqlalchemy_patcher.stop()
        super(DatabaseTestCase, self).tearDown()


__all__ = ['DatabaseTestCase']
