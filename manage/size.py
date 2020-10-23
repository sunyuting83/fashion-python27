# coding:utf-8
from flask import Flask, render_template, redirect, session, url_for, request, g, flash, abort, jsonify, make_response
from flask_wtf import FlaskForm
from wtforms import TextField, BooleanField, PasswordField, SubmitField, SelectField, HiddenField
from wtforms.validators import Required, Email, Length
from model import Size, and_, or_, desc, asc, func, db_session
from manage import api
from .public import *
import datetime


# 添加用户组表单
class AddSizeForm(FlaskForm):
	sizename = TextField('尺码标题', validators=[Length(min=2,max=30,message=(u'尺码名称必须2~30个字符之间'))], render_kw={"placeholder": "尺码标题","class": "form-control"})
	sizeis = TextField('尺码', validators=[Length(min=2,max=80,message=(u'尺码必须2~80个字符之间'))], render_kw={"placeholder": "尺码","class": "form-control"})
	submit = SubmitField('添加',render_kw={"class": "btn btn-primary"})

# 修改用户组表单
class EditSizeForm(FlaskForm):
	id = HiddenField('id')
	sizename = TextField('尺码标题', validators=[Length(min=2,max=30,message=(u'尺码名称必须2~30个字符之间'))], render_kw={"placeholder": "尺码标题","class": "form-control"})
	sizeis = TextField('尺码', validators=[Length(min=2,max=30,message=(u'尺码必须2~30个字符之间'))], render_kw={"placeholder": "尺码","class": "form-control"})
	submit = SubmitField('修改',render_kw={"class": "btn btn-primary"})


# 尺码列表
@api.route('/manage_size', methods=['GET', 'POST'])
def manage_size():
	sizelist = Size.query.all()

	return render_template(
		"manage_size.html", 
		pagename='manage_size', 
		sizelist=sizelist)

# 添加尺码
@api.route('/add_size', methods=['GET', 'POST'])
def add_size():
	form = AddSizeForm()
	if form.validate_on_submit():
		sizename = request.form.get('sizename')
		sizeis = request.form.get('sizeis')
		size = Size(size=sizeis, size_title=sizename)
		if len(sizeis):
			try:
				db_session.add(size)
				db_session.commit()
				# 记录日志
				actions = '增加尺码'
				savelog(actions)
			except:
				flash("数据库错误!")
				return redirect('/manage/add_size')

		flash("添加成功,<span id='time'>3</span>秒后自动跳转管理页。")
		return redirect('/manage/add_size')
	return render_template(
		"edit_size.html", 
		pagename='manage_size',
		this='add',
		form=form)

# 修改尺码
@api.route('/edit_size', methods=['GET', 'POST'])
def edit_size():
	getid = request.args.get('id')
	sizeData = db_session.query(Size).filter(Size.id == getid).\
		with_entities(Size.size, Size.size_title, Size.id).first()
	form = EditSizeForm()
	if sizeData:
		form.id.data = sizeData.id
		form.sizename.data = sizeData.size_title
		form.sizeis.data = sizeData.size
	
	db_session.close()
	if form.validate_on_submit():
		id = request.form.get('id')
		sizename = request.form.get('sizename')
		sizeis = request.form.get('sizeis')
		size = db_session.query(Size).filter_by(id = id).first()
		if size:
			size.size = sizeis
			size.size_title = sizename
			try:
				db_session.add(size)
				db_session.commit()
				# 记录日志
				actions = ('%s%s%s' %('修改尺码',':',id))
				savelog(actions)
				db_session.close()
			except:
				flash("数据库错误!")
				return redirect('/manage/edit_size')

		flash("修改成功,<span id='time'>3</span>秒后自动跳转管理页。")
		return redirect('/manage/edit_size')

	return render_template(
		"edit_size.html", 
		pagename='manage_size',
		this = 'edit',
		form=form)

# 删除尺码
@api.route('/del_size', methods=['GET', 'POST'])
@login_required
def del_size():
	getid = int(request.args.get('id'))
	delg = db_session.query(Size).filter(Size.id == getid).first();
	db_session.delete(delg)
	db_session.commit()
	# 记录日志
	actions = ('%s%s%s' %('删除尺码',':',getid))
	savelog(actions)
	db_session.close()
	return jsonify({"state":"ok"})