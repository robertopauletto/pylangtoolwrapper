# entities.py

import pylangtoolwrapper as pylt

__doc__ = """entities.py"""
__version__ = "0.1"
__changelog__ = """

"""

class Entity:
    """A generic LanguageTool Object"""
    def __init__(self, data: dict):
        self._data = data


class Error(Entity):

    def __init__(self, data):
        self.is_whitelisted = False
        self._context = None
        self._rule = None
        Entity.__init__(self,  data)
        if 'context' in self._data:
            self._context = Context(self._data['context'])
        if 'rule' in data:
            self._rule = Rule(self._data['rule'])

    @staticmethod
    def parse(data: dict, whitelist: list):
        """
        Parse response from the spell check engine and istantiate a collection
        of `Error` objects
        :param data:
        :param whitelist: words to ignore if in errors `is_whitelisted` will
                          be set to `True`
        :return: list
        """
        if 'matches' not in data:
            return None
        errors = [Error(match) for match in data['matches']]
        if whitelist:
            errors = Error.update_whitelisted(errors, whitelist)
        return errors

    @staticmethod
    def update_whitelisted(errors: list, whitelist: list):
        """
        Scan the text error in `errors` and set `is_whitelisted = True` if
        text matches a word in `whitelist` (**case insensitive**=)
        To use if `whitelist` has been updated

        :param errors:
        :param whitelist:
        :return: list
        """
        for error in errors:
            if error.text_error.lower() not in whitelist:
                continue
            error.is_whitelisted = True
        return errors

    @staticmethod
    def spell_errors(errors: list):
        """
        Filter  `error` returning misspelling errors only
        :param errors:
        :return: list of `Error`
        """
        return [error for error in errors if error.rule.type == 'misspelling']

    @staticmethod
    def whitelist_filtered(errors: list):
        return [error for error in errors if not error.is_whitelisted]

    @property
    def message(self):
        return self._data['message']

    @property
    def message_short(self):
        return self._data['shortMessage']

    @property
    def text_error(self):
        if isinstance(self._context, Context):
            return self._context.word
        return ''

    @property
    def context(self):
        if isinstance(self._context, Context):
            return self._context
        return None

    @property
    def rule(self):
        if isinstance(self._rule, Rule):
            return self._rule
        return None

    @property
    def suggestions(self):
        if 'replacements' in self._data:
            return [item['value'] for item in self._data['replacements']]
        return list()

    def absolute_position(self):
        start = self._data['offset']
        end = self._data['offset'] + self._data['length']
        return start, end, self._data['length']


class Context(Entity):
    """Where an error occurs, proximity, error text coordinates ..."""

    def __init__(self, data):
        Entity.__init__(self,  data)

    @property
    def proximity(self):
        """The text surrounding the error"""
        return self._data['text']

    @property
    def word(self):
        """The error text"""
        return self._data['text'][self.start:self.end]

    @property
    def start(self):
        """Start of the error text"""
        return self._data['offset']

    @property
    def end(self):
        """End of the error text"""
        return self.start + self._data['length']


class Rule(Entity):
    """Rule for the language"""

    def __init__(self, data):
        Entity.__init__(self,  data)
        self._categ = Category(self._data['category'])

    @property
    def id(self):
        return self._data['id']

    @property
    def sub_id(self):
        return self._data.get('subid', '')

    @property
    def description(self):
        return self._data['description']

    @property
    def urls(self):
        return self._data.get('urls', '')

    @property
    def type(self):
        return self._data.get('issueType', '')

    @property
    def category(self):
        return self._categ

    @property
    def category_name(self):
        return self._categ.name


class Category(Entity):
    """Unique rule category"""

    def __init__(self, data):
        Entity.__init__(self,  data)

    def __str__(self):
        return f'{self.id} - {self.name}'

    @property
    def id(self):
        return self._data['id']

    @property
    def name(self):
        return self._data['name']


if __name__ == '__main__':
    pass
