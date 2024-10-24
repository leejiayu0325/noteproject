from django.shortcuts import render,redirect,HttpResponse
from django.urls import reverse
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.core.mail import send_mail
# from django.views.generic import TemplateView
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_protect
from django.db.models import Q
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.hashers import make_password,check_password
from mynote.forms import LoginForm,ForgetForm,PersonForm,ProfileForm,RegisterForm,OldpwdForm,NewpwdForm
from mynote.models import Creatuser,Notedatas,Userlike,PersonalInformation,Profile,PredRecommendBook,DonloadBookandUser,NoteLisData,NotePath
from crawl.findnote import NavInfo,crawNote,list_image_files,mkdir,get_context_pbook,NoteLis,listNoteDowl
# from crawl.findnote import SiTo,SiTo_dowlond

import random
import urllib.parse
import os
import json
# Create your views here.
locurl="http://127.0.0.1:8000"
def index(request):    
    if request.method=="POST":        
        response =redirect(reverse('index')) 
        return response    
        # return render(request,"index.html", {})
    else:       
        context={}       
        request.session["no_pbook"]=True     
        # 取前40名 
        topkeep=list(Notedatas.objects.all().order_by("-keep")[:40])        
        topkeep1=list(Notedatas.objects.all().order_by("-keep")[40:80])  
        topwatch=list(Notedatas.objects.all().order_by("-watch")[:40])        
        topwatch1=list(Notedatas.objects.all().order_by("-watch")[40:80])        
        # 前40名中隨機10
        randomkeeptop=random.sample(topkeep,10)
        rkeeptop1=random.sample(topkeep1,10)
        randomwatchtop=random.sample(topwatch,10)
        rwatchtop=random.sample(topwatch1,10)
        if 'loginok' in request.session:
            if "useremail" in request.session:
                email=request.session["useremail"]
                # 取得預測書本
                pagetype="index"
                p_book=get_context_pbook(request,email,pagetype)   

                if not request.session["no_pbook"]:
                    # 有預測
                    wp_book=kp_book=list(p_book.order_by("?"))                            
                else:
                    # 沒有預測
                    wp_book=list(p_book.order_by('-watch')[:80])        
                    kp_book=list(p_book.order_by('-keep')[:80])

                wp_book=random.sample(wp_book,10) 
                kp_book=random.sample(kp_book,10)  
                context["wp_book"]=wp_book
                context["kp_book"]=kp_book
    
        context["keeptop"]=randomkeeptop
        context["keeptop1"]=rkeeptop1
        context["watchtop"]=randomwatchtop
        context["watchtop1"]=rwatchtop
        return render(request,"index.html", context)
# 登入
@csrf_protect
def login(request):
    if request.method=="POST":
        email = request.POST.get("email")  # 從 POST 請求中獲取 email        
        # 在 session 中設置 useremail 信息，登入失敗從session取得信箱，使用者可避免重複輸入  
        request.session['useremail'] = email
        # 透過forms.py檢查表單內容 
        myLoginForm=LoginForm(request.POST)
        if myLoginForm.is_valid():
            myLoginForm.cleaned_data['email']
            myLoginForm.cleaned_data['password']
            # 在 session 中設置 loginok 信息                        
            request.session['loginok'] = "ok"
            response =redirect(reverse('index')) 
            
            # 強制頁面刷新
            response['Refresh'] = '0;url=/index'
            # 進行使用者喜好預測
            pagetype="login"
            get_context_pbook(request,email,pagetype)
            # 建立使用者個人資訊資料庫
            userinfo_instance = Creatuser.objects.filter(email=email).first()                
            sor=PersonalInformation.objects.filter(email=userinfo_instance).first()                    
            if not sor:
                PersonalInformation(email=userinfo_instance).save()
            # 建立使用者擺放個人照片資料夾
            filename=email.split("@")[0] 
            mkdir(filename) 
            # 個人圖片的副檔名            
            fileEx=list_image_files(filename)           
            request.session["fileEx"]=fileEx
            return response
        else:            
            context={}
            context["form"]=myLoginForm
            if 'useremail' in request.session:                
                context["emailinput"]=request.session['useremail']
            return render(request,"login.html", context)
    else:
        emailinput=""
        context={}
        if 'useremail' in request.session:
            emailinput=request.session['useremail']
        
        context["emailinput"]=emailinput
        return render(request,"login.html", context)
# 登出
@csrf_protect    
def logout(request):
    if 'loginok' in request.session:
        request.session.flush()    
    response = redirect(reverse('index'))    
    # 強制頁面刷新
    response['Refresh'] = '0;url=/index'
    
    return response
# 註冊
@csrf_protect  
def register(request):
    context={}
    if request.method=="POST":      
        request.session["username"]=request.POST.get("name")
        request.session["useremail"]=request.POST.get("email")
        myregi=RegisterForm(request.POST)
        
        if myregi.is_valid():
            name=myregi.cleaned_data['name']       
            email=myregi.cleaned_data['email']     
            password=myregi.cleaned_data['password']  
            # myregi.cleaned_data['checkpw']     
            # print(name,email,password)
            rdnumb=''.join(str(random.randint(0, 9)) for _ in range(4))            
            encrypted_password = make_password(password)
            Creatuser(
                user=name,
                email=email,
                password=encrypted_password,
                randomnumber=rdnumb,
                chickemail=False
            ).save()
            # 發送郵件
            # http://127.0.0.1:5000/remail?username={user}&ranStr={random_str}
            a_url=locurl+f"/note/checkemail?name={name}&email={email}&number={rdnumb}"            
            mesage='''感謝您對[ N x N ]的支持與愛護。\n以下是驗證會員帳號之操作流程。
            \n請點擊以下連結，進行電子郵件地址的驗證手續。\n
            <a href="'''+f"{a_url}"+'''" style="text-decoration: none; color: blue;">會員帳號驗證</a>'''
            send_mail("[N x N] 會員帳號驗證信", "comment tu vas?", "cji3xu06@gmail.com", [email], html_message=mesage)
            response = redirect('creatok')
            return response
        else:            
            context["form"]=myregi
            
            if 'useremail' in request.session and "username" in request.session:                
                context["emailinput"]=request.session['useremail']    
                context["nameinput"]=request.session['username']   
        return render(request,"register.html", context)
           
        
    else:        
        nameinput=""
        emailinput=""        
        context={}        
        # 取得session
        if 'username' in request.session and 'useremail' in request.session:
            nameinput=request.session['username']
            emailinput=request.session['useremail']
            
        context["nameinput"]=nameinput
        context["emailinput"]=emailinput
        return render(request,"register.html", context)
    
# 使用者驗證後更新資料庫並跳轉到登入頁面
def checkemail(request):
    name=request.GET["name"]    
    email=request.GET["email"]    
    number=request.GET["number"]
    
    sorex=Creatuser.objects.filter(user=name)
    for i in sorex:
        if i.email == email:
            if i.randomnumber == number:
                i.chickemail=True
                i.save()
                messages.success(request, '註冊流程成功，開始登入吧！')

    return redirect(reverse('login'))

# 跳轉註冊成功頁面
# class CreatOk(TemplateView):
# 	template_name="ok_register.html" 
# 使用了以下方法直接跳轉，省去上面的動作
# url("creatok/", TemplateView.as_view(template_name='ok_register.html'), name='creatok'),
#    

# 忘記密碼
def forget(request):
    if request.method=="POST":
        # 取得信箱並設session
        email=request.POST.get("email")
        request.session['useremail']=email

        # 使用表單驗證email存在與否，及是否驗證
        forgetForm=ForgetForm(request.POST)
        
        if forgetForm.is_valid():
            forgetForm.cleaned_data['email']            
            a_url=locurl+"/note/changepsw/"
            mesage='''有人試圖對您的[ N x N ]密碼進行變動。<br>
            請點擊以下連結，進行密碼變更。<br>
            <a href="'''+f"{a_url}"+'''" style="text-decoration: none; color: blue;">更改密碼</a><br>
            若非本人，請忽略此信。'''
            send_mail("[N x N] 會員密碼更改", "", "cji3xu06@gmail.com", [email], html_message=mesage)
            response = redirect('ok_chpsw')
            
            return response
        
        # 驗證有問題時返回忘記密碼頁面，並傳error
        else:            
            context={}
            context["form"]=forgetForm
            if 'useremail' in request.session:                
                context["emailinput"]=request.session['useremail']    
            return render(request,"forget.html", context)
    else:
        emailinput=""
        context={}
        if 'useremail' in request.session:
            emailinput=request.session['useremail']
        
        context["emailinput"]=emailinput
        return render(request,"forget.html", context)
    
# 使用者點擊信件後更改密碼
def changepsw(request):
    context={}
    if request.method=="POST":        
        # 判斷有沒有 useremail ，若無則導回更改密碼頁面
        if "useremail" in request.session:
            email=request.session["useremail"]  
            context["email"]=email

            mypwdf=NewpwdForm(request.POST)
            if mypwdf.is_valid():                
                password=mypwdf.cleaned_data["password"]
                
                sore=Creatuser.objects.filter(email=email).first()
                encrypted_password = make_password(password)
                sore.password=encrypted_password
                sore.save()
                messages.success(request, '密碼更新成功！')
                if "loginok" in request.session:
                    return redirect('index')
                else:
                    return redirect('login')
            else:
                context["form"]=mypwdf
                return render(request,"changepsw.html",context)
        else:
            return redirect('forget')
    else:  
        email=""        
        if  "useremail" not in request.session:
            return redirect('login')   
        else:
            email= request.session["useremail"]         
        return render(request,"changepsw.html",{"email":email})
# 透過會員區更改密碼
def oldpswchange(request): 
    if request.method=="POST":
        myoldpw=OldpwdForm(request.POST)
        if myoldpw.is_valid():
            myoldpw.cleaned_data["password"]
            myoldpw.cleaned_data["checkpw"]
            return redirect('changepsw')
        else:
            context={}
            if  "useremail" in request.session:
                context["email"]=request.session["useremail"]
            
            context["form"]=myoldpw
            return render(request,"changeoldpsw.html",context)        
    else:    
        email="" 
        if  "useremail" not in request.session:
            return redirect('member')   
        else:
            email= request.session["useremail"]
        print(email)
        return render(request,"changeoldpsw.html",{"email":email})
    
# 會員
def member(request):     
    context={}
    # 使用者更新資料
    if request.method=="POST":  
        print("PO~~~~~~~~~~")      
        nickname=request.POST.get("nickname")
        birthday=request.POST.get("birthday")
        phone=request.POST.get("phone")
        request.session["birthday"]=birthday
        picfilename=request.POST.get("picfilename")
        
        if "useremail" in request.session:        
            email=request.session["useremail"]
        
        # 判斷使用者是否按了上傳鈕
        if picfilename!=None:
            MyProfileForm = ProfileForm(request.POST, request.FILES)
            if MyProfileForm.is_valid():
                profile = Profile()
                profile.picfilename = MyProfileForm.cleaned_data["picfilename"]                
                profile.picture = MyProfileForm.cleaned_data["picture"]
                
                # print(profile.picture,type(str(profile.picture)))
                # request.session["fileEx"]=str(profile.picture).split(".")[-1]
                request.session["fileEx"]=str(profile.picture)
                profile.save()
                response = redirect(reverse('member'))
                # 強制頁面刷新
                response['Refresh'] = '0;url=/member'
                
                return response
            else:                           
                context["form"]=MyProfileForm            
                email=request.session["useremail"]   
                user=Creatuser.objects.filter(email=email).first()
                # 顯示使用者名字與姓名
                context["name"]=user.user
                context["email"]=email
                if "nickname" in request.session:
                    context["nickname"]=request.session["nickname"]
                if "birthday" in request.session:
                    context["birthday"]=request.session["birthday"]
                if "phone" in request.session:
                    context["phone"]=request.session["phone"]
                if "fileEx" in request.session:
                    context["fileEx"]=request.session["fileEx"]
                filename=email.split("@")[0]
                
                fileEx=list_image_files(filename)
                if fileEx:
                    request.session["fileEx"]=fileEx
                    request.session["nouser"]=False
                    context["user"]=filename
                    context["fileEx"]=fileEx
                else:
                    request.session["nouser"]=True
                    context["user"]="nouser"
                return render(request,"member.html", context)
        userinfo_instance = Creatuser.objects.filter(email=email).first()
        sor=PersonalInformation.objects.filter(email=userinfo_instance).first()
        personForm=PersonForm(request.POST)   
        if personForm.is_valid():
            if nickname!=None:
                sor.nickname=personForm.cleaned_data['nickname']
                
            if birthday!=None:                        
                sor.birthday=personForm.cleaned_data['birthday']
                
            if phone!=None:
                sor.phone=personForm.cleaned_data['phone']
            sor.save()
            response = redirect(reverse('member'))
                
            # 強制頁面刷新
            response['Refresh'] = '0;url=/member'
            
            return response
        # 驗證有問題時返回忘記密碼頁面，並傳error
        else:            
            context={}
            context["form"]=personForm            
            
            email=request.session["useremail"]   
            user=Creatuser.objects.filter(email=email).first()
            # 顯示使用者名字與姓名
            context["name"]=user.user
            context["email"]=email
            if "nickname" in request.session:
                context["nickname"]=request.session["nickname"]
            if "birthday" in request.session:
                context["birthday"]=request.session["birthday"]
            if "phone" in request.session:
                context["phone"]=request.session["phone"]
            
            
            filename=email.split("@")[0]            
            fileEx=list_image_files(filename)
            if fileEx:
                request.session["fileEx"]=fileEx
                request.session["nouser"]=False
                context["user"]=filename
                context["fileEx"]=fileEx
            else:
                request.session["nouser"]=True
                context["user"]="nouser"
            return render(request,"member.html", context)
        #  redirect(reverse('target_view', kwargs={'value': some_value}))

    else:    
        print("GE~~~~~~~~~~")      
        if "useremail" in request.session and "loginok" in request.session:        
            email=request.session["useremail"]   
                        
            # 取得預測書本
            pagetype="member"
            p_book=get_context_pbook(request,email,pagetype)
            context["p_book"]=p_book
            
            # 取得使用者資料
            user=Creatuser.objects.filter(email=email).first()
            # 顯示使用者名字與姓名
            context["name"]=user.user
            context["email"]=email

            # 使用者的資料夾
            filename=email.split("@")[0]  
            context["picfilename"]=filename            
            
            # 確認會員個人資訊
            userinfo_instance = Creatuser.objects.filter(email=email).first()
            sor=PersonalInformation.objects.filter(email=userinfo_instance).first()

            #   判斷暱稱
            if sor.nickname!=None:
                context["nickname"]=sor.nickname
                request.session["nickname"]=sor.nickname
                request.session["nicknameok"]=True
            else:
                if "nickname" in request.session:
                    del request.session["nickname"] 
                if "nicknameok" in request.session:
                    del request.session["nicknameok"] 
            #   判斷生日
            if sor.birthday!=None:    
                birthday=sor.birthday.isoformat()            
                context["birthday"]=birthday
                request.session["birthday"]=f"{birthday}"
                request.session["birthdayok"]=True
            else:
                if "birthdayok" in request.session:
                    del request.session["birthdayok"]
                if "birthday" in request.session:
                    del request.session["birthday"]
            #   判斷手機
            if sor.phone!=None:
                phone=sor.phone
                context["phone"]=phone
                request.session["phone"]=f"{phone}"
                request.session["phoneok"]=True
            else:
                if "phoneok" in request.session:
                    del request.session["phoneok"]
                if "phone" in request.session:
                    del request.session["phone"]
            # ---------------------------------
            # 需要確認檔案圖片存在與否
            # 若存在則建立session
            # 透過資料夾存在與否判斷使用者是否有上傳個人照           
            # ---------------------------------
            fileEx=list_image_files(filename)
            if fileEx:
                request.session["fileEx"]=fileEx
                request.session["nouser"]=False
                context["user"]=filename
                context["fileEx"]=fileEx
            else:
                request.session["nouser"]=True
                context["user"]="nouser"            
            
        return render(request,"member.html", context)

# 會員-創作區
def creation(request):
    print("創作區")
    return render(request,"creation.html", {})

# 會員-收藏區
def memberkeep(request):       
    if  "useremail" not in request.session: 
        return redirect('member')  
    else:
        booktype="會員收藏"    
        context=note_universal_template(request,booktype)
        return render(request,"memberkeep.html",context)

# 會員-下載區
def memberdowload(request):
    if  "useremail" not in request.session: 
        return redirect('member')  
    else:
        booktype="會員下載"    
        context=note_universal_template(request,booktype)
        return render(request,"memberdow.html",context)

# 建立小說資料庫
def creatdatas(request):
    if request.method=="POST":
        email=request.POST.get("email")
        paswd=request.POST.get("password")
        if email=="20241021@0947":
            if paswd=="crawl102109":
                # 建立連結清單
                # NavInfo().getnavmodel()
                NavInfo().alltypeurl()
                return render(request,"t1.html", {})    
            else:
                return render(request,"creatdatas.html", {"pswerror":"密碼錯誤"})    
        else:
            return render(request,"creatdatas.html", {"emailerror":"帳號錯誤"})            
    else:        
        return render(request,"creatdatas.html", {})

# 清空資料庫內容 ------測試用
def clear(request):    
    # a=Notedatas.objects.all()
    # print(len(a))
    # Notedatas.objects.all().delete()
    print(Notedatas.objects.count())
    return render(request,"t2.html", {})

# 紀錄收藏
def keep(request):
    if request.method == 'POST':        
        book_url = request.POST.get('book_url')                
        book_name = request.POST.get('book_name')   
        print(book_name) 
        if 'useremail' in request.session:
            useremail=request.session["useremail"]
        try:          
            userinfo_instance = Creatuser.objects.filter(email=useremail).first()  
            notedatas_instance = Notedatas.objects.filter(bookurl=book_url).first()
            Userlike(user=userinfo_instance,bookurl=notedatas_instance).save()
        except Exception as e:
            print(e)
    return JsonResponse({'error': 'POST 請求缺少 book_url 參數'})

# 移除收藏
def dkep(request):    
    if request.method == 'POST':
        if 'useremail' in request.session:
            user=request.session["useremail"]
        
        book_url = request.POST.get('book_url')   
        userinfo_instance = Creatuser.objects.filter(email=user).first()       
        urlinfo=Notedatas.objects.get(bookurl=book_url)
        d_kep=Userlike.objects.get(user=userinfo_instance, bookurl=urlinfo)
        
        if d_kep:
            d_kep.delete()
            return JsonResponse({'message': '刪除成功'}, status=200)
        else:
            return JsonResponse({'error': '該用戶未收藏此書本'}, status=404)

    return JsonResponse({'error': '不支持的請求方法'}, status=405)

# 下載 需要上線測試
def download(request):
    if request.method == 'POST':        
        book_url = request.POST.get('book_url')
        book_name = request.POST.get('book_name')
        # note="hahahaha"
        file_name = f"{book_name}.txt"
        
        if 'useremail' in request.session:
            useremail=request.session["useremail"]
        # 紀錄下載資訊 
        try:
            userinfo_instance = Creatuser.objects.filter(email=useremail).first()  
            notedatas_instance = Notedatas.objects.filter(bookurl=book_url).first()
            DonloadBookandUser(user=userinfo_instance,bookurl=notedatas_instance).save()
        except Exception as e:
            print(e)

        author=Notedatas.objects.filter(bookurl=book_url).first().author.replace("?","").replace("/","_")
        directory = os.path.join(settings.BASE_DIR, 'static', 'txt',author) 
        # print(directory)       
        # 如果路徑不存在則創建資料夾
        if not os.path.exists(directory):
            os.makedirs(directory)

                
        txtfilepath=os.path.join(settings.BASE_DIR, 'static', 'txt',author, file_name)        
        notefilepath=NotePath.objects.filter(bookurl=book_url).first()
        lispath=NoteLisData.objects.filter(bookurl=book_url)
        
        # 建立路徑及下載檔案
        if not notefilepath:
            if lispath:                
                crawStore=listNoteDowl(lispath)
            else:                          
                # 小說狂人-爬資料
                crawStore=crawNote(book_url)
            note=crawStore.ok()            
            with open(txtfilepath, 'w',encoding="utf-8") as f:
                f.write(note)
            # 紀錄檔案路徑
            notedatas_instance = Notedatas.objects.filter(bookurl=book_url).first()                
            NotePath(bookurl=notedatas_instance,filepath=txtfilepath).save()
        else:                  
            notepath=notefilepath.filepath
            with open(notepath,"r",encoding="UTF-8") as f:
                note=f.read()
        # 思兔
        # crawStore=SiTo_dowlond(book_url)
        # note=crawStore.get_note_str()
        # 確保內容以 UTF-8 編碼
        content = note.encode('utf-8')
        
        # 返回文本檔給用戶
        response = HttpResponse(content, content_type='text/plain; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        
        return response
    else:
        return HttpResponse("僅支持 POST 請求", status=405)
# 9/27 各分類頁面
# 9/27搜尋
# def search(request):    
#     return render(request,"search.html", {})
# 9/27搜尋結果---需先建立資料庫
def searchanser(request):
    searchword=None
    booktype="搜尋"
    if request.method=="POST":
        searchword=request.POST.get("searchword").strip().replace(" ","")

    if searchword!=None:
        request.session["searchword"]=searchword
    if "searchword" in request.session:
        keyword=request.session["searchword"]
      
    context=note_universal_template(request,booktype,keyword)
    return render(request,"notebase.html",context)

# 爬-思兔網站
def dowlpage(request):
    if request.method=="POST":
        # skey=request.POST.get("searchword")
        # request.session["searchOK"]=True
        # if "useremail" in request.session:
        #     email=request.session["useremail"]
        # sorse=UserDonloadKeyWord.objects.filter(keyword=skey)
        # if sorse:
        #     pagelist=UserDonloadKeyWord.objects.filter(keyword=skey)
        # else:    
        #     gotowork=SiTo(email)
        #     gotowork.get_info(skey)
        #     pagelist=UserDonloadKeyWord.objects.filter(keyword=skey)
        # print(pagelist)
        # return render(request,"dowlopage.html",{"pagelist":pagelist})
        return render(request,"dowlopage.html",{})
    else:
        # request.session["searchOK"]=False
        # context={}
        return render(request,"dowlopage.html",{})

'''
if request.method=="POST":       
        
        html = render_to_string('notelistpage.html', context)
        return JsonResponse({'status': 'success', 'html': html})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
'''

# 書本細項列表
def notelist(request):    
    context={}
    if request.method=="POST":
        bookurl=request.POST.get("bookurl")        
        # 細項書籍連結
        sorse=NoteLisData.objects.filter(bookurl=bookurl).select_related('bookurl').order_by("no")
        bookstate=Notedatas.objects.filter(bookurl=bookurl).first()
        # if not bookstate:
        #     # 非完結本刪除細項重新抓取
        #     NoteLisData.objects.filter(bookurl=bookstate).delete()
        
        if not sorse:                        
            NoteLis(bookurl)
            sorse=NoteLisData.objects.filter(bookurl=bookurl).select_related('bookurl').order_by("no")
        
        # findbook=NoteLisData.objects.filter(bookurl=url).select_related('bookurl')
        bookname=sorse.first().bookurl.bookname        
        bookurl=sorse.first().bookurl.bookurl
        context["bookname"]=bookname
        context["bookurl"]=bookurl
        context["notelist"]=sorse
    #     html = render_to_string('notelistpage.html', context)
    #     return JsonResponse({'status': 'success', 'html': html})

    # return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
    
    return render(request,"notelistpage.html",context)
# 全部
def allnotes(request):    
    booktype="全部"
    context=note_universal_template(request,booktype)
    return render(request,"notebase.html",context)
    
# 玄幻奇幻
def xuanhuan(request):
    booktype="玄幻奇幻"
    context=note_universal_template(request,booktype)
    return render(request,"notebase.html",context)
    
# 言情
def yanqing(request):
    booktype="言情"
    context=note_universal_template(request,booktype)
    return render(request,"notebase.html",context)
    
# 武俠仙俠
def xianxia(request):
    booktype="武俠仙俠"
    context=note_universal_template(request,booktype)
    return render(request,"notebase.html",context)
    
# 軍事歷史
def lishi(request):
    booktype="軍事歷史"
    context=note_universal_template(request,booktype)
    return render(request,"notebase.html",context)
    
# 科幻未來
def wangyou(request):
    booktype="科幻未來"
    context=note_universal_template(request,booktype)
    return render(request,"notebase.html",context)
    
# 靈異玄幻
def lingyi(request):
    booktype="靈異玄幻"
    context=note_universal_template(request,booktype)
    return render(request,"notebase.html",context)
    
# 女生同人
def tongren(request):
    booktype="女生同人"
    context=note_universal_template(request,booktype)
    return render(request,"notebase.html",context)
    
# 原創同人
def erciyuan(request):
    booktype="原創同人"
    context=note_universal_template(request,booktype)
    return render(request,"notebase.html",context)
    
# 耽美
def danmei(request):
    booktype="耽美"
    context=note_universal_template(request,booktype)
    return render(request,"notebase.html",context)
    
# 百合
def baihe(request):
    booktype="百合"
    context=note_universal_template(request,booktype)
    return render(request,"notebase.html",context)
    
# 日系
def japan(request):
    booktype="日系"
    context=note_universal_template(request,booktype)
    return render(request,"notebase.html",context)
    
# 奇幻冒險
def fanatsy(request):
    booktype="奇幻冒險"
    context=note_universal_template(request,booktype)
    return render(request,"notebase.html",context)
    
# 電視劇
def drama(request):
    booktype="電視劇"
    context=note_universal_template(request,booktype)
    return render(request,"notebase.html",context)
    
# 情色工口
def herotic(request):
    booktype="情色工口"
    context=note_universal_template(request,booktype)
    return render(request,"notebase.html",context)
    
# 耽美工口
def blerotic(request):
    booktype="耽美工口"
    context=note_universal_template(request,booktype)
    return render(request,"notebase.html",context)
    
# 經典文學
def classicbook(request):
    booktype="經典文學"
    context=note_universal_template(request,booktype)
    return render(request,"notebase.html",context)
    # return render(request,"classicbook.html", {})
# 推理
def suspense(request):
    booktype="推理"
    context=note_universal_template(request,booktype)
    return render(request,"notebase.html",context)

# 女性向
def girl(request):
    booktype="女性向"
    context=note_universal_template(request,booktype)
    return render(request,"notebase.html",context)

# 短篇
def short(request):
    booktype="短篇"
    context=note_universal_template(request,booktype)
    return render(request,"notebase.html",context)
"""
# 取得分頁頁數區間
"""
def get_page_range(paginator,currentPage):
    if paginator.num_pages <=10:
        rangePage=range(1,paginator.num_pages+1)
    else:
        if currentPage-5<1:
            rangePage=range(1,11)
        elif currentPage+5>paginator.num_pages+1:
            rangePage=range(paginator.num_pages-9,paginator.num_pages+1)
        else:
            rangePage=range(currentPage-5,currentPage+5)
    return rangePage
"""
# 各分類使用通用區域
"""
def note_universal_template(req,booktype,searchkey=""): 
    sort_by = 'bookname'   
    context={}    
    if req.method=="POST":
        if req.POST.get("sort_by")!=None:
            sort_by=req.POST.get("sort_by")
            req.session["sort_by"]=sort_by
        else:
            req.session["sort_by"]="bookname"
        try:
            if req.POST.get("hiddenpage")!=None:
                page=req.POST.get("hiddenpage")
            else:
                page="1"
        except:
            page="1"
    else:
        page=req.GET.get('page',"1")

    if "sort_by" in req.session:
        sort_by=req.session["sort_by"]
    # 取得資料庫全部資料
    if booktype=="全部":
        alldatas=Notedatas.objects.all().order_by(sort_by)
    elif booktype=="搜尋":
        alldatas=Notedatas.objects.filter(Q(bookname__contains=searchkey)|Q(author__contains=searchkey)).order_by(sort_by)
    elif booktype=="會員收藏":
        if 'useremail' in req.session:
            useremail=req.session['useremail']
        userinfo_instance = Creatuser.objects.filter(email=useremail).first()    
        alldatas=Userlike.objects.filter(user=userinfo_instance).select_related('bookurl').order_by(f'-bookurl__{sort_by}')                    
    elif booktype=="會員下載":
        if 'useremail' in req.session:
            useremail=req.session['useremail']
        userinfo_instance = Creatuser.objects.filter(email=useremail).first()    
        alldatas=DonloadBookandUser.objects.filter(user=userinfo_instance).select_related('bookurl').order_by(f'-bookurl__{sort_by}')                    
    else:    
        alldatas=Notedatas.objects.filter(booktype=booktype).order_by(sort_by)
    
    if booktype=="會員收藏" or booktype=="會員下載":    
        alldatas=alldatas.order_by(f"-bookurl__{sort_by}")
    else:
        alldatas=alldatas.order_by(f"-{sort_by}")
    currentPage=int(page)#當前頁數
    
    # 將取得的資料作分頁處理
    paginator_datas=Paginator(alldatas,40)
    # 第幾個分頁
    pagelist=paginator_datas.page(currentPage)
    
    # 分頁區間        
    rangePage=get_page_range(paginator_datas,currentPage)

    context["pagetype"]=booktype
    context["rangePage"]=rangePage
    context["currentPage"]=currentPage
    context["pagelist"]=pagelist

    return context



     