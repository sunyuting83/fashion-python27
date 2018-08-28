# coding:utf-8
from flask import Flask, request, jsonify, g, render_template, redirect, url_for, session, current_app
from model import Product, db_session, desc, or_
from decorator import login_check

from mobile import api

import datetime
import json


@api.route('/getProduct')
def getProduct():
	# phone_number = request.headers.get('token')
	# print phone_number
	proid = int(request.args.get('proid'))
	if proid is None:
		abort(404)
	product = Product.query.filter_by(proid = proid)

	return jsonify({'product': Products.to_dict() for Products in product})