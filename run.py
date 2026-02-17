import os
from app import app, db
from flask_migrate import upgrade

# Цей блок автоматично запустить 'flask db upgrade' при старті на сервері
with app.app_context():
    # Якщо ми в інтернеті (на Render), запускаємо міграцію
    if os.environ.get('RENDER'):
        print("Запуск міграції бази даних...")
        upgrade()
        from app.models import User
        user = db.session.scalar(sa.select(User).where(User.name == 'Максим Глущенко'))
        if user:
            user.role = 'admin'
            db.session.commit()
            print("Максим тепер Адмін! 🦸‍♂️")
        print("Міграція завершена!")

if __name__ == '__main__':
    app.run()