from flask import Flask,render_template,request
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import json
from datetime import datetime
with open('config.json','r') as c:  #paramteres read from config.json file comes in the params variable and can read it
    params=json.load(c)["params"]
local_server=True
app=Flask(__name__)
app.config.update(
    MAIL_SERVER=  'smtp.gmail.com',
    MAIL_PORT= '465',
    MAIL_USE_SSL= True,
    MAIL_USERNAME= params['gmail-user'],
    MAIL_PASSWORD= params['gmail-password']  
)
#function to send the mail using the function imported from flask
mail= Mail(app)
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']
db = SQLAlchemy(app)   #initialisation of the db variable

# make class,equal to the table name which defines the tables of database
#classs name in python always starts with capital letters
class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False )
    phone_num = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    email = db.Column(db.String(20), nullable=False)

class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False )
    slug = db.Column(db.String(21), nullable=False)
    content= db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    img_file = db.Column(db.String(12), nullable=True)

@app.route("/")
def home():
    return render_template('index.html',params=params)
# here we are fetching posts as get requests already stored in the database based on the slug and then passing posts on to the posts.html 
@app.route("/post/<string:post_slug>",methods=['GET'])
def post_route(post_slug):
    post= Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html',params=params,post=post) 
@app.route("/about")
def about():
    return render_template('about.html',params=params)  
@app.route("/contact", methods=["GET","POST"])
def contact():
    if(request.method=='POST'):
        # Add entry to the database
        name=request.form.get('name') #get anything from the form #action in form allows request to be made to contact end point
        email=request.form.get('email')
        phone=request.form.get('phone')
        message=request.form.get('message')
        entry=Contacts(name=name,phone_num=phone,msg=message,date=datetime.now(),email=email)
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from '+name,
                          sender=email,
                          recipients=[params['gmail-user']],
                          body= message+"\n"+phone
                          )
    return render_template('contact.html',params=params)
