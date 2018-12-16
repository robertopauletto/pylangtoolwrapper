# pylangtoolwrapper.py

from collections import namedtuple
import requests
from entities import Error

__doc__ = """API Wrapper for the LanguageTool API REST
https://languagetool.org/http-api/languagetool-swagger.json
"""
__version__ = "0.1"
__changelog__ = """

"""

USER_AGENT = ('Mozilla/5.0 (X11; CrOS x86_64 10066.0.0) AppleWebKit/537.36 '
              '(KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36')

ROUTES = {
    'base': r'https://languagetool.org/api/v2/',
    'languages': 'languages',
    'check': 'check'
}

Language = namedtuple('Language', 'name code long_code')


class PyLangToolWrapperException(Exception):
    pass


def _get_req(url, verb='GET', payload=None, ua=None):
    """
    Manage request
    :param url: the API REST endpoing
    :param verb:
    :param payload: paramenters
    :param ua: user agent
    :return: response in json format
    """
    headers = {'user-agent': ua or USER_AGENT}
    if verb == 'GET':
        r = requests.get(url, headers=headers)
    elif verb == 'POST':
        r = requests.post(url, headers=headers, data=payload)
    else:
        raise PyLangToolWrapperException('not a valid verb for this API')
    if r.status_code != 200:
        raise PyLangToolWrapperException(f"Error {r.status_code}\n{r.text}")
    return r


def get_languages():
    """
    Get available languages
    :return: list
    """
    url = f"{ROUTES['base']}{ROUTES['languages']}"
    resp = _get_req(url)
    languages = list()
    for record in resp.json():
        languages.append(
            Language(record['name'], record['code'], record['longCode']
        ))
    return languages


def check(text, lang_code):
    """
    Send `text` for the spell check with `language`
    :param text: the text to check
    :param lang_code: language code, you can retrieve the code by calling first
                       `get_language()` - **No check first will be performed**
    :return: list of `Error` objects
    """
    url = f"{ROUTES['base']}{ROUTES['check']}"
    payload = {'text': text, 'language': lang_code}
    resp = _get_req(url, verb='POST', payload=payload)
    errors = Error.parse(resp.json())
    return errors


if __name__ == '__main__':
    pass
