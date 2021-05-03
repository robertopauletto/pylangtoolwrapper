# pylangtoolwrapper.py

from collections import namedtuple
from entities import Error
from typing import Union, Dict, Tuple, List

import requests

__doc__ = """API Wrapper for the LanguageTool API REST (free plan)
https://languagetool.org/http-api/languagetool-swagger.json
"""
__version__ = "0.2"
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


def _get_req(url: str, verb: str = 'GET',
             payload: Union[dict, None] = None,
             ua: Union[str, None] = None) -> requests.Response:
    """
    Manage request
    :param url: the API REST endpoint
    :param verb:
    :param payload: paramenters for request
    :param ua: user agent string
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


def get_languages() -> List[Language]:
    """
    Get available languages
    :return: list
    """
    url = f"{ROUTES['base']}{ROUTES['languages']}"
    resp = _get_req(url)
    languages = list()
    for record in resp.json():
        languages.append(
            Language(record['name'], record['code'], record['longCode'])
        )
    return languages


def _check_chars_for_req(text: str, max_chars: int) -> tuple:
    """
    Check `text` lenght against `max_chars`, blank spaces included because it's
    :param text:
    :param max_chars:
    :return: True if chars in `text` > `max_chars` and the total chars in `text`
    """
    return len(text) > max_chars, len(text)


def check(text: str, lang_code: str, whitelist=None,
          max_chars_per_req: int = 20000) -> List[Error]:
    """
    Main function: send `text` for the spell check with `language`
    :param text: the text to check
    :param lang_code: language code, you can retrieve the code by calling first
                       `get_language()` - **No check first will be performed**
    :param whitelist: list of words to ignore. The errors remains but they will
                      be tagged with `is_whitelisted = True`, then the consumer
                      can manage the object as he pleases.
    :param max_chars_per_req: for the free plan there is a limit of
                                    20000 (as per 2021-05-03) character for
                                    request. If the value is > 0 a check for
                                    the chars in `text` will be performed and a
                                    `PyLangToolWrapperException` will be raised
    :
    :return: list of `Error` objects
    """
    check_chars, len_chars = _check_chars_for_req(text, max_chars_per_req)
    if check_chars:
        raise PyLangToolWrapperException(
            f"Too many characters in text\nAllowed: {max_chars_per_req})\n"
            f"Present: {len_chars}")

    url = f"{ROUTES['base']}{ROUTES['check']}"
    payload = {'text': text, 'language': lang_code}
    resp = _get_req(url, verb='POST', payload=payload)
    errors = Error.parse(resp.json(), whitelist or list())
    return errors


if __name__ == '__main__':
    pass
