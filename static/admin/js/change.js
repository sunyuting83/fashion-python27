$(document).ready(function(){
    App.init();
});
// 全选
$('input').iCheck({
    checkboxClass: 'icheckbox_square-blue checkbox',
    radioClass: 'icheckbox_square-blue'
});

$("#check-all").on('ifChanged',function(){
    var checkboxes = $('[name="checks"]').find(':checkbox');
    if($(this).is(':checked')) {
        checkboxes.iCheck('check');
    } else {
        checkboxes.iCheck('uncheck');
    }
});

// 单选某个，记录checkbox的id值
var ListId = [];
$('input:checkbox[name=getid]').on('ifChanged', function(event){ //ifCreated 事件应该在插件初始化之前绑定 
    var spCodesTemp = $(this).val();
    if($(this).is(':checked')) {
        ListId.push(spCodesTemp);
    }else {
        ListId = remove(ListId,spCodesTemp);
    }
});

// 获得信息数
var _messagenb = $('#mymessages');
var hasuserid = _messagenb.data('thisid');
$.ajax({ 
    type: 'get', 
    url: '/manage/manage_booknb/'+hasuserid,
    traditional: false,
    success:function(data,textStatus){ 
        _messagenb.text(data.cont);
    }, 
    complete:function(XMLHttpRequest,textStatus){ 
        //HideLoading(); 
    }, 
    error:function(){ 
        //请求出错处理 
    } 
});

// 弹出函数
function LockLayer(active,geturl,getdata,post=false){
    layer.confirm('您确定要'+active+'？', {
        btn: ['确定'+active,'取消'] //按钮
    }, function(){
        console.log(getdata);
        var activate = '';
        if(post == true) {
            activate    = 'post';
            traditional = true;
        }else{
            activate    = 'get';
            traditional = false;
        };
        $.ajax({ 
            type: activate, 
            url: geturl,
            data: getdata,
            dataType: 'json',
            traditional: traditional,
            beforeSend:function(XMLHttpRequest){ 
                layer.load(1, {
                  shade: [0.1,'#fff']
                });
            }, 
            success:function(data,textStatus){ 
                if(data.state == 'ok'){
                    layer.msg(active+'成功', {icon: 1});
                    return window.location.reload()
                }else{
                    layer.confirm(active+'失败', {
                        btn: ['点击刷新']
                    },function(){
                        return window.location.reload()
                    });
                }
            }, 
            complete:function(XMLHttpRequest,textStatus){ 
                //HideLoading(); 
            }, 
            error:function(){ 
                //请求出错处理 
            } 
        });
        
    });
};

// ajax请求函数
function del_ajax(activate,geturl,getdata) {
    $.activate(geturl, getdata, function(data){
        if(data.state == 'ok'){
            layer.msg(active+'成功', {icon: 1});
            return window.location.reload()
        }else{
            layer.confirm(active+'失败', {
                btn: ['点击刷新']
            },function(){
                return window.location.reload()
            });
        }
    });
}

// 分页函数
function pagination(page_cont) {
    if ( $(".pagination").length > 0 ) { 
        var page = getUrlParam('page');
        var thispage = $('.pagination').children('li');
        if(page == 1 || page == null) {
            thispage.first().addClass('disabled');
            thispage.first().children('a').attr({href: '#'});
            thispage.eq(page).addClass('active');
            if(page == null){
                thispage.eq(page).removeClass('active');
                thispage.eq(1).addClass('active');
            }
        }else if(page == page_cont) {
            thispage.last().addClass('disabled');
            thispage.eq(page).addClass('active');
            thispage.last().children('a').attr({href: '#'});
        }
        else{
            thispage.eq(page).addClass('active')
        }
    };
}

//获取url中的参数
function getUrlParam(name) {
    var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)"); //构造一个含有目标参数的正则表达式对象
    var r = window.location.search.substr(1).match(reg);  //匹配目标参数
    if (r != null) return unescape(r[2]); return null; //返回参数值
};

// 滤掉数组中的某个值
function remove(arrPerson,objValue) {
    return $.grep(arrPerson, function(cur,i){
        return cur!=objValue;
    });
};
function removeByValue(arr, val) {
  for(var i=0; i<arr.length; i++) {
    if(arr[i] == val) {
      arr.splice(i, 1);
      break;
    }
  }
}

// 倒计时函数
function ChangeTime() {
    var time;
    time = $("#time").text();
    time = parseInt(time);
    time--;
    if (time <= 0) {
        window.location.href = "silder";
    } else { 
        $("#time").text(time); 
        setTimeout(ChangeTime, 1000); 
    } 
};

// 判断字符串是否包含某字符串
function isContains(str, substr) {
    return str.indexOf(substr) >= 0;
};

// 删除图片函数
function delpics(id){
    $.ajax({
         url: '/manage/del_pic?picid='+id,
         dataType: 'json',
         method: 'GET',
         success: function(data) {
         },
         error: function(xhr) {
             // 导致出错的原因较多，以后再研究
             // console.log(xhr)
         }
    });
};

// 删除数组中指定值
Array.prototype.removeByValue = function(val) {
  for(var i=0; i<this.length; i++) {
    if(this[i] == val) {
      this.splice(i, 1);
      break;
    }
  }
};