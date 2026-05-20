from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed # 🔥 ДОДАНО ДЛЯ ФАЙЛІВ
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FloatField, SelectField, HiddenField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
import sqlalchemy as sa
from app import db
from app.models import User

class LoginForm(FlaskForm):
    name = StringField("Ім'я користувача", validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField("Запам'ятати мене")
    submit = SubmitField('Увійти')

class RegistrationForm(FlaskForm):
    name = StringField("Ім'я користувача", validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Повторіть пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зареєструватися')

    def validate_name(self, name):
        user = db.session.scalar(sa.select(User).where(User.name == name.data))
        if user is not None:
            raise ValidationError("Це ім'я вже зайняте.")

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(User.email == email.data))
        if user is not None:
            raise ValidationError('Цей email вже використовується.')

class EditProfileForm(FlaskForm):
    name = StringField("Ім'я користувача", validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Телефон', validators=[Length(min=0, max=20)])
    city = StringField('Місто', validators=[Length(min=0, max=64)])
    about_me = TextAreaField('Про себе', validators=[Length(min=0, max=140)])
    contact_info = StringField('Інші контакти (Telegram тощо)', validators=[Length(min=0, max=140)])
    avatar = FileField('Оновити фото профілю', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Тільки зображення!')])
    submit = SubmitField('Зберегти зміни')

    def __init__(self, original_name, original_email, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_name = original_name
        self.original_email = original_email

    def validate_name(self, name):
        if name.data != self.original_name:
            user = db.session.scalar(sa.select(User).where(User.name == name.data))
            if user is not None:
                raise ValidationError("Це ім'я вже зайняте.")
                
    def validate_email(self, email):
        if email.data != self.original_email:
            user = db.session.scalar(sa.select(User).where(User.email == email.data))
            if user is not None:
                raise ValidationError("Цей email вже використовується.")

class AnnouncementForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired(), Length(min=1, max=100)])
    text = TextAreaField('Опис проблеми', validators=[DataRequired(), Length(min=1, max=500)])
    
    # 🔥 ДОДАЛИ ГАЛОЧКУ:
    is_urgent = BooleanField('🚨 Це критична ситуація (Потрібна термінова допомога)')
    
    # Приховані поля для координат...
    lat = FloatField('Lat', validators=[DataRequired()])
    lng = FloatField('Lng', validators=[DataRequired()])
    submit = SubmitField('Створити заявку')

class ReviewForm(FlaskForm):
    rating = SelectField('Оцінка', choices=[(5, '⭐⭐⭐⭐⭐ (5)'), (4, '⭐⭐⭐⭐ (4)'), (3, '⭐⭐⭐ (3)'), (2, '⭐⭐ (2)'), (1, '⭐ (1)')], coerce=int, validators=[DataRequired()])
    # 🔥 Видалили DataRequired(), тепер текст писати не обов'язково!
    body = TextAreaField('Ваш відгук', validators=[Length(min=0, max=200)])
    submit = SubmitField('Надіслати відгук')

class MessageForm(FlaskForm):
    message = StringField('Повідомлення', validators=[DataRequired(), Length(min=1, max=500)])
    submit = SubmitField('Надіслати')