# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings

import hashlib
import xmltodict
from copy import deepcopy
import time


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

    return HttpResponse('<html><body><h1>It is work</h1></body></html>')

def test(request):
    '''
    test server
    :param request:
    :return: None
    '''

    print(request.GET['name'])

    wechat_token = settings.WECHAT_TOKEN

    return HttpResponse(wechat_token + request.GET['name'])


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
        nonce = str(request.GET['nonce']).split(' HTTP')[0]
    except Exception as e:
        signature = timestamp = nonce = None

    if request.method == 'GET':

        try:
            echostr = request.GET['echostr']
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
        xml_str = request.POST
        xml_dict = xmltodict.parse(xml_str)
        if not xml_dict :
            return HttpResponse('success')
        '''message sample:
        <xml>
          <ToUserName>  <![CDATA[toUser]]>   </ToUserName>
          <FromUserName>  <![CDATA[fromUser]]>  </FromUserName>
          <CreateTime> 1348831860  </CreateTime>
          <MsgType>  <![CDATA[text]]>  </MsgType>
          <Content>  <![CDATA[this is a test]]>  </Content>
          <MsgId>  1234567890123456   </MsgId>
        </xml>
        '''
        response_dict =  dict()

        response_dict['xml']['ToUserName'] = xml_dict['xml']['FromUserName']
        response_dict['xml']['FromUserName'] = xml_dict['xml']['ToUserName']
        response_dict['xml']['CreateTime'] = int(time.time())
        response_dict['xml']['Content'] = xml_dict['xml']['Content']
        response_dict['xml']['MsgType'] = xml_dict['xml']['MsgType']
        response_dict['xml']['MsgId'] = xml_dict['xml']['MsgId']

        response_xml_str = xmltodict.unparse(response_dict)

        return HttpResponse(response_xml_str)

    else:
        return HttpResponse('illegal request mode ')
