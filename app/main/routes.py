from datetime import datetime
import sqlalchemy as sa
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.main import bp
from app.forms import EditProfileForm, AnnouncementForm, ReviewForm, MessageForm
from app.models import User, Announcement, Review, Message

# ---------------------------------------------------------
# ГОЛОВНА СТОРІНКА
# ---------------------------------------------------------
@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html', title='Головна')

# ---------------------------------------------------------
# ПРО НАС
# ---------------------------------------------------------
@bp.route('/about')
def about():
    return render_template('about.html', title='Про нас')

# ---------------------------------------------------------
# ПРОФІЛЬ КОРИСТУВАЧА
# ---------------------------------------------------------
@bp.route('/user/<name>')
@login_required
def user_profile(name):
    user = db.first_or_404(sa.select(User).where(User.name == name))
    
    if user.role == 'admin':
        return redirect('/admin')

    if user.role == 'volunteer':
        return render_template('volunteer.html', volunteer=user)
    
    elif user.role == 'needy':
        announcements = db.session.scalars(
            sa.select(Announcement).where(Announcement.author == user).order_by(Announcement.timestamp.desc())
        ).all()
        return render_template('needy.html', needy=user, announcements=announcements)
    
    return render_template('404.html')

# ---------------------------------------------------------
# РЕДАГУВАННЯ ПРОФІЛЮ (ВИПРАВЛЕНО!)
# ---------------------------------------------------------
@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    # Передаємо поточне ім'я для валідації
    form = EditProfileForm(current_user.name)
    if form.validate_on_submit():
        # БУЛО: form.username.data -> СТАЛО: form.name.data
        current_user.name = form.name.data
        current_user.about_me = form.about_me.data
        current_user.contact_info = form.contact_info.data
        db.session.commit()
        flash('Зміни збережено.')
        return redirect(url_for('main.user_profile', name=current_user.name))
    elif request.method == 'GET':
        # БУЛО: form.username.data -> СТАЛО: form.name.data
        form.name.data = current_user.name
        form.about_me.data = current_user.about_me
        form.contact_info.data = current_user.contact_info
    return render_template('edit_profile.html', title='Редагувати профіль', form=form)

# ---------------------------------------------------------
# СТВОРЕННЯ ЗАЯВКИ (ВИПРАВЛЕНО!)
# ---------------------------------------------------------
@bp.route('/create_announcement', methods=['GET', 'POST'])
@login_required
def create_announcement():
    if current_user.role != 'needy':
        flash('Тільки користувачі, які потребують допомоги, можуть створювати заявки.')
        return redirect(url_for('main.index'))
    
    form = AnnouncementForm()
    if form.validate_on_submit():
        announcement = Announcement(
            title=form.title.data,
            # БУЛО: form.description.data -> СТАЛО: form.text.data (як у шаблоні)
            text=form.text.data, 
            lat=form.lat.data,
            lng=form.lng.data,
            author=current_user,
            status='open'
        )
        db.session.add(announcement)
        db.session.commit()
        flash('Ваша заявка створена!')
        return redirect(url_for('main.user_profile', name=current_user.name))
        
    return render_template('create_announcement.html', title='Створити заявку', form=form)

# ---------------------------------------------------------
# СПИСОК ВСІХ ЗАЯВОК
# ---------------------------------------------------------
@bp.route('/announcements', methods=['GET', 'POST'])
@login_required
def announcements():
    if current_user.role != 'volunteer':
        flash('Ця сторінка доступна тільки волонтерам.')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        announcement_id = request.form.get('announcement_id')
        announcement = db.session.get(Announcement, announcement_id)
        if announcement and announcement.status == 'open':
            announcement.status = 'accepted'
            announcement.volunteer_id = current_user.id
            db.session.commit()
            flash(f'Ви взяли заявку "{announcement.title}" в роботу!')
            return redirect(url_for('main.active_requests'))

    query = sa.select(Announcement).where(Announcement.status == 'open').order_by(Announcement.timestamp.desc())
    announcements_list = db.session.scalars(query).all()
    
    return render_template('announcements.html', title='Всі заявки', announcements=announcements_list)

# ---------------------------------------------------------
# МОЇ АКТИВНІ ЗАВДАННЯ
# ---------------------------------------------------------
@bp.route('/active_requests')
@login_required
def active_requests():
    if current_user.role != 'volunteer':
        return redirect(url_for('main.index'))
    
    my_requests = db.session.scalars(
        sa.select(Announcement).where(
            Announcement.volunteer_id == current_user.id,
            Announcement.status == 'accepted' 
        )
    ).all()
    
    return render_template('active_requests.html', requests=my_requests)

# ---------------------------------------------------------
# ЗАВЕРШИТИ ЗАЯВКУ
# ---------------------------------------------------------
@bp.route('/complete_request/<int:announcement_id>')
@login_required
def complete_request(announcement_id):
    ann = db.session.get(Announcement, announcement_id)
    if ann and ann.volunteer_id == current_user.id:
        ann.status = 'completed'
        db.session.commit()
        flash('Заявку позначено як виконану! Дякуємо.')
    return redirect(url_for('main.active_requests'))

# ---------------------------------------------------------
# СКАСУВАТИ ЗАЯВКУ
# ---------------------------------------------------------
@bp.route('/cancel_request/<int:announcement_id>')
@login_required
def cancel_request(announcement_id):
    ann = db.session.get(Announcement, announcement_id)
    if ann and ann.volunteer_id == current_user.id:
        ann.status = 'open'
        ann.volunteer_id = None
        db.session.commit()
        flash('Ви відмовились від виконання заявки.')
    return redirect(url_for('main.active_requests'))

# ---------------------------------------------------------
# НАПИСАТИ ВІДГУК
# ---------------------------------------------------------
@bp.route('/leave_review/<int:volunteer_id>', methods=['GET', 'POST'])
@login_required
def leave_review(volunteer_id):
    if current_user.id == volunteer_id:
        flash("Ви не можете оцінювати самі себе.")
        return redirect(url_for('main.user_profile', name=current_user.name))

    volunteer = db.session.get(User, volunteer_id)
    if not volunteer:
        flash("Користувача не знайдено.")
        return redirect(url_for('main.index'))

    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(
            body=form.body.data,
            rating=int(form.rating.data),
            author=current_user,
            recipient=volunteer
        )
        db.session.add(review)
        db.session.commit()
        flash("Дякуємо! Ваш відгук збережено.")
        return redirect(url_for('main.user_profile', name=volunteer.name))

    return render_template('leave_review.html', form=form, volunteer=volunteer)

# ---------------------------------------------------------
# ЧАТ
# ---------------------------------------------------------
@bp.route('/chat/<int:announcement_id>', methods=['GET', 'POST'])
@login_required
def chat(announcement_id):
    ann = db.session.get(Announcement, announcement_id)
    
    if not ann:
        flash("Заявку не знайдено.")
        return redirect(url_for('main.index'))

    if current_user.id != ann.needy_id and current_user.id != ann.volunteer_id:
        flash("У вас немає доступу до цього чату.")
        return redirect(url_for('main.index'))

    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(
            body=form.message.data,
            sender=current_user,
            announcement=ann
        )
        db.session.add(msg)
        db.session.commit()
        return redirect(url_for('main.chat', announcement_id=announcement_id))

    messages = db.session.scalars(
        sa.select(Message).where(Message.announcement_id == announcement_id).order_by(Message.timestamp)
    ).all()

    return render_template('chat.html', title="Чат", form=form, ann=ann, messages=messages)

# ---------------------------------------------------------
# API ДЛЯ ЧАТУ
# ---------------------------------------------------------
@bp.route('/api/messages/<int:announcement_id>')
@login_required
def get_messages(announcement_id):
    ann = db.session.get(Announcement, announcement_id)
    if current_user.id != ann.needy_id and current_user.id != ann.volunteer_id:
        return jsonify([])

    messages = db.session.scalars(
        sa.select(Message).where(Message.announcement_id == announcement_id).order_by(Message.timestamp)
    ).all()

    data = []
    for msg in messages:
        data.append({
            'user': msg.sender.name,
            'avatar': msg.sender.avatar(36),
            'body': msg.body,
            'is_me': (msg.sender_id == current_user.id),
            'time': msg.timestamp.strftime('%H:%M')
        })
    return jsonify(data)