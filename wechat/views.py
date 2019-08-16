# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings

import hashlib

# Create your views here.

def test(request):

    print(request.GET['name'])

    wechat_token = settings.WECHAT_TOKEN

    return HttpResponse(wechat_token+request.GET['name'])

def wechat_auth(request):

    try :
        signature = request.GET['signature']
        timestamp = request.GET['timestamp']
        nonce = str(request.GET['nonce']).split(' HTTP')[0]

        echostr = request.GET['echostr']
    except Exception as e:
        signature = timestamp = nonce = echostr = None


    if None in  [signature,timestamp,nonce,echostr] :
        return HttpResponse('refusal accept connect')


    wechat_token = settings.WECHAT_TOKEN if settings.WECHAT_TOKEN != None else 'jiujue'
    argument = [timestamp,nonce,wechat_token]
    has1_res = hashlib.sha1( ''.join(   argument.sort().encode()  )   ).hexdigest()

    if has1_res == signature:
        return HttpResponse(echostr)

    return HttpResponse('signature have difference')
