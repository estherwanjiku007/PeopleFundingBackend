from .config import db
from sqlalchemy_serializer import SerializerMixin
import uuid
class Transactions(db.Model,SerializerMixin):
    __tablename__="transactions"

    id=db.Column(db.String(36),primary_key=True,default=lambda :str(uuid.uuid4()))
    verify_code=db.Column(db.String,unique=True,nullable=False)
    to_address=db.Column(db.String,nullable=False)
    from_address=db.Column(db.String,nullable=False)