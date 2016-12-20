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
        menubar: false,
        toolbar: 'undo redo | insert | styleselect | fontsizeselect bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image | code | fullscreen',
        fontsize_formats: "8px 10px 12px 14px 18px 24px 36px",
        file_picker_callback: function(callback, value, meta) {
            $('#img-upload-btn').click();
            upload(callback);
        },
        convert_urls: false,
        init_instance_callback: function(editor) {
            editor.setContent($('#mce-initial-content').html());
        },
        plugins: [
            "advlist autolink lists link image charmap print preview anchor",
            "searchreplace visualblocks code fullscreen",
            "insertdatetime media table contextmenu paste imagetools"
        ],
        setup: function(editor) {
            editor.addButton('mybutton', {
                text: 'My Button', 
                icon: false,
                onclick: function() {
                    editor.windowManager.open({
                        title: '插入微信文章',
                        width: 320,
                        body: [{
                            type: 'textbox',
                            name: 'url',
                            label: 'URL'
                        }],
                        onsubmit: function(e) {
                            alert('yes');
                        }
                    });
                }
            })
        }
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

    $('#datetimepicker1').datetimepicker({
        format: 'YYYY-MM-DD HH:mm',
    });

});
