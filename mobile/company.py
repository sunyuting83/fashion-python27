# coding:utf-8
from flask import Flask, request, jsonify, g, render_template, redirect, url_for, session, current_app
from model import Company ,db_session, desc, or_, func
from decorator import login_check

from mobile import api

import datetime
import json

# 新闻列表
@api.route('/company')
def company():

	company = Company.query

	return jsonify({'company': [Companys.to_dict() for Companys in company]})

