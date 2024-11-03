import os
import random
import bcrypt
import smtplib
from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from helpers.database import get_db_connection
from werkzeug.utils import secure_filename
from datetime import datetime

# Create a blueprint for user-related routes
user_bp = Blueprint('user', __name__)

# Helper functions
def send_otp_email(recipient_email, otp, first_name):
    """Send OTP via email."""
    user = "unimerce.ecommerce@gmail.com"
    password = "osww rkmj kpjp tghl"

    subject = "Verify Your Email - Welcome to UNIMERCE!"
    body = f"""
Hello {first_name},

Thank you for signing up with UNIMERCE! Please verify your email to activate your account using the OTP below:

OTP: {otp}

If you didn't request this, please ignore this email. 

Happy Shopping!  
The UNIMERCE Team
"""

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(user, password)
        message = f'Subject: {subject}\n\n{body}'
        server.sendmail(user, recipient_email, message)

def get_account_id(cursor, username):
    """Fetch account ID based on username."""
    cursor.execute("SELECT accountID FROM accountinformation WHERE username = %s", (username,))
    account = cursor.fetchone()
    return account['accountID'] if account else None

# Routes
@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if session.get('logged_in'):
        return redirect(url_for('homepage'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT accountID, username, password, userType 
            FROM accountinformation 
            WHERE username = %s OR email = %s
        """, (username, username))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and bcrypt.checkpw(password.encode(), user['password'].encode()):
            session.update({
                'userID': user['accountID'],
                'username': user['username'],
                'logged_in': True,
                'userType': user['userType']
            })
            flash('Login successful!', 'success')
            return redirect(url_for('super_admin' if user['userType'] == 'superadmin' else 'homepage'))
        flash('Invalid credentials.', 'error')

    return render_template('login.html')

@user_bp.route('/logout', methods=['POST'])
def logout():
    """Handle user logout."""
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('user.login'))

@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if request.method == 'POST':
        if 'otp' in request.form:  # Handle OTP submission
            entered_otp = request.form['otp']
            if entered_otp == str(session.get('otp')):
                conn = get_db_connection()
                cursor = conn.cursor()
                hashed_password = bcrypt.hashpw(session['user_data']['password'].encode(), bcrypt.gensalt())
                user_data = session['user_data']

                cursor.execute("""
                    INSERT INTO accountinformation (username, password, email, userType, firstName, lastName)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (user_data['username'], hashed_password, user_data['email'], 'buyer',
                      user_data['firstname'], user_data['lastname']))
                conn.commit()
                cursor.close()
                conn.close()

                flash('Account created successfully!', 'success')
                session.pop('otp', None)  # Clear OTP from session
                session.pop('otp_sent', None)
                return redirect(url_for('user.login'))
            else:
                flash('Invalid OTP.', 'error')

        user_data = {
            'firstname': request.form['firstname'],
            'lastname': request.form['lastname'],
            'username': request.form['username'],
            'email': request.form['email'],
            'password': request.form['password']
        }
        confirm_password = request.form['confirm-password']

        if user_data['password'] != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('user.register'))

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM accountinformation WHERE username = %s OR email = %s",
                    (user_data['username'], user_data['email']))
        if cursor.fetchone():
            flash('Username or email already exists.', 'error')
            return redirect(url_for('user.register'))

        otp = random.randint(100000, 999999)
        send_otp_email(user_data['email'], otp, user_data['firstname'])

        session.update({'otp': otp, 'user_data': user_data, 'otp_sent': True})
        flash('OTP sent. Please verify to complete registration.', 'info')
        return redirect(url_for('user.register'))

    return render_template('register.html', otp_sent=session.get('otp_sent', False))

@user_bp.route('/otp_verification', methods=['POST', 'GET'])
def otp_verification():
    """Handle OTP verification."""
    if request.method == 'POST':
        entered_otp = request.form['otp']
        if entered_otp == str(session.get('otp')):
            conn = get_db_connection()
            cursor = conn.cursor()
            hashed_password = bcrypt.hashpw(session['user_data']['password'].encode(), bcrypt.gensalt())
            user_data = session['user_data']

            cursor.execute("""
                INSERT INTO accountinformation (username, password, email, userType, firstName, lastName)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_data['username'], hashed_password, user_data['email'], 'buyer',
                  user_data['firstname'], user_data['lastname']))
            conn.commit()

            cursor.close()
            conn.close()

            flash('Account created successfully!', 'success')
            session.pop('otp', None)  # Clear OTP from session
            session.pop('otp_sent', None)
            return redirect(url_for('user.login'))
        else:
            flash('Invalid OTP.', 'error')

    return render_template('otp_verification.html')

@user_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    """Display and update user profile."""
    if not session.get('logged_in'):
        flash('Please log in to access your profile.', 'warning')
        return redirect(url_for('user.login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM accountinformation WHERE username = %s", (session['username'],))
    user = cursor.fetchone()

    if not user.get('profilePic'):
        user['profilePic'] = 'default_profile.jpg'

    if request.method == 'POST':
        profile_data = {
            'firstName': request.form['firstName'],
            'lastName': request.form['lastName'],
            'email': request.form['email'],
            'phone': request.form['phone'],
            'gender': request.form['gender'],
            'dob': request.form['dob']
        }

        cursor.execute("""
            UPDATE accountinformation 
            SET firstName=%s, lastName=%s, email=%s, phoneNumber=%s, gender=%s, dob=%s 
            WHERE accountID = %s
        """, (*profile_data.values(), user['accountID']))

        if 'profile_image' in request.files and request.files['profile_image'].filename != '':
            
            profile_image = request.files['profile_image']
            filename = secure_filename(profile_image.filename)
            unique_filename = f"{user['accountID']}_{filename}"
            
            save_directory = r"C:\Users\marka\Unimerce\static\savedimages"
            os.makedirs(save_directory, exist_ok=True)
            profile_image.save(os.path.join(save_directory, unique_filename))

            cursor.execute("UPDATE accountinformation SET profilePic = %s WHERE accountID = %s",
                        (f"static/savedimages/{unique_filename}", user['accountID']))
        else:
            # Retain the old image if no new image is uploaded
            unique_filename = user['profilePic']

        conn.commit()
        flash('Profile updated successfully!', 'success')

    cursor.close()
    conn.close()

    return render_template('profile.html', user=user)

@user_bp.route('/change_password', methods=['POST'])
def change_password():
    """Change user password."""
    username = session['username']
    old_password = request.form['old_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT password FROM accountinformation WHERE username = %s", (username,))
    user = cursor.fetchone()

    if not user or not bcrypt.checkpw(old_password.encode(), user['password'].encode()):
        flash('Invalid current password.', 'error')
        return redirect(url_for('user.profile'))

    if new_password != confirm_password:
        flash('New passwords do not match.', 'error')
        return redirect(url_for('user.profile'))

    hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
    cursor.execute("UPDATE accountinformation SET password = %s WHERE username = %s",
                   (hashed_password, username))

    conn.commit()
    cursor.close()
    conn.close()

    flash('Password changed successfully!', 'success')
    return redirect(url_for('user.profile'))

# Register the blueprint in the main app
def register_user_blueprint(app):
    """Register the user blueprint."""
    app.register_blueprint(user_bp, url_prefix='/user')
