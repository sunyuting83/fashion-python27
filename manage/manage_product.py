# coding:utf-8
from flask import Flask, render_template, redirect, session, url_for, request, g, flash, abort, jsonify, make_response
from flask_wtf import FlaskForm
from wtforms import TextField, BooleanField, PasswordField, SubmitField, SelectField, HiddenField, StringField, TextAreaField, SelectMultipleField, widgets
from wtforms.validators import Required, Email, Length
from wtforms.widgets import TextArea, ListWidget
from model import Product, Classify, Size, Recommend, UserLike, UserCart, ProColor, Manage, Images, Wash, and_, or_, desc, asc, func, db_session

from .public import *

from manage import api
import math
import datetime
import json

from html.parser import HTMLParser
import cgi

class MultiCheckboxField(SelectMultipleField): 
	widget = widgets.ListWidget(prefix_label=True) 
	option_widget = widgets.CheckboxInput() 

# 修改产品表单
class EditProductForm(FlaskForm):
	proid = HiddenField('id')
	pid = HiddenField('pid')
	new_p = HiddenField('new_p',default=0)
	covers = HiddenField('covers',default=None)
	oldcovers = HiddenField('oldcovers')
	oldpid = HiddenField('oldpid')
	creatorid = HiddenField('creatorid')
	teamid =  HiddenField('teamid')
	proname = TextField('产品名称', validators=[Length(min=2,max=30,message=(u'产品名称必须2~30个字符之间'))], render_kw={"placeholder": "产品名称","class": "form-control","parsley-trigger":"change","required":"required"})
	price = TextField('价格', render_kw={"placeholder": "价格","class": "form-control","parsley-trigger":"change","required":"required"})
	text_centont = StringField('简单介绍',widget=TextArea(), render_kw={"placeholder": "简单介绍","class": "form-control", "style":"height:150px;", "id":"some-textarea","parsley-trigger":"change","required":"required"})
	model_height = TextField('模特身高', render_kw={"placeholder": "模特身高","class": "form-control","parsley-trigger":"change","required":"required"})
	fabric = TextField('面料', render_kw={"placeholder": "面料","class": "form-control","parsley-trigger":"change","required":"required"})
	lining = TextField('里料', render_kw={"placeholder": "里料","class": "form-control","parsley-trigger":"change","required":"required"})
	wash = HiddenField('wash')
	size_table = HiddenField('size_table')
	weights = TextField('单件净重', render_kw={"placeholder": "单件净重","class": "form-control","parsley-trigger":"change","required":"required"})
	the_net = TextField('单件毛重', render_kw={"placeholder": "单件毛重","class": "form-control","parsley-trigger":"change","required":"required"})
	first_order = TextField('货期-首单', render_kw={"placeholder": "货期-首单","class": "form-control","parsley-trigger":"change","required":"required"})
	again_order = TextField('货期-翻单', render_kw={"placeholder": "货期-翻单","class": "form-control","parsley-trigger":"change","required":"required"})
	shipping = TextField('运输周期-海运', render_kw={"placeholder": "运输周期-海运","class": "form-control","parsley-trigger":"change","required":"required"})
	flying = TextField('运输周期-空运', render_kw={"placeholder": "运输周期-空运","class": "form-control","parsley-trigger":"change","required":"required"})
	place = TextField('产地', render_kw={"placeholder": "产地","class": "form-control","parsley-trigger":"change","required":"required"})
	colorid = HiddenField('colorid')
	size = HiddenField('size')
	display = SelectField('可见性', coerce=int, choices = [(0, '可见'), (1, '隐藏')],render_kw={"class": "form-control"})
	submit = SubmitField('修改',render_kw={"class": "btn btn-primary"})

# 添加产品表单
class AddProductForm(FlaskForm):
	pid = HiddenField('pid')
	oldpid = HiddenField('oldpid')
	creatorid = HiddenField('creatorid')
	teamid =  HiddenField('teamid')
	new_p = HiddenField('new_p',default=0)
	covers = HiddenField('covers',default=None)
	proname = TextField('产品名称', validators=[Length(min=2,max=30,message=(u'产品名称必须2~30个字符之间'))], render_kw={"placeholder": "产品名称","class": "form-control","parsley-trigger":"change","required":"required"})
	price = TextField('价格', render_kw={"placeholder": "价格","class": "form-control","parsley-trigger":"change","required":"required"})
	text_centont = StringField('简单介绍',widget=TextArea(), render_kw={"placeholder": "简单介绍","class": "form-control", "style":"height:150px;", "id":"some-textarea","parsley-trigger":"change","required":"required"})
	model_height = TextField('模特身高', render_kw={"placeholder": "模特身高","class": "form-control","parsley-trigger":"change","required":"required"})
	fabric = TextField('面料', render_kw={"placeholder": "面料","class": "form-control","parsley-trigger":"change","required":"required"})
	lining = TextField('里料', render_kw={"placeholder": "里料","class": "form-control","parsley-trigger":"change","required":"required"})
	wash = HiddenField('wash')
	size_table = HiddenField('size_table')
	weights = TextField('单件净重', render_kw={"placeholder": "单件净重","class": "form-control","parsley-trigger":"change","required":"required"})
	the_net = TextField('单件毛重', render_kw={"placeholder": "单件毛重","class": "form-control","parsley-trigger":"change","required":"required"})
	first_order = TextField('货期-首单', render_kw={"placeholder": "货期-首单","class": "form-control","parsley-trigger":"change","required":"required"})
	again_order = TextField('货期-翻单', render_kw={"placeholder": "货期-翻单","class": "form-control","parsley-trigger":"change","required":"required"})
	shipping = TextField('运输周期-海运', render_kw={"placeholder": "运输周期-海运","class": "form-control","parsley-trigger":"change","required":"required"},default="40")
	flying = TextField('运输周期-空运', render_kw={"placeholder": "运输周期-空运","class": "form-control","parsley-trigger":"change","required":"required"},default="10")
	place = TextField('产地', render_kw={"placeholder": "产地","class": "form-control","parsley-trigger":"change","required":"required"},default="中国（China）")
	colorid = HiddenField('colorid')
	size = HiddenField('size')
	display = SelectField('可见性', coerce=int, choices = [(0, '可见'), (1, '隐藏')],render_kw={"class": "form-control"})
	submit = SubmitField('添加',render_kw={"class": "btn btn-primary","disabled":"disabled"})

# 分类结构
def getChildren(id,towclass):
	# 分类调用
	change = towclass
	sz=[]
	for obj in change:
		if obj['topid'] == id:
			sz.append({"classid":obj['classid'],"classname":obj['classname'],"topid":obj['topid'],"sort":obj['sort'],"children":getChildren(obj['classid'],change)})
	return sz

# 产品页分类结构
def getaChildren(id,towclass):
	# 分类调用
	change = towclass
	sz=[]
	for obj in change:
		if obj['topid'] == id:
			sz.append({"id":obj['id'],"text":obj['text'],"topid":obj['topid'],"children":getaChildren(obj['id'],change)})
	return sz

# 推荐结构
def get_Children(id,towclass):
	# 分类调用
	change = towclass
	sz=[]
	for obj in change:
		if obj['topid'] == id:
			sz.append({"id":obj['id'],"titles":obj['titles'],"children":get_Children(obj['id'],change)})
	return sz

# 得到非list的json数据
def to_json(model):
	""" Returns a JSON representation of an SQLAlchemy-backed object. """
	json = {}
	# json['fields'] = {}
	# json['pk'] = getattr(model, 'id')
	for col in model._sa_class_manager.mapper.mapped_table.columns:
		# json['fields'][col.name] = getattr(model, col.name)
		json[col.name] = getattr(model, col.name)
	# return dumps([json])
	return json

# 得到list的json数据
def to_json_list(model_list):
	json_list = []
	for model in model_list:
		json_list.append(to_json(model))
	return json_list

# JSON数据化对时间的处理
class DateEncoder(json.JSONEncoder):
	def default(self, obj):  
		if isinstance(obj, datetime.datetime):  
			return obj.strftime('%Y-%m-%d %H:%M:%S')  
		elif isinstance(obj, date):  
			return obj.strftime("%Y-%m-%d")  
		else:  
			return json.JSONEncoder.default(self, obj)

# 图片增加proid和排序
def give_picid(state,picurl,data,up_date):
	checklist = len(data)
	sorts = []
	for x in range(len(picurl)):
		picx = picurl[x].split(',')
		sortx = []
		for y in range(len(picx)):
			sortx.append(y)
		sorty = ','.join(str(i) for i in sortx)
		sorts.append(sorty)

	colorsid = [] #定义一个颜色id的数组
	for i in range(checklist):
		colorsid.append(data[i].id) #通过for获得新添加颜色的id并添加到数组
	if state == 'update':
		for i in range(len(up_date)):
			colorsid.append(up_date[i].id)
	for (colorsid,picurl,sorts) in zip(colorsid,picurl,sorts): #排列颜色id与图片id的for循环
		sort = sorts.split(',') #拆分排序
		picx = picurl.split(',') #拆分前端提交的每组图片的ID
		for x in range(len(picx)): #拆分后的图片id进行循环得到单个id
			# print colorsid
			# print picx[x]
			db_session.query(Images).\
				filter(Images.id == picx[x]).\
				update(
					{
						Images.picid : colorsid,
						Images.sort : sort[x]
					}
				)

# 删除单个产品时，删除图片的函数
def del_onlypro_pic (thpro,thisdata):
	for pic in thisdata:
		colorpics = pic.colorpic.all()
		for picurl in colorpics:
			imgurl = picurl.picurl #获得图片物理地址
			imgurl = actros_split(imgurl)
			delImage(imgurl) #删除物理图片
		try:
			[db_session.delete(n) for n in colorpics]
			db_session.commit()
		except Exception as e:
			print (e)
			db_session.rollback()
			return jsonify({"state":"数据库错误"})
	try:
		db_session.delete(thpro)
		[db_session.delete(n) for n in thisdata]
		db_session.commit()
	except Exception as e:
		print (e)
		db_session.rollback()
		return jsonify({"state":"数据库错误"})

# 产品列表
@api.route('/manage_product', methods=['GET', 'POST'])
@login_required
def manage_product():

	'''
	以下代码是获取分类json。
	'''
	classify = Classify.classify_check().all()
	towclass = []
	for cls in classify:
		towclass.append({'classid':cls.classid, 'topid':cls.topid, 'classname':cls.classname, 'icon':cls.icon, 'ctype':cls.ctype, 'display':cls.display, 'sort':cls.sort})
	classifylist = json.dumps(getChildren(0,towclass))

	pid = int(request.args.get('pid'))
	
	display = request.args.get('display',0)

	proname = request.args.get('proname')
	
	# print title

	# 分页开始
	lim = int(30) #get到每页显示数量
	page = int(request.args.get('page',1)) #get到页数

	# 权限判断
	if pid is 0 or pid is None:
		if current_user.group.power == 0:  #超级管理员
			newcont = db_session.query(func.count(Product.proid)).filter( Product.display == display).scalar() #计算数据总数
		if current_user.group.power == 1:  #组长
			newcont = db_session.query(func.count(Product.proid)).filter(Product.display == display, Product.teamid == current_user.teamid).scalar() #计算数据总数
		if current_user.group.power == 2: #组员
			newcont = db_session.query(func.count(Product.proid)).filter(Product.display == display, Product.teamid == current_user.teamid, Product.creatorid == current_user.id).scalar() #计算数据总数
	else:
		if current_user.group.power == 0:  #超级管理员
			newcont = db_session.query(func.count(Product.proid)).filter(Product.pid == pid, Product.display == display).scalar() #计算数据总数
		if current_user.group.power == 1:  #组长
			newcont = db_session.query(func.count(Product.proid)).filter(Product.pid == pid, Product.display == display, Product.teamid == current_user.teamid).scalar() #计算数据总数
		if current_user.group.power == 2: #组员
			newcont = db_session.query(func.count(Product.proid)).filter(Product.pid == pid, Product.display == display, Product.teamid == current_user.teamid, Product.creatorid == current_user.id).scalar() #计算数据总数

	
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
	if previous is 0:
		previous = 0
	nextp = page + 1
	if nextp == page_cont:
		nextp = page_cont


	# 如果没有搜索条件，直接获取列表
	if pid is 0 or pid is None:
		if proname is None:
			proname = ''
			if current_user.group.power == 0:
				productlist = Product.query.\
					filter(Product.display == display).\
					group_by(Product.proid).limit(lim)[page_nb:page_show]
			if current_user.group.power == 1:
				productlist = Product.query.\
					filter( Product.display == display, Product.teamid == current_user.teamid).\
					group_by(Product.proid).limit(lim)[page_nb:page_show]
			if current_user.group.power == 2:
				productlist = Product.query.\
					filter(Product.display == display, Product.teamid == current_user.teamid, Product.creatorid == current_user.id).\
					group_by(Product.proid).limit(lim)[page_nb:page_show]
		# 如果有搜索条件，计算分页，加入条件
		else:
			if current_user.group.power == 0:  #超级管理员
				newcont = db_session.query(func.count(Product.proid)).\
					filter(Product.proname.like("%"+proname+"%"), Product.display == display).scalar() #计算数据总数
			if current_user.group.power == 1:  #组长
				newcont = db_session.query(func.count(Product.proid)).\
					filter(Product.proname.like("%"+proname+"%"), Product.display == display, Product.teamid == current_user.teamid).scalar() #计算数据总数
			if current_user.group.power == 2: #组员
				newcont = db_session.query(func.count(Product.proid)).\
					filter(Product.proname.like("%"+proname+"%"), Product.display == display, Product.teamid == current_user.teamid, Product.creatorid == current_user.id).scalar() #计算数据总数

			page_cont = int(math.ceil(round(float(newcont) / lim,2)))
			page_size = []
			for i in range(page_cont):
				page_size.append(i + 1)

			if newcont >= lim:
				if current_user.group.power == 0:  #超级管理员
					productlist = db_session.query(Product).\
						filter(Product.proname.like("%"+proname+"%"), Product.display == display).\
						group_by(Product.proid).limit(lim)[page_nb:page_show]
				if current_user.group.power == 1:  #组长
					productlist = db_session.query(Product).\
						filter(Product.proname.like("%"+proname+"%"),  Product.display == display, Product.teamid == current_user.teamid).\
						group_by(Product.proid).limit(lim)[page_nb:page_show]
				if current_user.group.power == 2: #组员
					productlist = db_session.query(Product).\
						filter(Product.proname.like("%"+proname+"%"), Product.display == display, Product.teamid == current_user.teamid, Product.creatorid == current_user.id).\
						group_by(Product.proid).limit(lim)[page_nb:page_show]
			else:
				page_show = int(newcont + ((newcont * page)-1))
				# print newcont,page_show,page
				if current_user.group.power == 0:  #超级管理员
					productlist = db_session.query(Product).\
						filter(Product.proname.like("%"+proname+"%"),Product.display == display).\
						group_by(Product.proid).limit(lim)[0:page_show]
				if current_user.group.power == 1:  #组长
					productlist = db_session.query(Product).\
						filter(Product.proname.like("%"+proname+"%"), Product.display == display, Product.teamid == current_user.teamid).\
						group_by(Product.proid).limit(lim)[0:page_show]
				if current_user.group.power == 2: #组员
					productlist = db_session.query(Product).\
						filter(Product.proname.like("%"+proname+"%"), Product.display == display, Product.teamid == current_user.teamid, Product.creatorid == current_user.id).\
						group_by(Product.proid).limit(lim)[0:page_show]
	else:
		if proname is None:
			proname = ''
			if current_user.group.power == 0:
				productlist = Product.query.\
					filter(Product.pid == pid, Product.display == display).\
					group_by(Product.proid).limit(lim)[page_nb:page_show]
			if current_user.group.power == 1:
				productlist = Product.query.\
					filter(Product.pid == pid, Product.display == display, Product.teamid == current_user.teamid).\
					group_by(Product.proid).limit(lim)[page_nb:page_show]
			if current_user.group.power == 2:
				productlist = Product.query.\
					filter(Product.pid == pid, Product.display == display, Product.teamid == current_user.teamid, Product.creatorid == current_user.id).\
					group_by(Product.proid).limit(lim)[page_nb:page_show]
		# 如果有搜索条件，计算分页，加入条件
		else:
			if current_user.group.power == 0:  #超级管理员
				newcont = db_session.query(func.count(Product.proid)).\
					filter(Product.proname.like("%"+proname+"%"), Product.pid == pid, Product.display == display).scalar() #计算数据总数
			if current_user.group.power == 1:  #组长
				newcont = db_session.query(func.count(Product.proid)).\
					filter(Product.proname.like("%"+proname+"%"), Product.pid == pid, Product.display == display, Product.teamid == current_user.teamid).scalar() #计算数据总数
			if current_user.group.power == 2: #组员
				newcont = db_session.query(func.count(Product.proid)).\
					filter(Product.proname.like("%"+proname+"%"), Product.pid == pid, Product.display == display, Product.teamid == current_user.teamid, Product.creatorid == current_user.id).scalar() #计算数据总数

			page_cont = int(math.ceil(round(float(newcont) / lim,2)))
			page_size = []
			for i in range(page_cont):
				page_size.append(i + 1)

			if newcont >= lim:
				if current_user.group.power == 0:  #超级管理员
					productlist = db_session.query(Product).\
						filter(Product.proname.like("%"+proname+"%"), Product.pid == pid, Product.display == display).\
						group_by(Product.proid).limit(lim)[page_nb:page_show]
				if current_user.group.power == 1:  #组长
					productlist = db_session.query(Product).\
						filter(Product.proname.like("%"+proname+"%"), Product.pid == pid, Product.display == display, Product.teamid == current_user.teamid).\
						group_by(Product.proid).limit(lim)[page_nb:page_show]
				if current_user.group.power == 2: #组员
					productlist = db_session.query(Product).\
						filter(Product.proname.like("%"+proname+"%"), Product.pid == pid, Product.display == display, Product.teamid == current_user.teamid, Product.creatorid == current_user.id).\
						group_by(Product.proid).limit(lim)[page_nb:page_show]
			else:
				page_show = int(newcont + ((newcont * page)-1))
				# print newcont,page_show,page
				if current_user.group.power == 0:  #超级管理员
					productlist = db_session.query(Product).\
						filter(Product.proname.like("%"+proname+"%"), Product.pid == pid, Product.display == display).\
						group_by(Product.proid).limit(lim)[0:page_show]
				if current_user.group.power == 1:  #组长
					productlist = db_session.query(Product).\
						filter(Product.proname.like("%"+proname+"%"), Product.pid == pid, Product.display == display, Product.teamid == current_user.teamid).\
						group_by(Product.proid).limit(lim)[0:page_show]
				if current_user.group.power == 2: #组员
					productlist = db_session.query(Product).\
						filter(Product.proname.like("%"+proname+"%"), Product.pid == pid, Product.display == display, Product.teamid == current_user.teamid, Product.creatorid == current_user.id).\
						group_by(Product.proid).limit(lim)[0:page_show]

	return render_template(
		"manage_product.html", 
		pagename = 'product',
		pid = pid, 
		productlist = productlist,
		page = page_size,
		previous = previous,
		nextp = nextp,
		page_cont = page_cont,
		proname = proname,
		newcont = newcont,
		classifylist = classifylist)


#查看产品
@api.route('/view_product', methods=['GET', 'POST'])
def view_product():
	getid = int(request.args.get('id'))

	productData = Product.query.filter_by(proid = getid, display = 0).first()
	washlist = Wash.query.filter(Wash.id.in_((productData.wash)))
	return render_template(
		"view_product.html", 
		pagename = 'product',
		productData = productData,
		washlist = washlist)


# 添加产品
@api.route('/add_product', methods=['GET', 'POST'])
def add_product():

	pid = int(request.args.get('pid'))

	this = 'add'

	washlist = Wash.wash_check().all()
	sizelist = Size.size_check().all()
	recommend = Recommend.recommend_check().all()
	towclass = []
	for cls in recommend:
		towclass.append({'id':cls.id, 'topid':cls.topid, 'titles':cls.titles})
	recommend = json.dumps(get_Children(0,towclass))

	classify = Classify.classify_check().all()
	towclass = []
	for cls in classify:
		towclass.append({'id':cls.classid, 'text':cls.classname, 'topid':cls.topid})
	classifylist = json.dumps(getaChildren(0,towclass))

	form = AddProductForm()
	if form.validate_on_submit():

		pid = int(request.form.get('pid'))
		oldpid = int(request.form.get('oldpid'))
		creatorid = int(request.form.get('creatorid'))
		teamid = int(request.form.get('teamid'))
		new_p = int(request.form.get('new_p'))
		covers = request.form.get('covers')
		proname = request.form.get('proname')
		price = request.form.get('price')
		model_height = request.form.get('model_height')
		fabric = request.form.get('fabric')
		lining = request.form.get('lining')
		wash = request.form.get('wash')
		size_table = request.form.get('size_table')
		weights = request.form.get('weights')
		the_net = request.form.get('the_net')
		first_order = request.form.get('first_order')
		again_order = request.form.get('again_order')
		shipping = request.form.get('shipping')
		flying = request.form.get('flying')
		place = request.form.get('place')
		size = request.form.get('size')
		colorid = request.form.get('colorid')
		display = request.form.get('display')

		html_parser = HTMLParser.HTMLParser()
		html_con = request.form.get('text_centont')
		text_centont = html_parser.unescape(html_con)

		if covers == '' or covers is None:
			covers = 0

		product = Product(
			pid          = pid,
			oldpid       = oldpid,
			new_p        = new_p,
			covers       = covers,
			creatorid    = creatorid,
			teamid       = teamid,
			proname      = proname,
			price        = price,
			text_centont = text_centont,
			model_height = model_height,
			fabric       = fabric,
			lining       = lining,
			wash         = wash,
			size_table   = size_table,
			weights      = weights,
			the_net      = the_net,
			first_order  = first_order,
			again_order  = again_order,
			shipping     = shipping,
			flying       = flying,
			place        = place,
			size         = size,
			colorid      = colorid,
			display      = display,
			add_time     = datetime.datetime.now()
		)

		product_check = db_session.query(Product).first()
		if len(proname):
			try:
				db_session.add(product)
				db_session.commit()
				db_session.flush()
				pro_id = product.proid
			except:
				flash("数据库错误!")
				return redirect('%s%s' %('/manage/add_product?pid=',pid))


			# 颜色部分
			colortitle = request.form.getlist('colortitle')
			color = request.form.getlist('color')
			number = request.form.getlist('number')
			proid = pro_id
			picurl = request.form.getlist('picid')
			cover = request.form.getlist('cover')
			# print picurl
			color_list = [ProColor(
							colortitle = str(colortitle[i]),
							color = str(color[i]),
							number = str(number[i]),
							cover = cover[i],
							picurl = picurl[i],
							proid = proid
						) for i in range(len(color))]
			color_check = db_session.query(ProColor).first()
			db_session.add_all(color_list)
			db_session.commit()
			db_session.flush()
			# 开始处理复杂的图片所属颜色id和排序问题

			# 开始处理得到排序
			give_picid('up',picurl,color_list,None) #调用图片排序添加proid函数

			db_session.commit()
			db_session.close()

			flash("添加成功,<span id='time'>3</span>秒后自动跳转管理页。")
			return redirect('%s%s' %('/manage/add_product?pid=',pid))
	# print recommend
	return render_template(
		"edit_product.html", 
		pagename='product',
		this = this,
		pid = pid,
		washlist = washlist,
		sizelist=sizelist,
		recommend= recommend,
		classifylist=classifylist,
		form = form)


# 修改产品
@api.route('/edit_product', methods=['GET', 'POST'])
def edit_product():

	this = 'edit'
	
	getid = request.args.get('id')

	washlist = Wash.wash_check().all()
	sizelist = Size.size_check().all()
	recommend = Recommend.recommend_check().all()
	towclass = []
	for cls in recommend:
		towclass.append({'id':cls.id, 'topid':cls.topid, 'titles':cls.titles})
	recommend = json.dumps(get_Children(0,towclass))

	classify = Classify.classify_check().all()
	towclass = []
	for cls in classify:
		towclass.append({'id':cls.classid, 'text':cls.classname, 'topid':cls.topid})
	classifylist = json.dumps(getaChildren(0,towclass))

	form = EditProductForm()


	productData = Product.query.filter_by(proid = getid).first()
	pid = productData.pid
	
	if productData:
		form.proid.data        = productData.proid
		form.pid.data          = productData.pid
		form.new_p.data        = productData.new_p
		form.covers.data       = productData.covers
		form.oldcovers.data    = productData.covers
		form.oldpid.data       = productData.oldpid
		form.creatorid.data    = productData.creatorid 
		form.teamid.data       = productData.teamid
		form.proname.data      = productData.proname
		form.price.data        = productData.price
		form.model_height.data = productData.model_height
		form.fabric.data       = productData.fabric
		form.lining.data       = productData.lining
		form.size_table.data   = productData.size_table
		form.weights.data      = productData.weights
		form.the_net.data      = productData.the_net
		form.first_order.data  = productData.first_order
		form.again_order.data  = productData.again_order
		form.shipping.data     = productData.shipping
		form.flying.data       = productData.flying
		form.place.data        = productData.place
		form.size.data         = productData.size
		form.colorid.data      = productData.colorid
		form.display.data      = productData.display

		form.text_centont.data = productData.text_centont

	if form.validate_on_submit():
		productData.proid = int(request.form.get('proid'))
		productData.pid = int(request.form.get('pid'))
		productData.oldpid = int(request.form.get('oldpid'))
		productData.new_p = int(request.form.get('new_p'))
		productData.creatorid = int(request.form.get('creatorid'))
		productData.teamid = int(request.form.get('teamid'))
		productData.proname = request.form.get('proname')
		productData.price = request.form.get('price')
		productData.model_height = request.form.get('model_height')
		productData.fabric = request.form.get('fabric')
		productData.lining = request.form.get('lining')
		productData.wash = request.form.get('wash')
		productData.size_table = request.form.get('size_table')
		productData.weights = request.form.get('weights')
		productData.the_net = request.form.get('the_net')
		productData.first_order = request.form.get('first_order')
		productData.again_order = request.form.get('again_order')
		productData.shipping = request.form.get('shipping')
		productData.flying = request.form.get('flying')
		productData.place = request.form.get('place')
		productData.size = request.form.get('size')
		productData.colorid = request.form.get('colorid')
		productData.display = request.form.get('display')

		html_parser = HTMLParser.HTMLParser()
		html_con = request.form.get('text_centont')
		productData.text_centont = html_parser.unescape(html_con)

		# 处理封面图片
		getcovers = request.form.get('covers')
		oldcovers = request.form.get('oldcovers')
		print (getcovers,oldcovers)
		if getcovers == '':
			productData.covers = oldcovers

			try:
				db_session.add(productData)
				db_session.commit()
			except:
				flash("数据库错误!")
				return redirect('%s%s' %('/manage/add_product?pid=',pid))
		if getcovers != oldcovers and getcovers != '':
			productData.covers = getcovers

			try:
				db_session.add(productData)
				db_session.commit()
			except:
				flash("数据库错误!")
				return redirect('%s%s' %('/manage/add_product?pid=',pid))

			if oldcovers != '' and oldcovers != None and oldcovers != '0':
				deli = db_session.query(Images).filter(Images.id == oldcovers).first();
				imgurl = deli.picurl
				imgurl = actros_split(imgurl)
				
				delImage(imgurl)
				db_session.delete(deli)
				db_session.commit()

		

		proid = int(request.form.get('proid'))


		color_check = productData.colors.all()

		# 颜色部分
		colortitle = request.form.getlist('colortitle')
		color = request.form.getlist('color')
		number = request.form.getlist('number')
		picurl = request.form.getlist('picid')
		cover = request.form.getlist('cover')

		if len(color_check) == len(color) :
			for i in range(len(color_check)):
				color_check[i].colortitle = colortitle[i]
				color_check[i].color = color[i]
				color_check[i].number = number[i]
				color_check[i].picurl = picurl[i]
				color_check[i].cover = cover[i]

		elif len(color_check) < len(color) :
			for i in range(len(color_check)):
				color_check[i].colortitle = colortitle[i]
				color_check[i].color = color[i]
				color_check[i].number = number[i]
				color_check[i].picurl = picurl[i]
				color_check[i].cover = cover[i]

			color_list = [ProColor(
						colortitle = str(colortitle[i]),
						color = str(color[i]),
						number = str(number[i]),
						cover = cover[i],
						proid = proid
					) for i in range(len(color_check),len(color))]
			db_session.add_all(color_list)
			db_session.commit()
			db_session.flush()
			'''
				调用图片排序添加proid函数
				因为是增加了新的颜色组，所以第一个参数使用 update
				最后一个参数加入新添加的数据 color_list
			'''
			give_picid('update',picurl,color_check,color_list)  #调用图片排序添加proid函数

		db_session.commit()
		db_session.flush()

		give_picid('up',picurl,color_check,None) #调用图片排序添加proid函数

		db_session.commit()
		db_session.close()

		flash("添加成功,<span id='time'>3</span>秒后自动跳转管理页。")
		return redirect('%s%s' %('/manage/add_product?pid=',pid))


	return render_template(
		"edit_product.html", 
		this = this,
		pid = pid,
		thdata = productData,
		washlist = washlist,
		sizelist = sizelist,
		recommend= recommend,
		classifylist=classifylist,
		pagename='product',
		form=form)


# 删除产品
@api.route('/del_product', methods=['GET', 'POST'])
@login_required
def del_product():
	if request.method == "POST":
		getid = request.form.getlist('id')
		if len(getid) is 1:
			# 如果只选择了一项
			getid = request.form.get('id')

			delproduct = Product.query.filter(Product.proid == getid).first()
			delproduct.display = 3
			try:
				db_session.add(delproduct)
				db_session.commit()
			except Exception as e:
				print (e)
				db_session.rollback()
				return jsonify({"state":"数据库错误"})
			likes = UserLike.query.filter_by(like_porid = getid).all()
			if likes:
				try:
					db_session.delete(likes)
					db_session.commit()
				except Exception as e:
					print (e)
					db_session.rollback()
					return jsonify({"state":"数据库错误"})
			usercart = UserCart.query.filter_by(proid = getid).all()
			if usercart:
				try:
					db_session.delete(usercart)
					db_session.commit()
				except Exception as e:
					print (e)
					db_session.rollback()
					return jsonify({"state":"数据库错误"})
			'''
			颜色保留
			delcolor = delproduct.colors.all()
			这里改成更新产品状态是消失，并删除用户购物车和喜欢的产品列表
			调用单独删除产品图片函数
			del_onlypro_pic(delproduct,delcolor)
			'''
		else:
			# 如果选择了多项
			# delproduct = db_session.query(Product).filter(Product.proid.in_((getid))).all()

			'''
			删除产品时删除颜色及图片的代码。用不到了
			for color in delproduct:
				colors = color.colors.all()

				for pic in colors:
					colorpics = pic.colorpic.all()
					for picurl in colorpics:
						imgurl = picurl.picurl #获得图片物理地址
						imgurl = actros_split(imgurl)
						delImage(imgurl) #删除物理图片
					try:
						[db_session.delete(n) for n in colorpics]
						db_session.commit()
					except Exception as e:
						print (e)
						db_session.rollback()
						return jsonify({"state":"数据库错误"})
				try:
					[db_session.delete(n) for n in colors]
					db_session.commit()
				except Exception as e:
					print (e)
					db_session.rollback()
					return jsonify({"state":"数据库错误"})
			'''
			for i in range(len(getid)):
				try:
					disproduct = db_session.query(Product).\
						filter(Product.proid == getid[i]).\
						update({Product.display : 3})
					db_session.commit()
				except:
					return jsonify({"state":"数据库错误"})
	else:
		# 直接提交
		getid = request.args.get('id')

		delproduct = db_session.query(Product).filter(Product.proid == getid).first()
		delproduct.display = 3
		try:
			db_session.add(delproduct)
			db_session.commit()
		except Exception as e:
			print (e)
			db_session.rollback()
			return jsonify({"state":"数据库错误"})
		'''
		删除产品时删除颜色及图片的代码。用不到了
		delcolor = delproduct.colors.all()
		# 调用单独删除产品图片函数
		del_onlypro_pic(delproduct,delcolor)
		'''
		
	
	
	return jsonify({"state":'ok'})

# 单独删除颜色
@api.route('/del_colors', methods=['GET', 'POST'])
@login_required
def del_colors():
	getid = request.args.get('id')

	delcolors = db_session.query(ProColor).filter(ProColor.id == getid).first()
	colorpics = delcolors.colorpic.all()

	for picurl in colorpics:
		imgurl = picurl.picurl #获得图片物理地址
		imgurl = actros_split(imgurl)
		delImage(imgurl) #删除物理图片
	try:
		[db_session.delete(n) for n in colorpics]
		db_session.commit()
	except Exception as e:
		print (e)
		db_session.rollback()
		return jsonify({"state":"数据库错误"})

	try:
		db_session.delete(delcolors)
		db_session.commit()
	except Exception as e:
		print (e)
		db_session.rollback()
		return jsonify({"state":"数据库错误"})

	db_session.close()
	return jsonify({"state":'ok'})

# 查询分类是否有产品
@api.route('/hasProduct', methods=['GET', 'POST'])
@login_required
def hasProduct():
	getClassid = request.args.get('classid')
	procont = db_session.query(func.count(Product.proid)).filter( Product.pid == getClassid).scalar()
	if procont != 0:
		return jsonify({"state":'haspro'})
	else:
		return jsonify({"state":'ok'})

# 获取颜色单独图片
@api.route('/color_Pic', methods=['POST'])
@login_required
def color_Pic():
	picid = request.form.getlist('picid')
	pics = Images.query.filter(Images.id.in_((picid))).order_by(Images.sort)

	return jsonify([Pics.to_dict() for Pics in pics])

# 保存颜色单独图片排序
@api.route('/pic_sorts', methods=['POST'])
@login_required
def pic_sorts():
	picid = request.form.getlist('picid')
	sorts = []
	for x in range(len(picid)):
		db_session.query(Images).\
				filter(Images.id == picid[x]).\
				update(
					{
						Images.sort : x
					}
				)
	try:
		db_session.commit()
		db_session.close()
	except Exception as e:
		print (e)
		return jsonify({'state':'数据库错误'})
	return jsonify({'state':'ok'})

# 更新产品推荐属性
@api.route('/up_pro_state', methods=['POST'])
@login_required
def up_pro_state():
	getid = request.form.getlist('id')
	getstate = request.form.get('new_p')
	for i in range(len(getid)):
		upst = Product.query.filter_by(proid=getid[i]).first()
		upst.new_p = getstate
		db_session.add(upst)
		try:
			db_session.commit()
		except Exception as e:
			print (e)
			return jsonify({"state":"数据库错误"})
	db_session.close()
	
	return jsonify({"state":'ok'})