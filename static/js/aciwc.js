$(function() {
    $('.aciwc-nav-item').click(function(e) {
        e.stopPropagation();
        var $dropdown = $(this).find('.aciwc-dropdown');
        $dropdown.toggle();
//        $(document).one('click', function(e) {
//            $dropdown.hide();
//        });
    });
})
