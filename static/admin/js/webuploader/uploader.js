// WebUploader demo js
jQuery(function() {

    var BASE_URL = './static/webuploader/';
    var $ = jQuery,
        $wrap = $('#uploader'),
        $queue = $('<ul class="filelist"></ul>').appendTo($wrap.find('.queueList')),
        $statusBar = $wrap.find('.statusBar'),
        $info = $statusBar.find('.info'),
        $upload = $wrap.find('.uploadBtn'),
        $placeHolder = $wrap.find('.placeholder'),
        $progress = $statusBar.find('.progress').hide(),
        fileCount = 0,
        fileSize = 0,
        ratio = window.devicePixelRatio || 1,
        thumbnailWidth = 110 * ratio,
        thumbnailHeight = 110 * ratio,
        state = 'pedding',
        percentages = {},
        supportTransition = (function() {
            var s = document.createElement('p').style,
                r = 'transition' in s || 'WebkitTransition' in s || 'MozTransition' in s || 'msTransition' in s || 'OTransition' in s;
            s = null;
            return r
        })(),
        uploader;
    if (!WebUploader.Uploader.support()) {
        alert('Web Uploader 不支持您的浏览器！如果你使用的是IE浏览器，请尝试升级 flash 播放器');
        throw new Error('WebUploader does not support the browser you are using.');
    }
    uploader = WebUploader.create({
        pick: {
            id: '#filePicker',
            label: '点击选择图片'
        },
        dnd: '#uploader .queueList',
        paste: document.body,
        duplicate: true,
        accept: {
            title: 'Images',
            extensions: 'gif,jpg,jpeg,bmp,png',
            mimeTypes: 'image/jpg,image/jpeg,image/png,image/gif'
        },
        swf: BASE_URL + '/Uploader.swf',
        disableGlobalDnd: true,
        chunked: true,
        server: '/manage/upload',
        fileNumLimit: 300,
        fileSizeLimit: 5 * 1024 * 1024,
        fileSingleSizeLimit: 1 * 1024 * 1024.
    });
    uploader.addButton({
        id: '#filePicker2',
        label: '继续添加'
    });

    function addFile(file) {
        var $li = $('<li id="' + file.id + '" name="tzuoz">' + '<p class="title">' + file.name + '</p>' + '<p class="imgWrap"></p>' + '<p class="progress"><span></span></p>' + '</li>'),
            $btns = $('<div class="file-panel">' + '<span class="cancel">删除</span>' + '<span class="rotateRight">向右旋转</span>' + '<span class="rotateLeft">向左旋转</span></div>').appendTo($li),
            $prgress = $li.find('p.progress span'),
            $wrap = $li.find('p.imgWrap'),
            $info = $('<p class="error"></p>'),
            showError = function(code) {
                switch (code) {
                case 'exceed_size':
                    text = '文件大小超出';
                    break;
                case 'interrupt':
                    text = '上传暂停';
                    break;
                default:
                    text = '上传失败，请重试';
                    break
                }
                $info.text(text).appendTo($li)
            };
        if (file.getStatus() === 'invalid') {
            showError(file.statusText)
        } else {
            $wrap.text('预览中');
            uploader.makeThumb(file, function(error, src) {
                if (error) {
                    $wrap.text('不能预览');
                    return
                }
                var img = $('<img src="' + src + '">');
                $wrap.empty().append(img)
            }, thumbnailWidth, thumbnailHeight);
            percentages[file.id] = [file.size, 0];
            file.rotation = 0
        }
        file.on('statuschange', function(cur, prev) {
            if (prev === 'progress') {
                $prgress.hide().width(0)
            } else if (prev === 'queued') {
                $li.off('mouseenter mouseleave');
                $btns.remove()
            }
            if (cur === 'error' || cur === 'invalid') {
                console.log(file.statusText);
                showError(file.statusText);
                percentages[file.id][1] = 1
            } else if (cur === 'interrupt') {
                showError('interrupt')
            } else if (cur === 'queued') {
                percentages[file.id][1] = 0
            } else if (cur === 'progress') {
                $info.remove();
                $prgress.css('display', 'block')
            } else if (cur === 'complete') {
                $li.append('<span class="success"></span>')
            }
            $li.removeClass('state-' + prev).addClass('state-' + cur)
        });
        $li.on('mouseenter', function() {
            $btns.stop().animate({
                height: 30
            })
        });
        $li.on('mouseleave', function() {
            $btns.stop().animate({
                height: 0
            })
        });
        $btns.on('click', 'span', function() {
            var index = $(this).index(),
                deg;
            switch (index) {
            case 0:
                uploader.removeFile(file);
                return;
            case 1:
                file.rotation += 90;
                break;
            case 2:
                file.rotation -= 90;
                break
            }
            if (supportTransition) {
                deg = 'rotate(' + file.rotation + 'deg)';
                $wrap.css({
                    '-webkit-transform': deg,
                    '-mos-transform': deg,
                    '-o-transform': deg,
                    'transform': deg
                })
            } else {
                $wrap.css('filter', 'progid:DXImageTransform.Microsoft.BasicImage(rotation=' + (~~ ((file.rotation / 90) % 4 + 4) % 4) + ')')
            }
        });
        $li.appendTo($queue)
    }
    function removeFile(file) {
        var $li = $('#' + file.id);
        delete percentages[file.id];
        updateTotalProgress();
        $li.off().find('.file-panel').off().end().remove()
    }
    function updateTotalProgress() {
        var loaded = 0,
            total = 0,
            spans = $progress.children(),
            percent;
        $.each(percentages, function(k, v) {
            total += v[0];
            loaded += v[0] * v[1]
        });
        percent = total ? loaded / total : 0;
        spans.eq(0).text(Math.round(percent * 100) + '%');
        spans.eq(1).css('width', Math.round(percent * 100) + '%');
        updateStatus()
    }
    function updateStatus() {
        var text = '',
            stats;
        if (state === 'ready') {
            text = '选中' + fileCount + '张图片，共' + WebUploader.formatSize(fileSize) + '。'
        } else if (state === 'confirm') {
            stats = uploader.getStats();
            if (stats.uploadFailNum) {
                text = '已成功上传' + stats.successNum + '张照片至XX相册，' + stats.uploadFailNum + '张照片上传失败，<a class="retry" href="#">重新上传</a>失败图片或<a class="ignore" href="#">忽略</a>'
            }
        } else {
            stats = uploader.getStats();
            text = '共' + fileCount + '张（' + WebUploader.formatSize(fileSize) + '），已上传' + stats.successNum + '张';
            if (stats.uploadFailNum) {
                text += '，失败' + stats.uploadFailNum + '张'
            }
        }
        $info.html(text)
    }
    function setState(val) {
        var file, stats;
        if (val === state) {
            return
        }
        $upload.removeClass('state-' + state);
        $upload.addClass('state-' + val);
        state = val;
        switch (state) {
        case 'pedding':
            $placeHolder.removeClass('element-invisible');
            $queue.parent().removeClass('filled');
            $queue.hide();
            $statusBar.addClass('element-invisible');
            uploader.refresh();
            break;
        case 'ready':
            $placeHolder.addClass('element-invisible');
            $('#filePicker2').removeClass('element-invisible');
            $queue.parent().addClass('filled');
            $queue.show();
            $statusBar.removeClass('element-invisible');
            uploader.refresh();
            break;
        case 'uploading':
            $('#filePicker2').addClass('element-invisible');
            $progress.show();
            $upload.text('暂停上传');
            break;
        case 'paused':
            $progress.show();
            $upload.text('继续上传');
            break;
        case 'confirm':
            $progress.hide();
            $upload.text('开始上传').addClass('disabled');
            stats = uploader.getStats();
            if (stats.successNum && !stats.uploadFailNum) {
                setState('finish');
                return
            }
            break;
        case 'finish':
            stats = uploader.getStats();
            if (stats.successNum) {
                // alert('上传成功')
                // layer.alert('上传成功')
                
            } else {
                state = 'done';
                location.reload()
            }
            break
        }
        updateStatus()
    }
    uploader.onUploadProgress = function(file, percentage) {
        var $li = $('#' + file.id),
            $percent = $li.find('.progress span');
        $percent.css('width', percentage * 100 + '%');
        percentages[file.id][1] = percentage;
        updateTotalProgress()
    };
    uploader.onFileQueued = function(file) {
        fileCount++;
        fileSize += file.size;
        if (fileCount === 1) {
            $placeHolder.addClass('element-invisible');
            $statusBar.show()
        }
        addFile(file);
        setState('ready');
        updateTotalProgress()
    };
    uploader.onFileDequeued = function(file) {
        fileCount--;
        fileSize -= file.size;
        if (!fileCount) {
            setState('pedding')
        }
        removeFile(file);
        updateTotalProgress()
    };
    uploader.on('all', function(type) {
        var stats;
        switch (type) {
        case 'uploadFinished':
            setState('confirm');
            break;
        case 'startUpload':
            setState('uploading');
            break;
        case 'stopUpload':
            setState('paused');
            break
        }
    });
    uploader.onError = function(code) {
        alert('Eroor: ' + code)
    };
    $upload.on('click', function() {
        if ($(this).hasClass('disabled')) {
            return false
        }
        if (state === 'ready') {
            uploader.upload()
        } else if (state === 'paused') {
            uploader.upload()
        } else if (state === 'uploading') {
            uploader.stop()
        }
    });
    $info.on('click', '.retry', function() {
        uploader.retry()
    });
    $info.on('click', '.ignore', function() {
        alert('todo')
    });
    $upload.addClass('state-' + state);

    var returnid = [];
    var imgpath = [];
    uploader.on('uploadSuccess', function(file,response) {
        var imgid  = response.imgid;
        var imgurl = response.image_path;
        returnid.push(imgid);
        $('#colorid').val(returnid);

        var strs= new Array(); //定义一数组 
        strs=imgurl.split(","); //字符分割
        for (i=0;i<strs.length ;i++ ) { 
        };
        var imgout = strs[2];
        imgpath.push(imgout);
        $('#imgpath').val(imgpath);

    });
    updateTotalProgress();
});