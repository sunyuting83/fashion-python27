# coding:utf-8
from flask import Flask, render_template, redirect, session, url_for, request, g, flash, abort, jsonify, make_response
from flask_wtf import FlaskForm
from wtforms import TextField, BooleanField, PasswordField, SubmitField, SelectField, HiddenField
from wtforms.validators import Required, Email, Length
from model import Group, and_, or_, desc, asc, func, db_session
from manage import api
from .public import *
import datetime


# 添加用户组表单
class AddadminForm(FlaskForm):
	name = TextField('用户组名称', validators=[Required()],render_kw={"placeholder": "用户组名称","class": "form-control"})
	powerlist = SelectField('权限', coerce=int, choices = [ (1, '组长'), (2, '组员'), (3, '资讯组')],render_kw={"class": "form-control"})
	submit = SubmitField('添加',render_kw={"class": "btn btn-primary"})

# 修改用户组表单
class EditadminForm(FlaskForm):
	group_id = HiddenField('group_id')
	name = TextField('用户组名称', validators=[Required()],render_kw={"placeholder": "用户组名称","class": "form-control"})
	powerlist = SelectField('权限', coerce=int, choices = [ (1, '组长'), (2, '组员'), (3, '资讯组')],render_kw={"class": "form-control"})
	submit = SubmitField('修改',render_kw={"class": "btn btn-primary"})


# 管理员用户组列表
@api.route('/manage_group', methods=['GET', 'POST'])
def manage_group():
	grouplist = Group.query.all()

	return render_template(
		"manage_group.html", 
		pagename='manage_group', 
		grouplist=grouplist)

# 添加用户组
@api.route('/add_group', methods=['GET', 'POST'])
def add_group():
	form = AddadminForm()
	if form.validate_on_submit():
		name = request.form.get('name')
		powerlist = request.form.get('powerlist')
		group = Group(name=name, power=powerlist, addtime=datetime.datetime.now())
		group_check = db_session.query(Group).filter(Group.name == name).first()
		if group_check:
			flash('用户组已存在')
			return redirect('/manage/add_group')
		if len(name) and len(powerlist):
			try:
				db_session.add(group)
				db_session.commit()
				db_session.close()
			except:
				flash("数据库错误!")
				return redirect('/manage/add_group')

			flash("添加成功,<span id='time'>3</span>秒后自动跳转管理页。")
			return redirect('/manage/add_group')
	return render_template(
		"add_group.html", 
		pagename='manage_group', 
		form=form)

# 修改用户组
@api.route('/edit_group', methods=['GET', 'POST'])
@api.route('/edit_group/', methods=['GET', 'POST'])
def edit_group():
	getid = request.args.get('group_id')
	groupData = db_session.query(Group).filter(Group.group_id == getid).\
		with_entities(Group.name, Group.power, Group.group_id).first()
	form = EditadminForm()
	if groupData:
		form.group_id.data = groupData.group_id
		form.name.data = groupData.name
		form.powerlist.data = groupData.power
	
	db_session.close()
	if form.validate_on_submit():
		group_id = request.form.get('group_id')
		name = request.form.get('name')
		powerlist = request.form.get('powerlist')
		group = Group(name=name, power=powerlist)
		db_session.query(Group).filter(Group.group_id == group_id).update(
			{
				Group.name : name,
				Group.power : powerlist
			})
		db_session.commit()
		db_session.close()

		flash("修改成功,<span id='time'>3</span>秒后自动跳转管理页。")
		return redirect('/manage/edit_group')
	return render_template(
		"edit_group.html", 
		pagename='manage_group', 
		form=form)

# 删除用户组
@api.route('/del_group', methods=['GET', 'POST'])
@login_required
def del_group():
	getid = int(request.args.get('group_id'))
	delg = db_session.query(Group).filter(Group.group_id == getid).first();
	db_session.delete(delg)
	db_session.commit()
	db_session.close()
	return jsonify({"state":"ok"})