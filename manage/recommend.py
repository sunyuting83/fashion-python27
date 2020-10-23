# coding:utf-8
from flask import Flask, render_template, redirect, session, url_for, request, g, flash, abort, jsonify, make_response
from flask_wtf import FlaskForm
from wtforms import TextField, BooleanField, PasswordField, SubmitField, SelectField, HiddenField
from wtforms.validators import Required, Email, Length
from model import Recommend, Images, and_, or_, desc, asc, func, db_session
from manage import api
from .public import *
import hashlib
import datetime
import json
import os

# 修改推荐类型表单
class EditrecommendForm(FlaskForm):

	id = HiddenField('id')
	icon =  HiddenField('icon',default=None)
	oldicon = HiddenField('oldicon')
	sort = TextField('排序', render_kw={"placeholder": "排序","class": "form-control"},default = 0)
	titles = TextField('推荐类型名', render_kw={"placeholder": "推荐类型名","class": "form-control"})
	submit = SubmitField('修改',render_kw={"class": "btn btn-primary"})

# 添加推荐类型表单
class AddrecommendForm(FlaskForm):

	icon =  HiddenField('icon',default=None)
	topid = HiddenField('topid')
	sort = TextField('排序', render_kw={"placeholder": "排序","class": "form-control"},default = 0)
	titles = TextField('推荐类型名', render_kw={"placeholder": "推荐类型名","class": "form-control"})
	submit = SubmitField('添加',render_kw={"class": "btn btn-primary"})


# 推荐类型结构
def getChildren(id,towclass):
	# 推荐类型调用
	change = towclass
	sz=[]
	for obj in change:
		if obj['topid'] == id:
			sz.append({"id":obj['id'],"titles":obj['titles'],"topid":obj['topid'],"sort":obj['sort'],"children":getChildren(obj['id'],change)})
	return sz

# 推荐类型列表
@api.route('/manage_recommend', methods=['GET', 'POST'])
def manage_recommend():

	'''
	以下代码是获取推荐类型json。
	'''
	recommend = Recommend.recommend_check().all()
	towclass = []
	for cls in recommend:
		towclass.append({'id':cls.id, 'topid':cls.topid, 'titles':cls.titles, 'icon':cls.icon, 'sort':cls.sort})
	recommendlist = json.dumps(getChildren(0,towclass))
	# print recommendlist

	# recommendlist = Recommend.recommend_check().all()

	return render_template(
		"manage_recommend.html", 
		pagename = 'manage_recommend', 
		recommendlist = recommendlist)

# 搜索推荐类型列表
@api.route('/search_recommend', methods=['GET', 'POST'])
def search_recommend():
	titles = request.args.get('titles')
	recommendlist = db_session.query(Recommend).filter(Recommend.titles == titles).all()
	return render_template(
		"manage_recommend.html", 
		pagename='manage_recommend', 
		recommendlist = recommendlist)
	db_session.close()


# 添加推荐类型
@api.route('/add_recommend', methods=['GET', 'POST'])
def add_recommend():
	this = 'add'
	topid = request.args.get('id',0)

	form = AddrecommendForm()
	if form.validate_on_submit():
		icon = request.form.get('icon')
		topid = request.form.get('topid')
		sort = request.form.get('sort')
		titles = request.form.get('titles')

		if icon == '' or icon is None:
			icon = 0

		recommend = Recommend(topid=topid, titles=titles, icon=icon, sort=sort)
		db_session.query(Recommend)
		if len(titles):
			try:
				db_session.add(recommend)
				db_session.commit()
				# 记录日志
				actions = ('%s%s%s' %('增加推荐类型',':',titles))
				savelog(actions)
			except Exception as e:
				print (e)
				db_session.rollback()
				flash("数据库错误!")
				return redirect('/manage/add_recommend')

			flash("添加成功,<span id='time'>3</span>秒后自动跳转管理页。")
			return redirect('/manage/add_recommend')
	return render_template(
		"edit_recommend.html", 
		pagename='manage_recommend',
		this = this,
		topid = topid,
		form=form)


# 修改推荐类型
@api.route('/edit_recommend', methods=['GET', 'POST'])
def edit_recommend():
	this = 'edit'
	getid = request.args.get('id')
	recommendData = db_session.query(Recommend).filter(Recommend.id == getid).\
		with_entities(Recommend.titles, Recommend.icon, Recommend.sort, Recommend.id).first()
	form = EditrecommendForm()
	if recommendData:
		form.id.data = recommendData.id
		form.titles.data = recommendData.titles
		form.oldicon.data = recommendData.icon
		form.sort.data = recommendData.sort
	
	db_session.close()
	if form.validate_on_submit():
		id = request.form.get('id')
		titles = request.form.get('titles')
		icon = request.form.get('icon')
		oldpicid = request.form.get('oldicon')
		sort = request.form.get('sort')

		# 增加一个旧图片id 再增加一个新图片id 如果两个id相同则不修改。如果不一样则删除旧id的图片和库
		if icon == '':
			uppicid = oldpicid
			db_session.query(Recommend).filter(Recommend.id == id).update(
				{
					Recommend.titles : titles,
					Recommend.icon : uppicid,
					Recommend.sort : sort
				})
		elif icon != oldpicid and icon != '':
			uppicid = icon
			db_session.query(Recommend).filter(Recommend.id == id).update(
				{
					Recommend.titles : titles,
					Recommend.icon : uppicid,
					Recommend.sort : sort
				})
			if oldpicid != '' and oldpicid != None and oldpicid != '0':
				deli = db_session.query(Images).filter(Images.id == oldpicid).first();
				imgurl = deli.picurl
				imgurl = actros_split(imgurl)
				
				delImage(imgurl)
				db_session.delete(deli)
		try:
			db_session.commit()

			# 记录日志
			actions = ('%s%s%s' %('修改推荐类型',':',titles))
			savelog(actions)
			db_session.close()
		except:
			flash("数据库错误!")
			return redirect('/manage/edit_recommend')

		flash("修改成功,<span id='time'>3</span>秒后自动跳转管理页。")
		return redirect('/manage/edit_recommend')

	iconurl = db_session.query(Recommend).\
				filter(Recommend.id == getid).first()
	return render_template(
		"edit_recommend.html", 
		pagename='manage_recommend', 
		this = this,
		iconurl = iconurl,
		form=form)

# 删除推荐类型
@api.route('/del_recommend', methods=['GET', 'POST'])
@login_required
def del_recommend():
	getid = int(request.args.get('id'))
	topid = int(request.args.get('topid'))

	product = db_session.query(Product).filter(Product.pid == getid).first()
	if product:
		return jsonify({'state':'havedate'})
	else:
		delclass = db_session.query(Recommend).filter(Recommend.id == getid).first()
		try:
			db_session.delete(delclass)
			db_session.commit()
			# 记录日志
			actions = ('%s%s'%('删除推荐类型id:',getid))
			savelog(actions)
			db_session.close()
		except:
			return jsonify({"state":"数据库错误"})
		return jsonify({"state":"ok"})

# 更新排序
@api.route('/updatere_sort', methods=['GET', 'POST'])
@login_required
def updatere_sort():

	getid = request.form.getlist('id')
	sort = request.form.getlist('sort')
	if len(getid) is 1:
		getid = request.form.get('id')
	else:
		for (getid,sort) in zip(getid,sort):
			try:
				upsort = db_session.query(Recommend).\
					filter(Recommend.id == getid).\
					update({Recommend.sort : sort})
				db_session.commit()
			except:
				return jsonify({"state":"数据库错误"})
	# 记录日志
	actions = '更新的推荐类型排序'
	savelog(actions)
	db_session.close()
	
	return jsonify({"state":'ok'})
