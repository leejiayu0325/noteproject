
import os
import django
import pandas as pd
import requests
import threading
from bs4 import BeautifulSoup
from threading import Thread
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
# from sklearn.preprocessing import LabelEncoder

# 設定 Django 專案的環境變數
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'note.settings')  # 替換為你的專案名稱
# 初始化 Django
django.setup()
from mynote.models import Notedatas,Userlike,PredRecommendBook,Creatuser,NoteLisData,NotePath,DonloadBookandUser
from crawl.findnote import NoteLis


class SVM_recommendedBook():
    def __init__(self,email):
        self.email=email
        self.book=Notedatas.objects.all()
        self.user=Userlike.objects.filter(user=email)
        self.columns=["booktype","bookname","author"]
        self.get_balanced_df()
    
    # 取得平衡後資料
    def get_balanced_df(self):
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
        self.result=recom_book[["booktype", "bookname", 'author']]
        self.saveSql()
    # 將預測書本存入資料庫
    def saveSql(self):
        PredRecommendBook.objects.filter(user=self.email).delete()
        recom=self.result.head(50)
        for i in range(len(recom)):
            #  print(recom.iloc[i])
            booktype=recom.iloc[i]["booktype"]
            bookname=recom.iloc[i]["bookname"]
            author=recom.iloc[i]["author"]
            data=Notedatas.objects.filter(booktype=booktype,bookname=bookname,author=author).first()
            url=data.bookurl
            notedatas_instance = Notedatas.objects.filter(bookurl=url).first()
            PredRecommendBook(user=self.email,bookurl=notedatas_instance).save()
            # print(booktype,bookname,author,url)

def get_context_pbook(request,email,pagetype):
    context={}
    userlike=Userlike.objects.filter(user=email)    
    cont_p=PredRecommendBook.objects.filter(user=email)

    if len(userlike)<2:        
        request.session["no_pbook"]=True
        if pagetype=="login":            
            return
        elif pagetype=="member":            
            p_book=Notedatas.objects.all().order_by('?')[:3]
            
        elif pagetype=="index":            
            p_book=Notedatas.objects.all().order_by('?')[:40]
    else:
        print("user>=2")
        # 進行預測必須使用者收藏數量>=2
        if len(cont_p)==0:                      
            SVM_recommendedBook(email)
        request.session["no_pbook"]=False
        if pagetype=="login":            
            return
        elif pagetype=="member":            
            p_book=PredRecommendBook.objects.filter(user=email).select_related('bookurl').order_by('?')[:3]
        elif pagetype=="index":            
            p_book=PredRecommendBook.objects.filter(user=email).select_related('bookurl').order_by('?')[:40]
    context["p_book"]=p_book
    return context

class NavInfo():
    def __init__(self):
        self.lock = threading.Lock()
        self.url="https://czbooks.net/"
        header={"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"}
        reps=requests.get(self.url,headers=header)
        # print(reps.text)
        if reps.status_code==200:
            print("OK")
            soup=BeautifulSoup(reps.text,"lxml")
            self.alla=soup.find("ul",class_="nav menu").find_all("a")

if __name__=="__main__":
    user="gototest@gmail.com"
    pagetype="login"
    request=""
    # a=SVM_recommendedBook(user)
    # print(a)

    # p_book=PredRecommendBook.objects.filter(user=user).select_related('bookurl').order_by('?')[:3]
    # for i in p_book:
    #     print(i.bookurl.booktype,i.bookurl.bookname,i.bookurl.author,i.bookurl.bookurl,i.bookurl.imageurl)
    # NavInfo()
    # a=get_context_pbook(request,user,pagetype)
    # print(a)
    # PredRecommendBook.objects.all().delete()
    email="cji3xu06@gmail.com"
    # a=Creatuser.objects.filter(email=email).first()
    # print(a.password)
    # a=linebot_pbook(email)
    # print(a,type(a))
    # for i in a:
    #     print(i.booktype,i.author,i.watch,i.keep,i.bookname,i.imageurl,i.bookurl)
    #     print()
    # print("go")
    # url="https://czbooks.net/n/crlc9"
    # url="https://czbooks.net/n/cpggmm1"
    # sorse=NoteLisData.objects.filter(bookurl=url).select_related('bookurl')
    # if sorse:
    #     print("已建立")
    # else:
    #     print("未建立，要建立")
    #     NoteLis(url)
    # findbook=NoteLisData.objects.filter(bookurl=url).select_related('bookurl')
    # bookname=findbook.first().bookurl.bookname
    # print(bookname)
    # for i in a:
    #     print(i.no,">>>",i.booklisurl)
    # 
    a=Notedatas.objects.all()
    print(a)
    # a.delete()
    print(a.count)