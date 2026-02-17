import unittest
from app import app, db
from app.models import Volunteer

class TestVolunteerApp(unittest.TestCase):
    
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False 
        app.config['WTF_CSRF_CHECK_DEFAULT'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # ТЕСТ 1: Перевірка доступності головної сторінки
    def test_home_page(self):
        """Перевіряємо, чи сервер відповідає кодом 200 на запит головної сторінки"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    # ТЕСТ 2: Перевірка реєстрації волонтера
    def test_volunteer_registration(self):
        """Перевіряємо, чи створюється запис у БД при відправці форми реєстрації"""
        response = self.app.post('/register/volunteer', data={
            'name': 'TestUser',
            'email': 'test@example.com',
            'password': 'password123',
            'password2': 'password123', 
            'submit': True
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        user = db.session.scalar(db.select(Volunteer).where(Volunteer.email == 'test@example.com'))
        self.assertIsNotNone(user, "Помилка: Користувача не знайдено в базі даних після реєстрації.")
        self.assertEqual(user.name, 'TestUser')

    # ТЕСТ 3: Перевірка входу в систему (Login)
    def test_login_process(self):
        """Перевіряємо, чи працює механізм авторизації"""
        u = Volunteer(name='LoginUser', email='login@example.com')
        u.set_password('12345')
        db.session.add(u)
        db.session.commit()

        response = self.app.post('/login/volunteer', data={
            'name': 'LoginUser',
            'password': '12345',
            'remember_me': False
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

    # ТЕСТ 4: Перевірка виходу з системи (Logout)
    def test_logout(self):
        """Перевіряємо, чи працює вихід з аккаунту"""
        u = Volunteer(name='OutUser', email='out@example.com')
        u.set_password('12345')
        db.session.add(u)
        db.session.commit()

        self.app.post('/login/volunteer', data={'name': 'OutUser', 'password': '12345'}, follow_redirects=True)

        response = self.app.get('/logout', follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)

    # ТЕСТ 5: Перевірка безпеки паролів (Unit Test Моделі)
    def test_password_hashing(self):
        """Чистий Unit-тест: перевіряє, чи правильно хешується та перевіряється пароль"""
        u = Volunteer(name='HashTester', email='hash@example.com')
        u.set_password('secret_pass')
    
        self.assertNotEqual(u.password_hash, 'secret_pass')

        self.assertTrue(u.check_password('secret_pass'))

        self.assertFalse(u.check_password('wrong_pass'))

if __name__ == '__main__':
    unittest.main()