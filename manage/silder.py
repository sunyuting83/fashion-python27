# coding:utf-8
from flask import Flask, render_template, redirect, session, url_for, request, g, flash, abort, jsonify, make_response
from flask_wtf import FlaskForm
from wtforms import TextField, BooleanField, PasswordField, SubmitField, SelectField, HiddenField, IntegerField, StringField
from wtforms.validators import Required, Email, Length
from model import Silder, Images, Product, and_, or_, desc, asc, func, db_session
from manage import api
from public import *
import os
import math

# 修改轮显表单
class EditsilderForm(FlaskForm):

	id = HiddenField('id')
	sort = TextField('排序', validators=[Required()], render_kw={"placeholder": "排序","class": "form-control"},default=0)
	title = TextField('标题', validators=[Length(min=2,max=30,message=(u'标题必须2~30个字符之间'))], render_kw={"placeholder": "标题","class": "form-control"})
	url = HiddenField('url')
	oldpicid = HiddenField('oldpicid')
	picid = HiddenField('picid')
	submit = SubmitField('修改', validators=[Required()],render_kw={"class": "btn btn-primary"})

# 添加轮显表单
class AddsilderForm(FlaskForm):
	sort = TextField('排序', validators=[Required()], render_kw={"placeholder": "排序","class": "form-control"},default=0)
	title = TextField('标题', validators=[Length(min=2,max=30,message=(u'标题必须2~30个字符之间'))], render_kw={"placeholder": "标题","class": "form-control"})
	url = HiddenField('url')
	picid = HiddenField('picid', default=None)
	submit = SubmitField('添加', validators=[Required()],render_kw={"class": "btn btn-primary"})


# 轮显列表
@api.route('/silder', methods=['GET', 'POST'])
def silder():
	silderlist = db_session.query(Silder).all()
	return render_template(
		"silder.html", 
		pagename='silder', 
		silderlist=silderlist)
	db_session.close()


# 添加轮显
@api.route('/add_silder', methods=['GET', 'POST'])
def add_silder():
	this = 'add'
	form = AddsilderForm()
	if form.validate_on_submit():
		title = request.form.get('title')
		url = request.form.get('url')
		picid = request.form.get('picid')
		sort = request.form.get('sort')

		silder = Silder(title=title, url=url, picid=picid, sort=sort)

		silder_check = db_session.query(Silder).order_by(Silder.id)

		if len(title):
			try:
				db_session.add(silder)
				db_session.commit()
				db_session.close()
			except:
				flash("数据库错误!")
				return redirect('/manage/add_silder')

			flash("添加成功,<span id='time'>3</span>秒后自动跳转管理页。")
			return redirect('/manage/add_silder')
	return render_template(
		"edit_silder.html", 
		pagename='silder',
		this = this,
		form=form)


# 修改轮显
@api.route('/edit_silder', methods=['GET', 'POST'])
def edit_silder():
	this = 'edit'
	getid = request.args.get('id')
	picurl = request.args.get('picurl')
	silderData = db_session.query(Silder).filter(Silder.id == getid).\
		with_entities(Silder.id, Silder.title, Silder.url, Silder.picid, Silder.sort, Silder.img_url).first()

	form = EditsilderForm()
	if silderData:
		form.id.data = silderData.id
		form.title.data = silderData.title
		form.url.data = silderData.url
		form.oldpicid.data = silderData.picid
		form.sort.data = silderData.sort

	db_session.close()
	if form.validate_on_submit():
		id = int(request.form.get('id'))
		title = request.form.get('title')
		url = request.form.get('url')
		oldpicid = int(request.form.get('oldpicid'))
		picid = request.form.get('picid')
		sort =  int(request.form.get('sort'))

		print picid
		print oldpicid

		# 增加一个旧图片id 再增加一个新图片id 如果两个id相同则不修改。如果不一样则删除旧id的图片和库
		if picid == '':
			uppicid = oldpicid
			db_session.query(Silder).filter(Silder.id == id).update(
				{
					Silder.title : title,
					Silder.url : url,
					Silder.picid : uppicid,
					Silder.sort : sort,
				})
		elif picid != oldpicid and picid != '':
			uppicid = picid
			db_session.query(Silder).filter(Silder.id == id).update(
				{
					Silder.title : title,
					Silder.url : url,
					Silder.picid : uppicid,
					Silder.sort : sort,
				})
			deli = db_session.query(Images).filter(Images.id == oldpicid).first();
			imgurl = deli.picurl
			imgurl = actros_split(imgurl)
			
			delImage(imgurl)
			db_session.delete(deli)

		db_session.commit()
		db_session.close()


		flash("修改成功,<span id='time'>3</span>秒后自动跳转管理页。")
		return redirect('/manage/edit_silder')
	return render_template(
		"edit_silder.html", 
		pagename='silder', 
		this = this,
		picurl = picurl,
		form = form)

# 删除轮显
@api.route('/del_silder', methods=['GET', 'POST'])
@login_required
def del_silder():
	getid = int(request.args.get('id'))
	picid = int(request.args.get('picid'))
	# print getid,picid
	delg = db_session.query(Silder).filter(Silder.id == getid).first();
	db_session.delete(delg)
	deli = db_session.query(Images).filter(Images.id == picid).first();
	imgurl = deli.picurl
	imgurl = actros_split(imgurl)
	
	delImage(imgurl)
	
	db_session.delete(deli)

	db_session.commit()
	db_session.close()
	return jsonify({"state":"ok"})

# 选择产怕
@api.route('/chose_pro', methods=['GET', 'POST'])
@login_required
def chose_pro():
	proname = request.args.get('proname')
	if proname is None or proname is '':
		proname = ''

	lim = int(10) #get到每页显示数量
	page = int(request.args.get('page',1)) #get到页数

	newcont = db_session.query(func.count(Product.proid)).\
		filter(Product.proname.like("%"+proname+"%"), Product.display == 0).scalar() #计算数据总数

	page_cont = int(math.ceil(round(float(newcont) / lim,2)))

	if page == 1:
		page_nb = 0 #如果第一页则从第0条数据开始调用
		page_show = int(lim + page_nb) #调用数量的结尾数
	else:
		page_nb = int((lim * (page - 1))) #否则用显示数量乘以当前页数减去1 得到开始数
		page_show = int(lim + page_nb) #调用数量的结尾数
	
	page_size = []
	for i in range(page_cont):
		page_size.append(i + 1)

	previous = page - 1
	if previous is 0:
		previous = 0
	nextp = page + 1
	if nextp == page_cont:
		nextp = page_cont

	if newcont >= lim:
		productlist = db_session.query(Product).\
			filter(Product.proname.like("%"+proname+"%"), Product.display == 0).\
			group_by(Product.proid).limit(lim)[page_nb:page_show]
	else:
		page_show = int(newcont + ((newcont * page)-1))
		# print newcont,page_show,page
		productlist = db_session.query(Product).\
			filter(Product.proname.like("%"+proname+"%"), Product.display == 0).\
			group_by(Product.proid).limit(lim)[0:page_show]

	return render_template(
		"chose_product.html",
		productlist = productlist,
		page = page_size,
		previous = previous,
		nextp = nextp,
		page_cont = page_cont,
		proname = proname,
		newcont = newcont)