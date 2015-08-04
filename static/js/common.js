/**
 * common.js
 */
 $(function(){
  $('.disabled').click(function(e) {
        e.preventDefault();
        return false;
    });
  $('input[type="text"]').attr('autocomplete', 'off');

  $(document).on('click', 'a[data-modal]', function(e){

    if($(this).parent().hasClass('disabled') || $(this).hasClass('disabled')) {
      return false;
    }

    $('.wrapper').spin();
    e.preventDefault();

    $('#modal').load($(this).attr('href'),
      function(){
        $('.wrapper').spin(false);
        $('#modal').modal({'backdrop': 'static'});
        $('#modal .modal-body input:visible:first').focus();

        $('#gsx-container').load($('#gsx-container').data('source'));
        $('#modal button[type="submit"]').click(function(e) {
          $('#modal form').submit();
        });
        $('#modal button[type="submit"]').focus();
        $('#modal .trigger-search').on('click', function(){
          $('#search-form').submit();
        });
      });
  });

});
