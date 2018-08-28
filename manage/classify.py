# coding:utf-8
from flask import Flask, render_template, redirect, session, url_for, request, g, flash, abort, jsonify, make_response
from flask_wtf import FlaskForm
from wtforms import TextField, BooleanField, PasswordField, SubmitField, SelectField, HiddenField
from wtforms.validators import Required, Email, Length
from model import Classify, Product, Images, and_, or_, desc, asc, func, db_session
from manage import api
from public import *
import hashlib
import datetime
import json
import os

# 修改分类表单
class EditclassifyForm(FlaskForm):

	classid = HiddenField('classid')
	icon =  HiddenField('icon',default=None)
	oldicon = HiddenField('oldicon')
	sort = TextField('排序', render_kw={"placeholder": "排序","class": "form-control"},default = 0)
	classname = TextField('分类名', render_kw={"placeholder": "分类名","class": "form-control"})
	display = SelectField('可见性', coerce=int, choices = [(0, '可见'), (1, '隐藏')],render_kw={"class": "form-control"})
	submit = SubmitField('修改',render_kw={"class": "btn btn-primary"})

# 添加分类表单
class AddclassifyForm(FlaskForm):

	icon =  HiddenField('icon',default=None)
	topid = HiddenField('topid')
	sort = TextField('排序', render_kw={"placeholder": "排序","class": "form-control"},default = 0)
	classname = TextField('分类名', render_kw={"placeholder": "分类名","class": "form-control"})
	ctype = SelectField('类型', coerce=int, choices = [(0, '产品分类'), (1, '资讯分类')],render_kw={"class": "form-control"})
	display = SelectField('可见性', coerce=int, choices = [(0, '可见'), (1, '隐藏')],render_kw={"class": "form-control"})
	submit = SubmitField('添加',render_kw={"class": "btn btn-primary"})


# 分类结构
def getChildren(id,towclass):
	# 分类调用
	change = towclass
	sz=[]
	for obj in change:
		if obj['topid'] == id:
			sz.append({"classid":obj['classid'],"classname":obj['classname'],"topid":obj['topid'],"sort":obj['sort'],"children":getChildren(obj['classid'],change)})
	return sz

# 分类列表
@api.route('/manage_classify', methods=['GET', 'POST'])
def manage_classify():

	'''
	以下代码是获取分类json。
	'''
	classify = Classify.classify_check().all()
	towclass = []
	for cls in classify:
		towclass.append({'classid':cls.classid, 'topid':cls.topid, 'classname':cls.classname, 'icon':cls.icon, 'ctype':cls.ctype, 'display':cls.display, 'sort':cls.sort})
	classifylist = json.dumps(getChildren(0,towclass))
	# print classifylist

	# classifylist = Classify.classify_check().all()

	return render_template(
		"manage_classify.html", 
		pagename = 'manage_classify', 
		classifylist = classifylist)

# 搜索分类列表
@api.route('/search_classify', methods=['GET', 'POST'])
def search_classify():
	classname = request.args.get('classname')
	classifylist = db_session.query(Classify).filter(Classify.classname == classname).all()
	return render_template(
		"manage_classify.html", 
		pagename='manage_classify', 
		classifylist = classifylist)
	db_session.close()


# 添加分类
@api.route('/add_classify', methods=['GET', 'POST'])
def add_classify():
	this = 'add'
	topid = request.args.get('classid',0)

	form = AddclassifyForm()
	if form.validate_on_submit():
		icon = request.form.get('icon')
		topid = request.form.get('topid')
		sort = request.form.get('sort')
		classname = request.form.get('classname')
		ctype = request.form.get('ctype')
		display = request.form.get('display')

		if icon == '' or icon is None:
			icon = 0

		classify = Classify(topid=topid, classname=classname, icon=icon, ctype=ctype, display=display, sort=sort, uptime=datetime.datetime.now())
		db_session.query(Classify)
		if len(classname):
			try:
				db_session.add(classify)
				db_session.commit()
				# 记录日志
				actions = ('%s%s%s' %('增加分类',':',classname))
				savelog(actions)
			except Exception as e:
				print e
				db_session.rollback()
				flash("数据库错误!")
				return redirect('/manage/add_classify')

			flash("添加成功,<span id='time'>3</span>秒后自动跳转管理页。")
			return redirect('/manage/add_classify')
	return render_template(
		"edit_classify.html", 
		pagename='manage_classify',
		this = this,
		topid = topid,
		form=form)


# 修改分类
@api.route('/edit_classify', methods=['GET', 'POST'])
def edit_classify():
	this = 'edit'
	getid = request.args.get('classid')
	classifyData = db_session.query(Classify).filter(Classify.classid == getid).\
		with_entities(Classify.classname, Classify.icon, Classify.sort, Classify.classid, Classify.display).first()
	form = EditclassifyForm()
	if classifyData:
		form.classid.data = classifyData.classid
		form.classname.data = classifyData.classname
		form.oldicon.data = classifyData.icon
		form.sort.data = classifyData.sort
		form.display.data = classifyData.display
	
	db_session.close()
	if form.validate_on_submit():
		classid = request.form.get('classid')
		classname = request.form.get('classname')
		icon = request.form.get('icon')
		oldpicid = request.form.get('oldicon')
		sort = request.form.get('sort')
		display = request.form.get('display')

		# 增加一个旧图片id 再增加一个新图片id 如果两个id相同则不修改。如果不一样则删除旧id的图片和库
		if icon == '':
			uppicid = oldpicid
			db_session.query(Classify).filter(Classify.classid == classid).update(
				{
					Classify.classname : classname,
					Classify.icon : uppicid,
					Classify.sort : sort,
					Classify.display : display
				})
		elif icon != oldpicid and icon != '':
			uppicid = icon
			db_session.query(Classify).filter(Classify.classid == classid).update(
				{
					Classify.classname : classname,
					Classify.icon : uppicid,
					Classify.sort : sort,
					Classify.display : display
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
			actions = ('%s%s%s' %('修改分类',':',classname))
			savelog(actions)
			db_session.close()
		except:
			flash("数据库错误!")
			return redirect('/manage/edit_classify')

		flash("修改成功,<span id='time'>3</span>秒后自动跳转管理页。")
		return redirect('/manage/edit_classify')

	iconurl = db_session.query(Classify).\
				filter(Classify.classid == getid).first()
	return render_template(
		"edit_classify.html", 
		pagename='manage_classify', 
		this = this,
		iconurl = iconurl,
		form=form)

# 删除分类
@api.route('/del_classify', methods=['GET', 'POST'])
@login_required
def del_classify():
	getid = int(request.args.get('classid'))
	topid = int(request.args.get('topid'))

	product = db_session.query(Product).filter(Product.pid == getid).first()
	if product:
		return jsonify({'state':'havedate'})
	else:
		delclass = db_session.query(Classify).filter(Classify.classid == getid).first()
		try:
			db_session.delete(delclass)
			db_session.commit()
			# 记录日志
			actions = ('%s%s'%('删除分类id:',getid))
			savelog(actions)
			db_session.close()
			db_session.close()
		except:
			return jsonify({"state":"数据库错误"})
		return jsonify({"state":"ok"})

# 更新排序
@api.route('/update_sort', methods=['GET', 'POST'])
@login_required
def update_sort():

	getid = request.form.getlist('classid')
	sort = request.form.getlist('sort')
	if len(getid) is 1:
		getid = request.form.get('classid')
	else:
		for (getid,sort) in zip(getid,sort):
			try:
				upsort = db_session.query(Classify).\
					filter(Classify.classid == getid).\
					update({Classify.sort : sort})
				db_session.commit()
			except:
				return jsonify({"state":"数据库错误"})
	# 记录日志
	actions = '更新的分类排序'
	savelog(actions)
	db_session.close()
	
	return jsonify({"state":'ok'})
