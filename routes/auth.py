from flask import Blueprint,session,request

import pymongo
import bcrypt
auth = Blueprint('simple_page', __name__)
auth.secret_key="xd"
client = pymongo.MongoClient("mongodb://localhost:27017/myapp")
db = client.get_database('total_records')
records = db.register
@auth.route("/", methods=['post', 'get'])
def index():
    message = ''
    if "email" in session:
        return redirect(url_for("logged_in"))
    if request.method == "POST":
        user = request.form.get("fullname")
        email = request.form.get("email")
        
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        
        user_found = records.find_one({"name": user})
        email_found = records.find_one({"email": email})
        if user_found:
            message = 'There already is a user by that name'
            return {"message":message}
        if email_found:
            message = 'This email already exists in database'
            return {"message":message}
        if password1 != password2:
            message = 'Passwords should match!'
            return {"message":message}
        else:
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            user_input = {'name': user, 'email': email, 'password': hashed}
            records.insert_one(user_input)
            
            user_data = records.find_one({"email": email})
            new_email = user_data['email']
   
            return {"message":"logged in ","new_email":new_email}
    return {message:"Success"}