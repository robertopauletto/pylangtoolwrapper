# test_pylangtoolwrapper

import json
import os
import unittest
import pylangtoolwrapper as pylt

__doc__ = """test_pylangtoolwrapper"""
__version__ = "0.1"
__changelog__ = """

"""

TEST_FOLDER = 'testdata'
TEXT_IT = 'test_it.txt'
LANG = 'it'
CACHED = 'errors.json'

class TestPylangToolWrapper(unittest.TestCase):
    cached = None

    def setUp(self):
        with open(os.path.join(TEST_FOLDER, TEXT_IT)) as fh:
            self.test_it = fh.read()

    def _get_lang(self):
        return  pylt.get_languages()

    def test_bad_request(self):
        self.assertRaises(
            pylt.PyLangToolWrapperException,
            pylt._get_req,
            f"{pylt.ROUTES['base']}ceck"
        )

    def test_bad_verb(self):
        self.assertRaises(
            pylt.PyLangToolWrapperException,
            pylt._get_req,
            f"{pylt.ROUTES['base']}check",
            'DELETE'
        )

    def test_get_languages_ok_retrieval(self):
        self.assertTrue(len(self._get_lang()) > 0, f'Should be more than zero')

    def test_get_specific_language_ok(self):
        italian = [lang for lang in pylt.get_languages()
                   if 'italian' in lang.name.lower()]
        self.assertTrue(
            len(italian) > 0, f'Expected at least one result, got none'
        )

    def _get_check(self):
        cached = os.path.join(TEST_FOLDER, CACHED)
        if not os.path.exists(cached):
            with open(cached, mode='w') as fh:
                json.dump(pylt.check(self.test_it, LANG), fh)
        with open(cached) as fh:
            return json.load(fh.read())

    def test_check_ok_retreival(self):
        self._get_check()
        self.assertTrue('matches' in TestPylangToolWrapper.cached)
