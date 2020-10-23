# coding:utf-8
from flask import Flask, render_template, redirect, session, url_for, request, g, flash, abort, jsonify, make_response
from flask_wtf import FlaskForm
from wtforms import TextField, BooleanField, PasswordField, SubmitField, SelectField, HiddenField, IntegerField, StringField
from wtforms.validators import Required, Email, Length
from model import ContactUs, Manage, and_, or_, desc, asc, func, db_session
from manage import api
from .public import *

# 修改管理员表单
class EditusForm(FlaskForm):

	id = HiddenField('id')
	department = TextField('部门', validators=[Length(min=2,max=50,message=(u'部门名称必须2~50个字符之间'))], render_kw={"placeholder": "部门","class": "form-control"})
	title = TextField('职位', validators=[Length(min=2,max=30,message=(u'职位必须2~30个字符之间'))], render_kw={"placeholder": "职位","class": "form-control"})
	name = TextField('联系人', validators=[Length(min=2,max=5,message=(u'联系人必须2~5个字符之间'))], render_kw={"placeholder": "联系人","class": "form-control"})
	phone = TextField('电话', validators=[Length(min=11,max=12,message=(u'电话必须11个字符'))], render_kw={"placeholder": "电话","class": "form-control"})
	mail = TextField('邮件', validators=[Length(min=6, message=(u'邮件地址太短！')),Email(message=(u'您输入的不是一个邮件地址！'))],render_kw={"placeholder": "邮箱","class": "form-control"})
	wechat = TextField('微信', validators=[Length(min=2,max=30,message=(u'微信必须2~30个字符之间'))], render_kw={"placeholder": "微信","class": "form-control"})
	sort = TextField('排序', validators=[Required()], render_kw={"placeholder": "排序","class": "form-control"})
	submit = SubmitField('修改', validators=[Required()],render_kw={"class": "btn btn-primary"})

# 添加管理员表单
class AddusForm(FlaskForm):

	department = TextField('部门', validators=[Length(min=2,max=50,message=(u'部门名称必须2~50个字符之间'))], render_kw={"placeholder": "部门","class": "form-control"})
	title = TextField('职位', validators=[Length(min=2,max=30,message=(u'职位必须2~30个字符之间'))], render_kw={"placeholder": "职位","class": "form-control"})
	name = TextField('联系人', validators=[Length(min=2,max=5,message=(u'联系人必须2~5个字符之间'))], render_kw={"placeholder": "联系人","class": "form-control"})
	phone = TextField('电话', validators=[Length(min=11,max=12,message=(u'电话必须11个字符'))], render_kw={"placeholder": "电话","class": "form-control"})
	mail = TextField('邮件', validators=[Length(min=6, message=(u'邮件地址太短！')),Email(message=(u'您输入的不是一个邮件地址！'))],render_kw={"placeholder": "邮箱","class": "form-control"})
	wechat = TextField('微信', validators=[Length(min=2,max=30,message=(u'微信必须2~30个字符之间'))], render_kw={"placeholder": "微信","class": "form-control"})
	sort = TextField('排序', validators=[Required()], render_kw={"placeholder": "排序","class": "form-control"},default=0)
	submit = SubmitField('修改',render_kw={"class": "btn btn-primary"})



# 联系人列表
# @api.route('/contactus', methods=['GET', 'POST'])
# def contactus():
# 	contactlist = db_session.query(ContactUs).all()
# 	return render_template(
# 		"contactus.html", 
# 		pagename='contact_us', 
# 		contactlist=contactlist)
# 	db_session.close()
# 联系人列表
@api.route('/contactus', methods=['GET', 'POST'])
@api.route('/contactus/', methods=['GET', 'POST'])
@login_required
def contactus():
	if current_user.group.power == 0:  #超级管理员
		contactlist = Manage.query.all()
	if current_user.group.power == 1:  #组长
		contactlist = Manage.query.filter_by(teamid = current_user.teamid).all()
	return render_template(
		"contactus.html", 
		pagename='contact_us', 
		contactlist=contactlist)
	db_session.close()


# 添加管理员
@api.route('/add_contact', methods=['GET', 'POST'])
@login_required
def add_contact():
	this = 'add'
	form = AddusForm()
	if form.validate_on_submit():
		department = request.form.get('department')
		title = request.form.get('title')
		name = request.form.get('name')
		phone = request.form.get('phone')
		mail = request.form.get('mail')
		wechat = request.form.get('wechat')
		sort = request.form.get('sort')

		contact = ContactUs(department=department, title=title, name=name, phone=phone, mail=mail, wechat=wechat, sort=sort)

		contact_check = db_session.query(ContactUs).order_by(ContactUs.sort)

		if len(department) and len(title) and len(name) and len(phone) and len(mail) and len(wechat):
			try:
				db_session.add(contact)
				db_session.commit()
				db_session.close()
			except:
				flash("数据库错误!")
				return redirect('/manage/add_contact')

			flash("添加成功,<span id='time'>3</span>秒后自动跳转管理页。")
			return redirect('/manage/add_contact')
	return render_template(
		"edit_contact.html", 
		pagename='contact_us',
		this = this,
		form=form)


# 修改管理员
@api.route('/edit_contact', methods=['GET', 'POST'])
@login_required
def edit_contact():
	this = 'edit'
	getid = request.args.get('id')
	contactData = db_session.query(ContactUs).filter(ContactUs.id == getid).\
		with_entities(ContactUs.id, ContactUs.department, ContactUs.title, ContactUs.name, ContactUs.phone, ContactUs.mail, ContactUs.wechat, ContactUs.sort).first()

	form = EditusForm()
	if contactData:
		form.id.data = contactData.id
		form.department.data = contactData.department
		form.title.data = contactData.title
		form.name.data = contactData.name
		form.phone.data = contactData.phone
		form.mail.data = contactData.mail
		form.wechat.data = contactData.wechat
		form.sort.data = contactData.sort
	
	db_session.close()
	if form.validate_on_submit():
		id = request.form.get('id')
		department = request.form.get('department')
		title = request.form.get('title')
		name = request.form.get('name')
		phone = request.form.get('phone')
		mail = request.form.get('mail')
		wechat = request.form.get('wechat')
		sort = request.form.get('sort')

		db_session.query(ContactUs).filter(ContactUs.id == id).update(
			{
				ContactUs.department : department,
				ContactUs.title : title,
				ContactUs.name : name,
				ContactUs.phone : phone,
				ContactUs.mail : mail,
				ContactUs.wechat : wechat,
				ContactUs.sort : sort
			})
		db_session.commit()
		db_session.close()


		flash("修改成功,<span id='time'>3</span>秒后自动跳转管理页。")
		return redirect('/manage/edit_contact')
	return render_template(
		"edit_contact.html", 
		pagename='contact_us', 
		this = this,
		form=form)

# 删除用户
@api.route('/del_contact', methods=['GET', 'POST'])
@login_required
def del_contact():
	getid = int(request.args.get('id'))
	delg = db_session.query(ContactUs).filter(ContactUs.id == getid).first();
	db_session.delete(delg)
	db_session.commit()
	db_session.close()
	return jsonify({"state":"ok"})

# 更新用户状态
@api.route('/up_contact', methods=['GET', 'POST'])
@api.route('/up_contact/', methods=['GET', 'POST'])
@login_required
def up_contact():
	getid = int(request.args.get('id'))
	status = int(request.args.get('status'))
	if status == 0:
		actioni = '在联系我们中显示用户：'
	else:
		actioni = '在联系我们中隐藏用户：'
	upthis = db_session.query(Manage).filter(Manage.id == getid).first();
	if upthis:
		upthis.contact = status
		db_session.add(upthis)
		try:
			db_session.add(upthis)
			db_session.commit()
			# 记录日志
			actions = ('%s%s' %(actioni,upthis.username))
			savelog(actions)
		except Exception as e:
			print (e)
			db_session.rollback()
			return jsonify({"state":"数据库错误"})
		db_session.close()
	return jsonify({"state":"ok"})