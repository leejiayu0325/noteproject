from django.shortcuts import render
from django.db.models import Q
from django.conf import settings
from django.http import HttpResponse,HttpResponseBadRequest,HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

from linebot import LineBotApi, WebhookHandler,WebhookParser
from linebot.exceptions import InvalidSignatureError,LineBotApiError
from linebot.models import MessageEvent,TextSendMessage,PostbackAction,URIAction, MessageAction, TemplateSendMessage, ButtonsTemplate,MessageTemplateAction,CarouselTemplate,CarouselColumn

from mynote.models import Notedatas,BookandUrl
line_bot_api = LineBotApi(settings.LINE_CHANNEL_TOKEN)
parse=WebhookParser(settings.LINE_CHANNEL_SECRET)
step=0

def get_note_type():
    datas=BookandUrl.objects.all()
    actions=[]
    for data in datas:
        actions.append(MessageTemplateAction(
                            label=f'{data.urlname}',
                            text=f'{data.urlname}',
                        ),)
    return actions
def get_columns(text,booktype=""):
    columns=[]
    order_by="watch" if text=="觀看人數" else "keep"
    print(order_by)
    if booktype!="":
        datas=Notedatas.objects.filter(Q(booktype__contains=booktype)).order_by(f"-{order_by}")[:10]
    else:        
        datas=Notedatas.objects.all().order_by(f"-{order_by}")[:10]

    for data in datas:
        columns.append(CarouselColumn(
                    text=f'作者：{data.author}',
                    title=data.bookname,
                    thumbnail_image_url=data.imageurl,
                    actions=[
                        URIAction(label='前往小說', uri=data.bookurl)
                    ]
                ))
    return columns
    
# Create your views here.
@csrf_exempt    
def callback(request):
    global step
    if request.method=='POST':
        signature=request.META['HTTP_X_LINE_SIGNATURE']
        body=request.body.decode('utf-8')
        try:
            events=parse.parse(body,signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()
        for event in events:
            if isinstance(event,MessageEvent):                
                text=event.message.text
                print(text)
                try:
                    if step==0:
                        print(step)
                        print(text)
                        message=TemplateSendMessage(
                                        alt_text='Buttons template',
                                        template=ButtonsTemplate(
                                            title='搜尋',
                                            text='請選擇要搜尋的分類',
                                            actions=[
                                                MessageTemplateAction(
                                                    label='觀看人數',
                                                    text='觀看人數',
                                                ),
                                                MessageTemplateAction(
                                                    label='收藏人數',
                                                    text='收藏人數',
                                                ),
                                                MessageTemplateAction(
                                                    label='書本分類',
                                                    text='書本分類',
                                                ),
                                                MessageTemplateAction(
                                                    label='其他',
                                                    text='其他',
                                                ),
                                            ]
                                        )
                                    )
                                
                        step+=1
                    elif step==1:
                        print(step)
                        print(text)
                        if text=="觀看人數":
                            usertext="觀看人數"
                            columns=get_columns(usertext,booktype="")
                        elif text=="收藏人數":
                            usertext="收藏人數"
                            columns=get_columns(usertext,booktype="")
                        elif text=="書本分類":
                            actions=get_note_type()
                            message=TemplateSendMessage(
                                        alt_text='Buttons template',
                                        template=ButtonsTemplate(
                                            title='搜尋',
                                            text='請選擇書本的分類',
                                            actions=actions
                                        )
                                    )
                                
                            step+=1                
                        elif text=="其他":
                            # 搜尋作者或書名
                            usertext=""
                            columns=get_columns(usertext,booktype="")
                            carousel_template = CarouselTemplate(columns=columns)
                            
                        message=TemplateSendMessage(alt_text='輪播樣板', template=carousel_template)
                    elif step==2:
                        print(step)
                        print(text)
                except Exception as e:
                    print(e)
                    text = "輸入不正確，請重新輸入...."
                    message = TextSendMessage(text=text)
                #if event.message.text=='hello':
                # line_bot_api.reply_message(
                #     event.reply_token,
                #     #TextSendMessage(text='hello world')
                #     TextSendMessage(text=event.message.text)
                # )
                line_bot_api.reply_message(event.reply_token,message)
        return HttpResponse()
    else:
        return HttpResponseBadRequest()
