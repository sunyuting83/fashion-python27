# coding:utf-8
from flask import Flask, request, jsonify, g, render_template, redirect, url_for, session, current_app
from model import Address, db_session, desc, or_
from .decorator import login_check

from mobile import api

import datetime
import json

@api.route('/addressList')
@login_check
def addressList():
	userid	 = g.current_user.id
	adlist = Address.query.filter_by(userid = userid).all()

	return jsonify({'adlist': [Adlist.to_list() for Adlist in adlist]})

@api.route('/get_address')
@login_check
def get_address():
	userid	 = g.current_user.id
	address = Address.query.filter_by(userid = userid).order_by(Address.default.desc()).first();
	if address:
		id = address.id
		contacts = address.contacts
		phone_number = address.phone_number
		address = address.address
		return jsonify({'address':[{'id':id, 'contacts':contacts, 'phone_number':phone_number ,'address': address}]})
	else:
		return jsonify({'code':3,'message':'还没有添加收货地址'})

@api.route('/add_address', methods=['POST'])
@login_check
def add_address():
	userid	 = g.current_user.id
	contacts = request.get_json().get('contacts')
	phone_number = request.get_json().get('phone_number')
	address = request.get_json().get('address')
	default = request.get_json().get('default')

	if int(default) == 1:
		addressd = Address.query.filter_by(userid = userid, default = default).first()
		if addressd:
			addressd.default = 0;
			try:
				db_session.add(addressd)
				db_session.commit()
			except Exception as e:
				print (e)
				db_session.rollback()
				return jsonify({'code': 0, 'message': '数据库错误'})


	addressa = Address( userid=userid, contacts=contacts, phone_number = phone_number, address = address, default = default)

	try:
		db_session.add(addressa)
		db_session.commit()		
	except Exception as e:
		print (e)
		db_session.rollback()
		return jsonify({'code': 0, 'message': '数据库错误'})
	db_session.close()

	return jsonify({'code' : 1, 'message': '添加成功'})

@api.route('/del_address', methods=['POST'])
@login_check
def del_address():
	id = request.get_json().get('id')

	delad = Address.query.filter_by(id = id).first();
	db_session.delete(delad)
	try:
		db_session.commit()
	except Exception as e:
		print (e)
		db_session.rollback()
		return jsonify({'code': 0, 'message': '数据库错误'})
	db_session.close()

	return jsonify({'code' : 1, 'message': '删除成功'})

@api.route('/setdf_address', methods=['POST'])
@login_check
def setdf_address():
	id = request.get_json().get('id')
	userid	 = g.current_user.id

	addressd = Address.query.filter_by(userid = userid, default = 1).first()
	if addressd:
		addressd.default = 0;
		try:
			db_session.add(addressd)
			db_session.commit()
		except Exception as e:
			print (e)
			db_session.rollback()
			return jsonify({'code': 0, 'message': '数据库错误'})

	setdefault = Address.query.filter_by(id = id).first()
	setdefault.default = 1;
	try:
		db_session.add(setdefault)
		db_session.commit()
	except Exception as e:
		print (e)
		db_session.rollback()
		return jsonify({'code': 0, 'message': '数据库错误'})

	return jsonify({'code' : 1, 'message': '设置默认成功'})

@api.route('/edit_Address', methods=['POST'])
@login_check
def edit_Address():
	id = request.get_json().get('id')
	userid	 = g.current_user.id
	contacts = request.get_json().get('contacts')
	phone_number = request.get_json().get('phone_number')
	address = request.get_json().get('address')
	default = request.get_json().get('default')

	if int(default) == 1:
		addressd = Address.query.filter_by(userid = userid, default = default).first()
		if addressd:
			if addressd.id != id:
				addressd.default = 0;
				try:
					db_session.add(addressd)
					db_session.commit()
				except Exception as e:
					print (e)
					db_session.rollback()
					return jsonify({'code': 0, 'message': '数据库错误'})


	editaddress = Address.query.filter_by(id = id).first()

	editaddress.contacts = contacts
	editaddress.phone_number = phone_number
	editaddress.address = address
	editaddress.default = default
	
	try:
		db_session.add(editaddress)
		db_session.commit()		
	except Exception as e:
		print (e)
		db_session.rollback()
		return jsonify({'code': 0, 'message': '数据库错误'})
	db_session.close()

	return jsonify({'code' : 1, 'message': '修改成功'})