from django.db import models
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField
import os
import glob
# Create your models here.
# 9/27 課堂中尚未python manage.py makemigrations



# 小說狂人-記錄小說分類與其url給nav標籤使用
class BookandUrl(models.Model):
    urlname=models.CharField(max_length=50)
    booktype=models.CharField(max_length=50)

    class Meta:
        db_table="bktypeurl"

# 小說狂人-記錄小說資訊
class Notedatas(models.Model):
    booktype=models.CharField(max_length=50,verbose_name="書本類型")
    bookname=models.CharField(max_length=100,verbose_name="書名")
    bookurl=models.URLField(verbose_name="書本連結",unique=True)
    author=models.CharField(max_length=50,verbose_name="作者")
    authorurl=models.URLField(verbose_name="作者連結")
    imageurl=models.URLField(verbose_name="圖片連結")
    keep=models.PositiveIntegerField(verbose_name="收藏人數")
    watch=models.PositiveIntegerField(verbose_name="觀看人數")
    bookstate=models.BooleanField(null=True, blank=True, default=False,verbose_name="完本記錄")

    def __str__(self):
        return self.bookname
    class Meta:
        db_table = "noteinfo"
# 小說狂人-書本細項連結
class NoteLisData(models.Model):    
    bookurl = models.ForeignKey(
        'Notedatas',  # 參考 Notedatas 模型
        on_delete=models.CASCADE,
        to_field='bookurl',  # 指向 Notedatas 的 bookurl 字段
        verbose_name="書本連結",
        null=True,
    )
    no=models.PositiveSmallIntegerField(verbose_name="書籍細項編號")
    booklisurl=models.URLField(verbose_name="書籍細項連結")

    class Meta:
        db_table="notelisinfo"
# 小說路徑存放
class NotePath(models.Model):
    bookurl = models.ForeignKey(
        'Notedatas',  # 參考 Notedatas 模型
        on_delete=models.CASCADE,
        to_field='bookurl',  # 指向 Notedatas 的 bookurl 字段
        verbose_name="書本連結",
        null=True,
    )
    filepath = models.CharField(max_length=255, verbose_name="TXT檔案路徑")
    class Meta:
        db_table="notepath"
# 思兔-使用者搜尋想下載的小說紀錄
class UserDonloadKeyWord(models.Model):
    user = models.CharField(max_length=50)
    keyword=models.CharField(max_length=50)
    imgurl=models.URLField(verbose_name="圖片連結")    
    bookurl=models.URLField(verbose_name="書本連結")
    bookname=models.CharField(max_length=50,verbose_name="書名")
    author=models.CharField(max_length=50,verbose_name="作者")

    class Meta:
        db_table = "userdownload_keyword"    



"""------------------------------------------------------------
測試用
------------------------------------------------------------"""
class sitoNote(models.Model):
    booktype=models.CharField(max_length=50,verbose_name="書本類型")
    bookname=models.CharField(max_length=100,verbose_name="書名")
    bookurl=models.URLField(verbose_name="書本連結")
    author=models.CharField(max_length=50,verbose_name="作者")
    imageurl=models.URLField(verbose_name="圖片連結")

    def __str__(self):
        return self.bookname
    class Meta:
        db_table = "sitonoteinfo"
"""------------------------------------------------------------
---------------------------------------------------------------
------------------------------------------------------------"""

# 記錄使用者會員資訊
class Creatuser(models.Model):
    user = models.CharField(max_length=50, null=False, blank=False)
    password = models.CharField(max_length=128, null=False, blank=False)    
    email = models.CharField(max_length=50, null=False, blank=False, unique=True)
    randomnumber = models.CharField(max_length=50, null=False, blank=False)
    chickemail= models.BooleanField( null=True, blank=True)

    class Meta:
        db_table = "userinfo"      
# 使用者個人資訊
class PersonalInformation(models.Model):
    email = models.OneToOneField(
        'Creatuser',  # 參考 Creatuser 模型
        on_delete=models.CASCADE,
        to_field='email',  # 指向 Notedatas 的 bookurl 字段
        verbose_name="使用者信箱",
        null=False,
        unique=True
    )
    nickname = models.CharField(max_length=50, null=True, blank=True,unique=True)
    birthday = models.DateField(help_text="user birthdate", null=True, blank=True)  # 允許為 None
    phone = PhoneNumberField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # 如果電話號碼是本地號碼，並且以 '09' 開頭，則假設它是台灣號碼並加上國際區號
        if self.phone and str(self.phone).startswith('09'):
            # 使用台灣的國際區號 +886
            self.phone = '+886' + str(self.phone)[1:]  # 去掉 '0'，加上國際區號
        super(PersonalInformation, self).save(*args, **kwargs)
    class Meta:
        db_table = "personalinfo"

# 記錄使用者收藏
class Userlike(models.Model):
    user = models.ForeignKey(
        'Creatuser',  # 參考 Creatuser 模型
        on_delete=models.CASCADE,
        to_field='email',  # 指向 Notedatas 的 bookurl 字段
        verbose_name="使用者信箱",
        null=False,
    )
    # bookname=models.CharField(max_length=100,verbose_name="書名",unique=True)
    bookurl = models.ForeignKey(
        'Notedatas',  # 參考 Notedatas 模型
        on_delete=models.CASCADE,
        to_field='bookurl',  # 指向 Notedatas 的 bookurl 字段
        verbose_name="書本連結",
        null=True,
    )
    
    class Meta:
        db_table = "userlike"    
        constraints = [
            models.UniqueConstraint(fields=['user', 'bookurl'], name='unique_user_bookurl')
        ]       
# 記錄使用者下載過的小說-小說狂人-
class DonloadBookandUser(models.Model):
    user = models.ForeignKey(
        'Creatuser',  # 參考 Creatuser 模型
        on_delete=models.CASCADE,
        to_field='email',  # 指向 Notedatas 的 bookurl 字段
        verbose_name="使用者信箱",
        null=False,
    )    
    bookurl = models.ForeignKey(
        'Notedatas',  # 參考 Notedatas 模型
        on_delete=models.CASCADE,
        to_field='bookurl',  # 指向 Notedatas 的 bookurl 字段
        verbose_name="書本連結",
        null=True,
    )

    class Meta:
        db_table="userdownload"
        constraints = [
            models.UniqueConstraint(fields=['user', 'bookurl'], name='unique_dowl_user_bookurl')
        ] 

# 儲存推薦書本
class PredRecommendBook(models.Model):
    user = models.ForeignKey(
        'Creatuser',  # 參考 Creatuser 模型
        on_delete=models.CASCADE,
        to_field='email',  # 指向 Notedatas 的 bookurl 字段
        verbose_name="使用者信箱",
        null=False,
    )
    bookurl = models.ForeignKey(
        'Notedatas',  # 參考 Notedatas 模型
        on_delete=models.CASCADE,
        to_field='bookurl',  # 指向 Notedatas 的 bookurl 字段
        verbose_name="書本連結",
        null=True,
    )
    score=models.PositiveIntegerField(verbose_name="分數")
    class Meta:
        db_table="pred_book"
# --------------------------------------------------------------------
# 使用者上傳照片
def user_directory_path(instance, filename):
    # 獲取原始檔案的副檔名
    ext = filename.split('.')[-1]
    # 使用使用者名稱和當前時間作為新文件名
    filename = f'person.{ext}'
    
    # 返回保存路徑，例如：'profile_pictures/user_name_20231003_151530.jpg'
    return os.path.join(f'static/user/{instance.picfilename}/img', filename)


class Profile(models.Model):
    picfilename = models.CharField(max_length=50)    
    picture = models.ImageField(upload_to=user_directory_path)

    class Meta:
        db_table = "profile"

    def delete_all_image_files(self, directory):
        """
        刪除指定目錄下所有的圖片文件 (.jpg, .jpeg, .png, .gif 等)
        """
        # 檢查目錄是否存在
        if os.path.exists(directory):
            # 定義支持的圖片擴展名
            image_extensions = ["*.jpg", "*.jpeg", "*.png", "*.gif", "*.bmp", "*.tiff"]
            
            # 遍歷所有定義的擴展名，查找對應的文件並刪除
            for ext in image_extensions:
                # 使用 glob 模塊列出指定擴展名的文件
                image_files = glob.glob(os.path.join(directory, ext))                
                # 遍歷找到的圖片文件並刪除
                for image_file in image_files:
                    try:
                        os.remove(image_file)  # 刪除文件
                        print(f"Deleted: {image_file}")
                    except OSError as e:
                        print(f"Error deleting file {image_file}: {e}")
        else:
            print(f"Directory {directory} does not exist.")
        
    def save(self, *args, **kwargs):
        # 根據使用者名稱生成路徑
        directory = os.path.join(settings.MEDIA_ROOT, f'static/user/{self.picfilename}/img')

        # 如果路徑不存在則創建資料夾
        if not os.path.exists(directory):
            os.makedirs(directory)

        # 刪除資料夾內所有 .png 文件
        if os.path.exists(directory):
            self.delete_all_image_files(directory)

        # 保存新圖片
        super(Profile, self).save(*args, **kwargs)