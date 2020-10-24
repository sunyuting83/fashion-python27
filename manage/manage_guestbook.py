# coding:utf-8
from flask import Flask, render_template, redirect, session, url_for, request, g, flash, abort, jsonify, make_response
from flask_wtf import FlaskForm
from wtforms import TextField, BooleanField, PasswordField, SubmitField, SelectField, HiddenField, StringField, TextAreaField

from model import Guestbook, Users, MuGb, and_, or_, desc, asc, func, db_session

from .public import *

from manage import api

import math
import datetime



# 留言列表
@api.route('/manage_guestbook/<int:status>', methods=['GET', 'POST'])
@api.route('/manage_guestbook/<int:status>/', methods=['GET', 'POST'])
@login_required
def manage_guestbook(status):

	# 分页开始
	lim = int(8) #get到每页显示数量
	page = int(request.args.get('page',1)) #get到页数


	if current_user.group.power == 0:  #超级管理员
		newcont = db_session.query(func.count(Guestbook.id)).\
				join(Users).\
				join(MuGb).\
				filter(Guestbook.id == MuGb.bookid).\
				filter(MuGb.manageid == current_user.id).\
				filter(MuGb.status == status).\
				scalar() #计算数据总数
	else:
		newcont = db_session.query(func.count(Guestbook.id)).\
				join(Users).\
				join(MuGb).\
				filter(current_user.id == MuGb.manageid).\
				filter(MuGb.status == status).\
				filter(Guestbook.id == MuGb.bookid).\
				filter(Users.teamid == current_user.teamid).\
				scalar() #计算数据总数
	if newcont == None:
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
	if previous == 0:
		previous = 0
	nextp = page + 1
	if nextp == page_cont:
		nextp = page_cont

	if current_user.group.power == 0:  #超级管理员
		guest = db_session.query(Guestbook).\
				join(Users).\
				join(MuGb).\
				filter(Guestbook.id == MuGb.bookid).\
				filter(MuGb.manageid == current_user.id).\
				filter(MuGb.status == status).\
				order_by(Guestbook.addtime.desc()).\
				limit(lim)[page_nb:page_show]
	else:
		guest = db_session.query(Guestbook).\
				join(Users).\
				join(MuGb).\
				filter(MuGb.status == status).\
				filter(current_user.id == MuGb.manageid).\
				filter(Guestbook.id == MuGb.bookid).\
				filter(Users.teamid == current_user.teamid).\
				order_by(Guestbook.addtime.desc()).\
				limit(lim)[page_nb:page_show]


	return render_template(
		"manage_guestbook.html", 
		pagename = 'manage_guestbook',
		booklist = guest,
		stat = status,
		page = page_size,
		previous = previous,
		nextp = nextp,
		page_cont = page_cont,
		newcont = newcont
	)


# 留言标记
@api.route('/upbooks', methods=['POST'])
@api.route('/upbooks/', methods=['POST'])
@login_required
def upbooks():
	getid = request.form.getlist('id')
	manageid = current_user.id
	if len(getid) == 1:
		bookid = getid[0]
		upstatus = MuGb.query.filter_by(bookid = bookid, manageid = manageid).first()
		if upstatus:
			upstatus.status = 1
			try:
				db_session.add(upstatus)
				db_session.commit()
			except Exception as e:
				print (e)
				db_session.rollback()
				return jsonify({"state":"数据库错误"})
	else:
		manageid = []
		for x in getid:
			manageid.append(current_user.id)
		for (getid,manageid) in zip(getid,manageid):
			try:
				db_session.query(MuGb).\
					filter(MuGb.bookid == getid, MuGb.manageid == manageid).\
					update({MuGb.status : 1})
				db_session.commit()
			except Exception as e:
				print (e)
				db_session.rollback()
				return jsonify({"state":"数据库错误"})
	return jsonify({'state':'ok'})

# 留言数量
@api.route('/manage_booknb/<int:userid>', methods=['GET', 'POST'])
@api.route('/manage_booknb/<int:userid>/', methods=['GET', 'POST'])
@login_required
def manage_booknb(userid):
	thisnb = db_session.query(func.count(MuGb.id)).filter(MuGb.manageid == userid,MuGb.status == 0).\
				scalar()
	return jsonify({'cont':thisnb})