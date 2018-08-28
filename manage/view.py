# coding:utf-8
from flask import Flask, render_template, redirect, session, url_for, request, g, flash, abort, jsonify, make_response
from manage import api
from model import Manage



@api.route('/')
def index():

	return render_template("index.html",
		title = '后台管理系统', active='true')
