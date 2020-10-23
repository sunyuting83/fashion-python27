# coding:utf-8
from flask import Flask, request, jsonify, g, render_template, redirect, url_for, session, current_app
from model import Users, db_session, desc
# 加载云片短信模块
from yunpian_python_sdk.model import constant as YC
from yunpian_python_sdk.ypclient import YunpianClient
from config import Conf

from .decorator import login_check

from mobile import api

import json


@api.before_request
def before_request():
	token = request.headers.get('token')
	phone_number = current_app.redis.get('token:%s' % token)
	if phone_number:
		g.current_user = Users.query.filter_by(phone=phone_number).first()
		g.token = token
	return

@api.teardown_request
def handle_teardown_request(exception):
	db_session.remove()


@api.route('/')
def hello_world():
	return 'Hello World!'


# 初始化client,apikey作为所有请求的默认值
def message_validate(phone_number,validate_number):
	clnt = YunpianClient(Conf.YunPian_APIKEY)
	country = phone_number[0:3]
	if country == '+86':
		text = '%s%s%s' %('【1ShowRoom】您的验证码是',validate_number,'。如非本人操作，请忽略本短信')
	else:
		text = '%s%s' %('【1ShowRoom】Your 1ShowRoomOnline ID Verification Code is:',validate_number)
	# print country,text
	param = {YC.MOBILE:phone_number,YC.TEXT:text}
	r = clnt.sms().single_send(param)
	# r = r.code()
	# print r.code()
	if r.code() == 0:
		return True, r.msg()
	else:
		return False, r.msg()