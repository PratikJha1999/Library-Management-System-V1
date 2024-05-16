from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt,check_password_hash


app = Flask(__name__)
app.config['SECRET_KEY'] = '123456789'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///library.db"
db = SQLAlchemy(app)
app.app_context().push()

bcrypt = Bcrypt(app)




login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.needs_refresh_message_category = 'danger'
login_manager.login_message = u'please login first' 

def create_app():
    from Library.books.routes import bp
    app.register_blueprint(bp)
    from Library.user.routes import bp
    app.register_blueprint(bp)
    from Library.admin.routes import bp
    app.register_blueprint(bp)
    
    return app

