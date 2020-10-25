# coding:utf-8
from flask import Flask, render_template, redirect, session, url_for, request, g, flash, abort, jsonify, make_response
from flask_wtf import FlaskForm
from wtforms import TextField, BooleanField, PasswordField, SubmitField, SelectField, HiddenField
from wtforms.validators import Required, Email, Length
from model import Manage, Group, Team, and_, or_, desc, asc, func, db_session
from manage import api
from .public import *
import hashlib
import datetime
import email_validator


# 修改管理员表单
class EditadminForm(FlaskForm):
	group = [(r.group_id, r.name) for r in  db_session.query(Group).filter(Group.power != 0).all()]
	team  = [(r.id, r.title) for r in Team.query.all()]
	id = HiddenField('id')
	
	username = TextField('职位', render_kw={"placeholder": "用户名","class": "form-control"})
	password = PasswordField('密码', render_kw={"placeholder": "密码","class": "form-control","onkeyup": "KeyUp()"})
	repassword = PasswordField('重复密码', render_kw={"placeholder": "重复密码","class": "form-control","onkeyup": "KeyUp()"})
	status = SelectField('状态', coerce=int, choices = [(0, '正常'), (1, '锁定')],render_kw={"class": "form-control"})
	purview = SelectField('职责', coerce=int, choices = [(0, '组长'), (1, '组员')],render_kw={"class": "form-control"},default=1)
	group_id = SelectField(u'管理组', coerce=int,choices = group, render_kw={"class": "form-control"},default=10)
	title = TextField('职位', validators=[Length(min=2,max=30,message=(u'职位必须2~30个字符之间'))], render_kw={"placeholder": "职位","class": "form-control"})
	name = TextField('联系人', validators=[Length(min=2,max=5,message=(u'联系人必须2~5个字符之间'))], render_kw={"placeholder": "联系人","class": "form-control"})
	phone = TextField('电话', validators=[Length(min=11,max=12,message=(u'电话必须11个字符'))], render_kw={"placeholder": "电话","class": "form-control"})
	mail = TextField('邮件', validators=[Length(min=6, message=(u'邮件地址太短！')),Email(message=(u'您输入的不是一个邮件地址！'))],render_kw={"placeholder": "邮箱","class": "form-control"})
	wechat = TextField('微信', validators=[Length(min=2,max=30,message=(u'微信必须2~30个字符之间'))], render_kw={"placeholder": "微信","class": "form-control"})
	submit = SubmitField('修改',render_kw={"class": "btn btn-primary"})
	teams = SelectField('所属组', coerce=int, choices = team, render_kw={"class": "form-control"})
	db_session.close()

# 添加管理员表单
class AddadminForm(FlaskForm):
	group = [(r.group_id, r.name) for r in  db_session.query(Group).filter(Group.power != 0).all()]
	team  = [(r.id, r.title) for r in  db_session.query(Team)]

	login_size = HiddenField('login_size',default=0)
	teamid = HiddenField('teamid')
	username = TextField('用户名',
		validators=[Length(min=4,max=30,message=(u'用户名必须4~30个字符之间'))],
		render_kw={
			"placeholder": "用户名",
			"class": "form-control",
			"onbeforepaste": "clipboardData.setData('text',clipboardData.getData('text').replace(/[\u4e00-\u9fa5]/g,''))",
			"onkeyup":"this.value=this.value.replace(/[\u4e00-\u9fa5]/g,'')",
	})
	password = PasswordField('密码', validators=[Length(min=6,max=16,message=(u'密码必须6~16个字符之间'))], render_kw={"placeholder": "密码","class": "form-control","onkeyup": "KeyUp()"})
	repassword = PasswordField('重复密码', render_kw={"placeholder": "重复密码","class": "form-control","onkeyup": "KeyUp()"})
	status = SelectField('状态', coerce=int, choices = [(0, '正常'), (1, '锁定')],render_kw={"class": "form-control"})
	purview = SelectField('职责', coerce=int, choices = [(0, '组长'), (1, '组员')],render_kw={"class": "form-control"},default=1)
	group_id = SelectField(u'管理组', coerce=int,choices = group, render_kw={"class": "form-control"},default=10)
	title = TextField('职位', validators=[Length(min=2,max=30,message=(u'职位必须2~30个字符之间'))], render_kw={"placeholder": "职位","class": "form-control"})
	name = TextField('联系人', validators=[Length(min=2,max=5,message=(u'联系人必须2~5个字符之间'))], render_kw={"placeholder": "联系人","class": "form-control"})
	phone = TextField('电话', validators=[Length(min=11,max=12,message=(u'电话必须11个字符'))], render_kw={"placeholder": "电话","class": "form-control"})
	mail = TextField('邮件', validators=[Length(min=6, message=(u'邮件地址太短！')),Email(message=(u'您输入的不是一个邮件地址！'))],render_kw={"placeholder": "邮箱","class": "form-control"})
	wechat = TextField('微信', validators=[Length(min=2,max=30,message=(u'微信必须2~30个字符之间'))], render_kw={"placeholder": "微信","class": "form-control"})
	submit = SubmitField('添加',render_kw={"class": "btn btn-primary"})
	teams = SelectField('所属组', coerce=int, choices = team, render_kw={"class": "form-control"})
	db_session.close()

# 我的信息表单
class MyInfoForm(FlaskForm):
	getid = HiddenField('getid')
	username = TextField('用户名', render_kw={"placeholder": "用户名","class": "form-control","readonly":"readonly",})
	title = TextField('职位', validators=[Length(min=2,max=30,message=(u'职位必须2~30个字符之间'))], render_kw={"placeholder": "职位","class": "form-control"})
	name = TextField('联系人', validators=[Length(min=2,max=5,message=(u'联系人必须2~5个字符之间'))], render_kw={"placeholder": "联系人","class": "form-control"})
	phone = TextField('电话', validators=[Length(min=11,max=12,message=(u'电话必须11个字符'))], render_kw={"placeholder": "电话","class": "form-control"})
	mail = TextField('邮件', validators=[Length(min=6, message=(u'邮件地址太短！')),Email(message=(u'您输入的不是一个邮件地址！'))],render_kw={"placeholder": "邮箱","class": "form-control"})
	wechat = TextField('微信', validators=[Length(min=2,max=30,message=(u'微信必须2~30个字符之间'))], render_kw={"placeholder": "微信","class": "form-control"})
	submit = SubmitField('修改',render_kw={"class": "btn btn-primary"})

# 修改密码表单
class MyPassForm(FlaskForm):
	password = PasswordField('密码', validators=[Length(min=6,max=16,message=(u'密码必须6~16个字符之间'))], render_kw={"placeholder": "密码","class": "form-control","onkeyup": "KeyUp()"})
	repassword = PasswordField('重复密码', render_kw={"placeholder": "重复密码","class": "form-control","onkeyup": "KeyUp()"})
	submit = SubmitField('修改',render_kw={"class": "btn btn-primary"})




# 管理员列表
@api.route('/manage_user', methods=['GET', 'POST'])
def manage_user():
	status = request.args.get('status',0)
	if current_user.teamid == 0:
		userlist = db_session.query(Manage).filter(Manage.status == status).all()
	else:
		userlist = db_session.query(Manage).filter(Manage.status == status, Manage.teamid == current_user.teamid).all()
	
	return render_template(
		"manage_user.html", 
		pagename='manage_user', 
		userlist=userlist)
	db_session.close()

# 搜索管理员列表
@api.route('/search_admin', methods=['GET', 'POST'])
def search_admin():
	username = request.args.get('username')
	if current_user.teamid == 0:
		userlist = db_session.query(Manage).filter(Manage.username.like("%"+username+"%")).all()
	else:
		userlist = db_session.query(Manage).filter(Manage.username.like("%"+username+"%"), Manage.teamid == current_user.teamid).all()
	return render_template(
		"manage_user.html", 
		pagename='manage_user', 
		userlist=userlist)
	db_session.close()


# 添加管理员
@api.route('/add_admin', methods=['GET', 'POST'])
def add_admin():
	this = 'add'
	form = AddadminForm()
	if form.validate_on_submit():
		teamsid = ''
		if current_user.group.power == 0:
			teamsid = request.form.get('teams')
		else:
			teamsid = request.form.get('teamid')

		username = request.form.get('username')
		password = request.form.get('password')
		status = request.form.get('status')
		purview = request.form.get('purview')
		group_id = request.form.get('group_id')
		title = request.form.get('title')
		name = request.form.get('name')
		phone = request.form.get('phone')
		mail = request.form.get('mail')
		wechat = request.form.get('wechat')
		login_size = request.form.get('login_size')
		teamid = teamsid

		m = hashlib.md5()
		m.update(request.form.get('password'))
		password = m.hexdigest()

		admin = Manage(
				username = username,
				password = password,
				status = status,
				purview = purview,
				group_id = group_id,
				last_login_time = datetime.datetime.now(),
				title = title,
				name = name,
				phone = phone,
				mail = mail,
				wechat = wechat,
				teamid = teamid,
				login_size = login_size,
				contact = 0	
		)

		admin_check = db_session.query(Manage).filter(Manage.username == username).first()
		if admin_check:
			flash('用户已存在')
			return redirect('/manage/add_admin')
		if len(username) and len(password):
			try:
				db_session.add(admin)
				db_session.commit()

				# 记录日志
				actions = ('%s%s%s' %('增加管理员',':',username))
				savelog(actions)
				db_session.close()
			except Exception as e:
				print (e)
				flash("数据库错误!")
				return redirect('/manage/add_admin')

			flash("添加成功,<span id='time'>3</span>秒后自动跳转管理页。")
			return redirect('/manage/add_admin')
	return render_template(
		"edit_admin.html", 
		pagename='manage_user',
		this = this,
		form=form)


# 修改管理员
@api.route('/edit_admin', methods=['GET', 'POST'])
def edit_admin():
	this = 'edit'
	getid = request.args.get('id')
	adminData = Manage.query.filter_by(id = getid).first()
	form = EditadminForm()
	if adminData:
		form.teams.data = adminData.teamid
		form.id.data = adminData.id
		form.username.data = adminData.username
		form.status.data = adminData.status
		form.purview.data = adminData.purview
		form.group_id.data = adminData.group_id
		form.title.data = adminData.title
		form.name.data = adminData.name
		form.phone.data = adminData.phone
		form.mail.data = adminData.mail
		form.wechat.data = adminData.wechat
	print ('这里')
	if form.validate_on_submit():
		print ('哪里')
		id = request.form.get('id')
		status = request.form.get('status')
		purview = request.form.get('purview')
		group_id = request.form.get('group_id')
		password = request.form.get('password')
		title = request.form.get('title')
		name = request.form.get('name')
		phone = request.form.get('phone')
		mail = request.form.get('mail')
		wechat = request.form.get('wechat')
		teams = request.form.get('teams')

		# 判断是否修改密码
		if not password.strip():
			db_session.query(Manage).filter(Manage.id == id).update(
				{
					Manage.status : status,
					Manage.purview : purview,
					Manage.group_id : group_id,
					Manage.title : title,
					Manage.name : name,
					Manage.phone : phone,
					Manage.mail : mail,
					Manage.teamid : teams,
					Manage.wechat : wechat
				})
			try:
				db_session.commit()
			except Exception as e:
				print (e)
				db_session.rollback()
				return jsonify({"state":"数据库错误"})
			db_session.close()
		# 如果修改密码
		else:
			m = hashlib.md5()
			m.update(request.form.get('password').encode('utf-8'))
			password = m.hexdigest()
			db_session.query(Manage).filter(Manage.id == id).update(
				{
					Manage.status : status,
					Manage.purview : purview,
					Manage.group_id : group_id,
					Manage.password : password,
					Manage.title : title,
					Manage.name : name,
					Manage.phone : phone,
					Manage.mail : mail,
					Manage.teamid : teams,
					Manage.wechat : wechat
				})
			db_session.commit()
			db_session.close()


		flash("修改成功,<span id='time'>3</span>秒后自动跳转管理页。")
		return redirect('/manage/edit_admin')
	return render_template(
		"edit_admin.html", 
		pagename='manage_user',
		this = this,
		form=form)

# 删除用户
@api.route('/del_admin', methods=['GET', 'POST'])
@login_required
def del_admin():
	getid = int(request.args.get('id'))
	delg = db_session.query(Manage).filter(Manage.id == getid).first();
	db_session.delete(delg)
	db_session.commit()
	db_session.close()
	return jsonify({"state":"ok"})


# 锁定用户
@api.route('/lock_admin', methods=['GET', 'POST'])
@login_required
def lock_admin():
	getid = int(request.args.get('id'))
	status = int(request.args.get('status'))
	thstatus = Manage.query.filter_by(id = getid).first()
	thstatus.status = status
	db_session.add(thstatus)
	db_session.commit()
	db_session.close()
	return jsonify({"state":"ok"})

# 我的信息
@api.route('/my_info', methods=['GET', 'POST'])
@api.route('/my_info/', methods=['GET', 'POST'])
def my_info():
	getid = request.args.get('getid')
	adminData = Manage.query.filter_by(id = getid).first()
	form = MyInfoForm()
	if adminData:
		form.getid.data = adminData.id
		form.username.data = adminData.username
		form.title.data = adminData.title
		form.name.data = adminData.name
		form.phone.data = adminData.phone
		form.mail.data = adminData.mail
		form.wechat.data = adminData.wechat
	
	if form.validate_on_submit():
		getid = request.form.get('getid')
		password = request.form.get('password')
		title = request.form.get('title')
		name = request.form.get('name')
		phone = request.form.get('phone')
		mail = request.form.get('mail')
		wechat = request.form.get('wechat')
		
		thuser = Manage.query.filter_by(id = getid).first()

		thuser.title  = title
		thuser.name   = name
		thuser.phone  = phone
		thuser.mail   = mail
		thuser.wechat = wechat

		try:
			db_session.add(thuser)
			db_session.commit()
		except Exception as e:
			print (e)
			db_session.rollback()
			return jsonify({"state":"数据库错误"})
		db_session.close()

		flash("修改成功,<span id='time'>3</span>秒后自动跳转管理页。")
		return redirect('/manage/my_info')
	return render_template(
		"admin_info.html", 
		pagename='manage_user',
		form=form)

# 修改我的密码
@api.route('/my_password/<int:getid>', methods=['GET', 'POST'])
@api.route('/my_password/<int:getid>/', methods=['GET', 'POST'])
def my_password(getid):
	form = MyPassForm()
	if form.validate_on_submit():
		m = hashlib.md5()
		m.update(request.form.get('password'))
		password = m.hexdigest()
		mypassword = Manage.query.filter_by(id = getid).first()
		if mypassword:
			mypassword.password = password
			try:
				db_session.add(mypassword)
				db_session.commit()
			except Exception as e:
				print (e)
				db_session.rollback()
				return jsonify({"state":"数据库错误"})
			db_session.close()

		flash("修改成功,<span id='time'>3</span>秒后自动跳转管理页。")
		return redirect(url_for('manage.my_password', getid = getid))
	return render_template(
		"my_password.html", 
		pagename='manage_user',
		form=form)
