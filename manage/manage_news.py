# coding:utf-8
from flask import Flask, render_template, redirect, session, url_for, request, g, flash, abort, jsonify, make_response
from flask_wtf import FlaskForm
from wtforms import TextField, BooleanField, PasswordField, SubmitField, SelectField, HiddenField, StringField, TextAreaField
from wtforms.validators import Required, Email, Length
from model import News, and_, or_, desc, asc, func, db_session

from .public import *

from manage import api

import math
import datetime
from html.parser import HTMLParser
import cgi
import html


# 修改资讯表单
class EditNewsForm(FlaskForm):
	id = HiddenField('id')
	userid = HiddenField('userid')
	content = HiddenField('content')
	title = TextField('标题', validators=[Length(min=2,max=30,message=(u'职位必须2~30个字符之间'))], render_kw={"placeholder": "标题","class": "form-control"})
	display = SelectField('可见性', coerce=int, choices = [(0, '可见'), (1, '隐藏')],render_kw={"class": "form-control"})
	submit = SubmitField('修改',render_kw={"class": "btn btn-primary"})

# 添加资讯表单
class AddNewsForm(FlaskForm):
	userid = HiddenField('userid')
	title = TextField('标题', validators=[Length(min=2,max=30,message=(u'职位必须2~30个字符之间'))], render_kw={"placeholder": "标题","class": "form-control"})
	display = SelectField('可见性', coerce=int, choices = [(0, '可见'), (1, '隐藏')],render_kw={"class": "form-control"})
	submit = SubmitField('添加',render_kw={"class": "btn btn-primary"})



# 资讯列表
@api.route('/manage_news', methods=['GET', 'POST'])
@login_required
def manage_news():
	pid = int(request.args.get('pid'))
	if pid == 1:
		tsActive = "manage_news"
	elif pid == 2:
		tsActive = "help"
	elif pid == 3:
		tsActive = "manage_company"
	display = request.args.get('display',0)

	title = request.args.get('title')
	# print title

	# 分页开始
	lim = int(25) #get到每页显示数量
	page = int(request.args.get('page',1)) #get到页数

	if current_user.group.power == 0:  #超级管理员
		newcont = db_session.query(func.count(News.id)).filter(News.pid == pid, News.display == display).scalar() #计算数据总数
	if current_user.group.power == 1:  #组长
		newcont = db_session.query(func.count(News.id)).filter(News.pid == pid, News.display == display, News.teamid == current_user.teamid).scalar() #计算数据总数
	if current_user.group.power == 2: #组员
		newcont = db_session.query(func.count(News.id)).filter(News.pid == pid, News.display == display, News.teamid == current_user.teamid, News.userid == current_user.id).scalar() #计算数据总数

	if newcont == None:
		newcont = 0
	page_cont = int(math.ceil(round(float(newcont) / lim,2))) #总数除以显示数量得到分页总数

	if page == 1:
		page_nb = 0 #如果第一页则从第0条数据开始调用
		page_show = int(lim + page_nb) #调用数量的结尾数
	else:
		page_nb = int((lim * (page - 1))) #否则用显示数量乘以当前页数减去1 得到开始数
		page_show = int(lim + page_nb) #调用数量的结尾数
	
	page_size = []
	for i in range(page_cont):
		page_size.append(i + 1)

	# print '%s%s%s%s%s%s%s%s%s%s%s%s%s%s' %('总信息数：',newcont,'  每页显示数：',lim,'  当前页：',page,'  总页数：',page_cont,'  当前显示首数：',page_nb,'  当前显示尾数：',page_show,'  分页：',page_size)

	previous = page - 1
	if previous == 0:
		previous = 0
	nextp = page + 1
	if nextp == page_cont:
		nextp = page_cont

	# 如果没有搜索条件，直接获取列表
	if title == None:
		title = ''
		if current_user.group.power == 0:  #超级管理员
			newslist = db_session.query(News).\
				filter(News.pid == pid, News.display == display).\
				group_by(News.id).limit(lim)[page_nb:page_show]
		if current_user.group.power == 1:  #组长
			newslist = db_session.query(News).\
				filter(News.pid == pid, News.display == display, News.teamid == current_user.teamid).\
				group_by(News.id).limit(lim)[page_nb:page_show]
		if current_user.group.power == 2: #组员
			newslist = db_session.query(News).\
				filter(News.pid == pid, News.display == display, News.teamid == current_user.teamid, News.userid == current_user.id).\
				group_by(News.id).limit(lim)[page_nb:page_show]
	# 如果有搜索条件，计算分页，加入条件
	else:
		if current_user.group.power == 0:  #超级管理员
			newcont = db_session.query(func.count(News.id)).\
				filter(News.title.like("%"+title+"%"), News.pid == pid, News.display == display).scalar() #计算数据总数
		if current_user.group.power == 1:  #组长
			newcont = db_session.query(func.count(News.id)).\
				filter(News.title.like("%"+title+"%"), News.pid == pid, News.display == display, News.teamid == current_user.teamid).scalar() #计算数据总数
		if current_user.group.power == 2: #组员
			newcont = db_session.query(func.count(News.id)).\
				filter(News.title.like("%"+title+"%"), News.pid == pid, News.display == display, News.teamid == current_user.teamid, News.userid == current_user.id).scalar() #计算数据总数

		page_cont = int(math.ceil(round(float(newcont) / lim,2)))
		page_size = []
		for i in range(page_cont):
			page_size.append(i + 1)
		# print '%s%s%s%s%s%s%s%s%s%s%s%s%s%s' %('总信息数：',newcont,'  每页显示数：',lim,'  当前页：',page,'  总页数：',page_cont,'  当前显示首数：',page_nb,'  当前显示尾数：',page_show,'  分页：',page_size)
		if newcont >= lim:
			if current_user.group.power == 0:  #超级管理员
				newslist = db_session.query(News).\
					filter(News.title.like("%"+title+"%"), News.pid == pid, News.display == display).\
					group_by(News.id).limit(lim)[page_nb:page_show]
			if current_user.group.power == 1:  #组长
				newslist = db_session.query(News).\
					filter(News.title.like("%"+title+"%"), News.pid == pid, News.display == display, News.teamid == current_user.teamid).\
					group_by(News.id).limit(lim)[page_nb:page_show]
			if current_user.group.power == 2: #组员
				newslist = db_session.query(News).\
					filter(News.title.like("%"+title+"%"), News.pid == pid, News.display == display, News.teamid == current_user.teamid, News.userid == current_user.id).\
					group_by(News.id).limit(lim)[page_nb:page_show]
		else:
			page_show = int(newcont + ((newcont * page)-1))
			# print newcont,page_show,page
			if current_user.group.power == 0:  #超级管理员
				newslist = db_session.query(News).\
					filter(News.title.like("%"+title+"%"), News.pid == pid, News.display == display).\
					group_by(News.id).limit(lim)[0:page_show]
			if current_user.group.power == 1:  #组长
				newslist = db_session.query(News).\
					filter(News.title.like("%"+title+"%"), News.pid == pid, News.display == display, News.teamid == current_user.teamid).\
					group_by(News.id).limit(lim)[0:page_show]
			if current_user.group.power == 2: #组员
				newslist = db_session.query(News).\
					filter(News.title.like("%"+title+"%"), News.pid == pid, News.display == display, News.teamid == current_user.teamid, News.userid == current_user.id).\
					group_by(News.id).limit(lim)[0:page_show]

	return render_template(
		"manage_news.html", 
		pagename = tsActive,
		pid = pid, 
		newslist = newslist,
		page = page_size,
		previous = previous,
		nextp = nextp,
		page_cont = page_cont,
		title = title,
		newcont = newcont)
	db_session.close()


# 添加资讯
@api.route('/add_news', methods=['GET', 'POST'])
def add_news():
	
	pid = int(request.args.get('pid'))

	if pid == 1:
		tsActive = "manage_news"
	elif pid == 2:
		tsActive = "help"
	elif pid == 3:
		tsActive = "manage_company"
	this = 'add'

	form = AddNewsForm()
	if form.validate_on_submit():
		userid = int(request.form.get('userid'))
		title = request.form.get('title')
		getcontent = html.escape(request.form.get('editor'))
		display = int(request.form.get('display'))

		news = News(pid=pid, title=title, content=getcontent, display=display, userid=userid, teamid =current_user.teamid, addtime=datetime.datetime.now())
		news_check = db_session.query(News).filter(News.title == title).first()
		if news_check:
			if pid == 1:
				flash('资讯已存在')
			elif pid ==2:
				flash('帮助已存在')
			return redirect('%s%s' %('/manage/add_news?pid=',pid))
		if len(title) and len(getcontent):
			try:
				db_session.add(news)
				db_session.commit()
				db_session.close()
			except:
				flash("数据库错误!")
				return redirect('%s%s' %('/manage/add_news?pid=',pid))

			flash("添加成功,<span id='time'>3</span>秒后自动跳转管理页。")
			return redirect('%s%s' %('/manage/add_news?pid=',pid))
	return render_template(
		"edit_news.html", 
		pagename=tsActive,
		this = this,
		pid = pid,
		form=form)


# 修改资讯
@api.route('/edit_news', methods=['GET', 'POST'])
def edit_news():
	pid = int(request.args.get('pid'))
	if pid == 1:
		tsActive = "manage_news"
	elif pid == 2:
		tsActive = "help"
	elif pid == 3:
		tsActive = "manage_company"

	this = 'edit'
	

	getid = request.args.get('id')

	form = EditNewsForm()


	newsData = db_session.query(News).filter(News.id == getid).\
		with_entities(News.id, News.title, News.content, News.display).first()
	
	if newsData:
		form.id.data = newsData.id
		form.title.data = newsData.title
		form.display.data = newsData.display

		html_parser = HTMLParser.HTMLParser()
		html_con = newsData.content
		content = html_parser.unescape(html_con)

		form.content.data = content
	
	db_session.close()

	if form.validate_on_submit():
		id = request.form.get('id')
		title = request.form.get('title')
		content = html.escape(request.form.get('editor'))
		display = request.form.get('display')
		# print content,title

		try:
			db_session.query(News).filter(News.id == id).update(
				{
					News.title : title,
					News.content : content,
					News.display : display
				})
			db_session.commit()
			db_session.close()
		except:
			flash("数据库错误!")
			return redirect('%s%s%s%s' %('/manage/edit_news?pid=',pid,'&id=',id))


		flash("修改成功,<span id='time'>3</span>秒后自动跳转管理页。")
		return redirect('%s%s%s%s' %('/manage/edit_news?pid=',pid,'&id=',id))


	return render_template(
		"edit_news.html", 
		this = this,
		pid = pid,
		pagename=tsActive,
		form=form)


# 删除资讯
@api.route('/del_news', methods=['GET', 'POST'])
@login_required
def del_news():
	if request.method == "POST":
		getid = request.form.getlist('id')
		if len(getid) == 1:
			getid = request.form.get('id')
			delg = db_session.query(News).filter(News.id == getid).first()
			try:
				db_session.delete(delg)
				db_session.commit()
				db_session.close()
			except:
				return jsonify({"state":"数据库错误"})
		else:
			delg = db_session.query(News).filter(News.id.in_((getid))).all()
			try:
				[db_session.delete(n) for n in delg]
				db_session.commit()
				db_session.close()
			except:
				return jsonify({"state":"数据库错误"})
		
	else:
		getid = request.args.get('id')
		delg = db_session.query(News).filter(News.id == getid).first()
		try:
			db_session.delete(delg)
			db_session.commit()
			db_session.close()
		except:
			return jsonify({"state":"数据库错误"})
	
	
	return jsonify({"state":'ok'})