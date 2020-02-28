(function($){
    $(document).ready(function(){
        updatePrice();
        $(document).on('change input click', function(e){
            var $target = $(e.target);
            var elementId = $target.attr('id');
            var elementClass = $target.attr('class');
            if (elementId && (elementId.match(/id_orderedproduct_set/) != null || elementClass == 'inline-deletelink')) {
                updatePrice();
            }
        });
    })
    function updatePrice(){
        var orderAmount = parseFloat(0.00);
        $('#orderedproduct_set-group .form-row').each(function (index, product) {
                    var price_text = $(product).find('.field-product select').children("option").filter(":selected").text();
                    if (price_text){
                        price_text = parseFloat(price_text.slice(price_text.lastIndexOf(' ')+1, price_text.length));
                    }
                    var quantity = parseFloat($(product).find('.field-quantity input').val());
                    if (!isNaN(quantity) && price_text) {
                        orderAmount += price_text*quantity;
                    }
                });
                $('.order-amount').text(parseFloat(orderAmount).toFixed(2));
    }
})($);
/*
$('#orderedproduct_set-group').on('input select2:select change', function(e){
    console.log(e.target.type);
    var orderAmount = 0;
    $('#orderedproduct_set-group form-row').each(function(index, product){
        console.log($(product).find('select').text());
        console.log($(product).find('input').val());
    })
});
*/