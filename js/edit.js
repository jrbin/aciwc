$(function () {
    function upload(callback) {

        $('#img-upload-btn').on('change', function (e) {
            if ($(this)[0].files.length > 0) {
                var formData = new FormData();
                formData.append('image', $(this)[0].files[0]);

                $.ajax({
                    type: 'POST',
                    url: '/upload',
                    data: formData,
                    cache: false,
                    contentType: false,
                    processData: false,
                    success: function(data) {
                        callback(data);
                    },
                    error: function(xhr, textStatus, errorThrown) {
                        alert(xhr.status + ': ' + xhr.responseText);
                    }
                });
            }
        });
    }

    tinymce.init({ 
        selector:'textarea.mce',
        height: 400,
        plugins: [
            'advlist autolink lists link image charmap print preview anchor',
            'searchreplace visualblocks code fullscreen',
            'insertdatetime media table contextmenu paste code'
        ],
        toolbar: 'insertfile undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image',
        file_picker_callback: function(callback, value, meta) {
            $('#img-upload-btn').click();
            upload(callback);
        },
        convert_urls: false,
        init_instance_callback: function(editor) {
            editor.setContent($('#mce-initial-content').html());
        },
    });

    $('form').bind('form-pre-serialize', function(e) {
        tinymce.triggerSave();
    });

    $('#img-upload-label').on('click', function(e) {
        $('#img-upload-btn').click();
        upload(function(data) {
            $('input[name="logo_url"]').val(data);
            $('input[name="logo_url"]').trigger('change');
        });
    });

    $('input[name="logo_url"]').on('change', function(e) {
        $('#logo-img').attr('src', $(this).val());
    });
});