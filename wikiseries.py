import requests 
from bs4 import BeautifulSoup as Bfs
from dataclasses import dataclass
import logging

LOGGER_BASENAME = 'wikisearch'
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())

@dataclass
class SearchResult:
    user_search: str
    query: str
    type: str
    response_title: str 
    url: str

    @property
    def title(self):
        filters = {'episode_lists': lambda x: x[8:-9],
                   'miniseries': lambda x: x[:-13],
                   'tv_series': lambda x: x[:-12],
                   'vanila': lambda x: x}
        return filters[self.type](self.response_title)

class LoggerMixin:
    def __init__(self):
        self._logger = logging.getLogger(f'{LOGGER_BASENAME}.{self.__class__.__name__}')

class Wikiseries(LoggerMixin):

    def __init__(self):
        super(Wikiseries, self).__init__()
        self._base_url = 'https://en.wikipedia.org/w/api.php'

    @staticmethod
    def _get_types(name):
        return {'episode_lists': f'list of {name} episodes',
                'miniseries': f'{name} (miniseries)',
                'tv_series': f'{name} (tv series)',
                'vanila': name}

    def _search(self, name, term, search_type, limit):
        parameters = {'action': 'opensearch',
                      'format': 'json',
                      'formatversion': '1',
                      'namespace': '0',
                      'limit': limit,
                      'search': term}
        response = requests.get(self._base_url, params=parameters)
        if not response.ok:
            self._logger.error('Failed getting response with status code %s and response', response.status_code, response.text)
            return []
        data = response.json()
        return [SearchResult(name, data[0], search_type, *args) for args in zip(data[1], data[3])]

    def search_by_name(self, name, limit=5):
        for search_type, term in self._get_types(name).items():
            self._logger.info('Trying out search type "%s" for name "%s"', search_type, name)
            results = self._search(name, term, search_type, limit)
            if results:
                break
        self._logger.debug('Returning results "%s" for name "%s"', results, name)
        return results

    def get_by_name(self, name):
        return next((match for match in self.search_by_name(name)  
                     if match.title.lower() == name.lower()), None)