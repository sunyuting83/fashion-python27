# coding:utf-8
from flask import Flask, request, jsonify, g, render_template, redirect, url_for, session, current_app
from model import Product, db_session, desc, or_, func
from decorator import login_check

from mobile import api

import datetime
import json


@api.route('/getProductList', methods=['GET'])
def getProductList():
	topid = int(request.args.get('topid'))
	page = int(request.args.get('pageNo',1)) #get到页数
	if topid is None:
		abort(404)

	lim = int(6) #get到每页显示数量

	newcont = db_session.query(func.count(Product.proid)).\
				filter(Product.pid == topid, Product.display == 0).scalar() #计算数据总数
	if newcont is None:
		newcont = 0

	if page == 1:
		page_nb = 0 #如果第一页则从第0条数据开始调用
		page_show = int(lim + page_nb) #调用数量的结尾数
	else:
		page_nb = int((lim * (page - 1))) #否则用显示数量乘以当前页数减去1 得到开始数
		page_show = int(lim + page_nb) #调用数量的结尾数
	

	productlist = Product.query.\
				filter_by(pid = topid).\
				filter_by(display = 0).\
				order_by(Product.add_time).limit(lim)[page_nb:page_show]

	return jsonify({'productlist': [Productls.to_list() for Productls in productlist]})


@api.route('/getSearchList', methods=['GET'])
def getSearchList():
	proname = request.args.get('proname')
	page = int(request.args.get('pageNo',1)) #get到页数
	if proname is None or proname is '':
		proname = ''

	print proname

	lim = int(6) #get到每页显示数量

	newcont = db_session.query(func.count(Product.proid)).\
				filter(Product.proname.like("%"+proname+"%"), Product.display == 0).scalar() #计算数据总数
	if newcont is None:
		newcont = 0

	if page == 1:
		page_nb = 0 #如果第一页则从第0条数据开始调用
		page_show = int(lim + page_nb) #调用数量的结尾数
	else:
		page_nb = int((lim * (page - 1))) #否则用显示数量乘以当前页数减去1 得到开始数
		page_show = int(lim + page_nb) #调用数量的结尾数
	

	productlist = Product.query.\
				filter(Product.proname.like("%"+proname+"%")).\
				filter_by(display = 0).\
				order_by(Product.add_time).limit(lim)[page_nb:page_show]

	return jsonify({'productlist': [Productls.to_list() for Productls in productlist]})

@api.route('/getstProduct', methods=['GET'])
def getstProduct():
	topid = int(request.args.get('topid'))
	page = int(request.args.get('pageNo',1)) #get到页数
	if topid is None:
		abort(404)

	lim = int(6) #get到每页显示数量

	newcont = db_session.query(func.count(Product.proid)).\
				filter(Product.new_p == topid, Product.display == 0).scalar() #计算数据总数
	if newcont is None:
		newcont = 0

	if page == 1:
		page_nb = 0 #如果第一页则从第0条数据开始调用
		page_show = int(lim + page_nb) #调用数量的结尾数
	else:
		page_nb = int((lim * (page - 1))) #否则用显示数量乘以当前页数减去1 得到开始数
		page_show = int(lim + page_nb) #调用数量的结尾数
	

	productlist = Product.query.\
				filter_by(new_p = topid).\
				filter_by(display = 0).\
				order_by(Product.add_time).limit(lim)[page_nb:page_show]

	return jsonify({'productlist': [Productls.to_list() for Productls in productlist]})