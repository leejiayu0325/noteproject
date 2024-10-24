import os
from django.conf import settings
import requests
from bs4 import BeautifulSoup
from threading import Thread
import threading
import pandas as pd
import time
import random
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium import webdriver
# from selenium_stealth import stealth
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By

# from urllib.parse import quote

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score

from mynote.models import BookandUrl,Notedatas,Userlike,PredRecommendBook,UserDonloadKeyWord,NoteLisData,Creatuser
# 取得預測書本
# 用到區域-登入、主頁、會員
def get_context_pbook(request,email,pagetype):
    p_book=None
    userinfo_instance = Creatuser.objects.filter(email=email).first()  
    print(userinfo_instance)
    userlike=Userlike.objects.filter(user=userinfo_instance)    
    

    if len(userlike)<2:        
        
        request.session["no_pbook"]=True
        if pagetype=="login":            
            return
        elif pagetype=="member":            
            p_book=Notedatas.objects.all().order_by('?')[:3]
        elif pagetype=="index":            
            p_book=Notedatas.objects.all()
        
    else:        
        # 進行預測必須使用者收藏數量>=2
        SVM_recommendedBook(userinfo_instance)
        
        request.session["no_pbook"]=False
        if pagetype=="login":            
            return
        elif pagetype=="member":            
            p_book=PredRecommendBook.objects.filter(user=userinfo_instance).select_related('bookurl').order_by('?')[:3]
        elif pagetype=="index":            
            p_book=PredRecommendBook.objects.filter(user=userinfo_instance).select_related('bookurl')
        
    
    return p_book
"""
檢查指定目錄下是否有圖片文件 (.jpg, .jpeg, .png, .gif 等)
"""
def has_image_files(directory):   
    # 定義常見的圖片文件擴展名
    image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"}

    # 檢查目錄是否存在
    if os.path.exists(directory):
        # 遍歷目錄中的所有文件
        for filename in os.listdir(directory):
            # 獲取文件的擴展名並轉換為小寫
            file_ext = os.path.splitext(filename)[-1].lower()
            # 如果擴展名在定義的圖片擴展名集合中，則表示該目錄中有圖片
            if file_ext in image_extensions:
                return file_ext  # 找到圖片文件，返回 True
    return None  

# 建立資料夾
def mkdir(picfilename):
    directory = os.path.join(settings.MEDIA_ROOT, f'static/user/{picfilename}/img')

    # 如果路徑不存在則創建資料夾
    if not os.path.exists(directory):
        os.makedirs(directory)
# 找到附檔名
def list_image_files(filename):
    # 定義 images 目錄的路徑
    images_dir = os.path.join(settings.STATICFILES_DIRS[0], 'user', filename,"img")
    try:
        for filename in os.listdir(images_dir):
            # 取得文件完整路徑
            file_path = os.path.join(images_dir, filename)
            
            # 如果是文件而不是目錄
            if os.path.isfile(file_path):
                # 分離文件名和副檔名
                name, ext = os.path.splitext(filename)
                return ext
            else:
                return False
    except:
        return False

def get_soup(url):    
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
        }
        resp=requests.get(url,headers=headers)        
        if resp.status_code==200:
            soup=BeautifulSoup(resp.text,"lxml")
        else:
            soup=None
        return soup  
# 小說狂人-下載書籍
class crawNote():
    def __init__(self,url):
        self.url=url
        self.noteStr={}
        self.getlis()
    
    #   取得所有章節的連結
    def getlis(self):
        soup=get_soup(self.url)
        lis_a=soup.find("ul",id="chapter-list").find_all("a")
        datas={}
        for i,a in enumerate(lis_a):    
            datas[i]="https:"+a.get("href")    
        
        self.goThread(datas)    
    # 多工處理
    def goThread(self,data):
        count=0
        threads=[]   
        for i in data.items():              
            threads.append(Thread(target=self.getstr,args=(i,)))
            count+=1            
            if count%10==0:
                for j in threads:                    
                    j.start()
                for j in threads:
                    j.join()
                threads=[]
            
        for j in threads:            
            j.start()
        for j in threads:
            j.join()
        
    # 進入章節內取得內容
    def getstr(self,a_urlinfo):                
        orderby,url=a_urlinfo
        delay = random.uniform(1, 5)
        # print(f"Fetching {url} after a delay of {delay:.2f} seconds")
        time.sleep(delay)
        soup=get_soup(url)
        
        notestr=soup.find("div",class_="content").text.strip()
        self.noteStr[orderby]=notestr
        
    
    def ok(self):
        novel_order=sorted(self.noteStr.keys())
        note=""
        print("ok")
        for i in novel_order:            
            note+=self.noteStr[i]
        
        return note

# 小說狂人-從細項下載
class listNoteDowl():
    def __init__(self,data):        
        self.noteStr={}
        self.goThread(data)
    
    # 多工處理
    def goThread(self,data):
        count=0
        threads=[]   
        for i in data:    
            datainfo=(i.no,i.booklisurl)          
            threads.append(Thread(target=self.getstr,args=(datainfo,)))
            count+=1            
            if count%10==0:
                for j in threads:                    
                    j.start()
                for j in threads:
                    j.join()
                threads=[]
            
        for j in threads:            
            j.start()
        for j in threads:
            j.join()
        
    # 進入章節內取得內容
    def getstr(self,a_urlinfo):  
        delay = random.uniform(1, 5)
        # print(f"Fetching {url} after a delay of {delay:.2f} seconds")
        time.sleep(delay)            

        orderby,url=a_urlinfo
        soup=get_soup(url)
        notestr=soup.find("div",class_="content").text.strip()
        self.noteStr[orderby]=notestr
    
    def ok(self):
        novel_order=sorted(self.noteStr.keys())
        note=""
        print("ok")
        for i in novel_order:            
            note+=self.noteStr[i]
        
        return note
# 小說狂人-取得書籍
class NavInfo():
    def __init__(self):
        self.lock = threading.Lock()
        self.url="https://czbooks.net/"
        soup=get_soup(self.url)
        self.alla=soup.find("ul",class_="nav menu").find_all("a")

    # 取得分類與分類連結
    def getnavmodel(self):
        soup=get_soup(self.url)
        if soup!=None:
            alla=soup.find("ul",class_="nav menu").find_all("a")    
            for i in alla:
                bktype=i.get("href").strip().split("/")[-1]
                name=i.text.strip()
                sorex=BookandUrl.objects.filter(urlname=name)
                if not sorex:
                    # print(bktype,name)
                    # 儲存分類到資料庫
                    BookandUrl(
                        urlname=name,
                        booktype=bktype,
                    ).save()
                else:
                    continue
        else:
            return None
    # 開始點
    # 想抓取的分類1~20頁資料，利用多工(Thread)抓取
    def alltypeurl(self):                
        wantPage=20
        # wantPage=1
        for i in self.alla[:-7]:  
        # for i in self.alla[1:2]:  
            bktype=i.get("href").strip().split("/")[-1]          
            # print(bktype)
            url=f"https://czbooks.net/c/{bktype}/finish"
            url2=f"https://czbooks.net/c/{bktype}/total"
            
            self.gourlthread(wantPage,url)
            self.gourlthread(wantPage,url2)
            
    # 開始多工處理
    def gourlthread(self,wantPage,url):        
        threads=[]
        count=0
        soup=get_soup(url)
        totalpage=eval(soup.find("ul",class_="nav paginate").find_all("li")[-1].text.strip().replace("~",""))
        for j in range(1,wantPage+1): 
            # 當期望頁數超過實際頁數時則跳出
            if j>totalpage:  
                # print(newurl)
                break                         
            newurl=f"{url}/{j}"
            delay = random.uniform(1, 5)        
            time.sleep(delay)
            soup=get_soup(newurl)            
            totalpage=eval(soup.find("ul",class_="nav paginate").find_all("li")[-1].text.strip().replace("~",""))
            threads.append(Thread(target=self.getnoteinfo,args=(newurl,)))
            count+=1                    
            if count%10==0:
                for i in threads:                        
                    i.start()                        
                for i in threads:
                    i.join()
                threads=[]                
        for i in threads:            
            i.start()            
        for i in threads:
            i.join() 
    # 抓取單頁的資料
    def getnoteinfo(self,url):
        
        bookstate=True if "finish" in url else False
        delay = random.uniform(1, 5)        
        time.sleep(delay)        
        soup=get_soup(url)             
        booktype=soup.find("div",class_="novel-list-function").find("ul",class_="nav").find_all("li")[-1].text.strip().split("\n")[0]
        items=soup.find_all('div',class_='novel-item')
        for item in items:
            book_url='https:'+item.find('a').get('href')            
            sorex=Notedatas.objects.filter(bookurl=book_url).first()
            # 取得 lock
            # 判斷書本是否已存在資料庫中
            # print(book_url,booktype)
            self.lock.acquire()
            try:
                if sorex:              
                    keep,watch=map(int,item.find('ul').text.strip().split())  
                    if bookstate:
                        sorex.bookstate=bookstate                        
                    sorex.keep=keep
                    sorex.watch=watch
                    sorex.save()                    
                else:                
                    bookname=item.find('div',class_='novel-item-title').text.strip()
                    author=item.find('div',class_='novel-item-author').find('a').text.strip()                       
                    author_url='https:'+item.find('div',class_='novel-item-author').find('a').get('href')
                    img_url=item.find('img').get('src')
                    if "czbooks.net" not in img_url or "humbnail/thumbnail" in img_url:
                        n_img="https://czbooks.net/images/default_no_thumbnail.jpg"   
                    else:
                        n_img=item.find('img').get('src')
                    keep,watch=map(int,item.find('ul').text.strip().split())
                    try:
                        Notedatas(booktype=booktype,
                                bookname=bookname,
                                bookurl=book_url,
                                author=author,
                                authorurl=author_url,
                                imageurl=n_img,
                                keep=keep,
                                watch=watch,
                                bookstate=bookstate).save()
                    except Exception as e:
                        print(e)
                        
            finally:
                # 釋放 lock
                self.lock.release()
 
# 取得書本細項連結
class NoteLis():
    def __init__(self,url):        
        self.url=url
        self.getlis()    
    def getlis(self):
        soup=get_soup(self.url)
        lis_a=soup.find("ul",id="chapter-list").find_all("a")        
        notedatas_instance = Notedatas.objects.filter(bookurl=self.url).first()  
        for i,a in enumerate(lis_a):    
            lis_url="https:"+a.get("href")            
            NoteLisData(bookurl=notedatas_instance,no=i,booklisurl=lis_url).save()
        
    # notedatas_instance = Notedatas.objects.filter(bookurl=url).first()
    #         PredRecommendBook(user=self.email,bookurl=notedatas_instance,score=score).save()
# # 思兔
# class SiTo():
#     def __init__(self,email):
#         chrome_options = Options()
#         chrome_options.add_argument("--headless")
#         # 
#         chrome_options.add_argument("--disable-dev-shm-usage")
#         chrome_options.add_argument("--no-sandbox")
#         # 
#         chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
#         chrome_options.add_argument("accept-language=en-US,en;q=0.9")
#         chrome_options.add_argument("accept=text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8")
#         chrome_options.add_argument("upgrade-insecure-requests=1")
#         chrome_options.add_argument("referrer=https://www.google.com/")
#         service = Service(executable_path=os.environ.get("CHROMEDRIVER_PATH"))
#         self.driver = webdriver.Chrome(service=service, options=chrome_options)
#         stealth(self.driver,
#         languages=["en-US", "en"],
#         vendor="Google Inc.",
#         platform="Win32",
#         webgl_vendor="Intel Inc.",
#         renderer="Intel Iris OpenGL Engine",
#         fix_hairline=True)
#         self.email=email
        
#     def get_info(self,keword):
#         kewd=quote(keword)
#         url=f"https://www.sto.cx/sba.aspx?k={kewd}&c=0"        
#         soup=None        
#         for i in range(2):
#             print("找書的>>>>>driver.page",self.driver.page_source) 
#             self.driver.get(url)
#             WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
#             if "沒有找到相關結果" in self.driver.page_source:
#                 url=f"https://www.sto.cx/sbn.aspx?k={kewd}&c=0"
#                 print("NOOOO")
#             else:
                
#                 soup=BeautifulSoup(self.driver.page_source,"lxml")
#                 self.driver.quit()
#                 break
#         print("找書>>>soup",soup)
#         if soup:
#             sbd=soup.find_all("div",class_="slistbody")    
#             for i in sbd:        
#                 if i.find("div",class_="fl"):
#                     imgurl="https://www.sto.cx"+i.find("div",class_="fl").find("img").get("src")
#                 else:
#                     imgurl=""
#                 book_url="https://www.sto.cx"+i.find("div",class_="t").find("a").get("href")
#                 bookname=i.find("div",class_="t").find("a").text.strip().split("作者")[0]
#                 author=i.find("div",class_="t").find("a").text.strip().split("：")[-1].split("(")[0].strip()
#                 UserDonloadKeyWord(user=self.email,keyword=keword,imgurl=imgurl,bookurl=book_url,bookname=bookname,author=author).save()
#                 print(imgurl,book_url,author)
# class SiTo_dowlond():
#     def __init__(self,bookurl):
#         self.lock = threading.Lock()
#         chrome_options = Options()
#         chrome_options.add_argument("--headless")
#         chrome_options.add_argument("--disable-dev-shm-usage")
#         chrome_options.add_argument("--no-sandbox")
#         chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
#         chrome_options.add_argument("accept-language=en-US,en;q=0.9")
#         chrome_options.add_argument("accept=text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8")
#         chrome_options.add_argument("upgrade-insecure-requests=1")
#         chrome_options.add_argument("referrer=https://www.google.com/")
#         service = Service(executable_path=os.environ.get("CHROMEDRIVER_PATH"))
#         self.driver = webdriver.Chrome(service=service, options=chrome_options)
#         self.bookurl=bookurl
#         self.notedic={}
#         self.star_getinfo()

#     def star_getinfo(self):
#         self.driver.get(self.bookurl)
#         soup=BeautifulSoup(self.driver.page_source,"lxml")  
#         print("找頁的>>>>>driver.page",self.driver.page_source)      
#         self.allpage=eval(soup.find("div",id="webPage").find_all("a")[-1].get("href").split("-")[-1].split(".")[0])
#         self.bookno=self.bookurl.split("-")[1]
#         print("找頁>>>",soup)
#         self.go_thread()

#     def go_thread(self):
#         threads=[]
#         count=0
#         for i in range(0,self.allpage):
#             newurl=f'https://www.sto.cx/book-{self.bookno}-{i+1}.html'

#             # 用多工去跑
#             threads.append(threading.Thread(target=self.get_note_data,args=(newurl,)))
#             count+=1
#             if count%10==0:
#                 for i in threads:
#                     i.start()
#                 for i in threads:
#                     i.join()
#                 threads=[]
#         for i in threads:
#             i.start()
#         for i in threads:
#             i.join()
        
#         self.driver.quit()
#     def get_note_data(self,url):  
#         print("--------")
#         no=eval(url.split("-")[-1].split(".")[0])
#         self.lock.acquire()
#         self.driver.get(url)
        
        
#         soup=BeautifulSoup(self.driver.page_source,"lxml")
#         context=soup.find("div",id="BookContent").text.strip()
#         print(context)
#         print("--------")
#         self.notedic[no]=context
#         self.lock.release()
#         print(no)

#     def get_note_str(self):
#         print(self.notedic)
#         novel_order=sorted(self.notedic.keys())
#         note=""
#         for i in novel_order:  
#             print(">>>>>>>>>",i) 
#             print(self.notedic[i])         
#             note+=self.notedic[i]
        
#         return note




# 機器學習
class SVM_recommendedBook():
    def __init__(self,email):
        self.email=email
        self.book=Notedatas.objects.all()
        self.user=Userlike.objects.filter(user=email)
        self.columns=["booktype","bookname","author"]
        self.get_balanced_df()
    
    # 取得平衡後資料
    def get_balanced_df(self):
        if len(self.user) == 0:
            # print("0收藏")
            return
        else:
            book_info=[[i.booktype,i.bookname,i.author] for i in self.book]
            user_info=[[i.bookurl.booktype,i.bookurl.bookname,i.bookurl.author] for i in self.user]

            self.df_books=pd.DataFrame(book_info,columns=self.columns)
            df_likes=pd.DataFrame(user_info,columns=self.columns)

            self.df_books["Liked"]=0

            self.df_books=self.df_books.merge(df_likes,on=self.columns,how="left",indicator=True)    
            self.df_books["Liked"]=self.df_books["_merge"].apply(lambda x:1 if x =="both" else 0)
            
            self.df_books.drop(columns=["_merge"],inplace=True)
            
            unlike_book=self.df_books[self.df_books["Liked"]==0]        
            like_book=self.df_books[self.df_books["Liked"]==1]
            
            if len(unlike_book)>len(like_book):
                unlike_book=unlike_book.sample(n=len(like_book))
            
            self.balanced_df=pd.concat([unlike_book,like_book])
            self.go_svm()
    # 進行數據預測
    def go_svm(self):
        conb_text=self.balanced_df["booktype"]+" "+self.balanced_df["bookname"]+" "+self.balanced_df["author"]
        verctorizer=TfidfVectorizer()
        
        x=verctorizer.fit_transform(conb_text)    
        y=self.balanced_df["Liked"]

        x_train,x_test,y_train,y_test=train_test_split(x,y,test_size=0.2,random_state=42)
        svm_model=SVC(kernel="linear")
        svm_model.fit(x_train,y_train)

        y_pred=svm_model.predict(x_test)
        accuracy=accuracy_score(y_test,y_pred)
        print(f'模型準確率: {accuracy:.2f}')
        self.recommend_books(svm_model,verctorizer)

    # 取得預測推薦的書
    def recommend_books(self,svm_model,verctorizer):
        x_all=verctorizer.transform(self.df_books["booktype"]+" "+self.df_books["bookname"]+" "+self.df_books["author"])
        pred=svm_model.decision_function(x_all)
        self.df_books["Score"]=pred
        # print(self.df_books.sort_values(by="Score",ascending=False))
        recom_book=self.df_books[self.df_books["Liked"]==0].sort_values(by="Score",ascending=False)
        # print(recom_book)
        self.result=recom_book[["booktype", "bookname", 'author',"Score"]]
        # print(recom_book)
        self.saveSql()
    # 將預測書本存入資料庫
    def saveSql(self):        
        PredRecommendBook.objects.filter(user=self.email).delete()
        recom=self.result.head(80)
        print(recom)
        for i in range(len(recom)):
            #  print(recom.iloc[i])
            booktype=recom.iloc[i]["booktype"]
            bookname=recom.iloc[i]["bookname"]
            author=recom.iloc[i]["author"]
            score=recom.iloc[i]["Score"]
            data=Notedatas.objects.filter(booktype=booktype,bookname=bookname,author=author).first()
            url=data.bookurl
            notedatas_instance = Notedatas.objects.filter(bookurl=url).first()
            PredRecommendBook(user=self.email,bookurl=notedatas_instance,score=score).save()


if __name__=="__main__":
    url="https://czbooks.net/"
    reps=requests.get(url)
    if reps.status_code==200:
        soup=BeautifulSoup(reps.text,"lxml")
        alla=soup.find("ul",class_="nav menu").find_all("a") 
        for i in alla:
            bktype=i.get("href").strip().split("/")[-1]
            name=i.text.strip() 
            print(bktype)
    # user="ee456214@gmail.com"
    # a=SVM_recommendedBook(user)
    # print(a)