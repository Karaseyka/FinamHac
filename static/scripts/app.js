document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM загружен - отправляю запрос');
    loadData();
});


let news_table = document.getElementById('news-container');
let use_filter = document.getElementById('filter');
let create_news = document.getElementById('create');
const news_container = document.getElementById('news-container');

use_filter.addEventListener('click', async function() {loadData();});

async function loadData() {
    let selected_element = document.getElementById('selector');

    let selected_value = selected_element.value;
    console.log(selected_value);
    $.ajax({
        url: '/set_filter',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            'period': selected_value
        }),
        success: function(data) {
            console.log(data[0]);
            while (news_container.firstChild) {
                news_container.removeChild(news_container.firstChild);
            }
            for (news of data) {
                let id = news['id'];
                let headline = news['headline'];
                let description = news['short_descr'];
                let why_now = news['why_now'];
                let sources = news['sources'];
                let hotness = news['hotness'];
                let timeline = news['timeline'];


                news_container.innerHTML += `
                    <div class="card">
                        <h3 class="headline">${headline}</h3>
                        <p class="description">${description}</p>
                        <p class="why-not">${why_now}</p>
                        <div class="sources">
                            <p>Сообщают: </p>
                            <a href="${sources}">${sources}</a>
                        </div>
                        <div class="last-line">
                            <div>
                                <p class="hotness">Оценка "горячести": ${hotness}</p>
                                <button class="standard-button" id="${id}">Перейти к новости</button>
                            </div>

                            <div>
                                <p>Время публикации</p>
                                <p class="timeline">${timeline}</p>
                            </div>

                        </div>
                    </div>
                `
            }
        },
        error: function(error) {
            console.log('Error!!!');
        }
    });
}

create_news.addEventListener('click', async function() {
    window.location.href = '/create_news';
})

news_table.addEventListener('click', async function(event) {
    let id = event.target.id;
    console.log(id, 1);
    if (event.target.matches('button') && id) {
        fetch('/get_news_id', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                news_id: id
            })
        })
        .then(response => {
            if (response.redirected) {
                window.location.href = response.url;
            }
        })
        .catch(error => console.error('Error:', error));
    }
});



