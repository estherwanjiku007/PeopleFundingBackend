from Models.ModelHolder import app,db,Transactions,User,Admin
from flask import make_response, jsonify, request, url_for,send_from_directory,session
from dotenv import load_dotenv

# from flask_mail import Mail,Message
from flask_restful import Api, Resource
from itsdangerous import URLSafeTimedSerializer,SignatureExpired
# from flask_jwt_extended import JWTManager,create_access_token,jwt_required,get_jwt_identity
from Models.app import app
from flask_migrate import Migrate
from flask_cors import CORS,cross_origin
# from flask_socketio import SocketIO
from werkzeug.security import generate_password_hash
from sqlalchemy import or_,and_
from email.mime.text import MIMEText#import the  email.mime.text 
from email.mime.multipart import MIMEMultipart
import os
import base64
import random
from email.message import EmailMessage

otp=str(random.randint(100000,999999))
load_dotenv()
allowed_origins=os.environ.get("allowed_origins")

app.config["SQLALCHEMY DATABASE_URI"]="sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config["MAIL_USE_SSL"]=True
app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get("MAIL_USERNAME")
app.config["SECRET_KEY"] = base64.b64encode(os.urandom(24)).decode('utf-8')
db.init_app(app)
migrate=Migrate(app,db)

cors=CORS(app,resources={r'/api/*':{
    "origins":allowed_origins
}})
# mail=Mail(app)
api=Api(app)
all_usernames=[]
all_emails=[]
all_names=[]
all_phone_nums=[]

with app.app_context():
    all_usernames.extend([admin.username for admin in db.session.query(Admin).all()])
    all_usernames.extend([user.username for user in db.session.query(User).all()])
    all_phone_nums.extend([admin.phone_number for admin in db.session.query(Admin).all()])
    all_phone_nums.extend([user.phone_number for user in db.session.query(User).all()])    

def authenticate_url(url):
    try:        
        if url:
            if allowed_origins:
                if url != allowed_origins:
                    return make_response({"Error": "Unauthorized URL"}, 401)
                else:
                    return make_response({"Message": "URL is ok"}, 200)
            else:
                return make_response({"Error": "Allowed origins not configured"}, 401)
        else:
            return make_response({"Error": "Request origin not configured"}, 401)
    except Exception as exc:
        return make_response({"Error": f"An error occurred: {str(exc)}"}, 500)

def create_user(data):
    try:
        request_origin=request.headers.get("Origin")
        new_status=authenticate_url(request_origin)
        if  new_status.status_code==200:
            if not isinstance(data,dict):
                return make_response({"Error":"Incorrect Request data format"},415)
            required_fields=["name","email","username","password","confirm_password","role","phone_number"]
            if not all(key in data for key in required_fields):
                return make_response({"Error":"Missing required fields"},401)
            username=data.get("username")
            if username:
                if username in all_usernames:
                    return make_response({"Error":f"Username {username} already exists"},401)
            else:
                return make_response({"Error":"Username not sent in  the provided data"},401)
            
            email=data.get("email")
            if email:
                if email in all_emails:
                    return make_response({"Error":f"Email {email} already exists"},401)
            else:
                return make_response({"Error":"Email not sent in provided data"},401)
            role=data.get("role")
            if role:
                password=data.get("password")
                phone_number=data.get("phone_number")
                if password:
                    if phone_number:
                        new_password=generate_password_hash(password,"scrypt",16)
                        if role=="admin":
                            new_admin=Admin(
                                    name=data["name"],
                                    email=email,
                                    _password_hash=new_password,
                                    role=role,
                                    username=username,
                                    phone_number=phone_number
                                )
                            db.session.add(new_admin)
                            db.session.commit()
                            return make_response({"Message":f"{new_admin.username} added successfully"},200)
                        
                        elif role=="user":
                            new_user=User(
                                name=data["name"],
                                email=email,
                                username=username,
                                role=role,
                                phone_number=phone_number,
                                _password_hash=new_password
                            )
                            db.session.add(new_user)
                            db.session.commit()
                            return make_response({"Message":f"{new_user.username} added successfully"},200)
                        
                        else:
                            return make_response({"Error":"Invalid role"},404)
                    else:
                        return make_response({"Error":"Phone number is required"},404)
                else:
                    return make_response({"Error":"Password not set"},404)
            else:
                return make_response({"Error":"Role has not yet been set"},404)
        else:
            return make_response({"Error":f"An error ocurred creating a user "},401)
    except Exception as exc:
        return make_response({"Error":f"{str(exc)}"},500)
       
       
@app.route("/",methods=["GET"])
def root_url():
    return "<h1>Welcome to Peoplefunding app</h1>"

@app.route("/admins",methods=["GET","POST"])
def get_all_admins():
    try:
        request_origin=request.headers.get("Origin")
        verified_origin=authenticate_url(request_origin)
        if verified_origin.status_code==200:
            if request.method=="GET":
                all_admins=[admin.better_response() for admin in db.session.query(Admin).all()]
                return make_response({"Message":all_admins},200)
            elif request.method=="POST":
                data=request.json
                return create_user(data)
        else:
            return make_response({"Error":f"{verified_origin.status}"},401)

    except Exception as exc:
        return make_response({"Error":f"{str(exc)}"},500)

@app.route("/admins/<string:id>",methods=["GET","PATCH","DELETE"])
def admin_by_id(id):
    try:
        request_origin =request.headers.get("Origin")
        new_status=authenticate_url(request_origin)
        if new_status.status_code==200:
            admin=db.session.query(Admin).filter_by(id=id).first()
            if request.method=="GET":
                admin_values=[admin.to_dict()]
                return make_response(admin_values,200)
            elif request.method=="PATCH":
                data=request.json
                if not isinstance(data,dict):
                    return make_response({"Error":"Incorrect request data format"},401)
                required_values=["name","email","username","password","confirm_password","role","phone_number"]
                if not all(key in data for key in required_values):
                    return make_response({"Error":"Missing required fields"},401)
                username=data.get("username")
                if username:
                    if username in all_usernames:
                        return make_response({"Errro":f"Username {username} already exists"},401)
                else:
                    return make_response({"Error":f"Username not sent in data"},404)
                
                email=data.get("email")
                if email:
                    if email in all_emails:
                        return make_response({"Error":f"Email {email} already exists"},401)
                else:
                    return make_response({"Error":"Email does not exist in provided data"},404)
                
                phone_number=data.get("phone_number")
                if phone_number:
                    if phone_number in all_phone_nums:
                        return make_response({"Error":f"Phone number {phone_number} already exists"},401)
                else:
                    return make_response({"Error":f"Phone_number not found"},404)
                
                for attr,value in data.items:
                    if attr in required_values:
                        setattr(admin,attr,value)
                db.session.commit()
                return make_response({"Error":f"{admin.username} updated successfully"},200)

            elif request.method=="DELETE":
                db.session.delete(admin)
                db.session.commit()
                return make_response({"Error":f"Admin deleted successfully"},200)
            else:
                return make_response({"Error":"Method not allowed"},405)
    except Exception as exc:
        return make_response({"Error":f"An error ocuured ...{str(exc)}"},500)
    
@app.route("/users",methods=["GET","POST"])
def getting_all_admins():
    try:
        request_origin=request.headers.get("Origin")
        new_status=authenticate_url(request_origin)
        if new_status.status_code==200:
            if request.method=="GET":
                all_users=[user.to_dict() for user in db.session.query(User).all()]
                return make_response(all_users,200)
            elif request.method=="POST":
                data=request.json
                response=create_user(data)
                return response
            else:
                return make_response({"Error":"Method not allowed"},405)
        else:
            return new_status
    except Exception as exc:
        return make_response({"Error":f"An error ocurred {str(exc)}"},500)

@app.route("/users/<string:id>",methods=["GET","PATCH","DELETE"])
def user_by_id(id):
    try:
        request_origin=request.headers.get("Origin")
        new_status=authenticate_url(request_origin)
        if new_status.status_code==200:
            user=db.session.query(User).filter_by(id=id).first()
            if user:
                if request.method=="GET":
                    users_data=[user.to_dict()]
                    return make_response(users_data,200)
                elif request.method=="PATCH":
                    data=request.json
                    if not isinstance(data,dict):
                        return make_response({"Error":"Incorrect request data format"},415)
                    required_fields=["name","email","username","password","confirm_password","role","phone_number"]
                    if not all(key in data for key in required_fields):
                        return make_response({"Error":"Missing required fields"},401)
                    username=data.get("username")
                    if username:
                        if username in all_usernames:
                            return make_response({"Error":f"Username {username} already exists"},401)
                    else:
                        return make_response({"Error":f"Username not provided i data"},401)
                    
                    email=data.get("email")
                    if email:
                        if email in all_emails:
                            return make_response({"Error":f"Email {email} already exists"},401)
                    else:
                        return make_response({"Error":f"Email not provided in data"})
                    
                    phone_number=data.get("phone_number")
                    if phone_number:
                        if phone_number in all_phone_nums:
                            return make_response({"Error":f"Pohone number {phone_number} already exists"},401)
                    else:
                        return make_response({"Error":"Phone number not provided in data"},401)
                    
                    for attr,value in data.items():
                        if attr in required_fields:
                            setattr(user,attr,value)
                    db.session.commit()
                    return make_response({"Error":f"{user.username} updated successfully"},200)
                elif request.method=="DELETE":
                    db.session.delete(user)
                    db.session.commit()
                    return make_response({'Error':f"User deleted successfully"},200)
            
            else:
                return make_response({"Error":"User not found"},404)
    except Exception as exc:
        return make_response({"Error":f"{str(exc)}"},500)






    
    


