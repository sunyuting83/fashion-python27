# coding:utf-8
from flask import Flask, request, jsonify, g, render_template, redirect, url_for, session, current_app
from model import Manage ,db_session, desc, or_, func
from decorator import login_check

from mobile import api

import datetime
import json

# 验证喜欢
@api.route('/contactus')
@login_check
def contactus():
	teamid	 = g.current_user.teamid

	contact = Manage.query.filter_by(teamid=teamid,contact=0).all()

	return jsonify({'contact': [Contact.to_dict() for Contact in contact]})