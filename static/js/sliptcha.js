(function($) {
    var slidingTime = 500;

    $('.slider-bar').each(function(index, element) {
        var thisSliderBar = $(this);
        var thisSliderPiece = thisSliderBar.find('.slider-piece');
        var thisSliderLeft = thisSliderBar.find('.slider-left');
        var textBackground = thisSliderBar.find('.slider-text')
        var textRight = thisSliderPiece.find('.slider-text-right');
        var textLoading = thisSliderPiece.find('.slider-loading');
        var textDone = thisSliderPiece.find('.slider-done');
        var textFailed = thisSliderPiece.find('.slider-failed');

        var maxPos = thisSliderBar.width() - thisSliderPiece.width()
                   - 2 * parseInt(thisSliderBar.css('border-width'));
        console.log(maxPos);
        var positions = [];

        thisSliderPiece.draggable({
            cursor: 'move',
            axis: 'x',
            containment: 'parent',
            drag: function(event, ui) {
                var pos = ui.position.left;

                positions.push(pos);
                thisSliderLeft.css('width', pos);

                // have moved to the rightest
                if (pos >= maxPos) {
                    thisSliderPiece.css('left', maxPos);
                    thisSliderLeft.width(maxPos);
                    thisSliderPiece.draggable('disable');

                    return false;
                }
            },
            stop: function(event, ui) {
                var pos = ui.position.left;
                console.log(positions);
                if (0 < pos && pos < maxPos) {
                    // move the piece back to start
                    thisSliderPiece.animate({ left: 0 }, slidingTime);
                    thisSliderLeft.animate({ width: 0 }, slidingTime);
                } else if (pos >= maxPos) {

                    if (positions.length <= 10) {
                        sliptchaFail('你拖的太快了，请重试');
                    } else {
                        sliderPieceText('loading');

                        $.ajax({
                            url: '/sliptcha',
                            method: 'POST',
                            data: JSON.stringify(positions),
                            contentType: 'application/json',
                        })
                        .done(function(data, textStatus, jqXHR) {
                            sliptchaCheck(data);
                        })
                        .fail(function(jqXHR, textStatus, errorThrown) {
                            sliptchaFail(jqXHR.statusText);
                        })
                        .always(function() {

                        });
                    }
                }
                positions = [];
            },
        });

        function sliptchaCheck(data) {
            console.log(data);
            if (data) {
                sliderPieceText('done');
                textBackground.text('验证成功');
                $("input[name='sliptcha_token']").val(data);
            } else {
                sliptchaFail('验证失败，请重试');
            }
        }

        function sliptchaFail(errorText) {
            var oldText = textBackground.text();
            var oldColor = thisSliderLeft.css('background-color');
            textBackground.text(errorText);
            thisSliderLeft.animate({'background-color': 'red'}, 100);
            //thisSliderLeft.css({'background-color': 'red'});
            sliderPieceText('fail');
            thisSliderPiece.draggable('disable');
            setTimeout(function() {
                thisSliderPiece.animate({ left: 0 }, slidingTime);
                thisSliderLeft.animate({ width: 0 }, slidingTime);
                sliderPieceText('right');
                setTimeout(function() {
                    textBackground.text(oldText);
                    thisSliderLeft.css('background-color', oldColor);
                    thisSliderPiece.draggable('enable');
                }, slidingTime);
            }, 1000);
        }

        function sliderPieceText(text) {
            if ('right' == text) {
                textRight.show();
                textLoading.hide();
                textDone.hide();
                textFailed.hide();
            } else if ('loading' == text) {
                textRight.hide();
                textLoading.show();
                textDone.hide();
                textFailed.hide();
            } else if ('done' == text) {
                textRight.hide();
                textLoading.hide();
                textDone.show();
                textFailed.hide();
            } else if ('fail' == text) {
                textRight.hide();
                textLoading.hide();
                textDone.hide();
                textFailed.show();
            }
        }

        function reset() {
            thisSliderPiece.css({ left: 0 });
            thisSliderLeft.css({ width: 0 });
            textBackground.text('向右拖动滑块');
            sliderPiece('right');
        }
    });

//    $('.slider-piece').draggable({
//        cursor: 'move',
//        containment: "parent",
//        drag: function(event, ui) {
//            positions.push(ui.position.left);
//            $('.slider-left').css('width', ui.position.left);
//
//            if (ui.position.left >= 241) {
//                $(this).draggable('disable');
//                $(this).unbind('mousedown');
//                $(document).unbind('mouseup');
//                $(this).css('left', 241);
//                $('.slider-left').css('width', 241);
//                return false;
//            }
//        },
//    });
//
//    $('.slider-piece').mousedown(function() {
//        var sliderPiece = $(this);
//        $(document).one('mouseup', function() {
//            var time = 500;
//            if (parseInt(sliderPiece.css('left')) > 0)
//                sliderPiece.animate({
//                    left: 0,
//                }, time);
//            var sliderLeft = $('.slider-left');
//            if (parseInt(sliderLeft.css('width')) > 0)
//                sliderLeft.animate({
//                    width: 0,
//                }, time);
//        });
//    });

})(jQuery);
