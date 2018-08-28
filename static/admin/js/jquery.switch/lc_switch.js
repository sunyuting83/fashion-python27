/**
 * lc_switch.js
 * Version: 1.0
 * Author: LCweb - Luca Montanari
 * Download: http://www.mycodes.net
 * Licensed under the MIT license
 */
(function($){if(typeof($.fn.lc_switch)!='undefined'){return false}$.fn.lc_switch=function(on_text,off_text){$.fn.lcs_destroy=function(){$(this).each(function(){var $wrap=$(this).parents('.lcs_wrap');$wrap.children().not('input').remove();$(this).unwrap()});return true};$.fn.lcs_on=function(){$(this).each(function(){var $wrap=$(this).parents('.lcs_wrap');var $input=$wrap.find('input');if(typeof($.fn.prop)=='function'){$wrap.find('input').prop('checked',true)}else{$wrap.find('input').attr('checked',true)}$wrap.find('input').trigger('lcs-on');$wrap.find('input').trigger('lcs-statuschange');$wrap.find('.lcs_switch').removeClass('lcs_off').addClass('lcs_on');if($wrap.find('.lcs_switch').hasClass('lcs_radio_switch')){var f_name=$input.attr('name');$wrap.parents('form').find('input[name='+f_name+']').not($input).lcs_off()}});return true};$.fn.lcs_off=function(){$(this).each(function(){var $wrap=$(this).parents('.lcs_wrap');if(typeof($.fn.prop)=='function'){$wrap.find('input').prop('checked',false)}else{$wrap.find('input').attr('checked',false)}$wrap.find('input').trigger('lcs-off');$wrap.find('input').trigger('lcs-statuschange');$wrap.find('.lcs_switch').removeClass('lcs_on').addClass('lcs_off')});return true};return this.each(function(){if(!$(this).parent().hasClass('lcs_wrap')){var ckd_on_txt=(typeof(on_text)=='undefined')?'显示':on_text;var ckd_off_txt=(typeof(off_text)=='undefined')?'隐藏':off_text;var on_label=(ckd_on_txt)?'<div class="lcs_label lcs_label_on">'+ckd_on_txt+'</div>':'';var off_label=(ckd_off_txt)?'<div class="lcs_label lcs_label_off">'+ckd_off_txt+'</div>':'';var disabled=($(this).is(':disabled'))?true:false;var active=($(this).is(':checked'))?true:false;var status_classes='';status_classes+=(active)?' lcs_on':' lcs_off';if(disabled){status_classes+=' lcs_disabled'}var structure='<div class="lcs_switch '+status_classes+'">'+'<div class="lcs_cursor"></div>'+on_label+off_label+'</div>';if($(this).is(':input')&&($(this).attr('type')=='checkbox'||$(this).attr('type')=='radio')){$(this).wrap('<div class="lcs_wrap"></div>');$(this).parent().append(structure);$(this).parent().find('.lcs_switch').addClass('lcs_'+$(this).attr('type')+'_switch')}}})};$(document).ready(function(){$(document).delegate('.lcs_switch:not(.lcs_disabled)','click tap',function(e){if($(this).hasClass('lcs_on')){if(!$(this).hasClass('lcs_radio_switch')){$(this).lcs_off()}}else{$(this).lcs_on()}});$(document).delegate('.lcs_wrap input','change',function(){if($(this).is(':checked')){$(this).lcs_on()}else{$(this).lcs_off()}})})})(jQuery);
