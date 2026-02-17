from flask import Flask, redirect, url_for, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_moment import Moment
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'auth.login' # УВАГА: тепер auth.login

moment = Moment(app)

# ---------------------------------------------------------
# АДМІНКА
# ---------------------------------------------------------
class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login', next=request.url))

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'admin'
        
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login', next=request.url))

admin = Admin(app, name='Help System Admin',
              index_view=MyAdminIndexView(),
              url='/admin')

admin.add_link(MenuLink(name='🏠 На сайт', url='/'))
admin.add_link(MenuLink(name='🚪 Вихід', url='/auth/logout'))

from app import models
from app.models import User, Announcement, Review, Message

admin.add_view(SecureModelView(User, db.session, name="Користувачі"))
admin.add_view(SecureModelView(Announcement, db.session, name="Заявки"))
admin.add_view(SecureModelView(Review, db.session, name="Відгуки"))
admin.add_view(SecureModelView(Message, db.session, name="Повідомлення"))

# ---------------------------------------------------------
# 🔥 РЕЄСТРАЦІЯ BLUEPRINTS (НОВИЙ КОД)
# ---------------------------------------------------------

from app.errors import bp as errors_bp
app.register_blueprint(errors_bp)

from app.auth import bp as auth_bp
app.register_blueprint(auth_bp, url_prefix='/auth')

from app.main import bp as main_bp
app.register_blueprint(main_bp)