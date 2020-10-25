# coding:utf-8
from flask import Flask, request, jsonify, g, render_template, redirect, url_for, session, current_app
from model import Users, db_session, desc
from .main import message_validate #加载云片短信发送模块
from .decorator import login_check #加载验证模块
from mobile import api #加载蓝图
import hashlib
import time
import random
import datetime

# 获取汉字首字母
def get_cn_first_letter(str,codec="UTF8"):
	# if codec!="GBK":
	# 	if codec!="unicode":
	# 		str=str.decode(codec)
	# 	str=str.encode("GBK")

	if str<"\xb0\xa1" or str>"\xd7\xf9":
		return "X"
	if str<"\xb0\xc4":
		return "A"
	if str<"\xb2\xc0":
		return "B"
	if str<"\xb4\xed":
		return "C"
	if str<"\xb6\xe9":
		return "D"
	if str<"\xb7\xa1":
		return "E"
	if str<"\xb8\xc0":
		return "F"
	if str<"\xb9\xfd":
		return "G"
	if str<"\xbb\xf6":
		return "H"
	if str<"\xbf\xa5":
		return "J"
	if str<"\xc0\xab":
		return "K"
	if str<"\xc2\xe7":
		return "L"
	if str<"\xc4\xc2":
		return "M"
	if str<"\xc5\xb5":
		return "N"
	if str<"\xc5\xbd":
		return "O"
	if str<"\xc6\xd9":
		return "P"
	if str<"\xc8\xba":
		return "Q"
	if str<"\xc8\xf5":
		return "R"
	if str<"\xcb\xf9":
		return "S"
	if str<"\xcd\xd9":
		return "T"
	if str<"\xce\xf3":
		return "W"
	if str<"\xd1\x88":
		return "X"
	if str<"\xd4\xd0":
		return "Y"
	if str<"\xd7\xf9":
		return "Z"

@api.route('/login', methods=['POST'])
def login():
	phone_number = request.get_json().get('phone_number')
	password = request.get_json().get('password')
	touchid = request.get_json().get('touchid')

	user = Users.query.filter_by(phone=phone_number).first()
	if not user:
		return jsonify({'code': 0, 'message': '没有此用户'})

	if user.password != password:
		return jsonify({'code': 0, 'message': '密码错误'})

	if user.verify != 0:
		return jsonify({'code': 0, 'message': '账户还没有通过审核'})

	if user.lock != 0:
		return jsonify({'code': 0, 'message': '账户被锁定'})

	if user.touchid != touchid or user.touchid != None:
		user.touchid = touchid
		try:
			db_session.add(user)
			db_session.commit()
		except Exception as e:
			print (e)
			db_session.rollback()
			return jsonify({'code': 0, 'message': '数据库错误'})

	m = hashlib.md5()
	m.update(str(phone_number).encode('utf-8'))
	m.update(str(password).encode('utf-8'))
	m.update(str(int(time.time())).encode('utf-8'))
	token = m.hexdigest()

	pipeline = current_app.redis.pipeline()
	pipeline.hmset('user:%s' % user.phone, {'token': token, 'company': user.company, 'app_online': 1})
	pipeline.set('token:%s' % token, user.phone)
	pipeline.expire('token:%s' % token, 3600*24*30)
	pipeline.execute()
	return jsonify({'code': 1, 'message': '成功登录', 'userid': user.id, 'token': token})


@api.route('/user')
@login_check
def user():
	user = g.current_user
	touched = user.touchid
	if touched == None:
		touchis = 0
	else:
		touchis = 1

	company = current_app.redis.hget('user:%s' % user.phone, 'company').decode('utf-8')
	pingying = user.truename[-1]
	pingying = get_cn_first_letter(pingying)
	return jsonify({'code': 1, 'company': company, 'phone': user.phone, 'mail': user.mail, 'contact': user.truename, 'userid': user.id, 'pingying': pingying, 'touchis': touchis})


@api.route('/logout')
@login_check
def logout():
	user = g.current_user

	pipeline = current_app.redis.pipeline()
	pipeline.delete('token:%s' % g.token)
	pipeline.hmset('user:%s' % user.phone, {'app_online': 0})
	pipeline.execute()
	return jsonify({'code': 1, 'message': '成功注销'})



@api.route('/register-step-1', methods=['POST'])
def register_step_1():
	"""
	接受phone_number,发送短信
	"""
	phone_number = request.get_json().get('phone_number')
	send_phone_number = '%s%s' %('+',phone_number)
	# print send_phone_number
	user = Users.query.filter_by(phone=phone_number).first()

	if user:
		return jsonify({'code': 0, 'message': '该用户已经存在,注册失败'})
	validate_number = str(random.randint(100000, 1000000))
	result, err_message = message_validate(send_phone_number, validate_number) #调用发送短信函数

	if not result:
		return jsonify({'code': 0, 'message': err_message})

	pipeline = current_app.redis.pipeline()
	pipeline.set('validate:%s' % phone_number, validate_number)
	pipeline.expire('validate:%s' % phone_number, 300)
	pipeline.execute()

	return jsonify({'code': 1, 'message': '发送成功'})


@api.route('/register-step-2', methods=['POST'])
def register_step_2():
	"""
	验证短信接口
	"""
	phone_number = request.get_json().get('phone_number')
	validate_number = request.get_json().get('validate_number')
	validate_number_in_redis = current_app.redis.get('validate:%s' % phone_number).decode('utf-8')

	if validate_number != validate_number_in_redis:
		return jsonify({'code': 0, 'message': '验证没有通过'})

	pipe_line = current_app.redis.pipeline()
	pipe_line.set('is_validate:%s' % phone_number, '1')
	pipe_line.expire('is_validate:%s' % phone_number, 300)
	pipe_line.execute()

	return jsonify({'code': 1, 'message': '短信验证通过'})


@api.route('/register-step-3', methods=['POST'])
def register_step_3():
	"""
	密码提交
	"""
	phone_number = request.get_json().get('phone_number')
	password = request.get_json().get('password')
	password_confirm = request.get_json().get('password_confirm')

	if len(password) < 6 or len(password) > 30:
		# 这边可以自己拓展条件
		return jsonify({'code': 0, 'message': '密码长度不符合要求'})

	if password != password_confirm:
		return jsonify({'code': 0, 'message': '密码和密码确认不一致'})

	is_validate = current_app.redis.get('is_validate:%s' % phone_number).decode('utf-8')

	if is_validate != '1':
		return jsonify({'code': 0, 'message': '验证码没有通过'})

	pipeline = current_app.redis.pipeline()
	pipeline.hset('register:%s' % phone_number, 'password', password)
	pipeline.expire('register:%s' % phone_number, 300)
	pipeline.execute()

	return jsonify({'code': 1, 'message': '提交密码成功'})


@api.route('/register-step-4', methods=['POST'])
def register_step_4():
	"""
	基本资料提交
	"""
	phone_number = request.get_json().get('phone_number')
	mail = request.get_json().get('mail')
	company = request.get_json().get('company')
	truename = request.get_json().get('truename')

	is_validate = current_app.redis.get('is_validate:%s' % phone_number).decode('utf-8')

	if is_validate != '1':
		return jsonify({'code': 0, 'message': '验证码没有通过'})

	password = current_app.redis.hget('register:%s' % phone_number, 'password').decode('utf-8')

	new_user = Users(phone=phone_number, password=password, mail=mail, company=company, truename=truename, lock=0, verify=1, teamid=0, addtime=datetime.datetime.now())
	db_session.add(new_user)

	try:
		db_session.commit()
	except Exception as e:
		print (e)
		db_session.rollback()
		return jsonify({'code': 0, 'message': '注册失败'})
	finally:
		current_app.redis.delete('is_validate:%s' % phone_number)
		current_app.redis.delete('register:%s' % phone_number)

	return jsonify({'code': 1, 'message': '注册成功，请等待审核'})


@api.route('/post_userinfo', methods=['POST'])
def post_userinfo():
	userid = g.current_user.id
	truename = request.get_json().get('truename')
	mail = request.get_json().get('mail')

	userinfo = Users.query.filter_by(id=userid).first()
	if userinfo:
		userinfo.truename = truename
		userinfo.mail = mail
		try:
			db_session.add(userinfo)
			db_session.commit()
		except Exception as e:
			print (e)
			db_session.rollback()
			return jsonify({'code': 0, 'message': '数据库错误'})

	return jsonify({'code' : 1, 'message': '修改资料成功'})

@api.route('/change_password', methods=['POST'])
def change_password():
	userid = g.current_user.id
	password = request.get_json().get('password')

	userinfo = Users.query.filter_by(id=userid).first()
	if userinfo:
		userinfo.password = password
		try:
			db_session.add(userinfo)
			db_session.commit()
		except Exception as e:
			print (e)
			db_session.rollback()
			return jsonify({'code': 0, 'message': '数据库错误'})

	return jsonify({'code' : 1, 'message': '修改密码成功'})

# 指纹登陆
@api.route('/touch_login', methods=['POST'])
def touch_login():

	touchid = request.get_json().get('touchid')

	user = Users.query.filter_by(touchid = touchid).first()

	if user.lock != 0:
		return jsonify({'code': 0, 'message': '账户被锁定'})

	m = hashlib.md5()
	m.update(str(int(user.phone)).encode('utf-8'))
	m.update(str(user.password).encode('utf-8'))
	m.update(str(int(time.time())).encode('utf-8'))
	token = m.hexdigest()

	pipeline = current_app.redis.pipeline()
	pipeline.hmset('user:%s' % user.phone, {'token': token, 'company': user.company, 'app_online': 1})
	pipeline.set('token:%s' % token, user.phone)
	pipeline.expire('token:%s' % token, 3600*24*30)
	pipeline.execute()

	return jsonify({'code': 1, 'message': '成功登录', 'userid': user.id, 'token': token})

# 开启指纹
@api.route('/open_touch', methods=['POST'])
@login_check
def open_touch():
	userid = g.current_user.id

	m = hashlib.md5()
	m.update(str(request.get_json().get('touchid')).encode('utf-8'))
	touchid = m.hexdigest()

	print (touchid)

	userinfo = Users.query.filter_by(id = userid).first()
	if userinfo:
		userinfo.touchid = touchid
		try:
			db_session.add(userinfo)
			db_session.commit()
		except Exception as e:
			print (e)
			db_session.rollback()
			return jsonify({'code': 0, 'message': '数据库错误'})

	return jsonify({'code' : 1, 'message': '指纹开启成功'})

# 关闭指纹
@api.route('/close_touch', methods=['POST'])
@login_check
def close_touch():
	userid = g.current_user.id
	touchid = None

	userinfo = Users.query.filter_by(id = userid).first()
	if userinfo:
		userinfo.touchid = touchid
		try:
			db_session.add(userinfo)
			db_session.commit()
		except Exception as e:
			print (e)
			db_session.rollback()
			return jsonify({'code': 0, 'message': '数据库错误'})

	return jsonify({'code' : 1, 'message': '指纹关闭成功'})

'''
忘记密码开始
'''
@api.route('/forget-1', methods=['POST'])
def forget_1():
	"""
	接受phone_number,发送短信
	"""
	phone_number = request.get_json().get('phone_number')
	send_phone_number = '%s%s' %('+',phone_number)
	# print send_phone_number
	user = Users.query.filter_by(phone=phone_number).first()

	if user:
		validate_number = str(random.randint(100000, 1000000))
		print (validate_number)
		result, err_message = message_validate(send_phone_number, validate_number) #调用发送短信函数

		if not result:
			return jsonify({'code': 0, 'message': err_message})

		pipeline = current_app.redis.pipeline()
		pipeline.set('validate:%s' % phone_number, validate_number)
		pipeline.expire('validate:%s' % phone_number, 300)
		pipeline.execute()

		return jsonify({'code': 1, 'message': '发送成功'})
	else:
		return jsonify({'code': 0, 'message': '没有此用户'})

@api.route('/forget-2', methods=['POST'])
def forget_2():
	"""
	验证短信接口
	"""
	phone_number = request.get_json().get('phone_number')
	validate_number = request.get_json().get('validate_number')
	validate_number_in_redis = current_app.redis.get('validate:%s' % phone_number).decode('utf-8')

	if validate_number != validate_number_in_redis:
		return jsonify({'code': 0, 'message': '验证没有通过'})

	pipe_line = current_app.redis.pipeline()
	pipe_line.set('is_validate:%s' % phone_number, '1')
	pipe_line.expire('is_validate:%s' % phone_number, 300)
	pipe_line.execute()

	return jsonify({'code': 1, 'message': '短信验证通过'})

@api.route('/forget-3', methods=['POST'])
def forget_3():
	"""
	密码提交
	"""
	phone_number = request.get_json().get('phone_number')
	password = request.get_json().get('password')
	password_confirm = request.get_json().get('password_confirm')

	if len(password) < 6 or len(password) > 30:
		# 这边可以自己拓展条件
		return jsonify({'code': 0, 'message': '密码长度不符合要求'})

	if password != password_confirm:
		return jsonify({'code': 0, 'message': '密码和密码确认不一致'})

	is_validate = current_app.redis.get('is_validate:%s' % phone_number).decode('utf-8')

	if is_validate != '1':
		return jsonify({'code': 0, 'message': '验证码没有通过'})

	userinfo = Users.query.filter_by(phone=phone_number).first()
	if userinfo:
		userinfo.password = password
		try:
			db_session.add(userinfo)
			db_session.commit()
		except Exception as e:
			print (e)
			db_session.rollback()
			return jsonify({'code': 0, 'message': '数据库错误'})
		finally:
			current_app.redis.delete('is_validate:%s' % phone_number)
			current_app.redis.delete('register:%s' % phone_number)

		return jsonify({'code' : 1, 'message': '修改密码成功'})
