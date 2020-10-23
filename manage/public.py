# coding:utf-8
from flask import Flask, render_template, redirect, session, url_for, request, g, flash, abort, jsonify, make_response
from flask_login import LoginManager, login_user, logout_user, current_user, login_required  #登录
from flask_wtf import FlaskForm #表单
from wtforms import TextField, BooleanField, PasswordField, SubmitField
from wtforms.validators import Required, Email, Length
from flask_mail import Mail, Message #Mail
from uploader import Uploader  #加载上传组件
from yunpian_python_sdk.model import constant as YC  #加载短信组件
from yunpian_python_sdk.ypclient import YunpianClient  #加载短信组件
from threading import Thread
from config import Conf  #载入配置文件

from model import Manage, Images, ActionLog, and_, or_, desc, asc, func, db_session

from manage import api

import datetime
import hashlib
import time
import os
import time
import json
import re
from PIL import Image
from io import StringIO

# 解决flask-login与Blueprint冲突
lm = LoginManager()
@api.record_once
def on_load(state):
	lm.init_app(state.app)

lm.session_protection="basic"

# 解决flask-mail与Blueprint冲突
mail = Mail()
@api.record_once
def on_load(state):
	mail.init_app(state.app)

# 保存日志文件
def savelog(actions):
	savelog = ActionLog(username = current_user.username, actions=actions, addtime=datetime.datetime.now())
	log_check = db_session.query(ActionLog).first()

	db_session.add(savelog)
	db_session.commit()
	

# 表单验证
class LoginForm(FlaskForm):
	user_name = TextField('用户名', validators=[Required()],render_kw={"placeholder": "用户名","class": "form-control"})
	user_password = PasswordField('密  码', validators=[Required()],render_kw={"placeholder": "密码","class": "form-control"})
	remember_me = BooleanField('记住我', default=False)
	submit = SubmitField('登录',render_kw={"placeholder": "密码","class": "btn btn-primary"})

# 登录验证
@lm.user_loader
def load_user(user_id):
	return Manage.query.get(int(user_id))


@api.teardown_request
def handle_teardown_request(exception=None):
	db_session.remove()

# 登录
@api.route('/login', methods=['GET', 'POST'])
def login():
	# 验证用户是否被验证
	if current_user.is_authenticated:
		return redirect('/manage/')
	# 注册验证
	form = LoginForm()
	if form.validate_on_submit():
		m = hashlib.md5()
		m.update(str(request.form.get('user_password')).encode('utf-8'))
		upassword = m.hexdigest()
		user = Manage.login_check(request.form.get('user_name'),upassword)
		# print form.remember_me.data
		if user:
			# login_user(user, form.remember_me.data)
			login_user(user, False, False, False)
			print(current_user.manage_group.id)
			# 记录登录次数和最后登录时间IP
			user.last_login_time = datetime.datetime.now()
			user.login_size += 1
			user.last_login_ip = request.remote_addr

			try:
				db_session.add(user)
				db_session.commit()
				# 记录日志
				actions = "登录系统"
				savelog(actions)
			except:
				flash("The Database error!")
				return redirect('/manage/login')

			flash('用户名: ' + request.form.get('user_name'))
			flash('密  码: ' + request.form.get('user_password'))
			flash('记住我? ' + str(request.form.get('remember_me')))
			return redirect(url_for("manage.index", user_id = current_user.id))
		else:
			flash('登录失败，用户名不存在或密码错误')
			return redirect('/manage/login')

		db_session.close()

	return render_template(
		"login.html",
		title="后台管理系统登录",
		form=form)


# 登出
@api.route('/logout')
def logout():
	logout_user()

	return redirect(url_for('manage.index'))

# Excel上传组件
@api.route('/upexcel', methods=['GET', 'POST'])
@login_required
def upexcel():

	mimetype = 'application/json'
	result = {}
	fieldName = "file"
	config = {
		"pathFormat": "/upload/goodslist/{yyyy}{mm}{dd}/{time}{rand:6}",
		"maxSize": "2048000",
		"allowFiles": [".xls", ".xlsx"]
	}
	field = request.files['file']
	# print field
	folder =  './static'
	uploader = Uploader(field, config, folder)
	result = uploader.getFileInfo()

	result = json.dumps(result)

	if 'callback' in request.args:
		callback = request.args.get('callback')
		if re.match(r'^[\w_]+$', callback):
			result = '%s(%s)' % (callback, result)
			mimetype = 'application/javascript'
		else:
			result = json.dumps({'state': 'callback参数不合法'})

	res = make_response(result)
	res.mimetype = mimetype
	res.headers['Access-Control-Allow-Origin'] = '*'
	res.headers['Access-Control-Allow-Headers'] = 'X-Requested-With,X_Requested_With'
	return res


# 图片上传组件
@api.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():

	mimetype = 'application/json'
	result = {}
	fieldName = "file"
	config = {
		"pathFormat": "/upload/image/{yyyy}{mm}{dd}/{time}{rand:6}",
		"maxSize": "2048000",
		"allowFiles": [".png", ".jpg", ".jpeg", ".gif", ".bmp"]
	}
	field = request.files['file']
	# print field
	folder =  './static'
	uploader = Uploader(field, config, folder)
	result = uploader.getFileInfo()


	result = json.dumps(result)
	# result = result
	addresult = savePicDate(result)

	result = addresult
	# return result

	if 'callback' in request.args:
		callback = request.args.get('callback')
		if re.match(r'^[\w_]+$', callback):
			result = '%s(%s)' % (callback, result)
			mimetype = 'application/javascript'
		else:
			result = json.dumps({'state': 'callback参数不合法'})

	res = make_response(result)
	res.mimetype = mimetype
	res.headers['Access-Control-Allow-Origin'] = '*'
	res.headers['Access-Control-Allow-Headers'] = 'X-Requested-With,X_Requested_With'
	return res

# 图片上传组件
@api.route('/coverupload', methods=['GET', 'POST'])
@login_required
def coverupload():

	mimetype = 'application/json'
	result = {}
	fieldName = "file"
	config = {
		"pathFormat": "/upload/image/{yyyy}{mm}{dd}/{time}{rand:6}",
		"maxSize": "2048000",
		"allowFiles": [".png", ".jpg", ".jpeg", ".gif", ".bmp"]
	}
	field = request.files['file']
	# print field
	folder =  './static'
	uploader = Uploader(field, config, folder)
	result = uploader.getFileInfo()


	result = json.dumps(result)
	# result = result

	if 'callback' in request.args:
		callback = request.args.get('callback')
		if re.match(r'^[\w_]+$', callback):
			result = '%s(%s)' % (callback, result)
			mimetype = 'application/javascript'
		else:
			result = json.dumps({'state': 'callback参数不合法'})

	res = make_response(result)
	res.mimetype = mimetype
	res.headers['Access-Control-Allow-Origin'] = '*'
	res.headers['Access-Control-Allow-Headers'] = 'X-Requested-With,X_Requested_With'
	return res

# 多次选择删除图片
@api.route('/del_pic', methods=['GET', 'POST'])
@login_required
def del_pic():
	picid = int(request.args.get('picid'))
	deli = db_session.query(Images).filter(Images.id == picid).first();
	imgurl = deli.picurl
	imgurl = actros_split(imgurl)
	
	delImage(imgurl)
	
	db_session.delete(deli)

	db_session.commit()
	db_session.close()
	return jsonify({"state":"ok"})

# 图片地址使用,分割成数组
def actros_split(self):
	if not self:
		return []
	return self.split(',')

# 删除图片函数
def delImage(imgurl):
	root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),"..")) #获取当前文件夹的绝对路径
	for i in range(len(imgurl)):
		file_path = ("%s%s" %(root_dir, imgurl[i]))
		if os.path.isfile(file_path):
			# print file_path
			os.remove(file_path)
	return jsonify({'state':'ok'})

# 保存图片信息到数据库函数
def savePicDate(self):
	self = json.loads(self)
	imgurl = self['url']
	img_path = "./static"+self['fullName']
	imgName = resize_img(img_path,imgurl)
	imgName = ','.join(imgName) #转换数组成字符串并用,分割
	# return json.dumps({'image_path':imgName,'imgid':'sdf'}) #测试时候用的返回数据
	saveimages = Images(picurl=imgName)
	images_check = db_session.query(Images).first()
	
	try:
		db_session.add(saveimages)
		db_session.commit()
		db_session.flush()
		a_id = saveimages.id
		# 记录日志
		# actions = ('%s%s' %("上传图片",a_id))
		# savelog(actions)
		return json.dumps({'image_path':imgName,'imgid':a_id})
		db_session.close()
		
	except:
		return json.dumps({'state': '数据库错误'})
	

# 保存多种尺寸图片
def resize_img(img_path,imgurl):
	# print img_path
	url = os.path.dirname(imgurl)  #获取网址加路径
	imgpath = os.path.dirname(img_path)
	imgpath = ("%s%s"%(imgpath[1:],'/')) #获取保存路径相对地址

	filename = os.path.basename(img_path) #获取文件名+后缀

	# 拆分获得文件扩展名及文件名 shotname 不带后缀的文件名
	(filepath,tempfilename) = os.path.split(filename)
	(shotname,extension) = os.path.splitext(tempfilename)
	# 获得完整的文件路径url
	fullUrl = ("%s%s"%(imgpath,shotname))
	# print fullUrl
	# print filename,shotname
	firstName = ("%s%s" %(imgpath,filename))

	try:
		img = Image.open(img_path)
		(width,height) = img.size
		newsize = [640,230,60]
		newname = [firstName]
		for nsize in newsize:
			new_width = nsize
			hz = '_'+str(new_width)
			new_height = height * new_width / width
			out = img.resize((new_width,new_height),Image.ANTIALIAS)
			ext = os.path.splitext(img_path)[1]
			path = os.path.splitext(img_path)[0]
			new_file_name = '%s%s%s' %(path,hz,ext)
			out.save(new_file_name,quality=80)
			newname.append('%s%s%s' %(fullUrl,hz,ext))
		return newname
	except Exception as e:
		print (e)

# 短信发送函数
def message_validate(phone_number,message):
	clnt = YunpianClient(Conf.YunPian_APIKEY)
	text = message
	param = {YC.MOBILE:phone_number,YC.TEXT:text}
	r = clnt.sms().single_send(param)
	# r = r.code()
	# print r.code()
	if r.code() == 0:
		return True, r.msg()
	else:
		return False, r.msg()
 
# 发送邮件函数
def send_email(title,recipients,body,attach=None,atitle=None):
	sender = Conf.MAIL_USERNAME
	msg = Message(title, sender=sender, recipients = recipients)
	msg.html = body
	if attach != None and atitle != None:
		with open(attach) as fp:
			msg.attach(atitle, "application/x-xls", fp.read())
 
	mail.send(msg)
	return json.dumps({'state':'ok'})

# 百度编辑器上传组件
@api.route('/uploads/', methods=['GET', 'POST', 'OPTIONS'])
def local_upload():
	"""UEditor文件上传接口

	config 配置文件
	result 返回结果
	"""
	mimetype = 'application/json'
	result = {}
	action = request.args.get('action')


	# 解析JSON格式的配置文件
	with open(os.path.join(api.static_folder, 'ueditor', 'php',
						'config.json')) as fp:
		try:
			# 删除 `/**/` 之间的注释
			CONFIG = json.loads(re.sub(r'\/\*.*\*\/', '', fp.read()))
		except:
			CONFIG = {}

	if action == 'config':
		# 初始化时，返回配置文件给客户端
		result = CONFIG

	elif action in ('uploadimage', 'uploadfile', 'uploadvideo'):
		# 图片、文件、视频上传
		if action == 'uploadimage':
			fieldName = CONFIG.get('imageFieldName')
			config = {
				"pathFormat": CONFIG['imagePathFormat'],
				"maxSize": CONFIG['imageMaxSize'],
				"allowFiles": CONFIG['imageAllowFiles']
			}
		elif action == 'uploadvideo':
			fieldName = CONFIG.get('videoFieldName')
			config = {
				"pathFormat": CONFIG['videoPathFormat'],
				"maxSize": CONFIG['videoMaxSize'],
				"allowFiles": CONFIG['videoAllowFiles']
			}
		else:
			fieldName = CONFIG.get('fileFieldName')
			config = {
				"pathFormat": CONFIG['filePathFormat'],
				"maxSize": CONFIG['fileMaxSize'],
				"allowFiles": CONFIG['fileAllowFiles']
			}

		if fieldName in request.files:
			field = request.files[fieldName]
			uploader = Uploader(field, config, api.static_folder)
			result = uploader.getFileInfo()
		else:
			result['state'] = '上传接口出错'

	elif action in ('uploadscrawl'):
		# 涂鸦上传
		fieldName = CONFIG.get('scrawlFieldName')
		config = {
			"pathFormat": CONFIG.get('scrawlPathFormat'),
			"maxSize": CONFIG.get('scrawlMaxSize'),
			"allowFiles": CONFIG.get('scrawlAllowFiles'),
			"oriName": "scrawl.png"
		}
		if fieldName in request.form:
			field = request.form[fieldName]
			uploader = Uploader(field, config, api.static_folder, 'base64')
			result = uploader.getFileInfo()
		else:
			result['state'] = '上传接口出错'

	elif action in ('catchimage'):
		config = {
			"pathFormat": CONFIG['catcherPathFormat'],
			"maxSize": CONFIG['catcherMaxSize'],
			"allowFiles": CONFIG['catcherAllowFiles'],
			"oriName": "remote.png"
		}
		fieldName = CONFIG['catcherFieldName']

		if fieldName in request.form:
			# 这里比较奇怪，远程抓图提交的表单名称不是这个
			source = []
		elif '%s[]' % fieldName in request.form:
			# 而是这个
			source = request.form.getlist('%s[]' % fieldName)

		_list = []
		for imgurl in source:
			uploader = Uploader(imgurl, config, api.static_folder, 'remote')
			info = uploader.getFileInfo()
			_list.append({
				'state': info['state'],
				'url': info['url'],
				'original': info['original'],
				'source': imgurl,
			})

		result['state'] = 'SUCCESS' if len(_list) > 0 else 'ERROR'
		result['list'] = _list

	else:
		result['state'] = '请求地址出错'

	result = json.dumps(result)

	if 'callback' in request.args:
		callback = request.args.get('callback')
		if re.match(r'^[\w_]+$', callback):
			result = '%s(%s)' % (callback, result)
			mimetype = 'application/javascript'
		else:
			result = json.dumps({'state': 'callback参数不合法'})

	res = make_response(result)
	res.mimetype = mimetype
	res.headers['Access-Control-Allow-Origin'] = '*'
	res.headers['Access-Control-Allow-Headers'] = 'X-Requested-With,X_Requested_With'
	return res