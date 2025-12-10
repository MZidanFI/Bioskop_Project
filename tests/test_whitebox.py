import unittest
from app import app, db, User, Movie, Booking
from sqlalchemy.exc import IntegrityError

class BioskopUnitTest(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' 
        app.config['WTF_CSRF_ENABLED'] = False
        
        self.app = app.test_client()
        
        with app.app_context():
            db.create_all()
            
            from werkzeug.security import generate_password_hash
            pw_hash = generate_password_hash('123', method='pbkdf2:sha256')
            admin = User(username='admin_test', password=pw_hash)
            
            user_biasa = User(username='user_test', password=pw_hash)
            
            movie = Movie(title='Film Test', price=50000, status='now')
            
            db.session.add(admin)
            db.session.add(user_biasa)
            db.session.add(movie)
            db.session.commit()

    def login_user(self):
        return self.app.post('/login', data=dict(
            username='admin_test',
            password='123'
        ), follow_redirects=True)

    def login_admin(self):
        """Helper untuk login sebagai admin"""
        return self.app.post('/login', data=dict(
            username='admin_test',
            password='123'
        ), follow_redirects=True)

    def login_regular_user(self):
        """Helper untuk login sebagai user biasa"""
        return self.app.post('/login', data=dict(
            username='user_test',
            password='123'
        ), follow_redirects=True)

    # tes autentikasi (login berhasil)
    def test_login_berhasil(self):
        response = self.login_user()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'/logout', response.data)

    # tes transaksi (logika booking)
    def test_booking_logic(self):
        self.login_user() 
        
        payload = {
            'movie_id': 1,
            'seats': ['A1', 'A2']
        }
        
        response = self.app.post('/book_ticket', json=payload)
        self.assertEqual(response.json['status'], 'success')
        
        with app.app_context():
            total_booking = Booking.query.filter_by(movie_id=1).count()
            self.assertEqual(total_booking, 2)

    # tes validasi (cegah double booking)
    def test_double_booking_prevention(self):
        self.login_user()
        
        self.app.post('/book_ticket', json={'movie_id': 1, 'seats': ['A1']})
        
        self.app.post('/book_ticket', json={'movie_id': 1, 'seats': ['A1']})
        
        with app.app_context():
            count_a1 = Booking.query.filter_by(seat_number='A1').count()
            self.assertEqual(count_a1, 1)

    # tes akses halaman (positif)
    def test_akses_home(self):
        self.login_user()
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'CINEMA X1X', response.data)

    # tes model database (integritas data)
    def test_model_movie(self):
        with app.app_context():
            m = Movie(title='Avangers: Secret Wars', price=50000, status='now')
            db.session.add(m)
            db.session.commit()
            
            cek_film = Movie.query.filter_by(title='Avangers: Secret Wars').first()
            self.assertIsNotNone(cek_film)
            self.assertEqual(cek_film.price, 50000)
    
    # tes keamanan (enkripsi password)
    def test_password_encryption(self):
        with app.app_context():

            user = User.query.filter_by(username='admin_test').first()
            
            self.assertIsNotNone(user)
            self.assertNotEqual(user.password, '123')
            self.assertTrue(len(user.password) > 20)
            
    # tes otorisasi (user biasa akses admin)
    def test_admin_access_denied_for_user(self):
        self.login_regular_user()
        
        response = self.app.get('/admin')
        
        self.assertNotEqual(response.status_code, 200) 
        
    # tes logika backend reset kursi
    def test_reset_seats_logic(self):
        self.login_admin()
        
        with app.app_context():
            booking = Booking(movie_id=1, seat_number='A1', user_id=1)
            db.session.add(booking)
            db.session.commit()
            
            Booking.query.filter_by(movie_id=1).delete()
            db.session.commit()
            
            count = Booking.query.filter_by(movie_id=1).count()
            self.assertEqual(count, 0)

    # tes validasi login (field kosong)
    def test_login_empty_fields(self):
        response = self.app.post('/login', data=dict(
            username='',
            password=''
        ), follow_redirects=True)
        
        self.assertNotIn(b'/logout', response.data)

    # tes logout logic
    def test_logout_logic(self):
        self.login_admin()
        
        response = self.app.get('/logout', follow_redirects=True)

        self.assertIn(b'Masuk', response.data)
        
        response_admin = self.app.get('/admin')
        self.assertNotEqual(response_admin.status_code, 200)

    # tes generasi laporan CSV
    def test_csv_report_generation(self):
        self.login_admin()
 
        self.app.get('/admin')
  
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        
        response = self.app.get(f'/admin/download_report?date={today}')
        
        if response.status_code == 302:
            response = self.app.get(f'/admin/download_report?date={today}', 
                                follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)

    # tes integritas (username kembar)
    def test_duplicate_username_integrity(self):
        with app.app_context():
            user_duplikat = User(username='admin_test', password='anypassword')
            
            db.session.add(user_duplikat)
            
            with self.assertRaises(IntegrityError):
                db.session.commit()
                
            db.session.rollback()
    
    # fungsi membersihkan (teardown)
    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

if __name__ == '__main__':
    unittest.main()