# -*- coding: UTF-8 -*-
import os

PORT = 5001
DEBUG = True
CONTAINER_NAME = "vatic"

#Admin info
ADMIN_NAME = "Max"
ADMIN_ID = "max.hsu@ironyun.com"

K_FRAME = 300
OFFSET = 21
#VATIC_ADDRESS = "http://172.16.22.51:8887"

EXT_ADDR = os.environ.get('EXTERNAL_ADDRESS')
if EXT_ADDR == None:
    EXT_ADDR = "172.16.22.51"
VATIC_ADDRESS = "http://"+EXT_ADDR+":8892"



EXTRA_VATIC_ADDRESS = "http://172.16.22.51:8892"
EXTRA_CONTAINER_NAME = "angry_hawking"
VATIC_PATH = "/root/vatic"
LABELS = ['bus', 'van', 'truck', 'trailer-head', 'sedan/suv', 'scooter', 'bike','undefined','person','car']

smtp_host="smtp.gmail.com"
smtp_port="587"
smtp_tls=True

## Gmail 需啟用 [允許安全性較低的應用程式] 設定處於啟用狀態
## URL: https://myaccount.google.com/lesssecureapps
## 或是啟用 2FA 後，使用應用程式專用密碼登入
smtp_user="pawanhsu@gmail.com"
smtp_pass="xwlrhauvhmiinnjt"

## Gmail 的寄件地址必須與登入帳號相同
## 或是帳戶中加入「以這個地址寄送郵件」
smtp_sender = ''
smtp_sender_name = ''

smtp_encoding = 'utf-8'

ALLOW_IP = ["172.16.22.51","172.16.12.209", "127.0.0.1", "*"]
