from flask import Flask
from flask_wtf.csrf import CSRFProtect
# from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message

csrf =CSRFProtect()
mail = Mail()


#instantiate the object of Flask
# app = Flask(__name__)
# app.config.from_pyfile("config.py")
# csrf = CSRFProtect(app)#this protects all our POST routes from csrf attacks whether we are using flaskform or not 
# db = SQLAlchemy(app)#instantialtion sqldatabase connector 





def create_app():
    from bookapp.models import db
    app = Flask(__name__,instance_relative_config=True)
    app.config.from_pyfile("config.py",silent=True)
    db.init_app(app)
    migrate =Migrate(app,db)
    mail.init_app(app)
    csrf.init_app(app)
    return app

app = create_app()



#load routes from here 
from bookapp import admin_routes, user_routes
from bookapp.forms import*