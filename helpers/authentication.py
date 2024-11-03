from flask import Blueprint, redirect, url_for, flash, session
from flask_dance.contrib.google import make_google_blueprint, google
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from helpers.database import get_db_connection
import bcrypt

auth_bp = Blueprint('auth', __name__)

login_manager = LoginManager()
login_manager.login_view = "auth.google_login"

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

@login_manager.user_loader
def load_user(user_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM accountinformation WHERE accountID = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    connection.close()
    return User(user["accountID"]) if user else None

# Set up Google OAuth
google_bp = make_google_blueprint(
    client_id="652272862984-ucgu6qq0tnbgh6ni0hhakvfi92aqctt9.apps.googleusercontent.com",
    client_secret="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",
    redirect_to="auth.google_callback"
)
auth_bp.register_blueprint(google_bp, url_prefix="/login")

@auth_bp.route('/google_login')
def google_login():
    return redirect(url_for("google.login"))

@auth_bp.route('/google_callback')
def google_callback():
    if not google.authorized:
        flash("Authorization failed.", "danger")
        return redirect(url_for("auth.google_login"))

    resp = google.get("/oauth2/v1/userinfo")
    if not resp.ok:
        flash("Failed to fetch user info.", "danger")
        return redirect(url_for("auth.google_login"))

    user_info = resp.json()
    user = save_or_fetch_user(user_info)
    login_user(user)
    flash("Successfully logged in!", "success")
    return redirect(url_for("homepage"))

def save_or_fetch_user(user_info):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM accountinformation WHERE provider_id = %s AND provider = 'google'",
        (user_info["id"],)
    )
    user = cursor.fetchone()

    if not user:
        cursor.execute(
            """
            INSERT INTO accountinformation 
            (firstName, lastName, email, username, provider, provider_id, createdAt) 
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """,
            (
                user_info["given_name"],
                user_info["family_name"],
                user_info["email"],
                user_info["email"],
                "google",
                user_info["id"]
            )
        )
        connection.commit()
        user_id = cursor.lastrowid
    else:
        user_id = user["accountID"]

    cursor.close()
    connection.close()
    return User(user_id)

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash("Logged out successfully!", "success")
    return redirect(url_for("auth.google_login"))

def hash_password(plain_password):
    """Hash a plain password."""
    return bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt())

def check_password(plain_password, hashed_password):
    """Check if the plain password matches the hashed password."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)
