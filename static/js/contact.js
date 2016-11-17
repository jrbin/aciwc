$(function() {

    $('#contact-form').submit(function(e) {
        e.preventDefault();
        var thisForm = $(this);
        var formBtn = thisForm.find('button[type="submit"]');
        var hintSuccess = $('#hint-success');
        var hintFailure = $('#hint-failure');
        formBtn.addClass('disabled');
        formBtn.text('提交中...');
        $.ajax({
            url: '/send',
            data: thisForm.serialize(),
            method: 'POST'
        })
        .done(function(response) {
            console.log(response);
            hintSuccess.show().delay(5000).fadeOut();
            thisForm[0].reset();
        })
        .fail(function(xhr, textStatus) {
            hintFailure.text('错误:' +  xhr.responseText + ', 您可以尝试直接给我们发邮件');
            hintFailure.show().delay(5000).fadeOut();
        })
        .always(function() {
            formBtn.removeClass('disabled');
            formBtn.text('提交');
            resetSliptcha();
        });
    });

    function resetSliptcha() {
        $('input[name="sliptcha_token"]').val('');
        $('.slider-piece').css({ left: 0 });
        $('.slider-left').css({ width: 0 });
        $('.slider-text').text('向右拖动滑块');
        $('.slider-text-right').show();
        $('.slider-loading').hide();
        $('.slider-done').hide();
        $('.slider-failed').hide();
        $('.slider-piece').draggable('enable');
    }

});
