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
            hintFailure.show().delay(5000).fadeOut();
        })
        .always(function() {
            formBtn.removeClass('disabled');
            formBtn.text('提交');
        });
    });
});