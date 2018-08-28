# coding:utf-8
from flask import Flask, request, jsonify, g, render_template, redirect, url_for, session, current_app
from model import Guestbook, MuGb, Manage, db_session, desc, or_
from decorator import login_check

from mobile import api

import datetime
import json

@api.route('/post_book', methods=['POST'])
@login_check
def post_book():
	userid	 = g.current_user.id
	content = request.get_json().get('getnav')
	# print userid

	if len(content) > 0:

		addbook = Guestbook( userid=userid, content=content, addtime=datetime.datetime.now())

		try:
			db_session.add(addbook)
			db_session.commit()
			db_session.flush()

			gbid = addbook.id
			teamid = g.current_user.teamid

			manageid = db_session.query(Manage).filter(or_(Manage.teamid == teamid,Manage.group_id == 1)).all()
			print len(manageid)
			if manageid:
				glbooks = [MuGb(
								manageid = manageid[i].id,
								bookid = gbid,
								status = 0
							) for i in range(len(manageid))]
				db_session.query(MuGb).first()
				try:
					db_session.add_all(glbooks)
					db_session.commit()
				except Exception as e:
					print e
					db_session.rollback()
					return jsonify({"state":"数据库错误"})
			
		except Exception as e:
			print e
			db_session.rollback()
			return jsonify({'code': 0, 'message': '数据库错误'})
	db_session.close()

	return jsonify({'state' : 'ok'})