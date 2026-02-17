import os
from app import app, db
from flask_migrate import upgrade

# Цей блок автоматично запустить 'flask db upgrade' при старті на сервері
with app.app_context():
    # Якщо ми в інтернеті (на Render), запускаємо міграцію
    if os.environ.get('RENDER'):
        print("Запуск міграції бази даних...")
        upgrade()
        print("Міграція завершена!")

if __name__ == '__main__':
    app.run()