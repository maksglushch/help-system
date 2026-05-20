from flask import render_template, redirect, url_for, flash, request
from urllib.parse import urlsplit
from flask_login import login_user, logout_user, current_user
import sqlalchemy as sa
from app import db
from app.auth import bp
from app.forms import LoginForm, RegistrationForm
from app.models import User
from datetime import datetime, timedelta, timezone

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
        
        # 1. Якщо такого юзера взагалі немає
        if user is None:
            flash('Невірне ім’я або пароль.', 'danger')
            return redirect(url_for('auth.login', user_type=user_type))

        # 2. ПЕРЕВІРКА НА БЛОКУВАННЯ: чи не заблокований він зараз?
        if user.locked_until and user.locked_until > datetime.now(timezone.utc):
            time_left = (user.locked_until - datetime.now(timezone.utc)).seconds // 60 + 1
            flash(f'⛔ Акаунт тимчасово заблоковано. Спробуйте через {time_left} хв.', 'danger')
            return redirect(url_for('auth.login', user_type=user_type))

        # 3. Якщо пароль неправильний (рахуємо спроби)
        if not user.check_password(form.password.data):
            user.failed_login_attempts += 1
            
            # Якщо помилився 3 рази - блокуємо на 5 хвилин
            if user.failed_login_attempts >= 3:
                user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=5)
                user.failed_login_attempts = 0 # Скидаємо лічильник для наступного разу
                db.session.commit()
                flash('🚨 Забагато невдалих спроб! Акаунт заблоковано на 5 хвилин.', 'danger')
            else:
                db.session.commit()
                flash(f'Невірний пароль. Залишилось спроб: {3 - user.failed_login_attempts}', 'warning')
                
            return redirect(url_for('auth.login', user_type=user_type))

        # 4. Якщо пароль ПРАВИЛЬНИЙ - обнуляємо помилки і пускаємо
        user.failed_login_attempts = 0
        user.locked_until = None
        db.session.commit()

        login_user(user, remember=form.remember_me.data)
        
        if user.role == 'admin':
            return redirect('/admin')

        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('main.user_profile', name=user.name)
        return redirect(next_page)

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