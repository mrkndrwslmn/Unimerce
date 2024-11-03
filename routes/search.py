from flask import Blueprint, request, render_template, session
from datetime import datetime
from helpers.database import get_db_connection
from helpers.data_accessed import get_categories_and_subcategories
from routes.product import get_search_results

# Create a blueprint for search-related routes
search_bp = Blueprint('search', __name__)

# Routes
@search_bp.route('/search', methods=['GET'])
def search():
    """Handle product search."""
    query = request.args.get('search', '')
    category = request.args.get('category', '')

    search_results = get_search_results(query, category)
    current_date = datetime.now().date()
    categories = get_categories_and_subcategories()

    # Debugging: Check if search results are being returned
    print(f"Search Query: {query}, Category: {category}, Results: {search_results}")

    return render_template('searchresults.html', categories=categories, search_results=search_results, current_date=current_date)

# Helper functions
def save_recent_search(account_id, search_term):
    """Save recent search term in the database."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "INSERT INTO recent_searches (accountID, searchTerm) VALUES (%s, %s)", 
            (account_id, search_term)
        )
        conn.commit()
    except Exception as e:
        print(f"Error saving search: {e}")
    finally:
        cursor.close()
        conn.close()

def get_recent_searches(account_id):
    """Fetch recent search terms from the database."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT searchTerm FROM recent_searches WHERE accountID = %s ORDER BY timestamp DESC LIMIT 5", 
            (account_id,)
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching recent searches: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

# Register the blueprint in the main app
def register_search_blueprint(app):
    """Register the search blueprint."""
    app.register_blueprint(search_bp, url_prefix='/search')
