
import os
import django

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
# 設定 Django 專案的環境變數
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'note.settings')  # 替換為你的專案名稱

# 初始化 Django
django.setup()

# 現在可以導入你的模型

from mynote.models import Creatuser,Notedatas,Userlike,PersonalInformation,Profile
# 取得 Notedatas 模型的欄位名稱

# fields = [field.name for field in Notedatas._meta.get_fields()]

# print(fields)
if __name__=="__main__":
    """
    """
    columns=["booktype","bookname","author"]
    
    datas=Notedatas.objects.all()
    userlike=Userlike.objects.filter(user="ee456214@gmail.com")
    
    # 使用者看過的書名
    
    user=[[i.bookurl.booktype,i.bookurl.bookname,i.bookurl.author] for i in userlike]    
    notedatas=[[i.booktype,i.bookname,i.author] for i in datas]
    
    df_books = pd.DataFrame(notedatas, columns=['booktype', 'Title', 'Author'])
    df_likes = pd.DataFrame(user, columns=['booktype', 'Title', 'Author'])

    # 3. 使用 merge 來標記正負樣本
    df_books['Liked'] = 0  # 預設所有書本為負樣本
    # print(df_books)
    df_books = df_books.merge(df_likes, on=['booktype', 'Title', 'Author'], how='left', indicator=True)
    df_books['Liked'] = df_books['_merge'].apply(lambda x: 1 if x == 'both' else 0)
    

    # 刪除輔助的 '_merge' 列
    df_books.drop(columns=['_merge'], inplace=True)
    print(df_books)
'''
    # 檢查正負樣本數量
    print(df_books['Liked'].value_counts())

    # 4. 平衡數據集
    liked_books = df_books[df_books['Liked'] == 1]
    unliked_books = df_books[df_books['Liked'] == 0]

    # 打印樣本數量，確認沒有為0的情況
    print(f"正樣本數量: {len(liked_books)}, 負樣本數量: {len(unliked_books)}")

    # 如果負樣本多於正樣本，進行下采樣
    if len(unliked_books) > len(liked_books):
        unliked_books = unliked_books.sample(n=len(liked_books), random_state=42)

    # 合併正負樣本
    balanced_df = pd.concat([liked_books, unliked_books])

    # 5. 提取文本特徵（使用Tfidf）
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(balanced_df['Title'] + ' ' + balanced_df['Author'] + ' ' + balanced_df['booktype'])

    # 6. 準備特徵和標籤
    y = balanced_df['Liked']

    # 7. 切分數據集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 8. 訓練SVM模型
    svm_model = SVC(kernel='linear')
    svm_model.fit(X_train, y_train)

    # 9. 預測結果並評估模型
    y_pred = svm_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f'模型準確率: {accuracy:.2f}')

    def recommend_books(svm_model, vectorizer, books_df, n_recommendations=5):
    # 對所有書籍進行預測，並只推薦未喜歡的書籍
        X_all = vectorizer.transform(books_df['Title'] + ' ' + books_df['Author'] + ' ' + books_df['booktype'])
        predictions = svm_model.decision_function(X_all)
        books_df['Score'] = predictions
        recommended_books = books_df[books_df['Liked'] == 0].sort_values(by='Score', ascending=False)
        # return recommended_books[['booktype', 'Title', 'Author']].head(n_recommendations)
        return recommended_books[['booktype', 'Title', 'Author']]

    # 11. 為用戶推薦書籍
    recommended = recommend_books(svm_model, vectorizer, df_books)
    print("推薦書籍:\n", recommended)
    # print(recommended_books[['booktype','bookname', 'author']])
    a=pd.DataFrame(recommended)
    a.to_csv("t1.csv",encoding="utf-8-sig")
    '''