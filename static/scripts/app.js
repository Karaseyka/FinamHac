document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM загружен - отправляю запрос');
    loadData();
});


let news_table = document.getElementById('news-container');
let use_filter = document.getElementById('filter');
let create_news = document.getElementById('create');

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
            location.reload;

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



