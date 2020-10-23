# coding:utf-8
from flask import Flask, render_template, redirect, session, url_for, request, g, flash, abort, jsonify, make_response
from flask_wtf import FlaskForm
from wtforms import TextField, BooleanField, PasswordField, SubmitField, SelectField, HiddenField
from wtforms.validators import Required, Email, Length
from model import Company, and_, or_, desc, asc, func, db_session
from manage import api
from html.parser import HTMLParser
import cgi




# 公司相关
@api.route('/company/<int:getid>', methods=['GET', 'POST'])
@api.route('/company/<int:getid>/', methods=['GET', 'POST'])
def company(getid):

	if getid == 1:
		pagename = "company"
	else:
		pagename = "company_plan"
	company = db_session.query(Company).filter(Company.id == getid).\
		with_entities(Company.id, Company.title, Company.content).first()

	html_parser = HTMLParser.HTMLParser()
	html_con = company.content
	content = html_parser.unescape(html_con)

	return render_template(
		"company.html",
		thisid = company.id,
		thistitle = company.title,
		thiscontent = content,
		pagename = pagename)
	db_session.close()

# 保存公司信息
@api.route('/save_company', methods=['GET', 'POST'])
def save_company():
	getid = request.form.get('id')
	getcontent = cgi.escape(request.form.get('editor'))

	db_session.query(Company).filter(Company.id == getid).update(
				{
					Company.content : getcontent
				})
	db_session.commit()
	db_session.close()
	return redirect('/manage/company?id='+getid)