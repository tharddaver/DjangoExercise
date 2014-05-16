$(document).ready(function () {
    $('#likes').click(function () {
        var catid = $(this).attr("data-catid");
        $.get('/rango/category/like', {category_id: catid}, function (data) {
            $('#like_count').html(data);
            $('#likes').hide();
        });
    });

    $('#suggestion').keyup(function () {
        var query = $(this).val();
        $.get('/rango/category/suggest/', {suggestion: query}, function (data) {
            $('#categories').html(data);
        });
    });

    $('.page-add').click(function () {
        var $this = $(this);
        var data = $this.data();
        $.post(data.url, {'title': data.title, 'url': data.link}, function (data) {
            console.log(data);
            if (data.success) {
                $this.remove();
                $('#category-pages').append('<li><a href="/rango/goto?page_id=' + data.page.id + '">' + data.page.title + '</a></li>')
            }
        }, 'json')
    });
});