# coding:utf-8
from flask import Flask, render_template, redirect, session, url_for, request, g, flash, abort, jsonify, make_response
from flask_wtf import FlaskForm
from wtforms import TextField, BooleanField, PasswordField, SubmitField, SelectField, HiddenField, StringField, TextAreaField

from model import Order, OrderDetailed, OrderState, and_, or_, desc, asc, func, db_session, extract

from public import *
from config import Conf
from excel import *

from manage import api

import math
import time
import datetime
import json

# 更新订单状态入库函数
def upst_to_st(orderid,state,text):
	orderstate = OrderState(
			orderid = orderid,
			state = state,
			text = text,
			uptime = datetime.datetime.now()
	)
	try:
		db_session.add(orderstate)
		db_session.commit()
	except Exception as e:
		print e
		db_session.rollback()
		return jsonify({"state":"数据库错误"})

# 短信自定义内容函数
def make_message(userphone,usernames,ordernumber,text):
	message = '%s%s%s%s%s%s%s' %('尊敬的客户',usernames,'，您的订单：',ordernumber,'，',text,'。')
	message_validate(userphone,message) # 调用发送短信函数


# 订单列表
@api.route('/manage_order/<int:order_type>/<int:state>', methods=['GET', 'POST'])
@api.route('/manage_order/<int:order_type>/<int:state>/', methods=['GET', 'POST'])
@login_required
def manage_order(order_type,state=0):

	if order_type is None:
		order_type = 0
		tsActive = 'manage_order'
	if order_type is 0:
		tsActive = 'manage_order'
	else:
		tsActive = 'manage_jdorder'

	ordernb = request.args.get('ordernb')
	
	# print title

	# 分页开始
	lim = int(8) #get到每页显示数量
	page = int(request.args.get('page',1)) #get到页数

	# 权限判断

	if current_user.group.power == 0:  #超级管理员
		newcont = db_session.query(func.count(Order.id)).\
				filter(Order.order_type == order_type, Order.state == state).scalar() #计算数据总数
	if current_user.group.power <= 2 and current_user.group.power > 0:  #组长
		newcont = db_session.query(func.count(Order.id)).\
				filter(Order.order_type == order_type, Order.state == state, Order.teamid == current_user.teamid).scalar() #计算数据总数

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
	if ordernb is None:
		ordernb = ''
		if current_user.group.power == 0:
			orderlist = db_session.query(Order).\
				filter(Order.order_type == order_type, Order.state == state).\
				order_by(Order.addtime.desc()).limit(lim)[page_nb:page_show]
		if current_user.group.power <= 2 and current_user.group.power > 0:
			orderlist = db_session.query(Order).\
				filter(Order.order_type == order_type, Order.state == state, Order.teamid == current_user.teamid).\
				order_by(Order.addtime.desc()).limit(lim)[page_nb:page_show]
	# 如果有搜索条件，计算分页，加入条件
	else:
		if current_user.group.power == 0:  #超级管理员
			newcont = db_session.query(func.count(Order.id)).\
				filter(Order.number == ordernb, Order.state == state, Order.order_type == order_type).scalar() #计算数据总数
		if current_user.group.power <= 2 and current_user.group.power > 0:  #组长
			newcont = db_session.query(func.count(Order.id)).\
				filter(Order.number == ordernb, Order.state == state, Order.order_type == order_type, Order.teamid == current_user.teamid).scalar() #计算数据总数

		page_cont = int(math.ceil(round(float(newcont) / lim,2)))
		page_size = []
		for i in range(page_cont):
			page_size.append(i + 1)

		if newcont >= lim:
			if current_user.group.power == 0:  #超级管理员
				orderlist = db_session.query(Order).\
					filter(Order.number == ordernb, Order.state == state, Order.order_type == order_type).\
					order_by(Order.addtime.desc()).limit(lim)[page_nb:page_show]
			if current_user.group.power <= 2 and current_user.group.power > 0:
				orderlist = db_session.query(Order).\
					filter(Order.number == ordernb, Order.state == state, Order.order_type == order_type, Order.teamid == current_user.teamid).\
					order_by(Order.addtime.desc()).limit(lim)[page_nb:page_show]
		else:
			page_show = int(newcont + ((newcont * page)-1))
			# print newcont,page_show,page
			if current_user.group.power == 0:  #超级管理员
				orderlist = db_session.query(Order).\
					filter(Order.number == ordernb, Order.state == state, Order.order_type == order_type).\
					order_by(Order.addtime.desc()).limit(lim)[0:page_show]
			if current_user.group.power <= 2 and current_user.group.power > 0:
				orderlist = db_session.query(Order).\
					filter(Order.number == ordernb, Order.state == state, Order.order_type == order_type, Order.teamid == current_user.teamid).\
					order_by(Order.addtime.desc()).limit(lim)[0:page_show]

	return render_template(
		"manage_order.html", 
		pagename = tsActive,
		order_type = order_type, 
		orderlist = orderlist,
		page = page_size,
		previous = previous,
		nextp = nextp,
		page_cont = page_cont,
		ordernb = ordernb,
		newcont = newcont,
		state = state)


# 订单详细
@api.route('/view_order', methods=['GET', 'POST'])
@login_required
def view_order():
	if request.args.get('order_type') is None:
		order_type = 0
	else:
		order_type = int(request.args.get('order_type'))

	display = request.args.get('display',0)

	orderid = request.args.get('id')

	if current_user.group.power == 0:
		orderview = Order.query.\
			filter_by(order_type = order_type, id = orderid).first()
	if current_user.group.power <= 2 and current_user.group.power > 0:
		orderview = Order.query.\
			filter_by(order_type = order_type, id = orderid, teamid = current_user.teamid).first()

	return render_template(
		"view_order.html",
		orderview = orderview,
		pagename = 'manage_order')

# 修改订单
@api.route('/up_order', methods=['POST'])
@login_required
def edit_order():
	state = request.form.get('state')
	orderid = request.form.get('orderid')
	ordertype = request.form.get('ordertype')
	upstate = Order.query.\
			filter_by(id = orderid).\
			first()

	userphone = upstate.od_address.phone_number #收货人手机号
	usernames = upstate.od_address.contacts #收货人姓名
	ordernumber = upstate.number #订单号
	usermail = upstate.users.mail #用户邮箱
	# print userphone,usernames,ordernumber,usermail

	if upstate:
		if int(ordertype) == 0:
			if int(state) == 1:
				text = request.form.get('text')

				'''
				定义短信内容
				'''
				message = '%s%s%s%s%s%s%s' %('尊敬的客户',usernames,'，您的订单：',ordernumber,'，已付订金。共￥',text,'。')
				message_validate(userphone,message) # 调用发送短信函数

				upst_to_st(orderid,state,text) #调用更新状态函数

				# 调用Excel生成函数
				makeexcel = write_excel(upstate)
				# print slkdjf

				# Json化返回结果
				excel = json.loads(makeexcel)

				
				# 发送邮件函数暂时去掉
				atitle = '订单详细信息.xls'
				if int(excel['code']) is 1:
					# 调用邮件函数
					title = '【iShowRoom】您的订单详细信息'
					recipients = [usermail,Conf.MAIL_USERNAME]
					body = '【iShowRoom】您的订单详细信息，详情请下载附件。'
					attach = excel['fullpath']
					send_email(title,recipients,body,attach,atitle)
				else:
					jsonify({'code': 0, 'message': '数据库错误'})
				

			if int(state) == 2:
				text = '已经开始面料采购'
				upst_to_st(orderid,state,text)
				make_message(userphone,usernames,ordernumber,text)
			if int(state) == 3:
				text = '面料已经到位，开始裁剪或织造。'
				upst_to_st(orderid,state,text)
				make_message(userphone,usernames,ordernumber,text)
			if int(state) == 4:
				text = '大货中查'
				upst_to_st(orderid,state,text)
				make_message(userphone,usernames,ordernumber,text)
			if int(state) == 5:
				text = '大货尾查'
				upst_to_st(orderid,state,text)
				make_message(userphone,usernames,ordernumber,text)
			if int(state) == 6:
				text = request.form.get('text')
				upst_to_st(orderid,state,text)
				make_message(userphone,usernames,ordernumber,text)

			if int(state) == 7:
				text = request.form.get('text')
				upst_to_st(orderid,state,text)
				make_message(userphone,usernames,ordernumber,text)

			if int(state) == 8:
				text = '你需要支付中期款60%方可发货。'
				upst_to_st(orderid,state,text)
				make_message(userphone,usernames,ordernumber,text)

			if int(state) == 9:
				text = request.form.get('text')
				upst_to_st(orderid,state,text)
				make_message(userphone,usernames,ordernumber,text)

			if int(state) == 10:
				thisexcel = request.form.get('thisexcel')
				usermail = request.form.get('usermail')
				make_message(userphone,usernames,ordernumber,text)
				'''
				发送邮件
				'''
				title = '【iShowRoom】您的订单已发货，附件是发货清单。'
				recipients = [usermail,Conf.MAIL_USERNAME]
				body = '【iShowRoom】您的订单已发货，附件是发货清单。'
				attach = thisexcel
				send_email(title,recipients,body,attach)
				# 在保存数据库
				upst_to_st(orderid,state,thisexcel)

			if int(state) == 11:
				text = '你的货物已经出中国海关'
				upst_to_st(orderid,state,text)
				make_message(userphone,usernames,ordernumber,text)
			if int(state) == 12:
				text = '你的货物已经到意大利海关，准备清关'
				upst_to_st(orderid,state,text)
				make_message(userphone,usernames,ordernumber,text)

			if int(state) == 13:
				text = request.form.get('text')
				upst_to_st(orderid,state,text)
				make_message(userphone,usernames,ordernumber,text)

			if int(state) == 14:
				text = '请支付尾款10%以完成订单。'
				make_message(userphone,usernames,ordernumber,text)

			if int(state) == 15:
				text = request.form.get('text')
				upst_to_st(orderid,state,text)
				make_message(userphone,usernames,ordernumber,text)

			'''
			下面是短信调用函数
			'''
			# 	text = request.form.get('message')
			# 	message = '%s%s%s%s%s%s%s' %('尊敬的客户',usernames,'，您的订单：',ordernumber,'，',text,'。')
			# 	message_validate(userphone,message) # 调用发送短信函数
		else:
			if int(state) == 1:
				text = '已确认借调样品'
				upst_to_st(orderid,state,text)
				make_message(userphone,usernames,ordernumber,text)
			if int(state) == 2:
				text = '样品已经发出'
				upst_to_st(orderid,state,text)
				make_message(userphone,usernames,ordernumber,text)
			if int(state) == 3:
				text = '样品已经出中国海关'
				upst_to_st(orderid,state,text)
				make_message(userphone,usernames,ordernumber,text)
			if int(state) == 4:
				text = '样品已经到意大利海关'
				upst_to_st(orderid,state,text)
				make_message(userphone,usernames,ordernumber,text)
			if int(state) == 5:
				text = '样品准备派件'
				upst_to_st(orderid,state,text)
				make_message(userphone,usernames,ordernumber,text)
			if int(state) == 6:
				text = '样品在海关，需要缴纳关税方可派件'
				upst_to_st(orderid,state,text)
				make_message(userphone,usernames,ordernumber,text)
			if int(state) == 7:
				text = '样品订单完成'
				upst_to_st(orderid,state,text)
				make_message(userphone,usernames,ordernumber,text)

		'''
		更新订单状态
		'''
		upstate.state = state
		upstate.uptime = datetime.datetime.now()
		try:
			db_session.add(upstate)
			db_session.commit()
		except Exception as e:
			print e
			db_session.rollback()
			return jsonify({"state":"数据库错误"})
	return jsonify({"state":"ok"})

# 订单统计
@api.route('/order_statistics', methods=['GET', 'POST'])
@api.route('/order_statistics/', methods=['GET', 'POST'])
@login_required
def order_statistics():
	thispage = request.args.get('thispage')
	getdate = ''
	if thispage is 'day' or thispage is None:
		thispage = 'day'
	if thispage == 'diy':
		getdate = request.form.get('diys')

	return render_template(
		'order_statistics.html',
		thispage= thispage,
		getdate = getdate,
		pagename = 'order_statistics')

# 订单统计获取接口
@api.route('/order_api', methods=['POST'])
@api.route('/order_api/', methods=['POST'])
@login_required
def order_api():
	date = request.form.get('date')
	startime = request.form.get('startime')
	endtime = request.form.get('endtime')
	if date == 'today':
		return jsonify(gethors(date,startime,endtime))
	if date == 'week':
		return jsonify(gethors(date,startime,endtime))
	if date == 'month':
		return jsonify(gethors(date,startime,endtime))
	if date == 'year':
		return jsonify(gethors(date,startime,endtime))
	if date == 'diy':
		return jsonify(gethors(date,startime,endtime))


# 得到24小时数据函数
def gethors(what,startime,endtime):

	today = {}
	pro = []
	diao = []
	hours = []

	firsttime = datetime.datetime.today()
	lasttime = datetime.datetime.today()

	if what == 'today':
		todays = datetime.datetime.today()
		NOW =  datetime.datetime(todays.year, todays.month, todays.day, 23, 59, 59)
		for i in range(24):

			hours.append('%s%s'%(i,'点'))

			procont = db_session.query(func.count(Order.id)).\
					filter(Order.addtime.between(NOW - datetime.timedelta(seconds=i*3600-1), NOW - datetime.timedelta(hours=i-1))).\
					filter(Order.order_type==0).scalar()
			pro.append(procont)
			# print NOW - datetime.timedelta(seconds=i*3600 - 1),NOW - datetime.timedelta(hours=i - 1)

			diaocont = db_session.query(func.count(Order.id)).\
					filter(Order.addtime.between(NOW - datetime.timedelta(seconds=i*3600-1), NOW - datetime.timedelta(hours=i-1))).\
					filter(Order.order_type==1).scalar()
			diao.append(diaocont)

		today['pro'] = pro[::-1]
		today['diao'] = diao[::-1]

		firsttime = datetime.datetime(todays.year, todays.month, todays.day, 0, 0, 0)
		lasttime = datetime.datetime(todays.year, todays.month, todays.day, 23, 59, 59)

	if what == 'week':
		now = datetime.datetime.now()
		firsttime = now - datetime.timedelta(days=now.weekday())
		firsttime = datetime.datetime(firsttime.year, firsttime.month, firsttime.day)
		lasttime = now + datetime.timedelta(days=6-now.weekday())
		lasttime = datetime.datetime(lasttime.year, lasttime.month, lasttime.day, 23, 59, 59)
		for i in range(1,8,1):
			procont = db_session.query(func.count(Order.id)).\
					filter(and_(
						extract('year', Order.addtime) == firsttime.year,
						extract('month', Order.addtime) == firsttime.month,
						extract('day', Order.addtime) == firsttime.day + i
					)).\
					filter(Order.order_type==0).scalar()
			pro.append(procont)

			diaocont = db_session.query(func.count(Order.id)).\
					filter(and_(
						extract('year', Order.addtime) == firsttime.year,
						extract('month', Order.addtime) == firsttime.month,
						extract('day', Order.addtime) == firsttime.day + i
					)).\
					filter(Order.order_type==1).scalar()
			diao.append(diaocont)

			if i == 1:
				i = '一'
			if i == 2:
				i = '二'
			if i == 3:
				i = '三'
			if i == 4:
				i = '四'
			if i == 5:
				i = '五'
			if i == 6:
				i = '六'
			if i == 7:
				i = '日'
			hours.append('%s%s'%('星期',i))

		today['pro'] = pro
		today['diao'] = diao

	if what == 'month':
		now = datetime.datetime.now()
		
		firsttime = datetime.datetime(now.year, now.month, 1)
		firsttime = datetime.datetime(firsttime.year, firsttime.month, firsttime.day)

		if now.month == 12:
			lasttime = datetime.datetime(now.year , 12, 31)
		else:
			lasttime = datetime.datetime(now.year, now.month + 1, 1) - datetime.timedelta(days=1)
		lasttime = datetime.datetime(lasttime.year, lasttime.month, lasttime.day, 23, 59, 59)
		
		lastday = lasttime.day

		for i in range(1,lastday + 1,1):
			hours.append('%s%s'%(i,'号'))
			procont = db_session.query(func.count(Order.id)).\
					filter(and_(
						extract('year', Order.addtime) == firsttime.year,
						extract('month', Order.addtime) == firsttime.month,
						extract('day', Order.addtime) == i
					)).\
					filter(Order.order_type==0).scalar()
			pro.append(procont)
			# print NOW - datetime.timedelta(seconds=i*3600 - 1),NOW - datetime.timedelta(hours=i - 1)

			diaocont = db_session.query(func.count(Order.id)).\
					filter(and_(
						extract('year', Order.addtime) == firsttime.year,
						extract('month', Order.addtime) == firsttime.month,
						extract('day', Order.addtime) == i
					)).\
					filter(Order.order_type==1).scalar()
			diao.append(diaocont)
		today['pro'] = pro
		today['diao'] = diao
	if what == 'year':
		now = datetime.datetime.now()
		
		firsttime = datetime.datetime(now.year, 1, 1)
		firsttime = datetime.datetime(firsttime.year, firsttime.month, firsttime.day)

		lasttime = datetime.datetime(now.year, 12, 31)
		lasttime = datetime.datetime(lasttime.year, lasttime.month, lasttime.day, 23, 59, 59)
		# procont = db_session.query(extract('month', Order.order_type).label('month'), func.count(Order.id).label('count')).group_by('month')

		for i in range(1,13,1):
			hours.append('%s%s'%(i,'月'))
			procont = db_session.query(func.count(Order.id)).\
					filter(and_(
						extract('year', Order.addtime) == firsttime.year,
						extract('month', Order.addtime) == i
					)).\
					filter(Order.order_type==0).scalar()
			# procont = db_session.query(func.count(Order.id)).\
			# 		filter(Order.addtime.between(datetime.datetime(now.year, i + 1, 1) + , datetime.datetime(now.year, i + 1, 1))).\
			# 		filter(Order.order_type==0).scalar()
			pro.append(procont)
			# print NOW - datetime.timedelta(seconds=i*3600 - 1),NOW - datetime.timedelta(hours=i - 1)

			diaocont = db_session.query(func.count(Order.id)).\
					filter(and_(
						extract('year', Order.addtime) == firsttime.year,
						extract('month', Order.addtime) == i
					)).\
					filter(Order.order_type==1).scalar()
			diao.append(diaocont)
		today['pro'] = pro
		today['diao'] = diao
	if what == 'diy':
		firsttime = datetime.datetime.strptime(startime,'%Y-%m-%d')
		lasttime = datetime.datetime.strptime(endtime,'%Y-%m-%d')
		lasttime = datetime.datetime(lasttime.year, lasttime.month, lasttime.day, 23, 59, 59)

		for d in gen_dates(firsttime, (lasttime-firsttime).days + 1):
			hours.append('%s%s%s%s%s'%(d.year,'-',d.month,'-',d.day))

		# c = lasttime - firsttime
		# for i in range(1,c.days + 1):

			procont = db_session.query(func.count(Order.id)).\
					filter(and_(
						extract('year', Order.addtime) == d.year,
						extract('month', Order.addtime) == d.month,
						extract('day', Order.addtime) == d.day
					)).\
					filter(Order.order_type==0).scalar()
			pro.append(procont)
			# print NOW - datetime.timedelta(seconds=i*3600 - 1),NOW - datetime.timedelta(hours=i - 1)

			diaocont = db_session.query(func.count(Order.id)).\
					filter(and_(
						extract('year', Order.addtime) == d.year,
						extract('month', Order.addtime) == d.month,
						extract('day', Order.addtime) == d.day
					)).\
					filter(Order.order_type==1).scalar()
			diao.append(diaocont)
		today['pro'] = pro
		today['diao'] = diao
	'''
	firsttime 当日0点
	lasttime 当日23点
	获取当日商品订单金额情况
	'''
	# print firsttime,lasttime
	daif = db_session.query(Order).\
			filter(Order.order_type == 0).\
			filter(Order.state == 0).\
			filter(Order.addtime.between(firsttime,lasttime)).all()
	firstmoney = db_session.query(OrderState).\
				filter(OrderState.orderid == Order.id).\
				filter(Order.order_type == 0).\
				filter(OrderState.state == 1).\
				filter(OrderState.uptime.between(firsttime,lasttime)).all()

	centermoney = db_session.query(OrderState).\
				filter(OrderState.orderid == Order.id).\
				filter(Order.order_type == 0).\
				filter(OrderState.state == 8).\
				filter(OrderState.uptime.between(firsttime,lasttime)).all()
	lastmoney = db_session.query(OrderState).\
				filter(OrderState.orderid == Order.id).\
				filter(Order.order_type == 0).\
				filter(OrderState.state == 13).\
				filter(OrderState.uptime.between(firsttime,lasttime)).all()
	# print firstmoney
	daiflen = 0
	firstmoneylen = 0
	centermoneylen = 0
	lastmoneylen = 0
	if daif:
		x = 0
		for x in daif:
			daiflen += int(x.order_total)

	if firstmoney:
		# print firstmoney
		x = 0
		for x in firstmoney:
			firstmoneylen += int(x.text)

	if centermoney:
		x = 0
		for x in centermoney:
			centermoneylen += int(x.text)

	if lastmoney:
		x = 0
		for x in lastmoney:
			lastmoneylen += int(x.text)

	'''
	获取当日借调订单金额
	'''
	diaomoneyed = db_session.query(Order).\
			filter(Order.id == OrderState.orderid).\
			filter(Order.order_type == 1).\
			filter(OrderState.uptime.between(firsttime,lasttime)).all()
	diaomed = 0
	if diaomoneyed:
		x = 0
		for x in diaomoneyed:
			diaomed += int(x.order_total)

	diaomoney = db_session.query(Order).\
			filter(Order.id != OrderState.orderid).\
			filter(Order.order_type == 1).\
			filter(Order.addtime.between(firsttime,lasttime)).all()
	diaom = 0
	if diaomoney:
		x = 0
		for x in diaomoney:
			diaom += int(x.order_total)


	today['hours'] = hours
	today['money'] = {
		'dai': daiflen,
		'dailen': len(daif),
		'first': firstmoneylen,
		'firstlen': len(firstmoney),
		'center': centermoneylen,
		'centerlen': len(centermoney),
		'last': lastmoneylen,
		'lastlen': len(lastmoney)
	}
	today['diao_money'] = {
		'daidiao': diaom,
		'diaoed': diaomed,
		'daidiaolen': len(diaomoney),
		'diaoedlen': len(diaomoneyed)
	}
	
	return today

# 日期列表函数
def gen_dates(b_date, days):
	day = datetime.timedelta(days=1)
	for i in range(days):
		yield b_date + day*i