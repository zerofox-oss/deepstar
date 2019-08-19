import sqlite3
import threading
import unittest

from deepstar.models.model import Model

from .. import deepstar_path


class TestModel(unittest.TestCase):
    """
    This class tests the Model class.
    """

    def test_init(self):
        with deepstar_path():
            self.assertEqual(type(Model.db), sqlite3.Connection)

    def test_isolation_level(self):
        with deepstar_path():
            Model.db.execute('CREATE TABLE test (test TEXT)')
            Model.db.execute("INSERT INTO test (test) VALUES ('test')")
            Model.close()
            Model.init()
            self.assertEqual(Model.db.execute('SELECT test FROM test').fetchone(), ('test',))  # noqa

    def test_foreign_key_constraints(self):
        with deepstar_path():
            Model.db.execute('CREATE TABLE test1 (id INTEGER PRIMARY KEY)')
            Model.db.execute('CREATE TABLE test2 ( fk_test1 INTEGER, FOREIGN KEY(fk_test1) REFERENCES test1(id))')  # noqa
            with self.assertRaises(sqlite3.IntegrityError):
                Model.db.execute('INSERT INTO test2 (fk_test1) VALUES (1)')

    def test_check_same_thread(self):
        with deepstar_path():
            def a():
                Model.init()

            thread = threading.Thread(target=a)

            Model.close()

            thread.start()

            thread.join()

            Model.close()

    def test_close(self):
        with deepstar_path():
            Model.close()
            self.assertEqual(Model.db, None)
