#VATIC-ADMIN 
##Thi is an extension for VATIC-DOCKER that helps you verify the difference of two or more worker on the same video.

###Make sure that you locate your vatic-docker directory under vatic-admin folder.

## To run the admin

### virtualenv (option)

Option - create virtual enviorment to avoid interference with different projects

```
sudo easy_install virtualenv
virtualenv .env
source .env/bin/activate
```

### dependency package

install dependency package (if no virtualenv, add sudo to install on system)

```
pip install flask scipy pillow matplotlib requests tinydb
```

### run server
```
#!shell
python admin_server.py

```
