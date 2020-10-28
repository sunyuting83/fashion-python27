# coding:utf-8
from flask import Flask, request, jsonify, g, render_template, redirect, url_for, session, current_app
from model import News ,db_session, desc, or_, func
from .decorator import login_check

from mobile import api

import datetime
import json

# 新闻列表
@api.route('/helper')
def helper():
	getpid = int(request.args.get('getid',1))
	helplist = News.query.filter_by(pid = getpid, display = 0).all()

	return jsonify({'help': [Help.to_list() for Help in helplist]})

# 新闻内容
@api.route('/viewhelp')
def viewhelp():
	getid = int(request.args.get('getid',1)) #get到页数
	getpid = int(request.args.get('pid',1))
	viewhelp = News.query.filter_by(pid = getpid,id = getid, display = 0).first()

	return jsonify({'help': [Help.to_dict() for Help in helplist]})

