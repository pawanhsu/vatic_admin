from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Numeric, String

import os
cwd = os.getcwd()
import sys
sys.path.insert(0, cwd + '/vatic-docker/vatic')

engine = create_engine('mysql+pymysql://root:1111' '@172.17.0.2:3306/vatic')
Session = sessionmaker (bind = engine)
session = Session()

Base = declarative_base()
