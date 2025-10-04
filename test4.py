import feedparser
import pandas as pd
from datetime import datetime
import re
from googletrans import Translator
import time
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Расширенный словарь RSS-источников с новыми специализированными сайтами
feeds_dict = {
    # Специализированные финансовые блоги и издания
    'e-disclosure': 'https://www.e-disclosure.ru/vse-novosti',
    'Investing.com RSS': 'https://ru.investing.com/rss/news.rss',
    'Финмаркет': 'https://www.finmarket.ru/news/',

    # Основные финансовые СМИ
    'WSJ Markets': 'https://feeds.a.dj.com/rss/RSSMarketsMain.xml',
    'Financial Times': 'https://www.ft.com/?format=rss',
    'Bloomberg ETF': 'https://www.bloomberg.com/feed/podcast/etf-report.xml',
    'MarketWatch': 'https://www.marketwatch.com/rss/topstories',
    'The Economist': 'https://www.economist.com/latest/rss.xml',
    'CNBC': 'https://www.cnbc.com/id/100003114/device/rss/rss.html',
    'Forbes Business': 'https://www.forbes.com/business/feed/',
    'Business Insider': 'https://www.businessinsider.com/rss',

    # Российские финансовые СМИ
    'Ведомости - Финансы': 'https://www.vedomosti.ru/rss/rubric/finance',
    'Ведомости - Рынки': 'https://www.vedomosti.ru/rss/rubric/finance/markets',
    'Ведомости - Банки': 'https://www.vedomosti.ru/rss/rubric/finance/banks',
    'Коммерсант': 'https://www.kommersant.ru/RSS/main.xml',
    'РБК': 'https://www.rbc.ru/rss/finances',
    'Lenta_comp': 'https://lenta.ru/rss/news/economics/companies/',
    'Lenta_mark': 'https://lenta.ru/rss/news/economics/markets/',
    'Lenta_fin': 'https://lenta.ru/rss/news/economics/finance/'
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


def translate_news_item(news_item):
    """Перевод заголовка и описания новости при необходимости"""
    title = news_item['Заголовок']
    description = news_item['Описание']

    # Проверяем, нужен ли перевод для заголовка
    if translator.needs_translation(title):
        translated_title = translator.translate_text(title)
        news_item['Заголовок'] = f"[ПЕРЕВОД] {translated_title}"
        news_item['Оригинальный_заголовок'] = title
    else:
        news_item['Оригинальный_заголовок'] = title

    # Проверяем, нужен ли перевод для описания
    if translator.needs_translation(description):
        translated_description = translator.translate_text(description)
        news_item['Описание'] = translated_description
        news_item['Оригинальное_описание'] = description
    else:
        news_item['Оригинальное_описание'] = description

    news_item['Переведено'] = translator.needs_translation(title) or translator.needs_translation(description)

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
    с автоматическим переводом иностранных статей
    """
    all_news = []

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
                combined_text = f"{title} {description}"

                # СТРОГАЯ проверка: относится ли новость к финансовой/трейдинговой тематике
                if contains_strict_finance_keywords(combined_text):
                    news_item = {
                        'Источник': source_name,
                        'Заголовок': title,
                        'Ссылка': entry.get('link', 'Нет ссылки'),
                        'Дата публикации': entry.get('published', 'Нет даты'),
                        'Описание': description,
                        'Дата парсинга': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }

                    # Переводим новость если нужно
                    news_item = translate_news_item(news_item)

                    if news_item['Переведено']:
                        translated_count += 1

                    all_news.append(news_item)
                    news_count += 1

            current_source_count = len([n for n in all_news if n['Источник'] == source_name])
            print(f"   Найдено финансовых/трейдинговых новостей: {current_source_count}")
            if translated_count > 0:
                print(f"   Переведено новостей: {translated_count}")

        except Exception as e:
            print(f"Ошибка при парсинге {source_name}: {e}")
            continue

    # Создаем DataFrame
    df = pd.DataFrame(all_news)
    return df


def save_news_with_timestamp(df):
    """Сохраняет DataFrame с временной меткой в имени файла"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'strict_financial_news_{timestamp}.csv'

    # Выбираем колонки для сохранения (включая новые колонки перевода)
    columns_to_save = ['Источник', 'Заголовок', 'Ссылка', 'Дата публикации',
                       'Описание', 'Дата парсинга', 'Переведено']

    # Добавляем оригинальные колонки если они есть
    if 'Оригинальный_заголовок' in df.columns:
        columns_to_save.extend(['Оригинальный_заголовок', 'Оригинальное_описание'])

    df.to_csv(filename, index=False, encoding='utf-8-sig', columns=columns_to_save)
    return filename


if __name__ == "__main__":
    print("Начинаем СТРОГИЙ парсинг финансовых и трейдинговых новостей...")
    print(f"Всего источников: {len(feeds_dict)}")
    print(f"Строгих ключевых слов для фильтрации: {len(STRICT_FINANCE_KEYWORDS)}")
    print("-" * 50)

    # Парсим все ленты
    news_df = parse_all_feeds(feeds_dict)

    # Сохраняем результат
    if len(news_df) > 0:
        filename = save_news_with_timestamp(news_df)

        # Статистика по переводам
        translated_count = len(news_df[news_df['Переведено'] == True]) if 'Переведено' in news_df.columns else 0

        print(f"\nПарсинг завершен! Собрано финансовых/трейдинговых новостей: {len(news_df)}")
        print(f"Переведено иностранных новостей: {translated_count}")
        print(f"Результаты сохранены в файл: {filename}")

        # Показываем статистику по источникам
        print("\nСтатистика по источникам:")
        source_stats = news_df['Источник'].value_counts()
        for source, count in source_stats.items():
            translated_from_source = len(news_df[(news_df['Источник'] == source) & (
                        news_df['Переведено'] == True)]) if 'Переведено' in news_df.columns else 0
            print(f"   {source}: {count} новостей (переведено: {translated_from_source})")

        # Показываем первые 5 строк
        print("\nПервые 5 финансовых/трейдинговых новостей:")
        display_columns = ['Источник', 'Заголовок']
        if 'Переведено' in news_df.columns:
            display_columns.append('Переведено')
        print(news_df[display_columns].head())

    else:
        print("\nНе найдено новостей по заданным строгим ключевым словам.")



