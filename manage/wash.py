# coding:utf-8
from flask import Flask, render_template, redirect, session, url_for, request, g, flash, abort, jsonify, make_response
from flask_wtf import FlaskForm
from wtforms import TextField, BooleanField, PasswordField, SubmitField, SelectField, HiddenField
from wtforms.validators import Required, Email, Length
from model import Wash, and_, or_, desc, asc, func, db_session
from manage import api
from .public import *
import datetime


# 添加用户组表单
class AddWashForm(FlaskForm):
	icon = HiddenField('icon')
	text = TextField('洗涤说明', validators=[Length(min=2,max=80,message=(u'产品组必须2~80个字符之间'))], render_kw={"placeholder": "洗涤说明","class": "form-control"})
	submit = SubmitField('添加',render_kw={"class": "btn btn-primary"})

# 修改用户组表单
class EditWashForm(FlaskForm):
	id = HiddenField('id')
	icon = HiddenField('icon')
	oldicon = HiddenField('oldicon')
	text = TextField('洗涤说明', validators=[Length(min=2,max=30,message=(u'产品组必须2~30个字符之间'))], render_kw={"placeholder": "洗涤说明","class": "form-control"})
	submit = SubmitField('修改',render_kw={"class": "btn btn-primary"})


# 产品组列表
@api.route('/manage_wash', methods=['GET', 'POST'])
def manage_wash():
	washlist = db_session.query(Wash).all()

	return render_template(
		"manage_wash.html", 
		pagename='manage_wash', 
		washlist=washlist)

# 添加产品组
@api.route('/add_wash', methods=['GET', 'POST'])
def add_wash():
	form = AddWashForm()
	if form.validate_on_submit():
		text = request.form.get('text')
		icon = request.form.get('icon')
		wash = Wash(text=text, icon=icon)
		if len(text):
			try:
				db_session.add(wash)
				db_session.commit()
				# 记录日志
				actions = '增加洗涤说明'
				savelog(actions)
				db_session.close()
			except:
				flash("数据库错误!")
				return redirect('/manage/add_wash')

			flash("添加成功,<span id='time'>3</span>秒后自动跳转管理页。")
			return redirect('/manage/add_wash')
	return render_template(
		"edit_wash.html", 
		pagename='manage_wash',
		this='add',
		form=form)

# 修改产品组
@api.route('/edit_wash', methods=['GET', 'POST'])
def edit_wash():
	getid = request.args.get('id')
	washData = db_session.query(Wash).filter(Wash.id == getid).\
		with_entities(Wash.text, Wash.icon, Wash.id).first()
	form = EditWashForm()
	if washData:
		form.id.data = washData.id
		form.text.data = washData.text
		form.oldicon.data = washData.icon
	
	db_session.close()
	if form.validate_on_submit():
		id = request.form.get('id')
		text = request.form.get('text')
		icon = request.form.get('icon')
		wash = Wash(text=text,icon=icon)
		db_session.query(Wash).filter(Wash.id == id).update(
			{
				Wash.text : text,
				Wash.icon : icon
			})
		db_session.commit()
		# 记录日志
		actions = ('%s%s%s' %('修改洗涤说明',':',id))
		savelog(actions)
		db_session.close()

		flash("修改成功,<span id='time'>3</span>秒后自动跳转管理页。")
		return redirect('/manage/edit_wash')
	return render_template(
		"edit_wash.html", 
		pagename='manage_wash',
		this = 'edit',
		form=form)

# 删除产品组
@api.route('/del_wash', methods=['GET', 'POST'])
@login_required
def del_wash():
	getid = int(request.args.get('id'))
	delg = db_session.query(Wash).filter(Wash.id == getid).first();
	db_session.delete(delg)
	db_session.commit()
	# 记录日志
	actions = ('%s%s%s' %('删除洗涤说明',':',getid))
	savelog(actions)
	db_session.close()
	return jsonify({"state":"ok"})