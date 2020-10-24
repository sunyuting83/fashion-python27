# coding:utf-8
from flask import Flask, request, jsonify, g, render_template, redirect, url_for, session, current_app
from model import UserCart, db_session, desc, func
from .decorator import login_check

from mobile import api
from config import Conf

import hashlib
import time
import random
import datetime
import json

@api.route('/post_cart', methods=['POST'])
@login_check
def post_cart():
	userid	 = g.current_user.id

	orderitems = request.get_json().get('orderdata')

	for i in range(len(orderitems)):
		orderjson =  json.loads(orderitems[i])

		hascart = UserCart.query.\
				filter_by(
					userid = int(userid), 
					order_type = int(orderjson['type']), 
					proid      = int(orderjson['proid']), 
					pronumber  = orderjson['pronumber'], 
					size       = orderjson['size'],
					color      = orderjson['color']
				).first()
		if hascart == None:
			cart = UserCart(
					userid = int(userid),
					order_type = int(orderjson['type']),
					proid = int(orderjson['proid']),
					pronumber = orderjson['pronumber'],
					size = orderjson['size'],
					color = orderjson['color'],
					unit = orderjson['number'],
					price = orderjson['price'],
					color_total = orderjson['color_total'],
					pic = orderjson['pic']
				)
			db_session.add(cart)
			try:
				db_session.commit()
			except Exception as e:
				print (e)
				db_session.rollback()
				return jsonify({'code': 0, 'message': '数据库错误'})
		else:
			db_session.query(UserCart).\
				filter(UserCart.userid == hascart.userid).\
				filter(UserCart.order_type == hascart.order_type).\
				filter(UserCart.proid == hascart.proid).\
				filter(UserCart.pronumber == hascart.pronumber).\
				filter(UserCart.size == hascart.size).\
				filter(UserCart.color == hascart.color).\
				update(
					{
						UserCart.userid : int(userid),
						UserCart.order_type : int(orderjson['type']),
						UserCart.proid : int(orderjson['proid']),
						UserCart.pronumber : orderjson['pronumber'],
						UserCart.size : orderjson['size'],
						UserCart.color : orderjson['color'],
						UserCart.unit : int(orderjson['number']) + int(hascart.unit),
						UserCart.price : int(orderjson['price']),
						UserCart.color_total : int(orderjson['color_total']) + int(hascart.color_total),
						UserCart.pic : orderjson['pic']
					}
				)
			try:
				db_session.commit()
			except Exception as e:
				print (e)
				db_session.rollback()
				return jsonify({'code': 0, 'message': '数据库错误'})
	return jsonify({'code':1, 'message': '成功添加购物车到'})



@api.route('/get_cart')
@login_check
def get_cart():
	userid	 = g.current_user.id
	types = int(request.args.get('type',0))

	cartlist = UserCart.query.filter_by(userid=userid,order_type=types)

	return jsonify({'cartlist': [Cartls.to_list() for Cartls in cartlist]})

@api.route('/del_cart', methods=['POST'])
@login_check
def del_cart():
	getid = request.get_json().get('cartid')

	thiscart = UserCart.query.filter_by(id=getid).first()
	db_session.delete(thiscart)

	try:
		db_session.commit()
	except Exception as e:
		print (e)
		db_session.rollback()
		return jsonify({'code': 3, 'message': '删除失败'})


	return jsonify({'code': 1, 'message': '删除成功'})

@api.route('/get_cart_cont')
@login_check
def get_cart_cont():
	userid	 = g.current_user.id

	cartcont = db_session.query(func.count(UserCart.userid)).\
				filter(UserCart.userid == userid).scalar() #计算数据总数

	return jsonify({'cartcont': cartcont})

@api.route('/up_cart_cont', methods=['POST'])
@login_check
def up_cart_cont():
	getid = request.get_json().get('cartid')
	getunit = request.get_json().get('unit')
	# print getid,getunit

	thiscart = UserCart.query.filter_by(id=getid).first()
	if thiscart:
		color_total = getunit * thiscart.price
		thiscart.unit = getunit
		thiscart.color_total = color_total
		db_session.add(thiscart)

		try:
			db_session.commit()
		except Exception as e:
			print (e)
			db_session.rollback()
			return jsonify({'code': 3, 'message': '更新失败'})


	return jsonify({'code': 1, 'message': '更新成功'})

@api.route('/del_many_cart', methods=['POST'])
@login_check
def del_many_cart():
	getid = request.get_json().get('cartid')
	delg = db_session.query(UserCart).filter(UserCart.id.in_((getid))).all()
	if delg:
		order_type = delg[0].order_type
		try:
			[db_session.delete(n) for n in delg]
			db_session.commit()
			db_session.close()
		except Exception as e:
			print (e)
			db_session.rollback()
			return jsonify({'code': 3, 'message': '删除失败','order_type':order_type})
		return jsonify({'code': 1, 'message': '删除成功','order_type':order_type})
