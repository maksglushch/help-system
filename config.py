import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    
    # ---------------------------------------------------------
    # БАЗА ДАНИХ (PostgreSQL)
    # ---------------------------------------------------------
    
    # Стара SQLite (закоментована, щоб не заважала, але залишилась на пам'ять)
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    #     'sqlite:///' + os.path.join(basedir, 'app.db')

    # Нова PostgreSQL (з твоїм паролем 12344321)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:12344321@localhost:5432/help_system'

    # Цей блок потрібен для майбутнього деплою на Render (там адреса починається з postgres://)
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_TRACK_MODIFICATIONS = False