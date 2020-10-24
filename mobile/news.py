# coding:utf-8
from flask import Flask, request, jsonify, g, render_template, redirect, url_for, session, current_app
from model import News ,db_session, desc, or_, func
from .decorator import login_check

from mobile import api

import datetime
import json

# 新闻列表
@api.route('/news')
def news():

	page = int(request.args.get('pageNo',1)) #get到页数
	getpid = request.args.get('pid',1) #get到页数

	lim = int(8) #get到每页显示数量

	newcont = db_session.query(func.count(News.id)).\
				filter(News.pid == getpid, News.display ==0).scalar() #计算数据总数
	if newcont == None:
		newcont = 0

	if page == 1:
		page_nb = 0 #如果第一页则从第0条数据开始调用
		page_show = int(lim + page_nb) #调用数量的结尾数
	else:
		page_nb = int((lim * (page - 1))) #否则用显示数量乘以当前页数减去1 得到开始数
		page_show = int(lim + page_nb) #调用数量的结尾数


	newslist = News.query.\
				filter_by(pid = getpid, display = 0).\
				order_by(News.addtime).limit(lim)[page_nb:page_show]

	return jsonify({'news': [New.to_newlist() for New in newslist]})

# 新闻内容
@api.route('/viewnews')
def viewnews():
	getid = request.args.get('id',1) #get到页数
	viewnews = News.query.filter_by(id = getid)

	return jsonify({'news': New.to_list() for New in viewnews})

