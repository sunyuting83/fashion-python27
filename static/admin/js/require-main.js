require.config({
    baseUrl: '/static/admin/js/',
    map: {
        '*': {
            'css': 'css.min'
        }
    },
    paths: {
        'jquery':'jquery',
        'gritter':'jquery.gritter/js/jquery.gritter',
        'nanoscroller':'jquery.nanoscroller/jquery.nanoscroller',
        'general':'behaviour/general',
        'jquery-ui':'jquery.ui/jquery-ui',
        'sparkline':'jquery.sparkline/jquery.sparkline.min',
        'easy-pie-chart':'jquery.easypiechart/jquery.easy-pie-chart',
        'nestable':'jquery.nestable/jquery.nestable',
        'bootstrap-switch':'bootstrap.switch/bootstrap-switch.min',
        'datetimepicker':'bootstrap.datetimepicker/js/bootstrap-datetimepicker.min',
        'select2':'jquery.select2/select2.min',
        'bootstrap-slider':'bootstrap.slider/js/bootstrap-slider',
        'bootstrap':'bootstrap/dist/js/bootstrap.min',
        'icheck':'jquery.icheck/icheck.min'
    },
    shim: {
        'gritter':[
            'jquery',
            'css!./jquery.gritter/css/jquery.gritter'
        ],
        'nanoscroller':[
            'jquery',
            'css!./jquery.nanoscroller/nanoscroller'
        ],
        'general':['jquery'],
        'jquery-ui':['jquery'],
        'sparkline':['jquery'],
        'easy-pie-chart':[
            'jquery',
            'css!./jquery.easypiechart/jquery.easy-pie-chart'
        ],
        'nestable':['jquery'],
        'bootstrap-switch':[
            'bootstrap',
            'css!./bootstrap.switch/bootstrap-switch'
        ],
        'datetimepicker':[
            'bootstrap',
            'css!./bootstrap.datetimepicker/css/bootstrap-datetimepicker.min'
        ],
        'select2':[
            'jquery',
            'css!./jquery.select2/select2'
        ],
        'bootstrap-slider':[
            'bootstrap',
            'css!./bootstrap.slider/css/slider'
        ],
        'bootstrap':['jquery'],
        'icheck':['jquery','css!./jquery.icheck/skins/square/blue']
    }
});

require(
    [
        'jquery',
        'gritter',
        'nanoscroller',
        'general',
        'jquery-ui',
        'sparkline',
        'easy-pie-chart',
        'nestable',
        'bootstrap-switch',
        'datetimepicker',
        'select2',
        'bootstrap-slider',
        'bootstrap',
        'icheck'
    ], function ($) {


        $(document).ready(function(){
            App.init();
            

            // 全选
            $('input').iCheck({
                checkboxClass: 'icheckbox_square-blue checkbox',
                radioClass: 'icheckbox_square-blue'
            });
              
            $("#check-all").on('ifChanged',function(){
                var checkboxes = $(".mails").find(':checkbox');
                if($(this).is(':checked')) {
                    checkboxes.iCheck('check');
                } else {
                    checkboxes.iCheck('uncheck');
                }
            });
        
        });
    
});
