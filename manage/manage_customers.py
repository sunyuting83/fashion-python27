# coding:utf-8
from flask import Flask, render_template, redirect, session, url_for, request, g, flash, abort, jsonify, make_response
from flask_wtf import FlaskForm
from wtforms import TextField, BooleanField, PasswordField, SubmitField, SelectField, HiddenField, StringField, TextAreaField
from wtforms.validators import Required, Email, Length
from model import Users, Team, and_, or_, desc, asc, func, db_session

from public import *

from manage import api
import math
import datetime
import HTMLParser
import cgi


# 修改客户表单
class EditCustomersForm(FlaskForm):
	id = HiddenField('id')
	password = PasswordField('密码', render_kw={"placeholder": "密码","class": "form-control","onkeyup": "KeyUp()"})
	repassword = PasswordField('重复密码', render_kw={"placeholder": "重复密码","class": "form-control","onkeyup": "KeyUp()"})
	submit = SubmitField('修改',render_kw={"class": "btn btn-primary"})

# 添加客户表单
class AddCustomersForm(FlaskForm):
	userid = HiddenField('userid')
	title = TextField('标题', validators=[Length(min=2,max=30,message=(u'职位必须2~30个字符之间'))], render_kw={"placeholder": "标题","class": "form-control"})
	display = SelectField('可见性', coerce=int, choices = [(0, '可见'), (1, '隐藏')],render_kw={"class": "form-control"})
	submit = SubmitField('添加',render_kw={"class": "btn btn-primary"})



# 客户列表
@api.route('/manage_customers', methods=['GET', 'POST'])
@login_required
def manage_customers(page = 1):

	search = request.args.get('search')
	verify = int(request.args.get('verify',1))
	status = int(request.args.get('status',0))

	if verify == 1 or verify == 2:
		tsActive = 'reg_customers'
	elif verify == 0:
		tsActive = 'manage_customers'

	# 工作组列表
	teamlist = Team.query.all()


	# 分页开始
	lim = int(30) #get到每页显示数量
	page = int(request.args.get('page',1)) #get到页数

	if current_user.group.power == 0:  #超级管理员
		newcont = db_session.query(func.count(Users.id)).filter(Users.verify == verify, Users.lock == status).scalar() #计算数据总数
	else:
		newcont = db_session.query(func.count(Users.id)).filter(Users.verify == verify, Users.lock == status, Users.teamid == current_user.teamid).scalar() #计算数据总数

	if newcont is None:
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
	if previous is 0:
		previous = 0
	nextp = page + 1
	if nextp == page_cont:
		nextp = page_cont

	# 如果没有搜索条件，直接获取列表
	if search is None:
		search = ''
		if current_user.group.power == 0:  #超级管理员
			userlist = Users.query.\
				filter(Users.verify == verify, Users.lock == status).\
				group_by(Users.id).limit(lim)[page_nb:page_show]
		else:
			userlist = Users.query.\
				filter(Users.verify == verify, Users.lock == status, Users.teamid == current_user.teamid).\
				group_by(Users.id).limit(lim)[page_nb:page_show]
	# 如果有搜索条件，计算分页，加入条件
	else:
		if current_user.group.power == 0:  #超级管理员
			newcont = db_session.query(func.count(Users.id)).\
				filter(or_(Users.phone.like("%"+search+"%"), Users.company.like("%"+search+"%"), Users.truename.like("%"+search+"%")), Users.verify == verify, Users.lock == status).scalar() #计算数据总数
		else:
			newcont = db_session.query(func.count(Users.id)).\
				filter(or_(Users.phone.like("%"+search+"%"), Users.company.like("%"+search+"%"), Users.truename.like("%"+search+"%")), Users.verify == verify, Users.lock == status, Users.teamid == current_user.teamid).scalar() #计算数据总数

		page_cont = int(math.ceil(round(float(newcont) / lim,2)))
		page_size = []
		for i in range(page_cont):
			page_size.append(i + 1)
		if newcont >= lim:
			if current_user.group.power == 0:  #超级管理员
				userlist = Users.query.\
					filter(or_(Users.phone.like("%"+search+"%"), Users.company.like("%"+search+"%"), Users.truename.like("%"+search+"%")), Users.verify == verify, Users.lock == status).\
					group_by(Users.id).limit(lim)[page_nb:page_show]
			else:
				userlist = Users.query.\
					filter(or_(Users.phone.like("%"+search+"%"), Users.company.like("%"+search+"%"), Users.truename.like("%"+search+"%")), Users.verify == verify, Users.lock == status, Users.teamid == current_user.teamid).\
					group_by(Users.id).limit(lim)[page_nb:page_show]
		else:
			page_show = int(newcont + ((newcont * page)-1))
			# print newcont,page_show,page
			if current_user.group.power == 0:  #超级管理员
				userlist = Users.query.\
					filter(or_(Users.phone.like("%"+search+"%"), Users.company.like("%"+search+"%"), Users.truename.like("%"+search+"%")), Users.verify == verify, Users.lock == status).\
					group_by(Users.id).limit(lim)[0:page_show]
			else:
				userlist = Users.query.\
					filter(or_(Users.phone.like("%"+search+"%"), Users.company.like("%"+search+"%"), Users.truename.like("%"+search+"%")), Users.verify == verify, Users.lock == status, Users.teamid == current_user.teamid).\
					group_by(Users.id).limit(lim)[0:page_show]

	return render_template(
		"manage_customers.html",
		pagename = tsActive,
		userlist = userlist,
		page = page_size,
		previous = previous,
		nextp = nextp,
		page_cont = page_cont,
		search = search,
		verify = verify,
		teamlist = teamlist,
		newcont = newcont)


# 添加客户
@api.route('/add_customers', methods=['GET', 'POST'])
def add_customers():
	
	this = 'add'

	form = AddUsersForm()
	if form.validate_on_submit():
		userid = int(request.form.get('userid'))
		title = request.form.get('title')
		getcontent = cgi.escape(request.form.get('editor'))
		display = int(request.form.get('display'))

		user = Users(pid=pid, title=title, content=getcontent, display=display, userid=userid, addtime=datetime.datetime.now())
		user_check = db_session.query(Users).filter(Users.title == title).first()
		if user_check:
			if pid == 1:
				flash('客户已存在')
			elif pid ==2:
				flash('帮助已存在')
			return redirect('%s%s' %('/manage/add_customers?pid=',pid))
		if len(title) and len(getcontent):
			try:
				db_session.add(user)
				db_session.commit()
				db_session.close()
			except:
				flash("数据库错误!")
				return redirect('%s%s' %('/manage/add_customers?pid=',pid))

			flash("添加成功,<span id='time'>3</span>秒后自动跳转管理页。")
			return redirect('%s%s' %('/manage/add_customers?pid=',pid))
	return render_template(
		"edit_customers.html",
		this = this,
		form=form)


# 修改客户
@api.route('/edit_customers', methods=['GET', 'POST'])
def edit_customers():

	this = 'edit'
	tsActive = 'manage_customers'

	getid = request.args.get('id')

	form = EditCustomersForm()

	userData = db_session.query(Users).filter(Users.id == getid).first()

	if form.validate_on_submit():
		id = request.form.get('id')
		password = request.form.get('password')

		
		# 判断是否修改密码
		if not password.strip():
			return redirect('/manage/manage_customers?verify=0&status=0')
		# 如果修改密码
		else:
			db_session.query(Users).filter(Users.id == id).update(
				{
					Users.password : password
				})
			db_session.commit()
			db_session.close()


		flash("修改成功,<span id='time'>3</span>秒后自动跳转管理页。")
		return redirect('%s%s' %('/manage/edit_customers?id=',id))


	return render_template(
		"edit_customers.html", 
		this = this,
		pagename = tsActive,
		userData = userData,
		form=form)

# 锁定用户
@api.route('/lock_customers', methods=['GET', 'POST'])
@login_required
def lock_customers():
	getid = int(request.args.get('id'))
	status = int(request.args.get('status'))
	Users.query.filter(Users.id == getid).update(
				{
					Users.lock : status
				})
	db_session.commit()
	db_session.close()
	return jsonify({"state":"ok"})

# 通过审核用户
@api.route('/examineall_customers', methods=['GET', 'POST'])
@login_required
def examineall_customers():

	getid = request.form.getlist('id')
	examine = request.args.get('examine',0)

	if len(getid) is 1:
		getid = request.form.get('id')
		try:
			upsort = db_session.query(Users).\
				filter(Users.id == getid).\
				update({Users.verify : examine})
			db_session.commit()
			# 记录日志
			# print upsort.phone
			actions = '%s%s' %('审核通过客户：',upsort.phone)
			savelog(actions)
		except:
			return jsonify({"state":"数据库错误"})
	else:
		for getid in getid:
			try:
				upsort = db_session.query(Users).\
					filter(Users.id == getid).\
					update({Users.verify : examine})
				db_session.commit()
				# 记录日志
				actions = '%s%s' %('审核通过客户：',upsort.phone)
				savelog(actions)
			except:
				return jsonify({"state":"数据库错误"})
	
	db_session.close()
	
	return jsonify({"state":'ok'})

# 通过审核用户
@api.route('/examine_customers', methods=['GET', 'POST'])
@login_required
def examine_customers():
	getid = request.args.get('id')
	examine = request.args.get('examine',0)
	teamid = request.args.get('teamid',0)

	upusers = Users.query.filter(Users.id == getid)

	upusers.update(
				{
					Users.verify : examine,
					Users.teamid : teamid
				})
	db_session.commit()

	#发送短信 password 和 phone 作为参数发送
	phone = '%s%s' %('+',upusers.first().phone)
	pssw = upusers.first().password
	user = upusers.first().truename

	message = '%s%s%s%s%s%s%s' %('【iShowRoom】尊敬的',user,'，您的帐号已审核通过，帐号：',phone,'，密码：',pssw,'。请您妥善保管密码，切勿泄漏给他人，若非您本人操作请忽略此短信！')

	result, err_message = message_validate(phone, message)
	if not result:
		return jsonify({'code': 0, 'message': err_message})
	

	# 记录日志
	actions = '%s%s' %('审核通过客户：',phone)
	savelog(actions)
	db_session.close()
	
	return jsonify({"state":'ok'})