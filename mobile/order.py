# coding:utf-8
from flask import Flask, request, jsonify, g, render_template, redirect, url_for, session, current_app
from model import Order, OrderDetailed, UserCart, db_session, desc, func
from .decorator import login_check

from mobile import api
from config import Conf

import hashlib
import time
import random
import datetime
import json

@api.route('/post_order', methods=['POST'])
@login_check
def post_order():
	userid	 = g.current_user.id
	userphone  = g.current_user.phone
	orderitems = request.get_json().get('orderitems')
	addressid = request.get_json().get('addressid')
	teamid	 = g.current_user.teamid


	# 设计订单编号
	nowTime = datetime.datetime.now().strftime("%Y%m%d%H%M")  #生成当前时间
	randomNum = random.randint(10000,100000)  #生成的随机5位整数n，其中1000<=n<=10000
	phnumber = str(userphone)[-4:]
	ordernumber = '%s%s%s%s' % (int(nowTime), int(phnumber), int(teamid), int(randomNum))

	# 订单类型
	order_type = orderitems[0]['order_type']


	# 计算订单总金额 和 图片真实地址 和 购物车id
	cartid = []
	all_total = 0
	for i in range(len(orderitems)):
		print(orderitems[i])
		# 计算订单总金额
		all_total += orderitems[i]['color_total']
		# 得到购物车id
		cartid.append(orderitems[i]['cartid'])
	

	if len(orderitems) > 0:

		addorder = Order(
			number = ordernumber, 
			userid = userid, 
			teamid = teamid, 
			addressid = addressid, 
			state = 0, 
			order_total = all_total,
			order_type = order_type, 
			addtime = datetime.datetime.now()
		)
	

		try:
			db_session.add(addorder)
			db_session.commit()
			# 获取刚加添加的id
			db_session.flush()
			order_id = addorder.id
			order_item = [OrderDetailed(
							proid = int(orderitems[i]['proid']),
							pronumber = orderitems[i]['pronumber'],
							size = orderitems[i]['size'],
							color = orderitems[i]['color'],
							unit = int(orderitems[i]['unit']),
							price = int(orderitems[i]['price']),
							color_total = int(orderitems[i]['color_total']),
							order_id = int(order_id)
						)for i in range(len(orderitems))]
			
			try:
				db_session.add_all(order_item)
				db_session.commit()
			except Exception as e:
				print (e)
				db_session.rollback()
				return jsonify({'code': 3, 'message': '数据库错误'})

		except Exception as e:
			print (e)
			db_session.rollback()
			return jsonify({'code': 3, 'message': '数据库错误'})

		# 删除购物车
		delcart = db_session.query(UserCart).filter(UserCart.id.in_((cartid))).all()
		try:
			[db_session.delete(n) for n in delcart]
			db_session.commit()
			db_session.close()
		except Exception as e:
			print (e)
			db_session.rollback()
			return jsonify({'code': 3, 'message': '数据库错误'})



		return jsonify({'code': 1, 'message': '下单成功'})

@api.route('/get_order')
@login_check
def get_order():
	userid	 = g.current_user.id
	ordertype = int(request.args.get('ordertype',0))
	state = request.args.get('state',0)

	if state == '0':
		state = [0]
	if state == '1':
		state = [1,2,3,4,5,6,7,8,9,10,11,12,13,14]
	if state == '15':
		state = [15]
	# print state

	page = int(request.args.get('pageNo',1)) #get到页数

	lim = int(3) #get到每页显示数量

	newcont = db_session.query(func.count(Order.id)).\
				filter(Order.userid == userid).\
				filter(Order.order_type == ordertype).\
				filter(Order.state.in_((state))).\
				scalar() #计算数据总数
	if newcont == None:
		newcont = 0

	if page == 1:
		page_nb = 0 #如果第一页则从第0条数据开始调用
		page_show = int(lim + page_nb) #调用数量的结尾数
	else:
		page_nb = int((lim * (page - 1))) #否则用显示数量乘以当前页数减去1 得到开始数
		page_show = int(lim + page_nb) #调用数量的结尾数

	orderlist = Order.query.\
					filter_by(userid = userid, order_type = ordertype ).\
					filter(Order.state.in_((state))).\
					order_by(Order.addtime).limit(lim)[page_nb:page_show]

	return jsonify({'orderlist': [Orders.to_list() for Orders in orderlist]})

@api.route('/cancel_order', methods=['POST'])
@login_check
def cancel_order():
	orderid = request.get_json().get('id')

	cancel =  Order.query.filter_by(id=orderid).first()
	if cancel:
		cancel.state = 99
		try:
			db_session.add(cancel)
			db_session.commit()
		except Exception as e:
			print (e)
			db_session.rollback()
			return jsonify({'code': 3, 'message': '数据库错误'})

	return jsonify({'code': 1, 'message': '订单取消成功'})