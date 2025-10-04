let news_table = document.getElementById('news-container');

news_table.addEventListener('click', async function(event) {
    let id = event.target.id;
    if (event.target.matches('button') && id) {
        $.ajax({
            url: '/news_page',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                'item_id': id
            }),
            success: function(response) {
                console.log(response);
                location.reload;
            },
            error: function(error) {
                console.log('Error!!!');
            }
        });
    }
});