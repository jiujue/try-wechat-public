# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings

import hashlib
import xmltodict
from copy import deepcopy
import time
import requests
import re





# Create your views here.

def wechat_Autu(timestamp, nonce):
    '''
    auth for wechat
    :param timestamp:
    :param nonce:
    :return: has1 result
    '''
    wechat_token = settings.WECHAT_TOKEN if settings.WECHAT_TOKEN != None else 'jiujue'
    argument = [str(timestamp), str(nonce), str(wechat_token)]
    argument.sort()
    has1_res = hashlib.sha1((''.join(argument)).encode()).hexdigest()

    return has1_res

def test(request):
    ''' dit path : /
    test server
    :param request:
    :return: None
    '''
    ip = request.META['REMOTE_ADDR']

    return render(request,'wechat/index.html',context={'ip':ip})



def wechat(request):
    '''
    web API services for wechat
    :param request:
    :return: response
    '''

    # wechat fixed argument for auth
    try:
        signature = request.GET['signature']
        timestamp = request.GET['timestamp']

    except Exception as e:
        signature = timestamp = nonce = None

    if request.method == 'GET':

        try:
            echostr = request.GET['echostr']
            nonce = str(request.GET['nonce']).split(' HTTP')[0]
        except Exception as e:
            echostr = None

        if None in [signature, timestamp, nonce, echostr]:
            return HttpResponse('refusal accept connect')

        # auth
        if wechat_Autu(timestamp=timestamp, nonce=nonce) == signature:
            return HttpResponse(echostr)

        return HttpResponse('signature have difference')

    # nonauth request of wechat
    elif request.method == 'POST':
        # print('have post connect')
        #
        # return HttpResponse('success')

        print('*'*10,'have post to connect---')
        xml_str = request.body
        print('8'*8,xml_str)
        xml_dict = xmltodict.parse(xml_str)
        print('/n/n/n/n------------------------')
        print('request xml_dict:',xml_dict)
        if not xml_dict :
            return HttpResponse('success')
        '''message sample:
        <xml>
          <ToUserName><![CDATA[toUser]]></ToUserName>
          <FromUserName><![CDATA[fromUser]]></FromUserName>
          <CreateTime>12345678</CreateTime>
          <MsgType><![CDATA[text]]></MsgType>
          <Content><![CDATA[你好]]></Content>
        </xml>
        '''

        response_content = xml_dict.get('xml').get('Content')
        try:
            if response_content == '首页':
                response_content = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid={appid}&redirect_uri={redirect_url}&response_type=code&scope=snsapi_userinfo&state=STATE#wechat_redirect' \
                    .format(appid=settings.WECHAT_APPID, redirect_url=settings.REDIRECT_URL)
            elif response_content.endswith('吗？'):
                response_content = response_content.split('吗？')[0] + '！'
            elif response_content.endswith('！'):
                response_content = response_content.split('！')[0] + '吗？'
            else:
                response_content = xml_dict.get('xml').get('Content')+'/::)'
        except:
            response_content = '....'


        if xml_dict['xml']['MsgType'] == 'text':
            xml_dict = xml_dict.get('xml')
            response_dict = {
                    "xml": {
                        "ToUserName": xml_dict.get("FromUserName"),
                        "FromUserName": xml_dict.get("ToUserName"),
                        "CreateTime": int(time.time()),
                        "MsgType": "text",
                        "Content": response_content
                    }
                }

            response_xml_str = xmltodict.unparse(response_dict)

            print('response xml str:',response_xml_str)

            return HttpResponse(str(response_xml_str).encode())
        else:
            return HttpResponse('success')

    else:
        return HttpResponse('illegal request mode ')

# /wechat/index
def index(request):
    """让用户通过微信访问的网页页面视图"""
    # 从微信服务器中拿去用户的资料数据
    # 1. 拿去code参数
    print('--',request.GET)
    code = request.GET["code"]
    if not code:
        print(' defect code argu')
        return  HttpResponse("缺失code参数")

    # 2. 向微信服务器发送http请求，获取access_token
    url = "https://api.weixin.qq.com/sns/oauth2/access_token?appid={appid}&secret={secret}&code={code}&grant_type=authorization_code" \
          .format (appid=settings.WECHAT_APPID, secret=settings.WECHAT_SECRET, code=code)

    # 使用urllib2的urlopen方法发送请求
    # 如果只传网址url参数，则默认使用http的get请求方式, 返回响应对象
    response = requests.get(url)

    # 获取响应体数据,微信返回的json数据
    resp_dict = response.json()

    print('===',resp_dict)

    if 'access_token' in resp_dict:
        settings.SECC_TOKEN = resp_dict['access_token']

    # # 提取access_token
    # if "errcode" in resp_dict:
    #     return HttpResponse("获取access_token失败")

    # access_token = resp_dict.get("access_token")
    open_id = resp_dict.get("openid")  # 用户的编号

    # 3. 向微信服务器发送http请求，获取用户的资料数据
    url = "https://api.weixin.qq.com/sns/userinfo?access_token=%s&openid=%s&lang=en" \
          % (settings.SECC_TOKEN, open_id)

    response = requests.get(url)

    # 读取微信传回的json的响应体数据

    user_dict_data = response.json()

    if "errcode" in user_dict_data:
        return HttpResponse("获取用户信息失败")
    else:
        # 将用户的资料数据填充到页面中
        print('--> obtain user info:',user_dict_data)
        re_res = re.match(r'(.*)/(0|46|64|96|132)+$', user_dict_data['headimgurl']).groups()
        user_dict_data['headimgurl_size'] = re_res[1] if re_res[1] != '0' else 640
        for key in user_dict_data:
            if user_dict_data[key] == '':
                user_dict_data[key] = '未知/未填写'

            if key== 'nickname':
                user_dict_data[key] =  user_dict_data[key].encode('iso-8859-1').decode('utf-8')

            if key== 'sex':
                user_dict_data[key] = '男' if  user_dict_data[key] == 1  else '女'
        print('<--> obtain user info:',user_dict_data)
        return render(request,'wechat/user-info.html',context={'user':user_dict_data})
#
