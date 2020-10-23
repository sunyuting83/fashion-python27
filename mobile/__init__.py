# coding:utf-8
from flask import Blueprint

# 解决中文显示问题
import sys
import imp
imp.reload(sys)

api = Blueprint('mobile', __name__)

from mobile import main, auth, decorator, order, guestbook, silder, classify, productlist, product, ilike, contactus, helper, address, news, company, cart