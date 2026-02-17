from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5

# ЗАГРУЗКА ПОЛЬЗОВАТЕЛЯ (Flask-Login)
@login.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# ЕДИНАЯ МОДЕЛЬ ПОЛЬЗОВАТЕЛЯ
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    
    # Общие поля для всех
    name: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[str] = so.mapped_column(sa.String(256))
    
    # Дополнительные поля (телефон, о себе)
    phone: so.Mapped[Optional[str]] = so.mapped_column(sa.String(20), nullable=True)
    
    # 🔥 ОСЬ ВОНИ, ДОДАНІ ПОЛЯ:
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140), nullable=True)
    contact_info: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140), nullable=True)
    
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(default=lambda: datetime.now(timezone.utc))

    # РОЛЬ ПОЛЬЗОВАТЕЛЯ
    role: so.Mapped[str] = so.mapped_column(sa.String(20), default='needy')

    # Связи с заявками
    created_announcements: so.Mapped[list['Announcement']] = so.relationship(
        'Announcement', foreign_keys='Announcement.needy_id',
        back_populates='author', lazy='select'
    )

    taken_announcements: so.Mapped[list['Announcement']] = so.relationship(
        'Announcement', foreign_keys='Announcement.volunteer_id',
        back_populates='volunteer', lazy='select'
    )

    reviews_written: so.Mapped[list['Review']] = so.relationship(
        'Review', foreign_keys='Review.author_id', back_populates='author', lazy='select'
    )
    reviews_received: so.Mapped[list['Review']] = so.relationship(
        'Review', foreign_keys='Review.recipient_id', back_populates='recipient', lazy='select'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'
    
    @property
    def is_volunteer(self):
        return self.role == 'volunteer'

    @property
    def is_needy(self):
        return self.role == 'needy'

    def __repr__(self):
        return f'<User {self.name} ({self.role})>'
    
    def get_rating(self):
        # Тут треба імпортувати Review всередині методу, щоб уникнути циклічного імпорту
        # Але оскільки Review визначено нижче, це може бути проблемою.
        # Краще використовувати db.session.scalars
        reviews = self.reviews_received
        if not reviews:
            return 0
        total = sum([r.rating for r in reviews])
        return round(total / len(reviews), 1)


# МОДЕЛЬ ЗАЯВКИ
class Announcement(db.Model):
    __tablename__ = 'announcement'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String(100))
    text: so.Mapped[str] = so.mapped_column(sa.String(500))
    timestamp: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.utcnow)
    status: so.Mapped[str] = so.mapped_column(sa.String(20), default='open')

    lat: so.Mapped[Optional[float]] = so.mapped_column(sa.Float, nullable=True)
    lng: so.Mapped[Optional[float]] = so.mapped_column(sa.Float, nullable=True)

    needy_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('users.id'))
    author: so.Mapped['User'] = so.relationship(
        foreign_keys=[needy_id], back_populates='created_announcements'
    )

    volunteer_id: so.Mapped[Optional[int]] = so.mapped_column(sa.ForeignKey('users.id'), nullable=True)
    volunteer: so.Mapped['User'] = so.relationship(
        foreign_keys=[volunteer_id], back_populates='taken_announcements'
    )

    messages: so.Mapped[list['Message']] = so.relationship(
        'Message', back_populates='announcement', cascade="all, delete-orphan", lazy='select'
    )

    def __repr__(self):
        return f"<Announcement '{self.title}' ({self.status})>"


class Review(db.Model):
    __tablename__ = 'review'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(200))
    rating: so.Mapped[int] = so.mapped_column(sa.Integer)
    timestamp: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.utcnow)

    author_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('users.id'))
    recipient_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('users.id'))

    author: so.Mapped['User'] = so.relationship(foreign_keys=[author_id], back_populates='reviews_written')
    recipient: so.Mapped['User'] = so.relationship(foreign_keys=[recipient_id], back_populates='reviews_received')

    def __repr__(self):
        return f'<Review {self.rating} stars>' 
    
class Message(db.Model):
    __tablename__ = 'message'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(500))
    timestamp: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.utcnow)

    sender_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('users.id'))
    announcement_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('announcement.id'))

    sender: so.Mapped['User'] = so.relationship(foreign_keys=[sender_id])
    announcement: so.Mapped['Announcement'] = so.relationship(foreign_keys=[announcement_id], back_populates='messages')

    def __repr__(self):
        return f'<Message {self.body}>'