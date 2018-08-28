# coding:utf-8
from flask import Flask, request, jsonify, g, render_template, redirect, url_for, session, current_app, make_response
from model import Silder, db_session, desc, or_
from decorator import login_check
from mobile import api

import datetime
import json

@api.route('/getSilders')
def getSilders():
	silders = db_session.query(Silder).\
				order_by(Silder.sort).limit(5)
    
#    return jsonify({'silder': [Silders.to_dict() for Silders in silders]})
	response = make_response(jsonify({'silder': [Silders.to_dict() for Silders in silders]}))
	response.headers['Access-Control-Allow-Origin'] = '*'
	response.headers['Access-Control-Allow-Methods'] = 'POST'
	response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
	return response
