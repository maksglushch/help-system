from flask import render_template, redirect, url_for, flash, request
from urllib.parse import urlsplit
from flask_login import login_user, logout_user, current_user
import sqlalchemy as sa
from app import db
from app.auth import bp
from app.forms import LoginForm, RegistrationForm
from app.models import User

@bp.route('/login', methods=['GET', 'POST'])
@bp.route('/login/<user_type>', methods=['GET', 'POST'])
def login(user_type=None):
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect('/admin')
        return redirect(url_for('main.user_profile', name=current_user.name))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.name == form.name.data))
        
        if user is None or not user.check_password(form.password.data):
            flash('Невірне ім’я або пароль.')
            return redirect(url_for('auth.login', user_type=user_type))

        login_user(user, remember=form.remember_me.data)
        
        if user.role == 'admin':
            return redirect('/admin')

        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('main.user_profile', name=user.name)
        return redirect(next_page)

    # 🔥 ОСЬ ТУТ БУЛА ПРОБЛЕМА: ми не передавали user_type у шаблон
    return render_template('login.html', title='Вхід', form=form, user_type=user_type)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
@bp.route('/register/<user_type>', methods=['GET', 'POST'])
def register(user_type='needy'):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(name=form.name.data, email=form.email.data, role=user_type)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Вітаємо, ви зареєстровані! Тепер увійдіть.')
        # Після реєстрації перекидаємо на логін ТОГО Ж типу
        return redirect(url_for('auth.login', user_type=user_type))
        
    return render_template('register.html', title='Реєстрація', form=form, user_type=user_type)