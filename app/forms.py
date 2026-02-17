from flask_wtf import FlaskForm
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
    # ДОДАЛИ ЦІ ДВА ПОЛЯ 👇
    about_me = TextAreaField('Про себе', validators=[Length(min=0, max=140)])
    contact_info = StringField('Контактна інформація (Телефон/Telegram)', validators=[Length(min=0, max=140)])
    submit = SubmitField('Зберегти')

    def __init__(self, original_name, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_name = original_name

    def validate_name(self, name):
        if name.data != self.original_name:
            user = db.session.scalar(sa.select(User).where(User.name == name.data))
            if user is not None:
                raise ValidationError("Це ім'я вже зайняте.")

class AnnouncementForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired(), Length(min=1, max=100)])
    text = TextAreaField('Опис проблеми', validators=[DataRequired(), Length(min=1, max=500)])
    # Приховані поля для координат (заповнюються через JavaScript)
    lat = FloatField('Lat', validators=[DataRequired()])
    lng = FloatField('Lng', validators=[DataRequired()])
    submit = SubmitField('Створити заявку')

class ReviewForm(FlaskForm):
    rating = SelectField('Оцінка', choices=[(5, '⭐⭐⭐⭐⭐ (5)'), (4, '⭐⭐⭐⭐ (4)'), (3, '⭐⭐⭐ (3)'), (2, '⭐⭐ (2)'), (1, '⭐ (1)')], validators=[DataRequired()])
    body = TextAreaField('Ваш відгук', validators=[DataRequired(), Length(min=1, max=200)])
    submit = SubmitField('Надіслати відгук')

class MessageForm(FlaskForm):
    message = StringField('Повідомлення', validators=[DataRequired(), Length(min=1, max=500)])
    submit = SubmitField('Надіслати')