# coding:utf-8
from flask import Flask, request, jsonify, g, render_template, redirect, url_for, session, current_app
from model import UserLike ,db_session, desc, or_, func
from decorator import login_check

from mobile import api

import datetime
import json

# 验证喜欢
@api.route('/iliked')
@login_check
def iliked():
	userid	 = g.current_user.id
	proid = int(request.args.get('proid',1))

	thislike = UserLike.query.filter_by(like_porid=proid, user_id=userid).first()
	if thislike:
		return jsonify({'code': 1, 'message': '已经收藏了'})

	return jsonify({'code': 0, 'message': '还未收藏'})

# 提交喜欢
@api.route('/ilike', methods=['POST'])
@login_check
def ilike():
	userid	 = g.current_user.id
	proid = request.get_json().get('proid')

	thislike = UserLike.query.filter_by(like_porid=proid, user_id=userid).first()
	if thislike:
		return jsonify({'code': 2, 'message': '已经收藏了'})

	user_like = UserLike(user_id=userid, like_porid=proid, add_time=datetime.datetime.now())
	db_session.add(user_like)

	try:
		db_session.commit()
	except Exception as e:
		print e
		db_session.rollback()
		return jsonify({'code': 3, 'message': '收藏失败'})


	return jsonify({'code': 1, 'message': '收藏成功'})

# 删除喜欢
@api.route('/dellike', methods=['POST'])
@login_check
def dellike():
	userid	 = g.current_user.id
	proid = request.get_json().get('proid')

	thislike = UserLike.query.filter_by(like_porid=proid, user_id=userid).first()
	if thislike:
		db_session.delete(thislike)

		try:
			db_session.commit()
		except Exception as e:
			print e
			db_session.rollback()
			return jsonify({'code': 3, 'message': '取消收藏失败'})


		return jsonify({'code': 1, 'message': '取消收藏成功'})
	return jsonify({'code': 3, 'message': '没有该产品'})

# 喜欢的产品列表
@api.route('/ilikelist')
@login_check
def ilikelist():
	userid	 = g.current_user.id

	page = int(request.args.get('pageNo',1)) #get到页数

	lim = int(6) #get到每页显示数量

	newcont = db_session.query(func.count(UserLike.user_id)).\
				filter(UserLike.user_id == userid).scalar() #计算数据总数
	if newcont is None:
		newcont = 0

	if page == 1:
		page_nb = 0 #如果第一页则从第0条数据开始调用
		page_show = int(lim + page_nb) #调用数量的结尾数
	else:
		page_nb = int((lim * (page - 1))) #否则用显示数量乘以当前页数减去1 得到开始数
		page_show = int(lim + page_nb) #调用数量的结尾数


	likelist = UserLike.query.\
				filter_by(user_id = userid).\
				order_by(UserLike.add_time).limit(lim)[page_nb:page_show]

	return jsonify({'likelist': [LikeList.to_list() for LikeList in likelist]})