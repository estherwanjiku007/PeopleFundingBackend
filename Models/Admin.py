from .config import db
from sqlalchemy_serializer import SerializerMixin
import uuid
from werkzeug.security import check_password_hash
class Admin(db.Model,SerializerMixin):
    __tablename__="admins"

    id=db.Column(db.String(36),primary_key=True,default=lambda :str(uuid.uuid4()))
    name=db.Column(db.String,nullable=False)
    email=db.Column(db.String(120),nullable=False,unique=True)
    username=db.Column(db.String,unique=True,nullable=False)
    _password_hash=db.Column(db.String(300),nullable=False)
    role=db.Column(db.String,nullable=False)
    phone_number=db.Column(db.Integer,nullable=False,unique=True)
    

    def authenticate(self,password):
        return check_password_hash(self._password_hash,password)
    
    def better_response(self):
        from .transactions import Transactions
        all_transactons=[trans.to_dict() for trans in db.session.query(Transactions).all()]
        return {
            "id":self.id,
            "name":self.name,
            "email":self.email,
            "username":self.username,
            "role":self.role,
            "AllTransaction":all_transactons
        }

