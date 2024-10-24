from django import forms
from mynote.models import Creatuser,PersonalInformation
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import check_password,make_password

from datetime import date
from PIL import Image
import phonenumbers
import re



# 登入
class LoginForm(forms.Form):
    email = forms.EmailField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput,max_length=50)    

    def clean(self):
        cleaned_data = super().clean()
        useremail=cleaned_data.get("email")
        password=cleaned_data.get("password")

        dbuser = Creatuser.objects.filter(email=useremail).first()        
        if not dbuser:
            self.add_error('email', "沒有該信箱，請先進行註冊。")
            # raise ValidationError("沒有該信箱，請先進行註冊。")
        
        elif dbuser and not dbuser.chickemail:
            self.add_error('email', "信箱尚未驗證，請先到信箱進行驗證。")
            # raise ValidationError("信箱尚未驗證，請先到信箱進行驗證。")
        
        else:
            if not check_password(password, dbuser.password):
                self.add_error('password',"密碼錯誤，請重新輸入。")
            # raise ValidationError("密碼錯誤，請重新輸入。")
        return cleaned_data

# 註冊
class RegisterForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField(max_length=50)
    password = forms.CharField(max_length=50)
    checkpw= forms.CharField(max_length=50)

    def clean_name(self):
        username=self.cleaned_data.get("name")
        if " "in username:
            raise ValidationError("不能包含空格字符。")
        if len(username)==0:
            raise ValidationError("不能為空。")
        return username

    def clean_email(self):
        useremail=self.cleaned_data.get("email")
        dbuser = Creatuser.objects.filter(email=useremail).first()
        if dbuser:
            
            raise ValidationError("信箱已註冊，請輸入其他信箱。")
        return useremail
    def clean_password(self):
        userpwd=self.cleaned_data.get("password")
        if " " in userpwd:
            raise ValidationError("密碼不能包含空格字符。")
        if len(userpwd)<8:
            raise ValidationError("密碼必須至少包含 8 個字符。")
        if not re.search(r"[a-zA-Z]",userpwd):
            raise ValidationError("密碼必須至少包含 1 個英文字母。")
        if not re.search(r"[0-9]",userpwd):
            raise ValidationError("密碼必須至少包含 1 個數字。")
        # encrypted_password = make_password(userpwd)
        return userpwd

    def clean(self):        
        userpwd=self.cleaned_data.get("password")
        userckpw=self.cleaned_data.get("checkpw")
        
        if userpwd and userckpw and userpwd!=userckpw:
            self.add_error('checkpw', "輸入的密碼不一致。")
# 修改密碼-透過會員-驗證舊密碼
class OldpwdForm(forms.Form):
    email = forms.EmailField(widget=forms.HiddenInput())
    password = forms.CharField(widget=forms.PasswordInput())
    checkpw= forms.CharField(widget=forms.PasswordInput())
    def clean(self): 
        email=self.cleaned_data.get("email")
        userpwd=self.cleaned_data.get("password")
        userckpw=self.cleaned_data.get("checkpw")
        user=Creatuser.objects.filter(email=email).first()

        if user and not check_password(userpwd, user.password):
            self.add_error('password', "密碼輸入錯誤。")
        if userpwd and userckpw and userpwd!=userckpw:
            self.add_error('checkpw', "輸入的密碼不一致。")

# 修改密碼-新密碼與舊密碼比對
class NewpwdForm(forms.Form):
    email = forms.EmailField(widget=forms.HiddenInput())
    password = forms.CharField(widget=forms.PasswordInput())
    checkpw= forms.CharField(widget=forms.PasswordInput())
    def clean_password(self):
        email=self.cleaned_data.get("email")
        userpwd=self.cleaned_data.get("password")
        
        
        user=Creatuser.objects.filter(email=email).first()
        if " " in userpwd:
            raise ValidationError("密碼不能包含空格字符。")
        if len(userpwd)<8:
            raise ValidationError("密碼必須至少包含 8 個字符。")
        if not re.search(r"[a-zA-Z]",userpwd):
            raise ValidationError("密碼必須至少包含 1 個英文字母。")
        if not re.search(r"[0-9]",userpwd):
            raise ValidationError("密碼必須至少包含 1 個數字。")
        
        if user and check_password(userpwd, user.password):
            self.add_error('password', "新密碼不能與舊密碼一樣。")
        return userpwd
    
    def clean(self): 
        
        userpwd=self.cleaned_data.get("password")
        userckpw=self.cleaned_data.get("checkpw")
        
        if userpwd and userckpw and userpwd!=userckpw:
            self.add_error('checkpw', "輸入的密碼不一致。")

# 忘記密碼-信箱驗證
class ForgetForm(forms.Form):
    email = forms.EmailField(max_length=50)        
    def clean_email(self):
        useremail=self.cleaned_data.get("email")
        dbuser = Creatuser.objects.filter(email=useremail).first()
        if not dbuser:
            # self.add_error('email', "沒有該信箱，請先進行註冊。")
            raise ValidationError("沒有該信箱，請先進行註冊。")
        
        elif dbuser and not dbuser.chickemail:
            # self.add_error('email', "信箱尚未驗證，請先到信箱進行驗證。")
            raise ValidationError("信箱尚未驗證，請先到信箱進行驗證。")        
        
        return useremail
# ------------------------------------------------------------------------------
# 使用者資料
class PersonForm(forms.Form):
    # email = forms.EmailField(max_length=50)
    nickname = forms.CharField(max_length=50, required=False)  # 允許空的暱稱
    birthday = forms.DateField(required=False)
    phone = forms.CharField(required=False)

    def clean_nickname(self):
        nickname = self.cleaned_data.get('nickname')
        if nickname:  # 確認是否提供了 nickname
            # 檢查資料庫中是否有重複的暱稱
            if PersonalInformation.objects.filter(nickname=nickname).exists():
                raise ValidationError("暱稱已經存在，請選擇其他暱稱。")
        return nickname   
    
    
    def clean_birthday(self):
        birthday = self.cleaned_data.get('birthday')
        
        if birthday:  # 如果輸入了生日
            today = date.today()

            # 1. 檢查生日是否是未來的日期
            if birthday > today:
                raise ValidationError("生日不能是未來的日期。")

            # 2. 檢查是否超過合理年齡（比如 150 歲）
            age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
            if age > 150:
                raise ValidationError("你輸入的年齡過大，請檢查是否正確。")
        return birthday
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')

        if phone:  # 如果輸入了電話號碼
            try:
                # 解析電話號碼，假設預設國家代碼為台灣（+886）
                parsed_phone = phonenumbers.parse(phone, "TW")

                # 驗證電話號碼是否合法
                if not phonenumbers.is_valid_number(parsed_phone):
                    raise ValidationError("電話號碼無效。")
            except phonenumbers.phonenumberutil.NumberParseException:
                raise ValidationError("電話號碼格式無效。")

        return phone
# --------------------------------------------------------------------
# 使用者上傳照片    
class ProfileForm(forms.Form):
    picfilename = forms.CharField(max_length=100)
    picture = forms.ImageField()    

    def clean_picture(self):
        picture=self.cleaned_data.get("picture")
        
        if picture:
            try:
                # 嘗試打開文件，確保它是一個有效的圖片
                img = Image.open(picture)
                img.verify()  # 驗證圖片文件的完整性
            except (IOError, SyntaxError) as e:
                raise ValidationError("上傳的文件不是有效的圖片。")
            # 限制為2MB
            max_size = 2 * 1024 * 1024
            if picture.size>max_size:
                raise ValidationError("圖片大小不能超過 2MB。")
        return picture