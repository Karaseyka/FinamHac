import feedparser
import pandas as pd
from datetime import datetime
import re
from googletrans import Translator
import time
import logging
import requests
from bs4 import BeautifulSoup
import html
import json
from urllib.parse import urljoin
import LLM
# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Расширенный словарь RSS-источников с новыми специализированными сайтами
feeds_dict = {
    'Forbes Business': 'https://www.forbes.com/business/feed/',
    # Российские финансовые СМИ
    'Ведомости - Финансы': 'https://www.vedomosti.ru/rss/rubric/finance',
    'Ведомости - Рынки': 'https://www.vedomosti.ru/rss/rubric/finance/markets',
    'Ведомости - Банки': 'https://www.vedomosti.ru/rss/rubric/finance/banks',
    'Коммерсант': 'https://www.kommersant.ru/RSS/main.xml',
    'РБК': 'https://www.rbc.ru/rss/finances',
}

# СТРОГИЙ список ключевых слов ТОЛЬКО для финансов, трейдинга и инвестиций
STRICT_FINANCE_KEYWORDS = [
    # Трейдинг и биржевая торговля
    'трейдинг', 'трейдер', 'трейдера', 'трейдеру', 'трейдером', 'трейдере', 'трейдеры', 'трейдеров', 'трейдерам',
    'трейдерами', 'трейдерах',
    'трейдинг', 'трейдинга', 'трейдингу', 'трейдингом', 'трейдинге',
    'алготрейдинг', 'алготрейдинга', 'алготрейдингу', 'алготрейдингом', 'алготрейдинге',
    'дневной трейдинг', 'свинг трейдинг', 'позиционный трейдинг',
    'скальпинг', 'скальпинга', 'скальпингу', 'скальпингом', 'скальпинге',
    'биржевой', 'биржевая', 'биржевое', 'биржевые', 'биржевых', 'биржевым', 'биржевыми',

    # Финансовые инструменты
    'акция', 'акции', 'акций', 'акцию', 'акцией', 'акции', 'акциям', 'акциями', 'акциях',
    'облигация', 'облигации', 'облигаций', 'облигацию', 'облигацией', 'облигации', 'облигациям', 'облигациями',
    'облигациях',
    'фьючерс', 'фьючерсы', 'фьючерсов', 'фьючерсу', 'фьючерсом', 'фьючерсе', 'фьючерсам', 'фьючерсами', 'фьючерсах',
    'опцион', 'опционы', 'опционов', 'опциону', 'опционом', 'опционе', 'опционам', 'опционами', 'опционах',
    'дериватив', 'деривативы', 'деривативов', 'деривативу', 'деривативом', 'деривативе', 'деривативам', 'деривативами',
    'деривативах',
    'ETF', 'ETFs', 'ЕТФ', 'биржевой фонд',
    'портфель', 'портфеля', 'портфелю', 'портфелем', 'портфеле', 'портфели', 'портфелей', 'портфелям', 'портфелями',
    'портфелях',

    # Рынки и биржи
    'фондовый рынок', 'фондового рынка', 'фондовому рынку', 'фондовым рынком', 'фондовом рынке', 'ЦБ',
    'рынок акций', 'рынка акций', 'рынку акций', 'рынком акций', 'рынке акций',
    'ММВБ', 'Мосбиржа', 'MOEX', 'RTS', 'SPB',
    'NYSE', 'NASDAQ', 'LSE', 'XETRA', 'TSE',
    'свечной анализ', 'японские свечи', 'свеча', 'свечи', 'свечей',
    'таймфрейм', 'таймфреймы', 'таймфреймов', 'таймфрейму', 'таймфреймом', 'таймфрейме', 'таймфреймам', 'таймфреймами',
    'таймфреймах',

    # Инвестиции и управление капиталом
    'инвестиция', 'инвестиции', 'инвестиций', 'инвестицию', 'инвестицией', 'инвестиции', 'инвестициям', 'инвестициями',
    'инвестициях',
    'инвестиционный', 'инвестиционная', 'инвестиционное', 'инвестиционные', 'инвестиционного', 'инвестиционной',
    'инвестиционному', 'инвестиционным', 'инвестиционном',
    'портфельные инвестиции', 'прямые инвестиции',
    'управление капиталом', 'управления капиталом', 'управлению капиталом', 'управлением капиталом',
    'управлении капиталом',
    'распределение активов', 'распределения активов', 'распределению активов', 'распределением активов',
    'распределении активов',
    'диверсификация', 'диверсификации', 'диверсификацию', 'диверсификацией', 'диверсификации',

    # Технический анализ
    'технический анализ', 'технического анализа', 'техническому анализу', 'техническим анализом', 'техническом анализе',
    'индикатор', 'индикаторы', 'индикаторов', 'индикатору', 'индикатором', 'индикаторе', 'индикаторам', 'индикаторами',
    'индикаторах',
    'RSI', 'Relative Strength Index', 'MACD', 'Moving Average', 'Bollinger Bands', 'Боллинджер',
    'поддержка', 'поддержки', 'поддержке', 'поддержкой', 'поддержке', 'поддержкам', 'поддержками', 'поддержках',
    'сопротивление', 'сопротивления', 'сопротивлению', 'сопротивлением', 'сопротивлении', 'сопротивлениям',
    'сопротивлениями', 'сопротивлениях',
    'тренд', 'тренды', 'трендов', 'тренду', 'трендом', 'тренде', 'трендам', 'трендами', 'трендах',
    'прорыв', 'прорывы', 'прорывов', 'прорыву', 'прорывом', 'прорыве', 'прорывам', 'прорывами', 'прорывах',
    'консолидация', 'консолидации', 'консолидацию', 'консолидацией', 'консолидации',

    # Фундаментальный анализ
    'фундаментальный анализ', 'фундаментального анализа', 'фундаментальному анализу', 'фундаментальным анализом',
    'фундаментальном анализе',
    'P/E', 'P/S', 'P/B', 'EV/EBITDA', 'дивидендная доходность', 'дивидендной доходности', 'дивидендную доходность',
    'дивидендной доходностью', 'дивидендной доходности',
    'выручка', 'выручки', 'выручку', 'выручкой', 'выручке', 'выручек', 'выручкам', 'выручками', 'выручках',
    'прибыль', 'прибыли', 'прибылью', 'прибыли', 'прибылей', 'прибылям', 'прибылями', 'прибылях',
    'EBITDA', 'чистая прибыль', 'операционная прибыль',
    'отчетность', 'отчетности', 'отчетность', 'отчетностью', 'отчетности', 'отчетностей', 'отчетностям', 'отчетностями',
    'отчетностях',

    # Риск-менеджмент
    'риск-менеджмент', 'риск-менеджмента', 'риск-менеджменту', 'риск-менеджментом', 'риск-менеджменте',
    'мани-менеджмент', 'мани-менеджмента', 'мани-менеджменту', 'мани-менеджментом', 'мани-менеджменте',
    'стоп-лосс', 'стоп-лосса', 'стоп-лоссу', 'стоп-лоссом', 'стоп-лоссе', 'стоп-лоссы', 'стоп-лоссов', 'стоп-лоссам',
    'стоп-лоссами', 'стоп-лоссах',
    'тейк-профит', 'тейк-профита', 'тейк-профиту', 'тейк-профитом', 'тейк-профите', 'тейк-профиты', 'тейк-профитов',
    'тейк-профитам', 'тейк-профитами', 'тейк-профитах',
    'профит', 'профита', 'профиту', 'профитом', 'профите', 'профиты', 'профитов', 'профитам', 'профитами', 'профитах',
    'лосс', 'лосса', 'лоссу', 'лоссом', 'лоссе', 'лоссы', 'лоссов', 'лоссам', 'лоссами', 'лоссах',

    # Английские термины (строго финансовые)
    'trading', 'trader', 'traders', 'day trading', 'swing trading', 'position trading',
    'algorithmic trading', 'algotrading', 'scalping',
    'stock', 'stocks', 'share', 'shares',
    'bond', 'bonds', 'future', 'futures', 'option', 'options', 'derivative', 'derivatives',
    'portfolio', 'portfolios', 'asset allocation',
    'technical analysis', 'fundamental analysis',
    'indicator', 'indicators', 'RSI', 'MACD', 'moving average', 'Bollinger Bands',
    'support', 'resistance', 'trend', 'breakout', 'consolidation',
    'risk management', 'money management', 'stop loss', 'take profit',
    'P/E ratio', 'P/S ratio', 'P/B ratio', 'dividend yield', 'revenue', 'profit', 'EBITDA',
    'exchange', 'stock exchange', 'broker', 'brokerage'
]


class NewsTranslator:
    def __init__(self):
        self.translator = Translator()
        self.translation_cache = {}

    def needs_translation(self, text):
        """Определяем, нужен ли перевод (проверяем наличие кириллицы)"""
        if not text:
            return False
        # Если в тексте меньше 30% кириллицы, считаем что нужен перевод
        cyrillic_count = sum(1 for char in text if '\u0400' <= char <= '\u04FF')
        return cyrillic_count / len(text) < 0.3

    def translate_text(self, text, max_retries=3):
        """Перевод текста с кэшированием и повторными попытками"""
        if not text or len(text.strip()) < 10:
            return text

        # Проверяем кэш
        text_hash = hash(text)
        if text_hash in self.translation_cache:
            return self.translation_cache[text_hash]

        for attempt in range(max_retries):
            try:
                translation = self.translator.translate(text, dest='ru', src='en')
                translated_text = translation.text

                # Сохраняем в кэш
                self.translation_cache[text_hash] = translated_text

                # Задержка чтобы избежать блокировки
                time.sleep(0.1)

                return translated_text

            except Exception as e:
                logging.warning(f"Ошибка перевода (попытка {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                continue

        # Если все попытки неудачны, возвращаем оригинальный текст
        logging.error(f"Не удалось перевести текст после {max_retries} попыток")
        return text


# Создаем глобальный объект переводчика
translator = NewsTranslator()


class SmartLabParser:
    def __init__(self):
        self.base_url = "https://smartlab.news/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_news_list(self):
        """Получает список новостей с главной страницы"""
        try:
            response = self.session.get(self.base_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            news_items = []

            # Ищем все блоки с новостями
            news_blocks = soup.find_all('div', class_='news__line')

            for block in news_blocks:
                try:
                    # Извлекаем дату и время
                    date_elem = block.find('div', class_='news__date')
                    date = date_elem.get('data-tippy-content', '') if date_elem else ''
                    time_text = date_elem.text.strip() if date_elem else ''

                    # Извлекаем иконку типа новости
                    icon_elem = block.find('div', class_='news__icon')
                    icon_text = icon_elem.text.strip() if icon_elem else ''
                    icon_title = icon_elem.get('title', '') if icon_elem else ''

                    # Извлекаем заголовок и ссылку
                    link_elem = block.find('div', class_='news__link').find('a') if block.find('div',
                                                                                               class_='news__link') else None

                    if link_elem:
                        title = link_elem.text.strip()
                        article_url = link_elem.get('href')

                        # Преобразуем относительную ссылку в абсолютную
                        if article_url and not article_url.startswith('http'):
                            article_url = urljoin(self.base_url, article_url)

                        news_item = {
                            'title': title,
                            'url': article_url,
                            'date': date,
                            'time': time_text,
                            'icon': icon_text,
                            'icon_title': icon_title
                        }
                        news_items.append(news_item)

                except Exception as e:
                    print(f"Ошибка при обработке блока новости: {e}")
                    continue

            return news_items

        except Exception as e:
            print(f"Ошибка при получении списка новостей: {e}")
            return []

    def get_article_text(self, article_url):
        """Получает полный текст статьи по URL"""
        try:
            response = self.session.get(article_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Извлекаем заголовок статьи со страницы
            title_element = soup.find('h1', class_='article__title')
            article_title = title_element.text.strip() if title_element else "Заголовок не найден"

            # Извлекаем основной текст статьи
            article_text_div = soup.find('div', class_='article__text')
            if article_text_div:
                # Удаляем баннеры и другие ненужные элементы
                for unwanted in article_text_div.find_all(['script', 'style', 'div', 'a']):
                    unwanted.decompose()

                # Извлекаем текст из параграфов
                paragraphs = article_text_div.find_all('p')
                if paragraphs:
                    full_text = '\n'.join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
                else:
                    # Если параграфов нет, извлекаем весь текст
                    full_text = article_text_div.get_text(strip=True)
            else:
                full_text = "Текст статьи не найден"

            return {
                'title': article_title,
                'full_text': full_text
            }

        except Exception as e:
            print(f"Ошибка при получении текста статьи {article_url}: {e}")
            return {
                'title': "Ошибка",
                'full_text': f"Не удалось загрузить статью: {str(e)}"
            }

    def parse_smartlab_news(self, limit=10):
        """Парсит новости с SmartLab и возвращает в формате для основного скрипта"""
        print("Парсим: SmartLab")
        news_list = self.get_news_list()
        smartlab_news = []

        for i, news in enumerate(news_list[:limit], 1):
            print(f"   Обрабатываем новость {i}/{min(limit, len(news_list))}: {news['title'][:50]}...")

            # Получаем полный текст статьи
            article_data = self.get_article_text(news['url'])

            news_item = {
                'ID': None,  # Будет установлен позже
                'Источник': 'SmartLab',
                'Заголовок': news['title'],
                'Ссылка': news['url'],
                'Дата публикации': f"{news['date']} {news['time']}",
                'Описание': article_data['full_text'][:200] + '...' if len(article_data['full_text']) > 200 else
                article_data['full_text'],
                'Полный_текст': article_data['full_text'],
                'Дата парсинга': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'Статус_загрузки_текста': 'Успешно' if article_data['full_text'] and article_data[
                    'full_text'] != "Текст статьи не найден" else 'Ошибка',
                'Тип_иконки': news['icon'],
                'Заголовок_иконки': news['icon_title']
            }

            smartlab_news.append(news_item)
            news_text = f"ЗАГОЛОВОК: {news_item['Заголовок']}\n\nОПИСАНИЕ: {news_item['Описание']}\n\nПОЛНЫЙ ТЕКСТ: {news_item['Полный_текст']}\n\nИСТОЧНИК: SmartLab"
            ai_analysis_json = LLM.get_news_info(news_text)
            print(ai_analysis_json, "buuu")
            # Выводим в консоль
            print(f"\n{'=' * 80}")
            print(f"ИСТОЧНИК: SmartLab")
            print(f"ЗАГОЛОВОК: {news['title']}")
            print(f"ССЫЛКА: {news['url']}")
            print(f"СТАТУС ЗАГРУЗКИ: {news_item['Статус_загрузки_текста']}")
            print(f"ПОЛНЫЙ ТЕКСТ НОВОСТИ:")
            print("-" * 50)
            display_text = news_item['Полный_текст']
            if display_text and display_text != "Текст статьи не найден":
                print(display_text[:1500] + "..." if len(display_text) > 1500 else display_text)
            else:
                print(display_text)
            print(f"{'=' * 80}\n")

            # Задержка между запросами чтобы не перегружать сервер
            time.sleep(2)

        print(f"   Найдено новостей в SmartLab: {len(smartlab_news)}")
        return smartlab_news


def fetch_full_article(url):
    """
    Загружает полный текст новости с веб-страницы
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Удаляем ненужные элементы (скрипты, стили)
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()

        # Поиск основного контента - распространенные селекторы
        content_selectors = [
            'article',
            '.article',
            '.content',
            '.post-content',
            '.news-content',
            '.story__content',
            '.entry-content',
            '[class*="content"]',
            '[class*="article"]',
            '[class*="post"]'
        ]

        content = None
        for selector in content_selectors:
            content = soup.select_one(selector)
            if content:
                break

        # Если не нашли по селекторам, берем основной текст страницы
        if not content:
            content = soup.find('body')

        if content:
            # Извлекаем текст и очищаем его
            text = content.get_text(separator='\n', strip=True)
            # Удаляем лишние пустые строки
            text = re.sub(r'\n\s*\n', '\n\n', text)
            # Декодируем HTML-сущности
            text = html.unescape(text)
            return text[:5000]  # Ограничиваем размер для производительности
        else:
            return None  # Возвращаем None вместо текста ошибки

    except Exception as e:
        logging.error(f"Ошибка при загрузке статьи {url}: {e}")
        return None  # Возвращаем None при ошибке


def translate_news_item(news_item):
    """Перевод заголовка, описания и полного текста новости при необходимости"""
    title = news_item['Заголовок']
    description = news_item['Описание']
    full_text = news_item.get('Полный_текст', '')

    translated_parts = False

    # Проверяем, нужен ли перевод для заголовка
    if translator.needs_translation(title):
        translated_title = translator.translate_text(title)
        news_item['Заголовок'] = f"[ПЕРЕВОД] {translated_title}"
        news_item['Оригинальный_заголовок'] = title
        translated_parts = True
    else:
        news_item['Оригинальный_заголовок'] = title

    # Проверяем, нужен ли перевод для описания
    if translator.needs_translation(description):
        translated_description = translator.translate_text(description)
        news_item['Описание'] = translated_description
        news_item['Оригинальное_описание'] = description
        translated_parts = True
    else:
        news_item['Оригинальное_описание'] = description

    # Проверяем, нужен ли перевод для полного текста
    if full_text and translator.needs_translation(full_text):
        translated_full_text = translator.translate_text(full_text)
        news_item['Полный_текст'] = translated_full_text
        news_item['Оригинальный_полный_текст'] = full_text
        translated_parts = True
    elif full_text:
        news_item['Оригинальный_полный_текст'] = full_text

    news_item['Переведено'] = translated_parts

    return news_item


def contains_strict_finance_keywords(text):
    """Строгая проверка на финансовые/трейдинговые ключевые слова"""
    if not text:
        return False

    text_lower = text.lower()

    # Проверяем каждое ключевое слово
    for keyword in STRICT_FINANCE_KEYWORDS:
        if re.search(r'\b' + re.escape(keyword.lower()) + r'\b', text_lower):
            return True

    return False


def parse_all_feeds(feeds_dict):
    """
    Парсит все RSS-ленты из словаря и возвращает DataFrame с новостями,
    отфильтрованными СТРОГО по финансовой и трейдинговой тематике
    с автоматическим переводом иностранных статей и загрузкой полного текста
    """
    all_news = []
    news_counter = 0  # Счетчик для простых числовых ID

    # Парсим RSS-ленты
    for source_name, rss_url in feeds_dict.items():
        try:
            print(f"Парсим: {source_name}")

            # Парсим RSS-ленту
            feed = feedparser.parse(rss_url)

            news_count = 0
            translated_count = 0

            # Обрабатываем каждую новость в ленте
            for entry in feed.entries:
                # Получаем заголовок и описание
                title = entry.get('title', '')
                description = entry.get('summary', entry.get('description', ''))
                link = entry.get('link', '')
                combined_text = f"{title} {description}"

                # СТРОГАЯ проверка: относится ли новость к финансовой/трейдинговой тематике
                if contains_strict_finance_keywords(combined_text):
                    # Получаем полный текст новости
                    print(f"   Загружаем полный текст: {title[:50]}...")
                    full_text = fetch_full_article(link)

                    # Создаем новость независимо от того, загрузился ли полный текст
                    news_item = {
                        'ID': news_counter,  # Используем простой числовой ID
                        'Источник': source_name,
                        'Заголовок': title,
                        'Ссылка': link,
                        'Дата публикации': entry.get('published', 'Нет даты'),
                        'Описание': description,
                        'Полный_текст': full_text if full_text else "Не удалось загрузить полный текст",
                        'Дата парсинга': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'Статус_загрузки_текста': 'Успешно' if full_text else 'Ошибка'
                    }

                    # Переводим новость если нужно (только если есть контент для перевода)
                    news_item = translate_news_item(news_item)

                    if news_item['Переведено']:
                        translated_count += 1

                    all_news.append(news_item)
                    news_count += 1
                    news_counter += 1  # Увеличиваем счетчик для следующей новости

                    # ВЫВОДИМ ПОЛНЫЙ ТЕКСТ НОВОСТИ В КОНСОЛЬ
                    print(f"\n{'=' * 80}")
                    print(f"ID: {news_item['ID']}")  # Показываем простой ID в консоли
                    print(f"ИСТОЧНИК: {source_name}")
                    print(f"ЗАГОЛОВОК: {news_item['Заголовок']}")  # Показываем уже переведенный заголовок
                    print(f"ССЫЛКА: {link}")
                    print(f"СТАТУС ЗАГРУЗКИ: {news_item['Статус_загрузки_текста']}")
                    print(f"ПОЛНЫЙ ТЕКСТ НОВОСТИ:")
                    print("-" * 50)
                    news_text = f"ЗАГОЛОВОК: {news_item['Заголовок']}\n\nОПИСАНИЕ: {news_item['Описание']}\n\nПОЛНЫЙ ТЕКСТ: {news_item['Полный_текст']}\n\nИСТОЧНИК: SmartLab"
                    ai_analysis_json = LLM.get_news_info(news_text)

                    # Показываем переведенный текст, если он есть
                    display_text = news_item['Полный_текст']
                    if display_text and display_text != "Не удалось загрузить полный текст":
                        print(display_text[:1500] + "..." if len(display_text) > 1500 else display_text)
                    else:
                        print(display_text)

                    print(f"{'=' * 80}\n")

            current_source_count = len([n for n in all_news if n['Источник'] == source_name])
            print(f"   Найдено финансовых/трейдинговых новостей: {current_source_count}")
            if translated_count > 0:
                print(f"   Переведено новостей: {translated_count}")

        except Exception as e:
            print(f"Ошибка при парсинге {source_name}: {e}")
            continue

    # Парсим SmartLab
    smartlab_parser = SmartLabParser()
    smartlab_news = smartlab_parser.parse_smartlab_news(limit=10)

    # Добавляем новости из SmartLab в общий список
    for news_item in smartlab_news:
        # Проверяем ключевые слова для SmartLab новостей
        combined_text = f"{news_item['Заголовок']} {news_item['Описание']}"
        if contains_strict_finance_keywords(combined_text):
            news_item['ID'] = news_counter
            # Переводим новость если нужно
            news_item = translate_news_item(news_item)
            all_news.append(news_item)
            news_counter += 1

    # Создаем DataFrame
    df = pd.DataFrame(all_news)
    return df


def save_news_with_timestamp(df):
    """Сохраняет DataFrame с временной меткой в имени файла"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'full_financial_news_{timestamp}.csv'

    # Выбираем колонки для сохранения (включая новые колонки перевода)
    columns_to_save = ['ID', 'Источник', 'Заголовок', 'Ссылка', 'Дата публикации',
                       'Описание', 'Полный_текст', 'Дата парсинга', 'Переведено',
                       'Статус_загрузки_текста']

    # Добавляем оригинальные колонки если они есть
    if 'Оригинальный_заголовок' in df.columns:
        columns_to_save.extend(['Оригинальный_заголовок', 'Оригинальное_описание'])

    if 'Оригинальный_полный_текст' in df.columns:
        columns_to_save.append('Оригинальный_полный_текст')

    # Добавляем колонки SmartLab если они есть
    if 'Тип_иконки' in df.columns:
        columns_to_save.append('Тип_иконки')
    if 'Заголовок_иконки' in df.columns:
        columns_to_save.append('Заголовок_иконки')

    # Сохраняем только существующие колонки
    existing_columns = [col for col in columns_to_save if col in df.columns]
    df.to_csv(filename, index=False, encoding='utf-8-sig', columns=existing_columns)
    return filename


if __name__ == "__main__":
    print("Начинаем парсинг финансовых новостей с полным текстом...")
    print(f"Всего RSS-источников: {len(feeds_dict)}")
    print(f"Строгих ключевых слов для фильтрации: {len(STRICT_FINANCE_KEYWORDS)}")
    print("=" * 60)

    # Парсим все ленты
    news_df = parse_all_feeds(feeds_dict)

    # Сохраняем результат
    if len(news_df) > 0:
        filename = save_news_with_timestamp(news_df)

        # Статистика по переводам
        translated_count = len(news_df[news_df['Переведено'] == True]) if 'Переведено' in news_df.columns else 0

        # Статистика по загрузке полного текста
        successful_loads = len(news_df[news_df[
                                           'Статус_загрузки_текста'] == 'Успешно']) if 'Статус_загрузки_текста' in news_df.columns else 0

        print(f"\nПарсинг завершен! Собрано финансовых/трейдинговых новостей: {len(news_df)}")
        print(f"Переведено иностранных новостей: {translated_count}")
        print(f"Успешно загружено полных текстов: {successful_loads} из {len(news_df)}")
        print(f"Результаты сохранены в файл: {filename}")

        # Показываем статистику по источникам
        print("\nСтатистика по источникам:")
        source_stats = news_df['Источник'].value_counts()
        for source, count in source_stats.items():
            translated_from_source = len(news_df[(news_df['Источник'] == source) & (
                        news_df['Переведено'] == True)]) if 'Переведено' in news_df.columns else 0
            successful_from_source = len(news_df[(news_df['Источник'] == source) & (news_df[
                                                                                        'Статус_загрузки_текста'] == 'Успешно')]) if 'Статус_загрузки_текста' in news_df.columns else 0
            print(
                f"   {source}: {count} новостей (переведено: {translated_from_source}, загружено текстов: {successful_from_source})")




    else:
        print("\nНе найдено новостей по заданным строгим ключевым словам.")
