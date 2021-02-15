import requests
import logging
from dataclasses import dataclass


LOGGER_BASENAME = 'wikisearch'
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


@dataclass
class SearchResult:
    original_search: str
    title: str
    url: str
    type: str

class LoggerMixin:
    def __init__(self) -> None:
        self._logger = logging.getLogger(f'{LOGGER_BASENAME}.{self.__class__.__name__}')

class Wikiseries(LoggerMixin):
    def __init__(self) -> None:
        super(Wikiseries, self).__init__()
        self.url = 'https://en.wikipedia.org/w/api.php'

    @staticmethod
    def _get_term_and_type(name):
        types = {'episode_list': f'list of {name} episodes',
                 'vanilla': f'{name}',
                 'miniseries': f'{name} (miniseries)'}
        return types

    def _search(self, original_name, term, search_type):
        parameters = {'action': 'opensearch',
                      'format': 'json',
                      'formatversion':'2',
                      'search': term,
                      'namespace': '0',
                      'limit': '3'}
        response = requests.get(self.url, params=parameters)
        if not response.ok:
            self._logger.error('Reponse failed with code %s and text %s', response.status_code, response.text)
        return [SearchResult(original_name, *args, search_type) 
                for args in zip(response.json()[1], response.json()[3])]

    def search_by_name(self, name):
        for search_type, term in self._get_term_and_type(name).items():
            self._logger.info('Searching for type %s and name %s', search_type, name)
            result = self._search(name, term, search_type)
            if result:
                break
        return result

    def get_by_name(self, name):
        return next((result for result in self.search_by_name(name)
                     if result.original_search.lower() == name.lower()), None)