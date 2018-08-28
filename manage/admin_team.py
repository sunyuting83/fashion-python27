# coding:utf-8
from flask import Flask, render_template, redirect, session, url_for, request, g, flash, abort, jsonify, make_response
from flask_wtf import FlaskForm
from wtforms import TextField, BooleanField, PasswordField, SubmitField, SelectField, HiddenField
from wtforms.validators import Required, Email, Length
from model import Team, and_, or_, desc, asc, func, db_session
from manage import api
from public import *
import datetime


# 添加用户组表单
class AddTeamForm(FlaskForm):
	title = TextField('产品组名称', validators=[Length(min=2,max=30,message=(u'产品组必须2~30个字符之间'))], render_kw={"placeholder": "产品组名称","class": "form-control"})
	submit = SubmitField('添加',render_kw={"class": "btn btn-primary"})

# 修改用户组表单
class EditTeamForm(FlaskForm):
	id = HiddenField('id')
	title = TextField('产品组名称', validators=[Length(min=2,max=30,message=(u'产品组必须2~30个字符之间'))], render_kw={"placeholder": "产品组名称","class": "form-control"})
	submit = SubmitField('修改',render_kw={"class": "btn btn-primary"})


# 产品组列表
@api.route('/manage_team', methods=['GET', 'POST'])
def manage_team():
	teamlist = db_session.query(Team).all()

	return render_template(
		"manage_team.html", 
		pagename='manage_team', 
		teamlist=teamlist)

# 添加产品组
@api.route('/add_team', methods=['GET', 'POST'])
def add_team():
	form = AddTeamForm()
	if form.validate_on_submit():
		title = request.form.get('title')
		team = Team(title=title, addtime=datetime.datetime.now())
		team_check = db_session.query(Team).filter(Team.title == title).first()
		if team_check:
			flash('产品组已存在')
			return redirect('/manage/add_team')
		if len(title):
			try:
				db_session.add(team)
				db_session.commit()
				# 记录日志
				actions = ('%s%s%s' %('增加产品组',':',title))
				savelog(actions)
				db_session.close()
			except:
				flash("数据库错误!")
				return redirect('/manage/add_team')

			flash("添加成功,<span id='time'>3</span>秒后自动跳转管理页。")
			return redirect('/manage/add_team')
	return render_template(
		"edit_team.html", 
		pagename='manage_team',
		this='add',
		form=form)

# 修改产品组
@api.route('/edit_team', methods=['GET', 'POST'])
def edit_team():
	getid = request.args.get('id')
	teamData = db_session.query(Team).filter(Team.id == getid).\
		with_entities(Team.title, Team.id).first()
	form = EditTeamForm()
	if teamData:
		form.id.data = teamData.id
		form.title.data = teamData.title
	
	db_session.close()
	if form.validate_on_submit():
		id = request.form.get('id')
		title = request.form.get('title')
		team = Team(title=title)
		db_session.query(Team).filter(Team.id == id).update(
			{
				Team.title : title
			})
		db_session.commit()
		# 记录日志
		actions = ('%s%s%s' %('修改产品组',':',title))
		savelog(actions)
		db_session.close()

		flash("修改成功,<span id='time'>3</span>秒后自动跳转管理页。")
		return redirect('/manage/edit_team')
	return render_template(
		"edit_team.html", 
		pagename='manage_team',
		this = 'edit',
		form=form)

# 删除产品组
@api.route('/del_team', methods=['GET', 'POST'])
@login_required
def del_team():
	getid = int(request.args.get('id'))
	delg = db_session.query(Team).filter(Team.id == getid).first();
	db_session.delete(delg)
	db_session.commit()
	# 记录日志
	actions = ('%s%s%s' %('删除产品组',':',getid))
	savelog(actions)
	db_session.close()
	return jsonify({"state":"ok"})