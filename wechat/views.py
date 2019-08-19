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

    return HttpResponse('<html><body><h1 style="margin: 20px auto;color: gold;">It is work</h1></body></html>')



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
        if xml_dict['xml']['MsgType'] == 'text':
            xml_dict = xml_dict.get('xml')
            response_dict = {
                    "xml": {
                        "ToUserName": xml_dict.get("FromUserName"),
                        "FromUserName": xml_dict.get("ToUserName"),
                        "CreateTime": int(time.time()),
                        "MsgType": "text",
                        "Content": xml_dict.get("Content")
                    }
                }

            response_xml_str = xmltodict.unparse(response_dict)

            print('response xml str:',response_xml_str)

            return HttpResponse(str(response_xml_str).encode())
        else:
            return HttpResponse('success')

    else:
        return HttpResponse('illegal request mode ')
