from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_bcrypt import bcrypt
metadata=MetaData()
from .ModelHolder import app
db=SQLAlchemy(app,metadata=MetaData)
