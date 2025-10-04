import requests
from urllib.parse import urlencode
from typing import Union, List, Optional
from dotenv import dotenv_values

config = dotenv_values(".env")
API_KEY = config["API_KEY"]


class UrlBuilder:
    """
    Класс для построения URL для Alpha Vantage News Sentiment API
    """

    def __init__(self, api_key: str):
        """
        Инициализация строителя URL

        Args:
            api_key: API ключ для Alpha Vantage
        """
        self.base_url = "https://www.alphavantage.co/query"
        self.api_key = api_key
        self.params = {
            'function': 'NEWS_SENTIMENT',
            'apikey': api_key
        }

    def add_tickers(self, tickers: Union[str, List[str]]) -> 'UrlBuilder':
        """
        Добавляет тикеры для фильтрации
        """
        if isinstance(tickers, list):
            self.params['tickers'] = ','.join(tickers)
        else:
            self.params['tickers'] = tickers
        return self

    def add_topics(self, topics: Union[str, List[str]]) -> 'UrlBuilder':
        """
        Добавляет темы для фильтрации
        'blockchain', 'earnings', 'ipo', 'mergers_and_acquisitions',
        'financial_markets', 'economy_fiscal', 'economy_monetary',
        'economy_macro', 'energy_transportation', 'finance',
        'life_sciences', 'manufacturing', 'real_estate',
        'retail_wholesale', 'technology'
        """
        if isinstance(topics, list):
            self.params['topics'] = ','.join(topics)
        else:
            self.params['topics'] = topics
        return self

    def add_time_from(self, time_from: str) -> 'UrlBuilder':
        """
        Добавляет начальное время в формате YYYYMMDDTHHMM
        """
        self.params['time_from'] = time_from
        return self

    def add_time_to(self, time_to: str) -> 'UrlBuilder':
        """
        Добавляет конечное время в формате YYYYMMDDTHHMM
        """
        self.params['time_to'] = time_to
        return self


    def add_sort(self, sort: str) -> 'UrlBuilder':
        """
        Добавляет параметр сортировки
        Args:
            sort: тип сортировки ("LATEST", "EARLIEST", "RELEVANCE")
        """
        if sort.upper() in self.SORT_VALUES:
            self.params['sort'] = sort.upper()
        else:
            raise ValueError(f"Invalid sort value. Must be one of: {self.SORT_VALUES}")
        return self

    def add_limit(self, limit: int) -> 'UrlBuilder':
        """
        Добавляет лимит результатов
        """
        if 1 <= limit <= 1000:
            self.params['limit'] = limit
        else:
            raise ValueError("Limit must be between 1 and 1000")
        return self

    def build(self) -> str:
        """
        Строит итоговый URL с добавленными параметрами
        """
        return f"{self.base_url}?{urlencode(self.params)}"

    def get_params(self) -> dict:
        """
        Возвращает текущие параметры
        """
        return self.params.copy()

    def reset(self) -> 'UrlBuilder':
        """
        Сбрасывает все параметры кроме базовых
        """
        self.params = {
            'function': 'NEWS_SENTIMENT',
            'apikey': self.api_key
        }
        return self

def simple_scraper(url):
    """ Формат date_time_from YYYYMMDDTHHMM """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        return [f"Title: \n {i['title']} \nSummary: \n {i['summary']}\n\n" for i in data["feed"]]


    except requests.exceptions.RequestException as e:
        print(f"Ошибка: {e}")
        return None




# Инициализация с API ключом
builder = UrlBuilder(api_key=API_KEY)

# Пример 1: Простой запрос с тикерами
url1 = builder.build()
print(url1)
print("".join(simple_scraper(url1)))

# # Пример 2: Запрос с темами и лимитом
# url2 = (builder.reset()
#         .add_topics(["technology", "earnings"])
#         .add_limit(100)
#         .add_sort("LATEST")
#         .build())
# print("Пример 2:", url2)
# simple_scraper(url2)
#
# # Пример 3: Полный запрос со всеми параметрами
# url3 = (builder.reset()
#         .add_tickers("COIN,CRYPTO:BTC,FOREX:USD")
#         .add_topics("blockchain")
#         .add_sort("RELEVANCE")
#         .add_limit(200)
#         .build())
# print("Пример 3:", url3)
# simple_scraper(url3)
#
# # Пример 4: Пошаговое построение
# builder.reset()
# builder.add_tickers(["MSFT", "GOOGL"])
# builder.add_topics("technology")
# builder.add_limit(50)
# url4 = builder.build()
# print("Пример 4:", url4)
# simple_scraper(url4)
#
#
#
