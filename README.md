#VATIC-ADMIN 
##Thi is an extension for VATIC-DOCKER that helps you verify the difference of two or more worker on the same video.

###Make sure that you locate your vatic-docker directory under vatic-admin folder.

## To run the admin

### get code

```
mkdir vatic 
git clone git@bitbucket.org:ccha97u/vatic_admin.git
cd vatic_admin
git clone git@bitbucket.org:ccha97u/vatic-docker.git
mkdir -p vatic-docker/data/query
```

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
pip install flask scipy pillow matplotlib requests tinydb sqlalchemy pymysql
```

### run server

before admin startup, startup vatic-docker first

if need setup external ip, using following command
```
export EXTERNAL_ADDRESS=192.168.168.76
```

```
#!shell
python admin_server.py
```

or run server background with virtualenv and tmux
```
tmux new-session -s vatic-admin -d 'source .env/bin/activate && while [ true ]; do python admin_server.py; done'
```
