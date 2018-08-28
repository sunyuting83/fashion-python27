# coding:utf-8
from flask import Flask, render_template, redirect, session, url_for, request, g, flash, abort, jsonify, make_response
from flask_wtf import FlaskForm
from wtforms import TextField, BooleanField, PasswordField, SubmitField, SelectField, HiddenField
from wtforms.validators import Required, Email, Length
from manage import api
from public import *
from config import Conf

import datetime
import json	

# 配置邮件表单
class EditEmailForm(FlaskForm):
	mail_server = TextField('邮件服务器地址', validators=[Required()],render_kw={"placeholder": "邮件服务器地址","class": "form-control"})
	mail_port = TextField('邮件服务器端口', validators=[Required()],render_kw={"placeholder": "邮件服务器端口","class": "form-control"})
	mail_use_tls = BooleanField('使用安全链接', default=True)
	mail_username = TextField('邮箱用户名', validators=[Required()],render_kw={"placeholder": "邮箱用户名","class": "form-control"})
	mail_password = PasswordField('邮箱密码', validators=[Required()],render_kw={"placeholder": "邮箱密码","class": "form-control","onkeyup": "KeyUp()"})
	repassword = PasswordField('重复密码', render_kw={"placeholder": "重复密码","class": "form-control","onkeyup": "KeyUp()"})
	submit = SubmitField('更新',render_kw={"class": "btn btn-primary"})
# 配置短信表单
class EditMassagesForm(FlaskForm):
	group_id = HiddenField('group_id')
	name = TextField('用户组名称', validators=[Required()],render_kw={"placeholder": "用户组名称","class": "form-control"})
	powerlist = SelectField('权限', coerce=int, choices = [ (1, '组长'), (2, '组员'), (3, '资讯组')],render_kw={"class": "form-control"})
	submit = SubmitField('更新',render_kw={"class": "btn btn-primary"})

def check_json_value(dic_json,k,v):
	if isinstance(dic_json,dict):
		for key in dic_json:
			if key == k:
				dic_json[key] = v
			elif isinstance(dic_json[key],dict):
				check_json_value(dic_json[key],k,v)

def loadConfig():
	data = open("config.json")
	setting = json.load(data)
	data.close()
	return setting


# 修改用户组
@api.route('/sys_config', methods=['GET', 'POST'])
@api.route('/sys_config/', methods=['GET', 'POST'])
def sys_config():
	mailform = EditEmailForm()

	# 旧数据显示
	mailform.mail_server.data   = Conf.MAIL_SERVER
	mailform.mail_port.data     = Conf.MAIL_PORT
	mailform.mail_use_tls.data  = Conf.MAIL_USE_TLS
	mailform.mail_username.data = Conf.MAIL_USERNAME
	mailform.mail_password.data = Conf.MAIL_PASSWORD
	mailform.repassword.data = Conf.MAIL_PASSWORD

	# 处理提交的邮件表单
	if mailform.validate_on_submit():
		mail_server = request.form.get('mail_server')
		mail_port = request.form.get('mail_port')
		mail_use_tls = request.form.get('mail_use_tls')
		mail_username = request.form.get('mail_username')
		mail_password = request.form.get('mail_password')

		
		if mail_use_tls is None:
			mail_use_tls = False
		else:
			mail_use_tls = True

		# 判断是否修改密码
		if not mail_password.strip():
			'''写入json文件开始'''
			date_json = loadConfig()
			check_json_value(date_json,'MAIL_SERVER',mail_server)
			check_json_value(date_json,'MAIL_PORT',mail_port)
			check_json_value(date_json,'MAIL_USE_TLS',mail_use_tls)
			check_json_value(date_json,'MAIL_USERNAME',mail_username)
			fb = open('config.json','w')  
			fb.write(json.dumps(date_json))  
			fb.close()
		else:
			'''
			写入json文件开始
			如果修改密码
			'''
			date_json = loadConfig()
			check_json_value(date_json,'MAIL_SERVER',mail_server)
			check_json_value(date_json,'MAIL_PORT',mail_port)
			check_json_value(date_json,'MAIL_USE_TLS',mail_use_tls)
			check_json_value(date_json,'MAIL_USERNAME',mail_username)
			check_json_value(date_json,'MAIL_PASSWORD',mail_password)
			fb = open('config.json','w')  
			fb.write(json.dumps(date_json))  
			fb.close()
			

	return render_template(
		"sys_config.html", 
		pagename='sys_config',
		mailform = mailform)