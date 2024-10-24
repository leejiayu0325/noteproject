
import os
import django
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
# from sklearn.preprocessing import LabelEncoder

# 設定 Django 專案的環境變數
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'note.settings')  # 替換為你的專案名稱
# 初始化 Django
django.setup()
from mynote.models import Notedatas,Userlike
def rec_book(svm_model,verctorizer,df_book,n=5):
        x_all=verctorizer.transform(df_book["booktype"]+" "+df_book["bookname"]+" "+df_book["author"])
        pred=svm_model.decision_function(x_all)
        df_book["Score"]=pred
        recom_book=df_book[df_book["Liked"]==0].sort_values(by="Score",ascending=False)
        # print(recom_book)
        result=recom_book[["booktype", "bookname", 'author']]
        
        return result.head(n)

if __name__=="__main__":
    user="ee456214@gmail.com"
    book=Notedatas.objects.all()
    user=Userlike.objects.filter(user=user)

    columns=["booktype","bookname","author"]
    book_info=[[i.booktype,i.bookname,i.author] for i in book]
    user_info=[[i.bookurl.booktype,i.bookurl.bookname,i.bookurl.author] for i in user]

    df_books=pd.DataFrame(book_info,columns=columns)
    df_likes=pd.DataFrame(user_info,columns=columns)

    df_books["Liked"]=0

    df_books=df_books.merge(df_likes,on=columns,how="left",indicator=True)    
    df_books["Liked"]=df_books["_merge"].apply(lambda x:1 if x =="both" else 0)
    
    df_books.drop(columns=["_merge"],inplace=True)
    
    unlike_book=df_books[df_books["Liked"]==0]        
    like_book=df_books[df_books["Liked"]==1]
    
    if len(unlike_book)>len(like_book):
        unlike_book=unlike_book.sample(n=len(like_book),random_state=42)
    
    balanced_df=pd.concat([unlike_book,like_book])

    conb_text=balanced_df["booktype"]+" "+balanced_df["bookname"]+" "+balanced_df["author"]
    verctorizer=TfidfVectorizer()
    
    x=verctorizer.fit_transform(conb_text)    
    y=balanced_df["Liked"]

    x_train,x_test,y_train,y_test=train_test_split(x,y,test_size=0.2,random_state=42)
    svm_model=SVC(kernel="linear")
    svm_model.fit(x_train,y_train)

    y_pred=svm_model.predict(x_test)
    accuracy=accuracy_score(y_test,y_pred)

    recom=rec_book(svm_model,verctorizer,df_books,n=5)
    # print(recom.iloc[0])

    for i in range(len(recom)):
        #  print(recom.iloc[i])
         booktype=recom.iloc[i]["booktype"]
         bookname=recom.iloc[i]["bookname"]
         author=recom.iloc[i]["author"]
         data=Notedatas.objects.get(booktype=booktype,bookname=bookname,author=author)
         url=data.bookurl
         print(booktype,bookname,author,url)

    

