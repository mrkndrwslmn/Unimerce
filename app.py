import os
from flask import Flask, render_template, session
from datetime import date, datetime, timedelta
from dotenv import load_dotenv
from routes.address import address_bp
from routes.product import product_bp
from routes.user import user_bp
from routes.seller import seller_bp
from routes.search import search_bp
from helpers.authentication import auth_bp, login_manager
from helpers.data_accessed import fetch_all_categories, fetch_userdetails
from helpers.formatting import currency_format
from routes.product import (
    fetch_top_sales_products,     
    get_active_campaigns, 
    fetch_deals, addFromCart
)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default_secret_key')
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Register blueprints
app.register_blueprint(address_bp, url_prefix='/address')
app.register_blueprint(product_bp, url_prefix='/products')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(auth_bp)
app.register_blueprint(seller_bp, url_prefix='/seller')
app.register_blueprint(search_bp, url_prefix='/search')

app.jinja_env.filters['currency_format'] = currency_format

@app.route('/')
def homepage():
    top_sales = fetch_top_sales_products()
    categories = fetch_all_categories()
    campaigns = get_active_campaigns()
    deals = fetch_deals()

    user = None
    if 'username' in session:
        username = session['username']
        user = fetch_userdetails(username)
    
    return render_template(
        'homepage.html',
        top_sales=top_sales,
        categories=categories,
        campaigns=campaigns,
        deals=deals,
        user=user,
        current_date=datetime.now().date()
    )

# Main entry point
if __name__ == '__main__':
    app.run(debug=True)
