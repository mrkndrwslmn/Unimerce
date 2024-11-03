import os
from flask import Blueprint, request, session, redirect, url_for, render_template, flash, jsonify
from datetime import datetime, date
import random
from werkzeug.utils import secure_filename
from helpers.database import get_db_connection
from helpers.data_accessed import (
    fetch_all_products, 
    fetch_all_categories,
    fetch_subcategories_by_category,
    fetch_all_variation_types,
    get_categories_and_subcategories,
    get_seller_info, 
    get_average_rating, 
    get_product_count, 
    get_follower_count,
    get_seller_id_by_username,
    get_seller_id)
from helpers.formatting import time_ago, currency_format
from routes.product import (
    get_product_by_id
)

# Create a blueprint for seller-related routes
seller_bp = Blueprint('seller', __name__, url_prefix='/seller')

# Route: Seller Application
@seller_bp.route('/application', methods=['GET', 'POST'])
def seller_application():
    """Handles seller application submission."""
    if request.method == 'POST':
        shop_name = request.form['shopName']
        business_registration = request.form['businessRegistrationNumber']
        business_address = request.form['businessAddress']
        img_file = request.files['imgURL']

        img_path = None
        if img_file:
            img_path = os.path.join('static/uploads', secure_filename(img_file.filename))
            img_file.save(img_path)

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO sellers (shopName, imgURL, joinDate, status, accountID)
                VALUES (%s, %s, %s, %s, %s)
            """, (shop_name, img_path, datetime.now(), 'Pending', session['accountID']))
            conn.commit()
            flash("Application submitted successfully!", 'success')
        except Exception as e:
            flash(f"Error: {str(e)}", 'error')
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('homepage'))

    return render_template('sellerapplication.html')

# Helper: Get seller info by product ID
def get_seller_info_by_product_id(product_id):
    """Fetches seller information based on product ID."""
    conn = get_db_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor(dictionary=True)
        seller_query = """
            SELECT s.sellerID, s.shopName, s.imgURL, s.join_date AS joinedDate, s.isVerified
            FROM sellers s
            JOIN products p ON s.sellerID = p.sellerID
            WHERE p.productID = %s
        """
        cursor.execute(seller_query, (product_id,))
        seller_info = cursor.fetchone()

        if not seller_info:
            return None

        seller_info['isVerified'] = seller_info['isVerified'] == 1
        seller_info['productsNum'] = get_product_count(seller_info['sellerID'])
        seller_info['totalRating'] = get_average_rating(seller_info['sellerID'])
        seller_info['totalFollowers'] = get_follower_count(seller_info['sellerID'])
        seller_info['joinedDate'] = time_ago(seller_info['joinedDate'])

        return seller_info

    finally:
        cursor.close()
        conn.close()

@seller_bp.route('/detail/<int:seller_id>', methods=['GET'])
def seller_detail(seller_id):
    
    
    return f"Seller ID: {seller_id}"

def get_seller_info_by_shop_name(shop_name):
    """Fetch seller information using the shop name."""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        query = "SELECT * FROM sellers WHERE shopName = %s"
        cursor.execute(query, (shop_name,))
        seller_info = cursor.fetchone()
    except Exception as e:
        print(f"Error fetching seller info: {e}")
        seller_info = None
    finally:
        cursor.close()
        connection.close()

    return seller_info

# Route: View Seller Profile
@seller_bp.route('/<shop_name>')
def seller(shop_name):
    """Displays the seller profile and their products."""
    seller_info = get_seller_info_by_shop_name(shop_name)
    if not seller_info:
        return "Seller not found", 404
    
    seller_id = seller_info['sellerID']
    products = fetch_all_products(seller_id)
    campaigns = get_campaigns_by_seller(seller_id)
    seller_info = get_seller_info(seller_id)
    seller_info['joinedDate'] = time_ago(seller_info['joinedDate'])
    suggested_products = fetch_suggested_products(seller_id)
    newest_arrivals = fetch_newest_arrivals(seller_id)
    if not products or not seller_info:
        return "Seller or products not found", 404

    return render_template('seller.html', 
                            products=products, 
                            seller=seller_info, 
                            campaigns=campaigns, 
                            suggested_products=suggested_products, 
                            newest_arrivals=newest_arrivals,
                            current_date=date.today())

def get_campaigns_by_seller(seller_id):
    """Fetch campaigns for a specific seller."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = """
            SELECT campaignID, imageURL, linkType, linkID, campaignDescription 
            FROM marketing_campaigns 
            WHERE accountID = %s
        """
        cursor.execute(query, (seller_id,))
        campaigns = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return campaigns

def fetch_suggested_products(seller_id):
    """Fetch suggested products for a seller, randomly sorted."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Random sorting options
    sorting_options = [
        "productRating DESC", 
        "discount_rate DESC", 
        "productSold DESC", 
        "productPrice ASC"
    ]

    # Randomly pick one sorting option
    random_sort = random.choice(sorting_options)

    try:
        query = f"""
            SELECT 
                p.productID, 
                p.productName, 
                p.productPrice, 
                p.imgURL, 
                COALESCE(AVG(r.rating), 0) AS productRating, 
                COALESCE(SUM(ti.quantity), 0) AS productSold,
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
            LEFT JOIN 
                product_reviews r ON p.productID = r.productID
            LEFT JOIN 
                transaction_items ti ON p.productID = ti.productID
            WHERE 
                p.sellerID = %s
            GROUP BY 
                p.productID
            ORDER BY 
             {random_sort}
            LIMIT 5;
        """
        cursor.execute(query, (seller_id,))
        suggested_products = cursor.fetchall()

    except Exception as e:
        print(f"Error fetching suggested products: {e}")
        suggested_products = []

    finally:
        cursor.close()
        conn.close()

    return suggested_products

def fetch_newest_arrivals(seller_id):
    """Fetch newest arrivals for a seller."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = """
            SELECT 
                p.productID, 
                p.productName, 
                p.productPrice, 
                p.imgURL, 
                COALESCE(AVG(r.rating), 0) AS productRating, 
                COALESCE(SUM(ti.quantity), 0) AS productSold,
                COALESCE(prom.discountRate, 0) AS discount_rate,             
                prom.startDate AS campaign_start, 
                prom.endDate AS campaign_end, 
                ROUND(p.productPrice * (1 - prom.discountRate / 100), 2) AS discounted_price,
                p.createdAt
            FROM 
                products p
            LEFT JOIN 
                promotions prom ON p.productID = prom.productID 
                    AND prom.startDate <= CURDATE() 
                    AND prom.endDate >= CURDATE()
            LEFT JOIN 
                product_reviews r ON p.productID = r.productID
            LEFT JOIN 
                transaction_items ti ON p.productID = ti.productID
            WHERE 
                p.sellerID = %s
            GROUP BY 
                p.productID
            ORDER BY 
                p.createdAt DESC
            LIMIT 5;
        """
        cursor.execute(query, (seller_id,))
        newest_arrivals = cursor.fetchall()

    except Exception as e:
        print(f"Error fetching newest arrivals: {e}")
        newest_arrivals = []

    finally:
        cursor.close()
        conn.close()

    return newest_arrivals

# Route: Manage Store Dashboard
@seller_bp.route('/manage_store')
def manage_store():

    """Displays the seller's management dashboard."""
    if 'logged_in' not in session:
        flash("Access Denied. Please log in to your account.", 'warning')
        return redirect(url_for('user.login'))    
    
    username = session.get('username')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Verify the user's type and fetch user information
        cursor.execute("SELECT * FROM accountinformation WHERE username = %s", (username,))
        user = cursor.fetchone()

        if not user:
            flash("User not found.", 'danger')
            return redirect(url_for('homepage'))
        
        cursor.execute("""
            SELECT s.sellerID 
            FROM sellers s
            JOIN accountinformation a ON s.accountID = a.accountID
            WHERE a.username = %s
        """, (username,))

        result = cursor.fetchone()
        if result:
            seller_id = result['sellerID']
            print(f"Seller ID: {seller_id}")
        else:
            flash("Seller not found.", 'danger')
            return redirect(url_for('homepage'))   

        products = fetch_all_products(seller_id)
        seller = get_seller_info(seller_id)

        if not seller:
            print("Seller info not found.")

        return render_template('seller_dashboard.html', user=user, seller=seller, products=products)
    
    except Exception as e:
        flash(f"An error occurred: {str(e)}", 'danger')
        return redirect(url_for('homepage'))

    finally:
        cursor.close()
        conn.close()

# Route: Product Management
@seller_bp.route('/products_management', methods=['GET', 'POST'])
def products_management():
    """Manages the seller's products."""
    if 'logged_in' not in session:
        flash("Please log in to access this page.", 'warning')
        return redirect(url_for('user.login'))    
    
    username = session.get('username')
    seller_id = get_seller_id_by_username(username)

    if not seller_id:
        flash("Seller not found or not authorized.", 'danger')
        return redirect(url_for('homepage'))

    products = fetch_all_products(seller_id)
    categories = fetch_all_categories()
    category_id = None
    subcategories = []
    selected_product = None

    if request.method == 'POST':
        category_id = request.form.get('categoryID')
        product_id = request.form.get('productID')

        if product_id:
            selected_product = get_product_by_id(product_id)
        if category_id:
            subcategories = fetch_subcategories(category_id)
    
    variation_types = fetch_all_variation_types

    return render_template(
        'product_management.html', products=products,
        categories=categories, selected_category_id=category_id, variation_types=variation_types,
        subcategories=subcategories, selected_product=selected_product
    )

@seller_bp.route('/fetch_subcategories/<int:category_id>', methods=['GET'])
def fetch_subcategories(category_id):
    """Fetch subcategories for a given category ID."""
    subcategories = fetch_subcategories_by_category(category_id)
    return jsonify(subcategories)

@seller_bp.route('/fetch_variation_types', methods=['GET'])
def fetch_variation_types():
    """Fetch all variation types."""
    variation_types = fetch_all_variation_types()
    return jsonify(variation_types)

@seller_bp.route('/fetch_option_types/<int:variation_type_id>', methods=['GET'])
def fetch_option_types(variation_type_id):
    """Fetch all option types for the given variation type."""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        query = """
            SELECT optionTypeID, optionTypeName 
            FROM option_types 
            WHERE variationTypeID = %s
        """
        cursor.execute(query, (variation_type_id,))
        option_types = cursor.fetchall()
        return jsonify(option_types)
    except Exception as e:
        print(f"Error fetching option types: {str(e)}")
        return jsonify([])
    finally:
        cursor.close()
        connection.close()

# Routes
@seller_bp.route('/add_or_update', methods=['POST'])
def add_or_update_product():
    try:
        """Add or update a product with variations and images."""
        product_id = request.form.get('productID')
        name = request.form.get('productName')
        desc = request.form.get('productDesc')
        category_id = request.form.get('categoryID')
        subcategory_id = request.form.get('subcategoryID')
        price = float(request.form.get('productPrice'))

        username = session.get('username')
        seller_id = get_seller_id_by_username(username)

        if not seller_id:
            raise ValueError("Seller ID not found in session.")
        
        variations = request.form.getlist('variationType[]')
        stock = None if variations else int(request.form.get('stockQuantity', 0))
        images = request.files.getlist('optionImage[]')
        
        print(f"Images received: {[img.filename for img in images]}")  # List all filenames in images

        print(f"Received Data: Product ID: {product_id}, Name: {name},  Desc: {desc}, Category: {category_id}, Subcategory: {subcategory_id}, Price: {price}, Stock: {stock}")

        connection = get_db_connection()
        cursor = connection.cursor()
        
        if product_id:  # Update product        
            print("Updating product...")
            cursor.execute("""
                UPDATE products SET productName=%s, productDesc=%s, categoryID=%s, 
                    subcategoryID=%s, productPrice=%s, stock_quantity=%s WHERE productID=%s
            """, (name, desc, category_id, subcategory_id, price, stock, product_id))
            connection.commit()
        else:
            print("Inserting new product...")
            cursor.execute("""
                INSERT INTO products (productName, productDesc, categoryID, subcategoryID, productPrice, sellerID) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, desc, category_id, subcategory_id, price, seller_id))
            product_id = cursor.lastrowid
            print(f"New Product ID: {product_id}")
            connection.commit()

        # Handle variations if provided
        if variations:
            print(f"Adding {len(variations)} variations...")
            for i, variation in enumerate(variations):
                option_value = request.form.getlist(f'optionValue[{i}][]') or [None]
                additional_cost_list = request.form.getlist(f'additionalCost[{i}][]')
                stock_quantity_list = request.form.getlist(f'stockQuantity[{i}][]')

                if not additional_cost_list or not stock_quantity_list:
                    print(f"Skipping variation {i}: Missing additional cost or stock quantity.")
                    continue

                try:
                    additional_cost = float(additional_cost_list[0])
                    stock_quantity = int(stock_quantity_list[0])
                except ValueError:
                    print(f"Skipping variation {i}: Invalid additional cost or stock quantity.")
                    continue

                print(f"Variation {i}: Type={variation}, Stock={stock_quantity}, Option Value={option_value}")

                try:
                    cursor.execute("""
                        INSERT INTO variations (productID, variationTypeID, stockQuantity) 
                        VALUES (%s, %s, %s)
                    """, (product_id, variation, stock_quantity))
                    variation_id = cursor.lastrowid

                    # Check if option_value[0] is not None before inserting into variation_options
                    if option_value[0]:
                        cursor.execute("""
                            INSERT INTO variation_options (variationID, optionValue, additionalCost) 
                            VALUES (%s, %s, %s)
                        """, (variation_id, option_value[0], additional_cost))
                except Exception as e:
                    print(f"Error inserting variation {i}: {str(e)}")
                    continue
        # Handle images
        for img in images:
            if img and img.filename:
                filename = secure_filename(img.filename)  # Sanitize the filename
            
                if filename:  # Check if filename is still valid after sanitizing
                    save_directory = r"C:\Users\marka\Unimerce\static\savedimages"
                    os.makedirs(save_directory, exist_ok=True)

                    try:
                        img.save(os.path.join(save_directory, filename))
                        cursor.execute("""
                            INSERT INTO productimages (productID, imageURL) VALUES (%s, %s)
                        """, (product_id, filename))
                        print(f"Image saved: {filename}")
                    except Exception as e:
                        print(f"Error saving image {filename}: {e}")
                    continue  # Skip to the next image if there's an error
                else:
                    print("Skipping image: No valid filename provided.")
            else:
                print("Skipping image: No image file provided or filename is empty.")


            connection.commit()
            flash('Product added/updated successfully!', 'success')

    except Exception as e:
        connection.rollback()
        print(f"Error: {e}")
        flash(f"Error: {e}", 'danger')

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('seller.products_management'))

def process_product_images(images):
    """Handle file uploads for product images."""
    image_urls = []
    for img in images:
        if img:
            filename = secure_filename(img.filename)
            img.save(os.path.join('static/uploads', filename))
            image_urls.append(filename)
    return image_urls

# Register the blueprint in the main app
def register_seller_blueprint(app):
    """Register the seller blueprint with the main app."""
    app.register_blueprint(seller_bp)
