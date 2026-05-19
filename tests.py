import unittest
from app import app, db
from app.models import User

class TestHelpSystemApp(unittest.TestCase):
    
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

    def test_home_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_volunteer_registration(self):
        # ВИПРАВЛЕНО ШЛЯХ: /auth/register/volunteer
        response = self.app.post('/auth/register/volunteer', data={
            'name': 'TestUser',
            'email': 'test@example.com',
            'password': 'password123',
            'password2': 'password123', 
            'submit': True
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        user = db.session.scalar(db.select(User).where(User.email == 'test@example.com'))
        self.assertIsNotNone(user, "Помилка: Користувача не знайдено.")
        self.assertEqual(user.name, 'TestUser')
        self.assertEqual(user.role, 'volunteer')

    def test_login_process(self):
        u = User(name='LoginUser', email='login@example.com', role='volunteer')
        u.set_password('12345')
        db.session.add(u)
        db.session.commit()

        # ВИПРАВЛЕНО ШЛЯХ: /auth/login/volunteer
        response = self.app.post('/auth/login/volunteer', data={
            'name': 'LoginUser',
            'password': '12345',
            'remember_me': False
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        u = User(name='OutUser', email='out@example.com', role='volunteer')
        u.set_password('12345')
        db.session.add(u)
        db.session.commit()

        self.app.post('/auth/login/volunteer', data={'name': 'OutUser', 'password': '12345'}, follow_redirects=True)

        # ВИПРАВЛЕНО ШЛЯХ: /auth/logout
        response = self.app.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_password_hashing(self):
        u = User(name='HashTester', email='hash@example.com', role='volunteer')
        u.set_password('secret_pass')
    
        self.assertNotEqual(u.password_hash, 'secret_pass')
        self.assertTrue(u.check_password('secret_pass'))
        self.assertFalse(u.check_password('wrong_pass'))

if __name__ == '__main__':
    unittest.main()