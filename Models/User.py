from .config import db
from sqlalchemy_serializer import SerializerMixin
import datetime
from flask import make_response,jsonify
import uuid
class User(db.Model,SerializerMixin):
    __tablename__="users"

    id=db.Column(db.String(36),primary_key=True,default=lambda :str(uuid.uuid4()))
    name=db.Column(db.String,nullable=False)
    email=db.Column(db.String(120),nullable=False,unique=True)
    username=db.Column(db.String(20),nullable=False,unique=True)
    _password_hash=db.Column(db.String(300),nullable=False)
    phone_number=db.Column(db.Integer,nullable=False,unique=True)
    role=db.Column(db.Integer,nullable=False)
    creation_time=db.Column(db.DateTime,default=datetime.datetime.utcnow)
    is_validated=db.Column(db.Boolean,nullable=False,default=False)
    is_logged=db.Column(db.Boolean,nullable=False,default=False)
    tier=db.Column(db.Integer,nullable=False)
    subscription_expiry = db.Column(db.DateTime, nullable=True)
   
    def set_logged(self):
        # Mark the user as logged when they make the initial payment
        self.is_logged=True
        return self.is_logged
    
    def set_validated(self,subscription_length=7):
        try:
            """
            Validate the user for donations after subscription payment.
            Optionally, set a subscription length in days.
            """
            if not self.is_logged:
                return make_response({"Error":f"{self.name} has not made the initial payment"},401)
            else:
                self.is_validated=True
                self.subscription_expiry=datetime.datetime.utcnow()+datetime.timedelta(days=subscription_length)
                return make_response({"Message":"Subscription made sucdessfully"},200)
        except Exception as exc:
            return make_response({"Error":f"{str(exc)}"},500)
    
    def check_subscription_status(self):
        try:
            if not self.is_logged:
                return make_response({"Error":f"{self.username} has not payed the initial payment"},401)
            else:
                if not self.is_validated:
                    return make_response({"Error":f"{self.username} has not made the second payment"})
                else:
                    return make_response({"Error":f"{self.username} is logged in and verified"},200)
        except Exception as exc:
            return make_response({"Error":f"{str(exc)}"},500)
    def revoke_subscription(self):
        try:
            if not self.is_logged:
                return make_response({"Error":f"{self.username} not logged in"},402)
            else:
                if  not self.is_validated:
                    return make_response({"Error":f'{self.username} is not validated'},402)
                else:
                    self.is_validated=False
                    return make_response({"Error":f'{self.username}"s subscription has ended'},200)
        except Exception as exc:
            return make_response({"Error":f"{str(exc)}"},500)
        
            





        

            

    
        


    





