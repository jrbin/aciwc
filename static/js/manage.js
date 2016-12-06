$(function() {

    $('#choose-image').click(function(e) {
        e.preventDefault();
        $('#img-upload-btn').click();
    });

    $('#img-upload-btn').on('change', function() {

        if ($(this)[0].files.length > 0) {
            var formData = new FormData();
            formData.append('image', $(this)[0].files[0]);
            $('#choose-image').addClass('disabled');

            $.ajax({
                type: 'POST',
                url: '/upload',
                data: formData,
                cache: false,
                contentType: false,
                processData: false,
            })
            .done(function (data) {
                $('#add-hero-form input[name="image_url"]').val(data);
            })
            .fail(function (jqXHR, textStatus, errorThrown) {
                alert(jqXHR.status + ': ' + jqXHR.responseText);
            })
            .always(function() {
                $('#choose-image').removeClass('disabled');
            });

        }
    });

    $('.hero-img').one('load', function() {
        $(this).closest('tr').find('.img-size').text(this.naturalWidth + ' x ' + this.naturalHeight);
    }).each(function() {
        if (this.complete) $(this).load();
    });
});
