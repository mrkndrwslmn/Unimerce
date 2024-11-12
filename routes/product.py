from flask import Blueprint, request, render_template, redirect, url_for, session, flash, jsonify, abort
from helpers.database import get_db_connection
from werkzeug.utils import secure_filename
from helpers.data_accessed import get_seller_info_by_product_id, fetch_all_categories, get_product_reviews, fetch_userdetails
from helpers.formatting import currency_format
import os
from rapidfuzz import process

# Create the product blueprint
product_bp = Blueprint('product', __name__)

# Helper functions
def get_search_results(query, category):
    """Retrieve search results based on query and category."""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    sql_query = """
        SELECT 
            p.productID, p.sellerID, p.productName, s.shopName
        FROM 
            products p
        JOIN 
            sellers s ON p.sellerID = s.sellerID
    """
    params = []

    if category:
        sql_query += " WHERE p.categoryID = %s"
        params.append(category)

    if query:
        sql_query += " AND p.productName LIKE %s" if params else " WHERE p.productName LIKE %s"
        params.append(f"%{query}%")

    cursor.execute(sql_query, params)
    potential_results = cursor.fetchall()

    # Fuzzy match using RapidFuzz
    product_names = [row['productName'] for row in potential_results]
    shop_names = [row['shopName'] for row in potential_results]

    matched_product_ids = {
        row['productID'] for match in process.extract(query, product_names, limit=10)
        for row in potential_results if row['productName'] == match[0]
    } | {
        row['productID'] for match in process.extract(query, shop_names, limit=10)
        for row in potential_results if row['shopName'] == match[0]
    }

    results = fetch_products_by_ids(matched_product_ids, cursor) if matched_product_ids else []

    cursor.close()
    connection.close()
    return results

def fetch_top_sales_products():
    """Fetch top-selling products ordered by the number of products sold."""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
            
            
    query = """
        SELECT 
            p.productID, p.productName, p.productPrice, p.imgURL, 
            COALESCE((
                SELECT AVG(r.rating) 
                FROM product_reviews r 
                WHERE r.productID = p.productID
            ), 0) AS productRating, 
            COALESCE((
                SELECT SUM(ti.quantity) 
                FROM transaction_items ti 
                JOIN transactions t ON ti.transactionID = t.transactionID
                WHERE ti.productID = p.productID AND t.status = 'successful'
            ), 0) AS productSold,
            COALESCE(prom.discountRate, 0) AS discount_rate,             
            prom.startDate AS campaign_start, 
            prom.endDate AS campaign_end, 
            ROUND(p.productPrice * (1 - prom.discountRate / 100), 2) AS discounted_price
        FROM 
            products p
        LEFT JOIN 
            promotions prom ON p.productID = prom.productID 
                        AND prom.startDate <= CURDATE() 
                        AND prom.endDate >= CURDATE()        
        GROUP BY 
            p.productID
        ORDER BY 
            productSold DESC
        LIMIT 10;
        """

    cursor.execute(query)
    top_sales = cursor.fetchall()

    cursor.close()
    connection.close()

    return top_sales

def get_active_campaigns():
    """Fetch active campaigns that are currently running."""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
    SELECT 
        campaignID, 
        linkID, 
        linkType, 
        imageURL, 
        campaignDescription, 
        startDate, 
        endDate 
    FROM 
        marketing_campaigns 
    WHERE 
        startDate <= CURDATE() 
        AND endDate >= CURDATE();
    """

    cursor.execute(query)
    campaigns = cursor.fetchall()

    cursor.close()
    connection.close()

    return campaigns

def fetch_deals():
    """Fetch current promotions or flash deals."""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT 
            prom.productID, 
            p.productName, 
            p.productDesc,
            p.productPrice AS original_price, 
            prom.discountRate, 
            ROUND((p.productPrice * (1 - prom.discountRate / 100)), 2) AS discounted_price, 
            prom.startDate, 
            prom.endDate, 
            p.imgURL AS img_url 
        FROM 
            promotions prom
        JOIN 
            products p ON prom.productID = p.productID
        WHERE 
            prom.startDate <= CURDATE() 
            AND prom.endDate >= CURDATE()
            ORDER BY prom.endDate ASC
        LIMIT 4;
    """

    cursor.execute(query)
    deals = cursor.fetchall()

    cursor.close()
    connection.close()

    return deals


def fetch_products_by_ids(product_ids, cursor):
    """Fetch detailed product information based on product IDs."""
    placeholders = ', '.join(['%s'] * len(product_ids))
    query = f"""
        SELECT 
            p.productID, p.sellerID, p.productName, p.imgURL, 
            COALESCE(AVG(r.rating), 0.0) AS productRating,
            p.productPrice, COALESCE(t.total_quantity, 0) AS productSold,
            COALESCE(prom.discountRate, 0) AS discountRate, 
            prom.startDate, prom.endDate
        FROM 
            products p
        LEFT JOIN product_reviews r ON p.productID = r.productID
        LEFT JOIN promotions prom ON p.productID = prom.productID
        LEFT JOIN (
            SELECT ti.productID, SUM(ti.quantity) AS total_quantity 
            FROM transaction_items ti 
            JOIN transactions t ON ti.transactionID = t.transactionID 
            WHERE t.status = 'successful' GROUP BY ti.productID
        ) t ON p.productID = t.productID
        WHERE p.productID IN ({placeholders})
        GROUP BY p.productID
        ORDER BY productSold DESC
    """
    cursor.execute(query, tuple(product_ids))
    return cursor.fetchall()


@product_bp.route('/<int:product_id>')
def product_detail(product_id):
    """Display product details."""
    product = get_product_by_id(product_id)
    
    if not product:
        return abort(404, description="Product not found")
    
    review_details = get_product_reviews(product_id)
    seller_info = get_seller_info_by_product_id(product_id)
    categories = fetch_all_categories()

    if not seller_info:
        seller_info = {
            'sellerID': None,
            'shopName': 'Unknown',
            'imgURL': '',
            'joinedDate': 'N/A',
            'isVerified': False,
            'productsNum': 0,
            'totalReviews': 0,
            'totalRating': 0.0,
            'totalFollowers': 0,
        }

    return render_template('product.html', product=product, seller=seller_info, categories = categories, reviews=review_details)

def get_product_by_id(product_id):
    """Fetch product details by product ID."""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = ("""
        SELECT
            p.productID, 
            p.productName, 
            p.productDesc, 
            p.productPrice, 
            p.categoryID,
            p.subcategoryID,
            p.stock_quantity AS stock, 
                COALESCE((
                    SELECT AVG(r.rating) 
                    FROM product_reviews r 
                    WHERE r.productID = p.productID
                ), 0) AS productRating,
                COALESCE((
                        SELECT COUNT(productID)
                        FROM product_reviews r 
                        WHERE r.productID = p.productID
                    ), 0) AS totalReviews,
                COALESCE((
                    SELECT SUM(ti.quantity) 
                    FROM transaction_items ti 
                    JOIN transactions t ON ti.transactionID = t.transactionID
                    WHERE ti.productID = p.productID AND t.status = 'successful'
                ), 0) AS productSold,
                COALESCE(GROUP_CONCAT(i.imageURL), '') AS imageURLs
            FROM products p
            LEFT JOIN productimages i ON p.productID = i.productID
            WHERE p.productID = %s
            GROUP BY p.productID
            """
        )
    
    cursor.execute(query, (product_id,))
    product = cursor.fetchone()

    return product

@product_bp.route('/search', methods=['GET'])
def search():
    """Search products by query and category."""
    query = request.args.get('query', '')
    category = request.args.get('category', '')
    search_results = get_search_results(query, category)
    return render_template('search_results.html', results=search_results)

@product_bp.route('/wishlist', methods=['GET'])
def wishlist():
    """Display the user's wishlist."""
    account_id = request.args.get('accountID')
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT w.wishlistID, p.productID, p.productName, p.imgURL
        FROM wishlist w JOIN products p ON w.productID = p.productID
        WHERE w.accountID = %s
    """, (account_id,))
    items = cursor.fetchall()
    
    cursor.close()
    connection.close()
    return render_template('wishlist.html', items=items)


# Routes
@product_bp.route('/shoppingcart', methods=['GET', 'POST'])
def shoppingcart():
    """Handle user login."""

    if 'logged_in' not in session:
        flash("Please log in to your account so you can add products to your cart.", 'warning')
        return redirect(url_for('user.login'))    
    
    account_id = session.get('userID')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    print(f"Your account id ahdha: {account_id}")

    user = None
    if 'username' in session:
        username = session['username']
        user = fetch_userdetails(username)

    try:
        # Fetch shopping cart data for the logged-in user
        cursor.execute("""
            SELECT sc.accountID, sc.productID, sc.quantity,
                    p.productName, p.productDesc, p.productPrice, p.imgURL, p.stock_quantity
            FROM shopping_cart sc
            JOIN products p ON sc.productID = p.productID
            WHERE sc.accountID = %s
        """, (account_id,))

        shopping_cart_data = cursor.fetchall()
        print(F"Your fetched shopping cart: {shopping_cart_data}")
        cursor.close()
        conn.close()
        
        # Return the shopping cart page with the data
        return render_template('shoppingcart.html', shopping_cart=shopping_cart_data, user=user,)

    except Exception as e:
        print(f"Error: {e}")
        cursor.close()
        conn.close()
        flash('Error fetching shopping cart data.', 'error')
        return redirect(url_for('homepage'))


@product_bp.route('/remove_from_cart', methods=['POST'])
def addFromCart():
    """Remove an item from the shopping cart based on productID."""
    
    if 'logged_in' not in session:
        flash("Please log in to add products to your cart.", 'warning')
        return redirect(url_for('user.login'))

    account_id = session.get('userID')  # Get the logged-in user's account ID
    product_id = request.form.get('productID')  # Get the product ID from the form

    if not product_id:
        flash("Product ID is missing.", 'error')
        return redirect(url_for('product.shoppingcart'))

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Delete the item from the shopping cart for the specific user and product
        cursor.execute("""
            INSERT INTO shopping_cart (accountID, productID, quantity, dateAdded)
            VALUES (%s, %s, 1, CURRENT_TIMESTAMP)
            ON DUPLICATE KEY UPDATE quantity = quantity + 1;
        """, (account_id, product_id))
        
        conn.commit()  # Commit the transaction
        
        flash("Item successfully added to your cart.", 'success')
        
        cursor.close()
        conn.close()

        return redirect(url_for('product.shoppingcart'))

    except Exception as e:
        print(f"Error adding item from cart: {e}")
        
        cursor.close()
        conn.close()
        flash('Error adding item from the cart.', 'error')
        return redirect(url_for('product.shoppingcart'))

@product_bp.route('/remove_from_cart', methods=['POST'])
def removeFromCart():
    """Remove an item from the shopping cart based on productID."""
    
    if 'logged_in' not in session:
        flash("Access Denied. Please log in to your account.", 'warning')
        return redirect(url_for('user.login'))

    account_id = session.get('userID')  # Get the logged-in user's account ID
    product_id = request.form.get('productID')  # Get the product ID from the form

    if not product_id:
        flash("Product ID is missing.", 'error')
        return redirect(url_for('shoppingcart'))

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Delete the item from the shopping cart for the specific user and product
        cursor.execute("""
            DELETE FROM shopping_cart
            WHERE accountID = %s AND productID = %s
        """, (account_id, product_id))
        
        conn.commit()  # Commit the transaction
        
        flash("Item successfully removed from your cart.", 'success')
        
        cursor.close()
        conn.close()

        return redirect(url_for('shoppingcart'))

    except Exception as e:
        print(f"Error removing item from cart: {e}")
        conn.rollback()  # Roll back the transaction in case of error
        cursor.close()
        conn.close()
        flash('Error removing item from the cart.', 'error')
        return redirect(url_for('shoppingcart'))


# Register Blueprint in main application
def register_product_blueprint(app):
    """Register the product blueprint."""
    app.register_blueprint(product_bp, url_prefix='/products')
