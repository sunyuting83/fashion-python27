$.fn.onlyNum = function () {
    $(this).keyup(function(){
        $(this).val($(this).val().replace(/\D|^/g,''));  
    }).bind("paste",function(){
        $(this).val($(this).val().replace(/\D|^/g,''));  
    }).css("ime-mode", "disabled");
};