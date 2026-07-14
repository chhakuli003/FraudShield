from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.secret_key = "fraudshield_secret_key"

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fraud.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -----------------------------
# Database Models
# -----------------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100))
    email = db.Column(db.String(100))
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    amount = db.Column(db.Float)
    location = db.Column(db.String(100))
    status = db.Column(db.String(20))

# -----------------------------
# Home Page
# -----------------------------

@app.route('/')
def home():
    return render_template('index.html')

# -----------------------------
# Register
# -----------------------------

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        fullname = request.form['fullname']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("Passwords do not match")
            return redirect('/register')

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash("Username already exists")
            return redirect('/register')

        new_user = User(
            fullname=fullname,
            email=email,
            username=username,
            password=password
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registration Successful")
        return redirect('/login')

    return render_template('register.html')

# -----------------------------
# Login
# -----------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(
            username=username,
            password=password
        ).first()

        if user:

            session['username'] = username

            return redirect('/dashboard')

        else:

            flash("Invalid Username or Password")

    return render_template('login.html')

# -----------------------------
# Dashboard
# -----------------------------

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():

    if 'username' not in session:
        return redirect('/login')

    if request.method == 'POST':
        print(request.form)

        amount = float(request.form['amount'])
        location = request.form['location']

        # Fraud Detection Rules

        if amount > 500000:
            status = "FRAUD"

        elif location.lower() != "india":
            status = "SUSPICIOUS"

        else:
            status = "SAFE"

        transaction = Transaction(
            username=session['username'],
            amount=amount,
            location=location,
            status=status
        )

        db.session.add(transaction)
        db.session.commit()

        flash(f"Transaction Submitted. Status: {status}")
        return redirect('/dashboard')

    return render_template('dashboard.html')

# -----------------------------
# Admin Panel
# -----------------------------

@app.route('/admin')
def admin():

    transactions = Transaction.query.all()

    total = Transaction.query.count()

    fraud = Transaction.query.filter_by(status="FRAUD").count()

    safe = Transaction.query.filter_by(status="SAFE").count()

    suspicious = Transaction.query.filter_by(status="SUSPICIOUS").count()

    return render_template(
        'admin.html',
        transactions=transactions,
        total=total,
        fraud=fraud,
        safe=safe,
        suspicious=suspicious
    )

# -----------------------------
# Logout
# -----------------------------

@app.route('/logout')
def logout():

    session.pop('username', None)

    flash("Logged Out Successfully")

    return redirect('/')

# -----------------------------
# Create Database
# -----------------------------

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)
    