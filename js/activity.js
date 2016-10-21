$(function() {

    $('#toggle-button').click(function() {
        $('#old-activity-list').slideToggle();
        if ($(this).text() == '查看往期活动')
            $(this).text('隐藏往期活动');
        else
            $(this).text('查看往期活动');
    });

    $('.timeline-badge.click-effect').click(function() {
        if ($(this).hasClass('success')) {
            $(this).removeClass('success');
            var badge = $(this).find('i');
            badge.removeClass('glyphicon-check');
            badge.addClass('glyphicon-unchecked');
        } else {
            $(this).addClass('success');
            var badge = $(this).find('i');
            badge.addClass('glyphicon-check');
            badge.removeClass('glyphicon-unchecked');
        }
    });

});