import json
import logging
import os
from time import ctime

import requests
from bs4 import BeautifulSoup
from django.http import FileResponse
from django.shortcuts import render, HttpResponse

from BotServer import settings
from BotServer.settings import PROXIES, BASE_DIR
from wlserver import models
# Create your views here.
from .commons import *

with open(os.path.join(BASE_DIR, "static", "faq.txt"), "w", encoding="utf8") as f:
    for ques in models.FAQ.objects.values():
        f.write(json.dumps(ques, ensure_ascii=False))
        f.write("\n")
first_msg = open(os.path.join(BASE_DIR, "static", "first_msg.txt"), "r", encoding="utf8").read()
print(first_msg)


class ModelUtils:
    @staticmethod
    def _get_user_info(username, app_flag=None):
        if not app_flag:
            return models.Info.objects.filter(customer_alias=username)
        else:
            return models.Info.objects.filter(customer_alias=username, app_flag=app_flag)


class ReplyUtils(object):
    @staticmethod
    def get_detail(user_name, app_flag):
        """
        根据用户名去数据库查找信息
        :param user_name:
        :return: dict：用户信息的字典
        """
        info_models = models.Info.objects.get(customer_alias=user_name, app_flag=app_flag)
        return json.dumps(info_models.__dict__)

    @staticmethod
    def getPM25(cityname):
        """
        输入city名，到site网址发送请求，返回城市名字+AQI指数+空气质量+空气质量描述的字符串
        :param cityname: 城市的名字
        :return: str（城市名字+AQI指数+空气质量+空气质量描述的字符串）

        """
        site = 'http://www.pm25.com/' + cityname + '.html'
        page = requests.get(site, proxies=PROXIES).content.decode()
        html = page
        soup = BeautifulSoup(html, "html.parser")
        city = soup.find(class_='bi_loaction_city')  # 城市名称
        aqi = soup.find("a", {"class", "bi_aqiarea_num"})  # AQI指数
        quality = soup.select(".bi_aqiarea_right span")  # 空气质量等级
        result = soup.find("div", class_='bi_aqiarea_bottom')  # 空气质量描述
        output = city.text + u'AQI指数：' + aqi.text + u'\n空气质量：' + quality[0].text + result.text
        print(output)
        print('*' * 20 + ctime() + '*' * 20)
        return output

    @staticmethod
    def tuling123(msg):
        """

        :param msg:
        :return:
        """
        url = "http://www.tuling123.com/openapi/api"
        info = msg
        key = "11d8a7c5e9564a3fa5217bdd9a868778"
        data = {u"key": key, 'info': info}
        r = requests.get(url, params=data, proxies=PROXIES)
        ret = json.loads(r.text)
        return (ret['text'])

    # server
    @staticmethod
    def get_reply_from_msg(msg, app_flag):
        """
        对分词后的消息进行匹配
        :param msg: 接受分词后的消息
        :return: 生成对应的回复
        """
        reply = ""
        # 进行匹配
        faq_query = models.FAQ.objects.filter(questions__contains=msg)  # sql 寻找
        if faq_query:
            reply = faq_query[0].answers
        elif msg == 'pm25':
            reply = ReplyUtils.getPM25("nanjing")
        elif msg == 'angry':
            reply = "contact_human"
        else:
            reply = ReplyUtils.tuling123(msg)
        return reply


def get_report(req):
    """
    查询报告并通过文件形式返回
    :param req:
    :return:
    """
    if req.method == "GET":
        report_name = req.GET.get("report_name")
        file_path = os.path.join(settings.BASE_DIR, "static/reports", report_name)
        if not os.path.exists(file_path):
            report_name = "report-1234.pdf"
            file_path = os.path.join(settings.BASE_DIR, "static/reports", report_name)

        file = open(file_path, 'rb')
        response = FileResponse(file)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="%s"' % (report_name)
        return response


def get_reply(req):
    """

    :param req: request
    :return: 返回对应请求的内容
    """
    reply = {}
    if req.method == "GET":
        # 1. 拿到用户名, 内容
        msg = req.GET.get("content")
        user_name = req.GET.get("user_name")
        app_flag = req.GET.get("app_flag")
        logger = logging.getLogger('django')
        logger.info("This is an error msg")
        # 2. 取数据库中匹配对应的相关个人信息，返回，
        user_query = ModelUtils._get_user_info(user_name, app_flag)
        all_info = user_query[0].__dict__ if user_query else {}
        all_info.pop("_state") if all_info else None
        # 3. 加入回复内容
        all_info.update({"reply": ReplyUtils.get_reply_from_msg(msg, app_flag)})
        return HttpResponse(json.dumps(all_info, ensure_ascii=False))


def get_user_info(req):
    if req.method == "GET":
        ca = req.GET.get("user_name")
        app_flag = req.GET.get("app_flag")
        usr_querys = ModelUtils._get_user_info(username=ca, app_flag=app_flag if app_flag else None)
        user_list = []
        if not usr_querys:
            return HttpResponse("user unregistered!")
        for usr_obj in usr_querys:
            user_list.append({"customer_alias": usr_obj.customer_alias,
                              "company": usr_obj.company,
                              "plb": usr_obj.plb,
                              "cs_name": usr_obj.cs_name,
                              "app_flag": usr_obj.get_app_flag_display(), })
        return HttpResponse(json.dumps(user_list, ensure_ascii=False))


def get_faqs_json(req):
    """
    返回所有问题---->FAQ.txt
    :param req:
    :return:
    """
    if req.method == "GET":
        file_path = os.path.join(settings.BASE_DIR, "static/faq.txt")
        file = open(file_path, 'rb')
        response = FileResponse(file)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="%s"' % ("faq.txt")
        return response


def get_first_msg(req):
    global first_msg
    if req.method == "GET":
        first_msg = first_msg
        return HttpResponse(first_msg)
