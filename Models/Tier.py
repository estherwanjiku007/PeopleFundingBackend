from .config import db
from sqlalchemy_serializer import SerializerMixin
import uuid
class Tier(db.Model,SerializerMixin):
    __tablename__="tiers"

   
