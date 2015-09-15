$(document).ready(function() {

    $('input[type="checkbox"]').click(function(e){
        if (e.altKey) {
            var checked = $(this).prop('checked');
            $(this).parents('.controls').find('input[type="checkbox"]').prop('checked', checked);
        }
    });

    $('.media-list blockquote').before('<a href="#" class="toggle-reply">...</a>');

    $('.toggle-reply').click(function(){
        $(this).next('blockquote').toggle();
        return false;
    });

    $('input.typeahead').each(function(i, e){
        var that = e;
        $.get($(that).data('source'), function(r){
            $(that).data('source', r);
        });
    });

    $('form ul').addClass('unstyled');
    $('.tt').tooltip({placement: 'bottom'});

    $('a.sn').click(function(){
        var sn = $(this).text();
        var eeeCode = (sn.length < 17) ? sn.substr(-4, 3) : sn.substr(-5, 4);
        $('.filter').val(eeeCode);
        $('.filter').trigger('keyup');
    });

    $('th input[type="checkbox"]').click(function(){
        $('td input[type="checkbox"]').attr('checked', $(this).attr('checked'));
    });

    $('div.async').each(function() {
        $('.wrapper').spin();
        $(this).load($(this).data('url'), function(){
            $('.wrapper').spin(false);
        });
    });

    $('.select-query_key').change(function(){
        var selector = '#select-' + $(this).val();
        var value = $(selector).find('select:first-child');
        var prefix = $(this).attr('name').replace('query_key', '');
        //var name = value.attr('name');
        var name = 'query_value';
        $(value).attr('name', prefix + name);
        $(value).attr('id', 'id_' + prefix + name);

        if ($(this).next().is('.rowcontrols')) {
            $(this).after(value);
        } else {
            $(this).next().replaceWith(value);
        }
    });

    $('button.removerow').click(function(){
        $(this).parents('.formrow').remove();
    });

    $('input.toggle-input').click(function(){
        var el = $(this).data('toggle');
        $(el).attr('disabled', !$(this).prop('checked'));
    });

    $('#label-menu a').click(function(e){
        var c = $(this).data("color");
        $('#active-labels').append($('<span class="label"/>').addClass(c).text($(this).text()));
    });

    $('#active-labels a.close').click(function(e) {
        $(this).parent().remove();
    });

    $('th input').click(function() {
        var checked = $(this).prop('checked');
        $('tbody input[type="checkbox"]').prop('checked', checked);
        $('button[type="submit"]').attr('disabled', !checked);
    });

    $('.toggle_part').click(function() {
        el = $(this).data('toggle');
        $(el).attr('checked', $(this).is(':checked'));
    });

    $('.toggle_row').click(function() {

        $(this).parents('tr').toggleClass('muted');
        // retabulate form
        var total_net = 0;
        var total_tax = 0;
        var total_gross = 0;

        _.each($('tbody tr:not(.muted)'), function(e) {
            amount = parseInt($(e).children('.amount').text(), 10);
            total_net += parseFloat($(e).children('.net').text()) * amount;
            total_tax += parseFloat($(e).children('.tax').text()) * amount;
            total_gross += parseFloat($(e).children('.gross').text()) * amount;
        });

        $('#total_net').val(total_net.toFixed(2));
        $('#total_tax').val(total_tax.toFixed(2));
        $('#total_gross').val(total_gross.toFixed(2));

    });

    $('input.toggle-submit').click(function(e){
        if (e.shiftKey) {
            var checked = $(this).prop('checked');
            $('input.toggle-submit').prop('checked', checked);
        }
        selected = ($('input.toggle-submit:checked').length > 0);
        $('button[type="submit"]').attr('disabled', !selected);
    });

    $('.copy-target').focus(function() {
        if($(this).val() === '') {
            $(this).val($('.copy-source').val());
        }
    });

    if($('.progress .bar').length) {
        window.setInterval(function() {
            var that = $('.progress .bar');
            var p = parseInt($(that).data('progress'), 10) + 10;

            if(p < 100) {
                $(that).data('progress', p).css('width', p+'%');
            } else {
                $(that).data('progress', 100).css('width', '100%');
                $(that).parent().addClass('active');
                $(that).parent().addClass('progress-striped');
            }

        }, 500);
    }

    $('a.nofollow').click(function(e) {
        var button = $(this);
        $.get($(button).attr('href'), function(r) {
            $(button).html(r);
        });
        e.preventDefault();
    });

    $('a.alt').click(function(e) {
        if (!e.altKey) {
            return true;
        }
        var button = $(this);
        $.get($(button).attr('href'), function(r) {
            rel = $(button).data('rel');
            v = parseInt($(rel).text()) - 1;
            if (v < 1) {v = ''};
            $(rel).text(v);
            $(button).remove();
        });
        e.preventDefault();
    });

    $('.label a.close').click(function(e) {
        var button = $(this);
        $.get($(button).attr('href'), function(r) {
            $(button).parent().remove();
        });
        e.preventDefault();
    });

    $(document).on('keyup', 'input.filter', function() {
        var rex = new RegExp($(this).val(), 'i');
        $('.searchable tr').hide();
        $('.searchable tr').filter(function() {
            return rex.test($(this).text());
        }).show();
    });

    $('#gsx-container').load($('#gsx-container').data('source'));

    $(document).on('change', '.property:last select',
        function(e) {
            var newRow = $('.property:last').clone().insertAfter($('.property:last'));
            $(newRow).children('select').data('value', $(this).val());
            $('.property:last option:selected').next()
                .attr('selected', 'selected');
            $('.property:last input').val('').focus();
            $(this).next().find('.remove_field').removeClass('disabled');
    });

    $(document).on('click', '.remove_field',
        function(e) {
            $(this).parents('.control-group').remove();
    });

    $('#id_sold_to').blur(function() {
        if($('#id_ship_to').val() === '') {
            $('#id_ship_to').val($('#id_sold_to').val());
        }
    });

    $('a.window').click(function(e){
        e.preventDefault();
        window.open($(this).attr('href'));
        return false;
    });

    $('input.toggle').click(function(e) {
        $.get($(this).data('url'));
    });

    $('select.overpack-select').change(function(){
        var rel = $(this).val();
        $(rel).val($(this).text());
    });

    $('#id_confirm').click(function(){
        var txt = $('#save-bulk-return').text();
        var ph = $('#save-bulk-return').data('placeholder');
        $('#save-bulk-return').data('placeholder', txt);
        $('#save-bulk-return').text(ph);
        $('#save-bulk-return').toggleClass('btn-warning');
    });

    $('form.spin').submit(function(e) {
        //e.preventDefault();
        $('.wrapper').spin();
    });

    $('#set_dt').click(function(){
        d = new Date();
        month = d.getMonth() + 1;
        v = vsprintf('%d-%02d-%02d %02d:%02d:%02d', [
            d.getFullYear(),
            month, d.getDate(),
            d.getHours(),
            d.getMinutes(),
            d.getSeconds()
        ]);
        $('#id_finished_at').val(v);
    });

    $('#id_gsx_soldto').blur(function(){
        $('#id_gsx_shipto').val($(this).val());
    });

    $(document).on('click', '#create_customer', function() {
        var url = $(this).attr('href') + '?name=' + $('#customer_name').val();
        document.location = url;
        return false;
    });

    $(document).on('submit', '#search-form', function(e) {
        e.preventDefault();
        var action = $(this).attr('action');
        var target = $(this).data('target');
        $('.wrapper').spin();
        $(target).load(action, $(this).serializeArray(), function() {
            $('.wrapper').spin(false);
        });
    });

    $('.datetimepicker').datetimepicker({
        weekStart: 1,
        pickSeconds: false
    });

    $('.datepicker').datetimepicker({
        weekStart: 1,
        pickTime: false,
        pickSeconds: false
    });

    $('.timepicker').datetimepicker({
        weekStart: 1,
        pickDate: false,
        pickSeconds: false
    });

    $('#table-queue-status input[type="number"]').addClass('input-mini');
    $('#table-queue-status select').addClass('span12');

    $('textarea.autocomplete').typeahead({
        items: 4,
        source: function(query, process){
            return $(this.$element).data('source');
        },
        updater: function(item){
            var that = $(this);
            $.post('/notes/render_template/', {title: item}, function(r){
                that[0].$element.val(r);
            });
        }
    });

    //$('#toolbar-search').focus();

});

function cloneMore(selector, type, keepVal)
{
    var newElement = $(selector).clone(true);
    var total = $('#id_' + type + '-TOTAL_FORMS').val();
    newElement.find(':input').each(function() {
        var name = $(this).attr('name').replace('-' + (total-1) + '-','-' + total + '-');
        var id = 'id_' + name;
        $(this).attr({'name': name, 'id': id});
        if(!keepVal) {
            $(this).val('').removeAttr('checked');
        }
    });
    newElement.find('label').each(function() {
        var newFor = $(this).attr('for').replace('-' + (total-1) + '-','-' + total + '-');
        $(this).attr('for', newFor);
    });
    total++;
    $('#id_' + type + '-TOTAL_FORMS').val(total);
    $(selector).after(newElement);
}
