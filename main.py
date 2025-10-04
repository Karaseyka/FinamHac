from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('news_list.html')


@app.route('/news_page/<ids>', methods=['GET'])
def news_page(ids):
    # вот тут передается АДИ новости - по нему надо остальную инфу
    return render_template('news_page.html', ids=ids)


@app.route('/get_news_id', methods=['POST'])
def get_news_id():
    data = request.get_json()
    return redirect(url_for('news_page', ids=data['news_id']))


@app.route('/set_filter', methods=['POST'])
def get_period_data():
    data = request.get_json()['period']
    print(data)
    # data 1h or 24h or 1w ВОТ ПРЯМ ТАК КАК НАПИСАНО И передавать как в формате ниже
    return jsonify([
        {'id': '1',
         'headline': 'Курс рубля вырос',
         'short_descr': 'По неопределенным обстоятельствам рубль стоит 10 евро',
         'why_now': 'Актуально ДЛЯ ВСЕХ',
         'sources': 'https://www.kommersant.ru/',
         'hotness': '1',
         'timeline': '14.88 04.10.2026'
         },
        {'id': '1',
         'headline': 'Курс рубля вырос',
         'short_descr': 'По неопределенным обстоятельствам рубль стоит 10 евро',
         'why_now': 'Актуально ДЛЯ ВСЕХ',
         'sources': 'https://www.kommersant.ru/',
         'hotness': '1',
         'timeline': '14.88 04.10.2026'
         },
        {'id': '1',
         'headline': 'Курс рубля вырос',
         'short_descr': 'По неопределенным обстоятельствам рубль стоит 10 евро',
         'why_now': 'Актуально ДЛЯ ВСЕХ',
         'sources': 'https://www.kommersant.ru/',
         'hotness': '1',
         'timeline': '14.88 04.10.2026'
         },
        {'id': '1',
         'headline': 'Курс рубля вырос',
         'short_descr': 'По неопределенным обстоятельствам рубль стоит 10 евро',
         'why_now': 'Актуально ДЛЯ ВСЕХ',
         'sources': 'https://www.kommersant.ru/',
         'hotness': '1',
         'timeline': '14.88 04.10.2026'
         },
        {'id': '1',
         'headline': 'Курс рубля вырос',
         'short_descr': 'По неопределенным обстоятельствам рубль стоит 10 евро',
         'why_now': 'Актуально ДЛЯ ВСЕХ',
         'sources': 'https://www.kommersant.ru/',
         'hotness': '1',
         'timeline': '14.88 04.10.2026'
         },
        {'id': '1',
         'headline': 'Курс рубля вырос',
         'short_descr': 'По неопределенным обстоятельствам рубль стоит 10 евро',
         'why_now': 'Актуально ДЛЯ ВСЕХ',
         'sources': 'https://www.kommersant.ru/',
         'hotness': '1',
         'timeline': '14.88 04.10.2026'
         }
    ])


@app.route('/create_news', methods=['GET'])
def create_news_window():
    pass


if __name__ == '__main__':    app.run()

