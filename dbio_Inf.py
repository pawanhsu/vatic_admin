from dbconnect import *
from dbmodels import *

a = session.query(User).first()

print(a.username)
