import os
import csv
import io
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import func

app = Flask(__name__)
app.secret_key = 'kunci_rahasia_bioskop'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'bioskop.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db = SQLAlchemy(app)

# --- MODEL DATABASE ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(150), nullable=True)
    description = db.Column(db.Text, nullable=True)
    showtime = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(10), default='now') 

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    seat_number = db.Column(db.String(10), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.String(20), default='booked')

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- ROUTING SYSTEM ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username sudah terpakai!', 'danger')
            return redirect(url_for('register'))
        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash('Registrasi berhasil! Silakan login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('home'))
        flash('Login Gagal! Username atau Password salah.', 'danger')
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Anda berhasil logout.', 'info')
    return redirect(url_for('login'))

@app.route('/')
def home():
    if 'user_id' not in session: return redirect(url_for('login'))
    
    search_query = request.args.get('q')
    
    if search_query:
        # Jika mencari, cari di kedua kategori
        movies_now = Movie.query.filter(Movie.title.ilike(f'%{search_query}%'), Movie.status == 'now').all()
        movies_soon = Movie.query.filter(Movie.title.ilike(f'%{search_query}%'), Movie.status == 'soon').all()
    else:
        # Pisahkan film berdasarkan status
        movies_now = Movie.query.filter_by(status='now').all()
        movies_soon = Movie.query.filter_by(status='soon').all()
        
    return render_template('index.html', movies_now=movies_now, movies_soon=movies_soon, username=session['username'])

@app.route('/movie/details/<int:movie_id>')
def movie_details_only(movie_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    movie = Movie.query.get_or_404(movie_id)
    
    avg_rating = db.session.query(func.avg(Rating.score)).filter_by(movie_id=movie_id).scalar()
    avg_rating = round(avg_rating, 1) if avg_rating else 0.0
    count_rating = Rating.query.filter_by(movie_id=movie_id).count()
    
    my_rating = Rating.query.filter_by(user_id=session['user_id'], movie_id=movie_id).first()
    my_score = my_rating.score if my_rating else 0
    
    return render_template('details.html', movie=movie, avg=avg_rating, count=count_rating, my_score=my_score)

@app.route('/rate_movie/<int:movie_id>', methods=['POST'])
def rate_movie(movie_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    score = int(request.form['score'])
    existing_rating = Rating.query.filter_by(user_id=session['user_id'], movie_id=movie_id).first()
    if existing_rating:
        existing_rating.score = score
        flash('Rating diperbarui!', 'info')
    else:
        db.session.add(Rating(user_id=session['user_id'], movie_id=movie_id, score=score))
        flash('Terima kasih!', 'success')
    db.session.commit()
    return redirect(url_for('movie_details_only', movie_id=movie_id))

@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    movie = Movie.query.get_or_404(movie_id)
    # Validasi: Jika statusnya 'soon', tidak boleh beli tiket
    if movie.status == 'soon':
        flash('Film ini belum tayang, tiket belum bisa dibeli.', 'warning')
        return redirect(url_for('movie_details_only', movie_id=movie.id))
        
    booked_seats = [b.seat_number for b in Booking.query.filter_by(movie_id=movie_id, status='booked').all()]
    return render_template('booking.html', movie=movie, booked_seats=booked_seats)

@app.route('/book_ticket', methods=['POST'])
def book_ticket():
    if 'user_id' not in session: return jsonify({'status': 'error', 'msg': 'Login required'})
    data = request.json
    for seat in data['seats']:
        existing = Booking.query.filter_by(movie_id=data['movie_id'], seat_number=seat, status='booked').first()
        if not existing:
            db.session.add(Booking(user_id=session['user_id'], movie_id=data['movie_id'], seat_number=seat, status='booked'))
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/history')
def history():
    if 'user_id' not in session: return redirect(url_for('login'))
    user_history = db.session.query(Booking, Movie).join(Movie).filter(Booking.user_id == session['user_id']).all()
    return render_template('history.html', history=user_history)

@app.route('/admin')
def admin_panel():
    if session.get('username') != 'admin': 
        flash('Anda bukan admin!', 'warning')
        return redirect(url_for('home'))
    
    movies = Movie.query.all()
    filter_date = request.args.get('date')
    if not filter_date: filter_date = datetime.now().strftime('%Y-%m-%d')
    daily_sales = db.session.query(Booking, User, Movie).join(User).join(Movie).filter(func.date(Booking.booking_date) == filter_date).all()
    daily_revenue = sum(sale[2].price for sale in daily_sales)

    movie_titles = []
    ticket_counts = []
    for movie in movies:
        count = Booking.query.filter_by(movie_id=movie.id).count()
        movie_titles.append(movie.title)
        ticket_counts.append(count)
    
    return render_template('admin.html', movies=movies, daily_sales=daily_sales, daily_revenue=daily_revenue, selected_date=filter_date, chart_labels=movie_titles, chart_values=ticket_counts)

@app.route('/admin/download_report')
def download_report():
    if session.get('username') != 'admin': return redirect(url_for('home'))
    date_str = request.args.get('date')
    if not date_str: return redirect(url_for('admin_panel'))
    sales = db.session.query(Booking, User, Movie).join(User).join(Movie).filter(func.date(Booking.booking_date) == date_str).all()
    output = io.StringIO()
    output.write(u'\ufeff')
    writer = csv.writer(output, delimiter=';')
    writer.writerow(['ID Transaksi', 'Tanggal', 'Jam', 'Username', 'Film', 'Kursi', 'Harga', 'Status'])
    total_revenue = 0
    movie_totals = {}
    for booking, user, movie in sales:
        writer.writerow([booking.id, booking.booking_date.strftime('%Y-%m-%d'), booking.booking_date.strftime('%H:%M:%S'), user.username, movie.title, booking.seat_number, movie.price, booking.status])
        if booking.status == 'booked' or booking.status == 'history':
            total_revenue += movie.price
            if movie.title in movie_totals: movie_totals[movie.title] += movie.price
            else: movie_totals[movie.title] = movie.price
    writer.writerow([]); writer.writerow([])
    writer.writerow(['', '', '', '', '--- RINCIAN PER FILM ---', '', '', ''])
    for title, amount in movie_totals.items(): writer.writerow(['', '', '', '', title, 'Total:', amount, ''])
    writer.writerow([]); writer.writerow(['', '', '', '', 'GRAND TOTAL HARI INI', '', total_revenue, ''])
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode('utf-8-sig')), mimetype='text/csv', as_attachment=True, download_name=f'Laporan_{date_str}.csv')

@app.route('/admin/add_movie', methods=['POST'])
def add_movie():
    if session.get('username') != 'admin': return redirect(url_for('home'))
    title = request.form['title']
    price = request.form['price']
    description = request.form['description']
    showtime = request.form['showtime']
    status = request.form['status'] # Ambil status dari form
    
    file = request.files['image']
    filename = None
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    # Simpan ke DB dengan status
    new_movie = Movie(title=title, price=int(price), image=filename, description=description, showtime=showtime, status=status)
    db.session.add(new_movie)
    db.session.commit()
    flash('Film berhasil ditambahkan!', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete_movie/<int:id>')
def delete_movie(id):
    if session.get('username') != 'admin': return redirect(url_for('home'))
    movie = Movie.query.get_or_404(id)
    if movie.image:
        try: os.remove(os.path.join(app.config['UPLOAD_FOLDER'], movie.image))
        except: pass
    Booking.query.filter_by(movie_id=id).delete()
    Rating.query.filter_by(movie_id=id).delete()
    db.session.delete(movie)
    db.session.commit()
    flash('Film berhasil dihapus.', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/reset_seats/<int:movie_id>')
def reset_seats(movie_id):
    if session.get('username') != 'admin': return redirect(url_for('home'))
    active_bookings = Booking.query.filter_by(movie_id=movie_id, status='booked').all()
    count = 0
    for booking in active_bookings:
        booking.status = 'history'
        count += 1
    db.session.commit()
    if count > 0: flash(f'{count} kursi berhasil di-reset.', 'success')
    else: flash('Studio sudah kosong.', 'info')
    return redirect(url_for('admin_panel'))

@app.route('/admin/edit_movie/<int:id>', methods=['GET', 'POST'])
def edit_movie(id):
    # 1. Cek Admin (PERBAIKAN DI SINI)
    # Gunakan 'username', bukan 'role', sesuai dengan fungsi login kamu
    if session.get('username') != 'admin':
        flash('Anda bukan admin!', 'danger')
        return redirect(url_for('home'))
    
    # 2. Ambil Data Film dari Database
    movie = Movie.query.get_or_404(id)

    # 3. Jika Tombol Simpan Ditekan (POST)
    if request.method == 'POST':
        movie.title = request.form['title']
        movie.price = request.form['price']
        movie.status = request.form['status']
        movie.description = request.form['description']
        movie.showtime = request.form['showtime']

        # Cek apakah ada upload gambar baru
        image = request.files['image']
        if image and image.filename != '':
            if allowed_file(image.filename): # Tambahkan validasi allowed_file agar aman
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                movie.image = filename
        
        db.session.commit()
        flash('Data film berhasil diperbarui!', 'success') # Tambahkan notifikasi
        return redirect(url_for('admin_panel')) # Gunakan url_for agar lebih rapi

    # 4. Jika baru buka halaman (GET)
    return render_template('edit_movie.html', movie=movie)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin_pw = generate_password_hash('123', method='pbkdf2:sha256')
            db.session.add(User(username='admin', password=admin_pw))
            if not Movie.query.first():
                # Data Dummy 1: Now Showing
                db.session.add(Movie(title='Avengers: Secret Wars', price=50000, showtime='12:00', status='now')) 
                # Data Dummy 2: Coming Soon
                db.session.add(Movie(title='Moana 2', price=45000, description='Segera di bioskop...', showtime='Coming Soon', status='soon')) 
            db.session.commit()
    app.run(debug=True)