import os

PORT = 5001
DEBUG = True
CONTAINER_NAME = "vatic_new"

#Admin info
ADMIN_NAME = "Max"
ADMIN_ID = "max.hsu@ironyun.com"

K_FRAME = 300
OFFSET = 21
#VATIC_ADDRESS = "http://172.16.22.51:8887"

EXT_ADDR = os.environ.get('EXTERNAL_ADDRESS')
if EXT_ADDR == None:
    EXT_ADDR = "172.16.12.91"
VATIC_ADDRESS = "http://"+EXT_ADDR+":8892"



EXTRA_VATIC_ADDRESS = "http://172.16.22.91:8892"
EXTRA_CONTAINER_NAME = "angry_hawking"
VATIC_PATH = "/root/vatic"
LABELS = ['bus', 'van', 'truck', 'trailer-head', 'sedan/suv', 'scooter', 'bike','undefined','person','car']
