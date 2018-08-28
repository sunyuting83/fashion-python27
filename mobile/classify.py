# coding:utf-8
from flask import Flask, request, jsonify, g, render_template, redirect, url_for, session, current_app
from model import Classify, Recommend, db_session, desc, or_
from decorator import login_check

from mobile import api

import datetime
import json

def getChildren(id,towclass):
	# 获取小类json
	change = towclass
	sz=[]
	for obj in change:
		if obj['topid'] ==id:
			sz.append({"classid":obj['classid'],"classname":obj['classname'],"topid":obj['topid'],"sort":obj['sort'],"icon":obj['icon'],"children":getChildren(obj['classid'],change)})
	return sz

def get_Children(id,towclass):
	# 获取小类json
	change = towclass
	sz=[]
	for obj in change:
		if obj['topid'] ==id:
			sz.append({"id":obj['id'],"titles":obj['titles'],"topid":obj['topid'],"sort":obj['sort'],"icon":obj['icon'],"children":get_Children(obj['id'],change)})
	return sz

@api.route('/getClassify', methods=['GET'])
def getClassify():
	topid = request.args.get('topid',0)
	if int(topid) is 0:
		classify = Classify.query.\
					filter_by(ctype = 0).\
					filter_by(display = 0).\
					order_by(Classify.sort).all()
	else:
		classify = Classify.query.\
				filter_by(topid = topid).\
				filter_by(ctype = 0).\
				filter_by(display = 0).\
				order_by(Classify.sort).all()

	towclass = [Class.to_dict() for Class in classify]
	return jsonify({'classify': getChildren(0,towclass)})

@api.route('/recommend', methods=['GET'])
def recommend():
	topid = request.args.get('topid',1)
	recommend = Recommend.query.all()

	towclass = [Class.to_dict() for Class in recommend]
	# print towclass
	return jsonify({'classify': get_Children(0,towclass)})