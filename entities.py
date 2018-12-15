# entities.py

from pylangtoolwrapper import PyLangToolWrapperException

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
        self._context = None
        Entity.__init__(self,  data)
        if 'context' in self._data:
            self._context = Context(self._data['context'])

    @staticmethod
    def parse(data: dict):
        if not 'matches' in data:
            return None
        return [Error(matches) for matches in data['matches']]

    @staticmethod
    def spell_errors(errors: list):
        """
        Filter  `error` returning misspelling errors only
        :param errors:
        :return: list of `Error`
        """
        return [error for error in errors if
                error.rule.type == 'misspelling']

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
        return self._context

    @property
    def suggestions(self):
        if 'replacements' in self._data:
            return [item['value'] for item in self._data['replacements']]
        return list()

    def absolute_position(self, text):
        start = text.index(self._context.proximity)
        return start + (self._context.start)


class Context(Entity):
    """Where an error occurs, proximity, error text corrdinates"""

    def __init__(self, data):
        Entity.__init__(self,  data)

    @property
    def proximity(self):
        """The text surrounging the errore"""
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
        return self.start + (self.start + self._data['length'])

    @property
    def rule(self):
        if not 'rule' in self._data:
            return None
        return Rule(self._data['rule'])


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
