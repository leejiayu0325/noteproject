from django.shortcuts import render
from django.db.models import Q
from django.conf import settings
from django.http import HttpResponse,HttpResponseBadRequest,HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

from linebot import LineBotApi, WebhookHandler,WebhookParser
from linebot.exceptions import InvalidSignatureError,LineBotApiError
from linebot.models import MessageEvent,TextSendMessage,PostbackAction,URIAction, MessageAction
from linebot.models import TemplateSendMessage, ButtonsTemplate,MessageTemplateAction,CarouselTemplate,CarouselColumn,StickerMessage

from mynote.models import Notedatas,BookandUrl,PredRecommendBook,Userlike,PersonalInformation,Creatuser
from crawl.findnote import NavInfo


line_bot_api = LineBotApi(settings.LINE_CHANNEL_TOKEN)
parse=WebhookParser(settings.LINE_CHANNEL_SECRET)
step=0
user_sletype=None
adm_superuser=None
adm_pw=None
def linebot_pbook(email):
    userinfo_instance = Creatuser.objects.filter(email=email).first()  
    userlike=Userlike.objects.filter(user=userinfo_instance)
    if len(userlike)<2:
        other=False
        p_book=Notedatas.objects.all().order_by('?')[:10]
    else:        
        other=True
        p_book=PredRecommendBook.objects.filter(user=userinfo_instance).select_related('bookurl').order_by('?')[:10]        
    return p_book,other
def get_note_type():
    datas=BookandUrl.objects.all()
    name=[]
    action=[]
    # MessageAction(label='選項1', text='選擇1')
    for i, d in enumerate(datas):
        if i == 19:
            break
        action.append(
            # MessageTemplateAction
            MessageAction(label=f'{d.urlname}',text=f'{d.urlname}'))
        name.append(d.urlname)
    
    return action,name
    # return actions
def get_columns(text,booktype="",searchkey=""):
    columns=[]
    order_by="watch" if text=="觀看人數" else "keep"
    
    if booktype!="":
        if booktype=="搜尋":            
            datas=Notedatas.objects.filter(Q(bookname__contains=searchkey)|Q(author__contains=searchkey)).order_by(f"-{order_by}")[:10]
        elif booktype=="會員":
            datas,other=linebot_pbook(email=text)
            if other:
                for data in datas:                    
                    columns.append(CarouselColumn(
                                text=f'分類：{data.bookurl.booktype}\n作者：{data.bookurl.author}\n觀看數：{data.bookurl.watch}\n收藏數：{data.bookurl.keep}',
                                title=data.bookurl.bookname,
                                thumbnail_image_url=data.bookurl.imageurl,
                                actions=[
                                    URIAction(label='前往小說', uri=data.bookurl.bookurl)
                                ]
                            ))
                
                return columns
        else:
            datas=Notedatas.objects.filter(Q(booktype__contains=booktype)).order_by(f"-{order_by}")[:10]
    else:        
        datas=Notedatas.objects.all().order_by(f"-{order_by}")[:10]

    for data in datas:
        columns.append(CarouselColumn(
                    text=f'分類：{data.booktype}\n作者：{data.author}\n觀看數：{data.watch}\n收藏數：{data.keep}',
                    title=data.bookname,
                    thumbnail_image_url=data.imageurl,
                    actions=[
                        URIAction(label='前往小說', uri=data.bookurl)
                    ]
                ))
       
    return columns
def temalatemessage():
    message=TemplateSendMessage(
                                alt_text='推薦',
                                template=ButtonsTemplate(
                                    title='推薦',
                                    text='第一步：請選擇分類',
                                    actions=[                                                    
                                        MessageTemplateAction(
                                            label='觀看人數前10名',
                                            text='觀看人數',
                                        ),
                                        MessageTemplateAction(
                                            label='收藏人數前10名',
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
    return message
    
# Create your views here.
@csrf_exempt    
def callback(request):
    global step,user_sletype,adm_superuser,adm_pw
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
            # while True:
            if isinstance(event.message, StickerMessage):  # 處理貼圖訊息
                    step=0
                    tempmessage=temalatemessage()
                    message=TextSendMessage(text="接收到貼圖，重新開始...."),tempmessage
                    step+=1
                    line_bot_api.reply_message(event.reply_token,message) 
            elif isinstance(event,MessageEvent):  
                text=event.message.text
                action,name=get_note_type()
                if text=="更新20241002":
                    adm_superuser="更新20241002"
                    step=90

                if adm_superuser=="更新20241002" and step==90:
                    if text=="getdatasnewinfo":                        
                        step=0                        
                        NavInfo().alltypeurl()
                        adm_superuser=None                        
                    if text=="離開" or text.lower()=="exit":
                        print(2)
                        step=0
                        adm_superuser=None
                        message = TextSendMessage(text="輸入任一鍵重新開始....")
                    else:
                        if step==90:                            
                            message = TextSendMessage(text="輸入關鍵字，離開則輸入(exit)")
                        else:                            
                            message = TextSendMessage(text="更新完畢，輸入任一鍵重新開始....")
                else:
                    try:
                        if text=="離開" or text.lower()=="exit":
                            step=0
                            message=temalatemessage()
                                        
                            step+=1
                        else:
                            if step==0:
                                message=temalatemessage()
                                        
                                step+=1
                            elif text=="書本分類" and step==1:                        
                                columns=[]             
                                for i,k in enumerate(action):                            
                                    if (i+1)%3==0:
                                        columns.append(
                                            CarouselColumn(
                                                text=f'第二步：選擇{i-1}:{i+1}',
                                                actions=action[i-2:i+1]                                        
                                            )
                                        )
                                carousel_template = CarouselTemplate(columns=columns)

                                message = TemplateSendMessage(alt_text='書本分類', template=carousel_template)
                                step+=1
                            elif step==1:
                                if text!="其他":                            
                                    columns=get_columns(text,booktype="")
                                    carousel_template = CarouselTemplate(columns=columns)                                                    
                                    message=TemplateSendMessage(alt_text='小說推薦', template=carousel_template),TextSendMessage(text="輸入任一鍵重新開始....")
                                    step=0
                                    
                                else:
                                    message=TemplateSendMessage(
                                                alt_text='推薦',
                                                template=ButtonsTemplate(
                                                    title='推薦與搜尋',
                                                    text='第二步：請選擇分類',
                                                    actions=[                                                    
                                                        MessageTemplateAction(
                                                            label='會員推薦',
                                                            text='會員推薦',
                                                        ),
                                                        MessageTemplateAction(
                                                            label='搜尋',
                                                            text='搜尋',
                                                        )
                                                    ]
                                                )
                                            )                   
                                    step=7
                            elif step==2:
                                user_sletype=text
                                message=TemplateSendMessage(
                                                alt_text='選擇排序',
                                                template=ButtonsTemplate(
                                                    title='排序',
                                                    text='第三步：請選擇排序的依據',
                                                    actions=[
                                                        MessageTemplateAction(
                                                            label='觀看數',
                                                            text='觀看人數',
                                                        ),
                                                        MessageTemplateAction(
                                                            label='收藏數',
                                                            text='收藏人數',
                                                        ),                                                
                                                    ]
                                                )
                                            )
                                        
                                step+=1
                            elif step==3:                        
                                columns=get_columns(text,booktype=user_sletype)
                                carousel_template = CarouselTemplate(columns=columns)                                                    
                                message=TemplateSendMessage(alt_text='小說推薦', template=carousel_template),TextSendMessage(text="輸入任一鍵重新開始....")
                                step=0
                            elif step==7:
                                if text=="會員推薦":
                                    chtext="第三步：請輸入會員帳號(email)"                            
                                    message = TextSendMessage(text=chtext)
                                    step=7.5
                                else:
                                    searchtext="第三步：請輸入要搜尋的作者/書名"                            
                                    message = TextSendMessage(text=searchtext)
                                    step=8
                            elif step==7.5:
                                userinfo_instance = Creatuser.objects.filter(email=text).first()                
                                sorse=PersonalInformation.objects.filter(email=userinfo_instance)

                                if sorse:
                                    columns=get_columns(text,booktype="會員")
                                    carousel_template = CarouselTemplate(columns=columns)
                                    message=TemplateSendMessage(alt_text='會員-小說搜尋', template=carousel_template),TextSendMessage(text="輸入任一鍵重新開始....")
                                    step=0
                                else:
                                    # 輸入任一鍵重新開始....
                                    message=TextSendMessage(text="輸入錯誤，沒有該會員，請先完成註冊～！"),TextSendMessage(text="請重新輸入或輸入「離開」重新開始....")
                                    step=7.5
                                
                            elif step==8:
                                columns=get_columns("觀看人數",booktype="搜尋",searchkey=text)
                                carousel_template = CarouselTemplate(columns=columns)                                                    
                                message=TemplateSendMessage(alt_text='小說搜尋', template=carousel_template),TextSendMessage(text="輸入任一鍵重新開始....")
                                step=0

                    except Exception as e:
                        print(e)
                        text = "輸入不正確，請重新輸入...."
                        message = TextSendMessage(text=text)
                        line_bot_api.reply_message(event.reply_token,message)
                
                line_bot_api.reply_message(event.reply_token,message)
        return HttpResponse()
    else:
        return HttpResponseBadRequest()
