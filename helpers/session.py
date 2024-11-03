from flask import session, redirect, url_for, flash

def login_user(user_id, username, user_type):
    """Log in a user by storing their information in the session."""
    session['userID'] = user_id
    session['username'] = username
    session['userType'] = user_type
    session['logged_in'] = True

def logout_user():
    """Log out the current user."""
    session.clear()
    flash("You have been logged out.", "success")

def is_logged_in():
    """Check if the user is currently logged in."""
    return session.get('logged_in', False)

def ensure_logged_in():
    """Redirect to login page if the user is not logged in."""
    if not is_logged_in():
        flash("Please log in to continue.", "warning")
        return redirect(url_for('login'))
