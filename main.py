from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('news_list.html')


@app.route('/news_page', methods=['POST'])
def news_page():
    data = request.get_json()
    return render_template('news_page.html', ids=data[0])

if __name__ == '__main__':    app.run()

