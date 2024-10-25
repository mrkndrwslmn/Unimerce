import os
from flask import Flask, render_template, request, jsonify
from flask import session, redirect, url_for, flash
from dotenv import load_dotenv
load_dotenv()
import mysql.connector
<<<<<<< HEAD
import jinja2
=======
from collections import defaultdict
from datetime import datetime, date
from werkzeug.utils import secure_filename
import smtplib
from email.message import EmailMessage
import random
>>>>>>> 81bccb2 (seller_dashboard edited)

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default_secret_key')

def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',   # e.g., 'localhost'
        user='root',   # e.g., 'root'
        password="",
        database='unimerce'
    )
    return connection

<<<<<<< HEAD
def product(product_id):
=======
def fetch_product(product_id):
    conn = get_db_connection()  
    if conn is None:
        return None  

    cursor = conn.cursor()

    cursor.execute(""" 
        SELECT 
            p.productID,
            p.sellerID,
            p.productName, 
            p.imgURL, 
            p.productRating, 
            p.productPrice, 
            p.productSold,
            v.variationType, 
            v.variationValue, 
            v.stockQuantity, 
            s.shopName
        FROM 
            products p 
        LEFT JOIN 
            variations v ON p.productID = v.productID 
        LEFT JOIN 
            sellers s ON p.sellerID = s.sellerID
        WHERE 
            p.productID = %s
    """, (product_id,))

    product_data = cursor.fetchall() 


    if product_data:
        product_info = {
            'id': product_data[0][0],
            'sellerID': product_data[0][1],
            'name': product_data[0][2],
            'image': product_data[0][3],
            'rating': product_data[0][4],
            'price': product_data[0][5],
            'sold': product_data[0][6],
            'seller': product_data[0][10],  # Add seller's shop name to the product_info
            'variations': []
        }

        # Iterate through variations
        for row in product_data:
            # Check if variationType is not None
            if row[7] is not None:
                variation_info = {
                    'type': row[7],
                    'value': row[8],
                    'stock': row[9]
                }
                product_info['variations'].append(variation_info)

        return product_info  

    cursor.close()
    conn.close()

    return None  

@app.route('/add_to_wishlist', methods=['POST'])
def add_to_wishlist():
    account_id = request.form['accountID']
    product_id = request.form['productID']
    
>>>>>>> 81bccb2 (seller_dashboard edited)
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if the product is already in the wishlist
    cursor.execute('SELECT * FROM wishlist WHERE accountID = %s AND productID = %s', (account_id, product_id))
    existing_item = cursor.fetchone()
    
    if not existing_item:
        cursor.execute('INSERT INTO wishlist (accountID, productID) VALUES (%s, %s)', (account_id, product_id))
        conn.commit()
    
    cursor.close()
    conn.close()
    
    return redirect(url_for('wishlist'))

@app.route('/remove_from_wishlist', methods=['POST'])
def remove_from_wishlist():
    wishlist_id = request.form['wishlistID']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM wishlist WHERE wishlistID = %s', (wishlist_id,))
    conn.commit()
    
    cursor.close()
    conn.close()
    
    return redirect(url_for('wishlist'))

@app.route('/wishlist', methods=['GET'])
def wishlist():
    account_id = request.args.get('accountID')  # Get the account ID from query parameters

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get the wishlist items for the user
    cursor.execute('''
        SELECT w.wishlistID, p.productID, p.productName, p.imgURL
        FROM wishlist w
        JOIN products p ON w.productID = p.productID
        WHERE w.accountID = %s
    ''', (account_id,))
    
    wishlist_items = cursor.fetchall()
    
    cursor.close()
    conn.close()

    return render_template('wishlist.html', wishlist_items=wishlist_items)

def get_products_with_variations(seller_id):
    conn = get_db_connection()  # Use the same connection method
    if conn is None:
        return []
    
    cursor = conn.cursor()

<<<<<<< HEAD
    # Fetch product details using product_id
    cursor.execute("SELECT name, image_url, rating, price, description FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()  # Fetch a single product

    cursor.close()
    conn.close()

    # Check if the product exists
    if product:
        return render_template('product.html', product=product)
    else:
        return render_template('404.html'), 404  # Return a 404 page if the product is not found

@app.route('/get_categories')
def get_categories():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Execute a query to fetch categories from your database
    cursor.execute("SELECT category_Name FROM categories")  # Ensure 'category_Name' is the correct column name

    # Fetch all the rows and extract the category names
    categories = [row[0] for row in cursor.fetchall()]
=======
    # Fetch all products and their associated sellers and variations
    cursor.execute("""
    SELECT 
        p.productID,
        p.sellerID,
        p.productName, 
        p.productDesc,  -- Include description
        p.imgURL, 
        p.productRating, 
        p.productPrice,
        p.productSold,
        v.variationID,
        v.variationType,
        v.variationValue,
        v.stockQuantity,
        v.productSold AS variationProductSold,
        v.productPrice AS variationPrice
    FROM 
        products p
    LEFT JOIN 
        variations v ON p.productID = v.productID
    ORDER BY 
        p.productName ASC  -- You can adjust the order as needed
    """)
>>>>>>> 81bccb2 (seller_dashboard edited)

    all_products_data = cursor.fetchall()  # Fetch all product data
    
    cursor.close()
    conn.close()

    products_dict = {}

    for row in all_products_data:
        product_id = row[0]
        seller_id = row[1]
        
        # If the product is not already in the dictionary, add it
        if product_id not in products_dict:
            products_dict[product_id] = {
                'productID': product_id,
                'sellerID': seller_id,
                'productName': row[2],
                'productDescription': row[3],  # Include product description
                'imgURL': row[4],
                'productRating': row[5],
                'productPrice': row[6],
                'productSold': row[7],
                'variations': []  # Empty list for variations
            }
        
        # Append the variation to the product's variations list
        if row[8]:  # row[8] is variationID, checking if variation exists
            variation_info = {
                'variationID': row[8],
                'variationType': row[9],
                'variationValue': row[10],
                'stockQuantity': row[11],
                'variationProductSold': row[12],
                'variationPrice': row[13]
            }


            products_dict[product_id]['variations'].append(variation_info)

    # Convert the dictionary values to a list for easier processing
    products_with_sellers_and_variations = list(products_dict.values())

    return products_with_sellers_and_variations

def get_top_sales():
    conn = get_db_connection()  # Use the same connection method
    if conn is None:
        return []
    
    cursor = conn.cursor()

<<<<<<< HEAD
    # Adjust your SQL query to match your schema
    cursor.execute("SELECT productName, imgURL, productRating, productPrice FROM products ORDER BY productRating DESC LIMIT 10")
    
    top_sales = cursor.fetchall()
=======
    # Fetch all products and their sales data
    cursor.execute(""" 
    SELECT 
        p.productID,
        p.sellerID,
        p.productName, 
        p.imgURL, 
        p.productRating, 
        p.productPrice, 
        p.productSold,
        COALESCE(pr.discountRate, 0) AS discountRate,
        pr.startDate,
        pr.endDate
    FROM 
        products p
    LEFT JOIN 
        promotions pr ON p.productID = pr.productID
    ORDER BY 
        p.productSold DESC
    LIMIT 10
""")

    all_products_data = cursor.fetchall()  # Fetch all product data
    
>>>>>>> 81bccb2 (seller_dashboard edited)
    cursor.close()
    conn.close()

    # Create a list to hold product details
    products_with_sellers = []

    for row in all_products_data:
        product_id = row[0]
        seller_id = row[1]
        
        # Create a product_info dictionary with necessary attributes
        product_info = {
            'productID': product_id,
            'sellerID': seller_id,
            'productName': row[2],
            'imgURL': row[3],
            'productRating': row[4],
            'productPrice': row[5],
            'productSold': row[6],
            'discount_rate': row[7],
            'original_price': float(row[5]),  # Set the original price
            'campaign_start': row[8],  # Promotion start date
            'campaign_end': row[9]     # Promotion end date
        }

    # Calculate the discounted price based on the original price and discount rate
        discount_rate = row[7]  # This is still a Decimal

        if discount_rate > 0:  # Ensure discount rate is positive
            discount_rate_float = float(discount_rate)  # Convert discount rate to float
            discount_amount = product_info['original_price'] * (discount_rate_float / 100)
            discounted_price = product_info['original_price'] - discount_amount
            product_info['discounted_price'] = discounted_price
        else:
            product_info['discounted_price'] = product_info['original_price']  # No discount

        products_with_sellers.append(product_info)

    # Sort products based on the number sold
    products_with_sellers.sort(key=lambda x: x['productSold'], reverse=True)

    # Limit to the top 10 products
    top_sales = products_with_sellers[:10]

    return top_sales


def get_categories_and_subcategories():    
    conn = get_db_connection()  # Use the same connection method
    if conn is None:
        return []
    
    cursor = conn.cursor()

    # Query to fetch categories and their subcategories
    cursor.execute("""
    SELECT c.categoryName, c.imgURL, s.subcategoryName
    FROM categories c
    LEFT JOIN subcategories s ON c.categoryID = s.categoryID
""")
    # Fetch results
    results = cursor.fetchall()
    
    # Organizing data into a structured format
    categories = []
    for row in results:
        category_name = row[0]
        category_imgURL = row[1]  # Get the imgURL from the query
        if category_name not in [category['name'] for category in categories]:
            categories.append({'name': category_name, 'imgURL': category_imgURL, 'subcategories': []})
        subcategory_name = row[2]
        if subcategory_name:
            for category in categories:
                if category['name'] == category_name:
                    category['subcategories'].append(subcategory_name)

    cursor.close()  # Corrected from connection.close()
    conn.close()    # Closing the connection properly

    return categories

@app.route('/deals_of_week')
def fetch_deals():
    conn = get_db_connection()  # Use the same connection method
    if conn is None:
        return render_template('error.html', message="Database connection failed.")
    
    cursor = conn.cursor()
    query = '''
        SELECT p.productID, p.productName, p.imgURL, p.productPrice, 
               p.productRating, p.productSold, p.productDesc, pr.discountRate, 
               pr.startDate, pr.endDate
        FROM products p
        JOIN promotions pr ON p.productID = pr.productID
        WHERE CURDATE() BETWEEN pr.startDate AND pr.endDate
        ORDER BY pr.discountRate DESC
        LIMIT 1;
    '''
    
    try:
        cursor.execute(query)
        deals = cursor.fetchall()  # Fetching the deals

        
        deals_with_prices = []
        for deal in deals:
            original_price = deal[3]  # This is a float
            discount_rate = float(deal[7])  # Adjusted index for discount rate
            discounted_price = original_price * (1 - discount_rate / 100)  # Correct multiplication
            
            if isinstance(deal[9], date):  # Check if it's a date
                formatted_end_date = deal[9].strftime("%Y-%m-%dT%H:%M:%S")  # ISO format for JavaScript
            else:
                formatted_end_date = deal[9]  # Ensure the else block handles other types appropriately

            # Append discounted price, description, and formatted end date to each deal
            deals_with_prices.append({
            'product_id': deal[0],
            'product_name': deal[1],
            'img_url': deal[2],
            'original_price': original_price,
            'discounted_price': discounted_price,
            'product_rating': deal[4],
            'product_sold': deal[5],
            'product_desc': deal[6],
            'discount_rate': discount_rate,
            'start_date': deal[8].strftime("%Y-%m-%d %H:%M:%S"),
            'end_date': formatted_end_date
        })

        print("Deal with prices:", deals_with_prices[-1])  # Check the last added deal

    except Exception as e:
        print("Error retrieving deals:", e)  # Logging the error
        return render_template('error.html', message="Failed to retrieve deals.")  # Return an error message
    finally:
        cursor.close()
        conn.close()

    return deals_with_prices

def get_products_by_seller_id(seller_id):
    conn = get_db_connection()  # Use the same connection method
    if conn is None:
        return render_template('error.html', message="Database connection failed.")
    
    try:
        cursor = conn.cursor(dictionary=True)  # Fetch results as dictionaries
        
        # Define the query to fetch products by seller ID, including variations
        query = """
        SELECT 
            p.productID,
            p.sellerID,
            p.productName, 
            p.productDesc, 
            p.imgURL, 
            p.productRating, 
            p.productPrice,
            p.productSold,
            v.variationID,
            v.variationType,
            v.variationValue,
            v.stockQuantity,
            v.productSold AS variationProductSold,
            v.productPrice AS variationPrice
        FROM 
            products p
        LEFT JOIN 
            variations v ON p.productID = v.productID
        WHERE 
            p.sellerID = %s
        """
        
        cursor.execute(query, (seller_id,))  # Execute the query with seller_id
        product_data = cursor.fetchall()  # Fetch all records related to the products by this seller
        
        # If no products are found, return an empty list
        if not product_data:
            return []

        # Initialize a dictionary to group products by productID
        products_by_seller = {}

        # Iterate over the fetched data to populate products and their variations
        for row in product_data:
            product_id = row['productID']
            
            # If this product hasn't been added yet, initialize it
            if product_id not in products_by_seller:
                products_by_seller[product_id] = {
                    'productID': product_id,
                    'sellerID': row['sellerID'],
                    'productName': row['productName'],
                    'productDescription': row['productDesc'],
                    'imgURL': row['imgURL'],
                    'productRating': row['productRating'],
                    'productPrice': float(row['productPrice']),
                    'productSold': row['productSold'],
                    'variations': []  # Initialize variations as an empty list
                }
            
            # Add variations if they exist
            if row['variationID']:
                variation_info = {
                    'variationID': row['variationID'],
                    'variationType': row['variationType'],
                    'variationValue': row['variationValue'],
                    'stockQuantity': row['stockQuantity'],
                    'variationProductSold': row['variationProductSold'],
                    'variationPrice': row['variationPrice']
                }
                products_by_seller[product_id]['variations'].append(variation_info)

        # Fetch promotions for each product
        for product in products_by_seller.values():
            promotion_query = '''
                SELECT pr.discountRate, pr.startDate, pr.endDate
                FROM promotions pr
                WHERE pr.productID = %s AND CURDATE() BETWEEN pr.startDate AND pr.endDate
                ORDER BY pr.discountRate DESC
                LIMIT 1;
            '''
            cursor.execute(promotion_query, (product['productID'],))
            promotion_data = cursor.fetchone()

            if promotion_data:
                start_date = datetime.strptime(promotion_data['startDate'], '%Y-%m-%d').date() if isinstance(promotion_data['startDate'], str) else promotion_data['startDate']
                end_date = datetime.strptime(promotion_data['endDate'], '%Y-%m-%d').date() if isinstance(promotion_data['endDate'], str) else promotion_data['endDate']
                
                current_date = date.today()  # Current date for comparison
                
                # Check if current date is within promotion period
                if start_date <= current_date <= end_date:
                    discount_rate = float(promotion_data['discountRate'])
                    discounted_price = product['productPrice'] * (1 - discount_rate / 100)
                    product['promotion'] = {
                        'discountRate': discount_rate,
                        'startDate': start_date,
                        'endDate': end_date,
                        'discountedPrice': round(discounted_price, 2)
                    }

        # Return the products as a list of dictionaries
        return list(products_by_seller.values())

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []  # Return an empty list in case of an error
    finally:
        cursor.close()  # Close the cursor
        conn.close()  # Close the database connection

def get_product_by_id(product_id):
    conn = get_db_connection()  # Use the same connection method
    if conn is None:
        return render_template('error.html', message="Database connection failed.")
    
    try:
        cursor = conn.cursor(dictionary=True)  # Fetch results as dictionaries
        
        # Define the query to fetch the product by ID, including variations
        query = """
        SELECT 
             p.productID,
            p.sellerID,
            p.productName, 
            p.productDesc, 
            p.imgURL, 
            p.productRating, 
            p.productPrice,
            p.productSold,
            v.variationID,
            v.variationType,
            v.variationValue,
            v.stockQuantity,
            v.productSold AS variationProductSold,
            v.productPrice AS variationPrice
        FROM 
            products p
        LEFT JOIN 
            variations v ON p.productID = v.productID
        WHERE 
            p.productID = %s
        """
        
        cursor.execute(query, (product_id,))  # Execute the query with product_id
        product_data = cursor.fetchall()  # Fetch all records related to the product
        
        # If no product is found, return None
        if not product_data:
            return None

        # Initialize product dictionary
        selected_product = {
            'productID': product_data[0]['productID'],
            'sellerID': product_data[0]['sellerID'],
            'productName': product_data[0]['productName'],
            'productDescription': product_data[0]['productDesc'],
            'imgURL': product_data[0]['imgURL'],
            'productRating': product_data[0]['productRating'],
            'productPrice': float(product_data[0]['productPrice']),
            'productSold': product_data[0]['productSold'],
            'variations': []  # Initialize variations as an empty list
        }
        
        # Iterate over the fetched data to populate variations
        for row in product_data:
            if row['variationID']:  # Only if variationID exists
                variation_info = {
                    'variationID': row['variationID'],
                    'variationType': row['variationType'],
                    'variationValue': row['variationValue'],
                    'stockQuantity': row['stockQuantity'],
                    'variationProductSold': row['variationProductSold'],
                    'variationPrice': row['variationPrice']
                }
                selected_product['variations'].append(variation_info)

        promotion_query = '''
            SELECT pr.discountRate, pr.startDate, pr.endDate
            FROM promotions pr
            WHERE pr.productID = %s AND CURDATE() BETWEEN pr.startDate AND pr.endDate
            ORDER BY pr.discountRate DESC
            LIMIT 1;
        '''
        cursor.execute(promotion_query, (product_id,))
        promotion_data = cursor.fetchone()

        print("Promotion Query Result:", promotion_data)

        # If a promotion is found, calculate the discounted price
        if promotion_data:
            start_date = datetime.strptime(promotion_data['startDate'], '%Y-%m-%d').date() if isinstance(promotion_data['startDate'], str) else promotion_data['startDate']
            end_date = datetime.strptime(promotion_data['endDate'], '%Y-%m-%d').date() if isinstance(promotion_data['endDate'], str) else promotion_data['endDate']
            
            current_date = date.today()  # Current date for comparison
            
            # Check if current date is within promotion period
            if start_date <= current_date <= end_date:
                discount_rate = float(promotion_data['discountRate'])
                discounted_price = selected_product['productPrice'] * (1 - discount_rate / 100)
                selected_product['promotion'] = {
                    'discountRate': discount_rate,
                    'startDate': start_date,
                    'endDate': end_date,
                    'discountedPrice': round(discounted_price, 2)
            }

        return selected_product  # Return the selected product with variations
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None  # Return None in case of an error
    finally:
        cursor.close()  # Close the cursor
        conn.close()  # Close the database connection

def time_ago(joined_date):
    now = datetime.now()
    diff = now - joined_date

    seconds = diff.total_seconds()
    minutes = seconds // 60
    hours = minutes // 60
    days = diff.days
    weeks = days // 7
    months = days // 30
    years = days // 365

    if years > 0:
        return f"{years} year{'s' if years > 1 else ''} ago"
    elif months > 0:
        return f"{months} month{'s' if months > 1 else ''} ago"
    elif weeks > 0:
        return f"{weeks} week{'s' if weeks > 1 else ''} ago"
    elif days > 0:
        return f"{days} day{'s' if days > 1 else ''} ago"
    elif hours > 0:
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif minutes > 0:
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"

def get_seller_info_by_product_id(product_id):
    conn = get_db_connection()
    if conn is None:
        return render_template('error.html', message="Database connection failed.")

    try:
        cursor = conn.cursor(dictionary=True)

        # Step 1: Get seller info based on productID
        seller_query = """
            SELECT s.sellerID, s.shopName, s.imgURL, s.join_date AS joinedDate, s.isVerified
            FROM sellers s
            JOIN products p ON s.sellerID = p.sellerID
            WHERE p.productID = %s
        """
        cursor.execute(seller_query, (product_id,))
        seller_info = cursor.fetchone()
        
        if not seller_info:
            return None  # If no seller info is found

        
        seller_info['isVerified'] = seller_info['isVerified'] == 1

        # Step 2: Get total product count for the seller
        product_count_query = """
            SELECT COUNT(*) AS productsNum
            FROM products
            WHERE sellerID = %s
        """
        cursor.execute(product_count_query, (seller_info['sellerID'],))
        product_count = cursor.fetchone()
        seller_info['productsNum'] = product_count['productsNum']

        # Step 3: Calculate average rating for seller’s products
        rating_query = """
            SELECT AVG(r.rating) AS totalRating
            FROM product_reviews r
            JOIN products p ON r.productID = p.productID
            WHERE p.sellerID = %s
        """
        cursor.execute(rating_query, (seller_info['sellerID'],))
        rating_data = cursor.fetchone()
        seller_info['totalRating'] = round(float(rating_data['totalRating'] or 0), 1)

        # Step 4: Get total followers count (if using the suggested followers table)
        followers_query = """
            SELECT COUNT(*) AS totalFollowers
            FROM followers
            WHERE sellerID = %s
        """
        cursor.execute(followers_query, (seller_info['sellerID'],))
        followers_data = cursor.fetchone()
        seller_info['totalFollowers'] = followers_data['totalFollowers']

        # Convert join_date to a formatted string (e.g., "Joined: YYYY-MM-DD")
        joined_date = seller_info['joinedDate']
        seller_info['joinedDate'] = time_ago(joined_date)

        return seller_info

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return None
    finally:
        cursor.close()
        conn.close()

def get_seller_info(seller_id):
    conn = get_db_connection()  # Assuming you have a function to establish a database connection
    if conn is None:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)

        # Define the SQL query to retrieve seller information
        query = """
        SELECT 
            sellerID, shopName, imgURL, join_date AS joinedDate, isVerified 
        FROM 
            sellers 
        WHERE 
            sellerID = %s
        """
        
        # Execute the query with the provided seller_id
        cursor.execute(query, (seller_id,))
        seller_info = cursor.fetchone()  # Fetch the seller info
        
        # If no seller info is found, return None
        if not seller_info:
            print("Error: No seller found with the specified ID.")
            return None
        

        seller_info['isVerified'] = seller_info['isVerified'] == 1

        # Step 2: Get total product count for the seller
        product_count_query = """
            SELECT COUNT(*) AS productsNum
            FROM products
            WHERE sellerID = %s
        """
        cursor.execute(product_count_query, (seller_info['sellerID'],))
        product_count = cursor.fetchone()
        seller_info['productsNum'] = product_count['productsNum']

        # Step 3: Calculate average rating for seller’s products
        rating_query = """
            SELECT AVG(r.rating) AS totalRating
            FROM product_reviews r
            JOIN products p ON r.productID = p.productID
            WHERE p.sellerID = %s
        """
        cursor.execute(rating_query, (seller_info['sellerID'],))
        rating_data = cursor.fetchone()
        seller_info['totalRating'] = round(float(rating_data['totalRating'] or 0), 1)

        # Step 4: Get total followers count (if using the suggested followers table)
        followers_query = """
            SELECT COUNT(*) AS totalFollowers
            FROM followers
            WHERE sellerID = %s
        """
        cursor.execute(followers_query, (seller_info['sellerID'],))
        followers_data = cursor.fetchone()
        seller_info['totalFollowers'] = followers_data['totalFollowers']

        # Convert join_date to a formatted string (e.g., "Joined: YYYY-MM-DD")
        joined_date = seller_info['joinedDate']
        seller_info['joinedDate'] = time_ago(joined_date)

        return seller_info
    
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        return None  # Return None in case of an error
    
    finally:
        cursor.close()
        conn.close()

@app.route('/seller/<int:seller_id>')
def seller(seller_id):
    products = get_products_by_seller_id(seller_id)
    seller_info = get_seller_info(seller_id)

    if products and seller_info:
        current_date_value = date.today()
        
        # Pass products, seller info, and current date to the template
        return render_template(
            'seller.html',
            products=products,
            seller=seller_info,
            current_date=current_date_value
        )
    elif not products:
        return "Products not found for this seller", 404
    else:
        return "Seller information not found", 404

@app.route('/product/<int:product_id>')
def product(product_id):
    # Fetch product details from the database using product_id
    selected_product = get_product_by_id(product_id)
    seller_info = get_seller_info_by_product_id(product_id)

    if selected_product and seller_info:
        current_date_value = date.today()
        print("Current Date:", current_date_value)

        return render_template(
            'product.html',
            product=selected_product,
            seller=seller_info,
            current_date=current_date_value
        )
    elif not selected_product:
        return "Product not found", 404
    else:
        return "Seller information not found", 404
        

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session and session['logged_in']:
        return redirect(url_for('homepage'))
    
    if request.method == 'POST':
        username = request.form['username']  # Assuming username is being used for login
        password = request.form['password']

        # Connect to the MySQL database
        conn = get_db_connection()
        if conn is None:
            flash('Database connection failed.', 'danger')
            return render_template('homepage.html')  # Assuming homepage is the login page

        cursor = conn.cursor(dictionary=True)

        # Query to find the user by either username or email
        cursor.execute("""
            SELECT u.accountID, u.username, u.password, a.email, u.userType 
            FROM accountinformation u
            JOIN accountinformation a ON u.accountID = a.accountID 
            WHERE u.username = %s OR a.email = %s
        """, (username, username))  # Query modified to search by username or email

        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and user['password'] == password:  # Check if user exists and validate the password
            # Successful login, store user information in session
            session['userID'] = user['accountID']
            session['username'] = user['username']
            session['logged_in'] = True
            
            flash('Login successful!', 'success')

            # Redirect based on user type
            if user['userType'] == 'superadmin':
                return redirect(url_for('super_admin'))  # Change to your superadmin route
            elif user['userType'] == 'admin':
                return redirect(url_for('manage_offices'))  # Change to your admin route
            else:
                return redirect(url_for('homepage'))  # Redirect to dashboard for regular users
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')  # Render login page if GET request

@app.route('/my_purchases')
def my_purchases():
    purchases = []
    username = session.get('username')  # Assuming you have user_id stored in session

    try:
        # Establish a database connection
        conn = get_db_connection()  # Use the same connection method
        if conn is None:
            return render_template('error.html', message="Database connection failed.")
        
        cursor = conn.cursor()    

        # Query to fetch user purchases
        query = "SELECT productName, purchaseDate, price FROM purchases WHERE accountID = %s"
        cursor.execute(query, (username,))

        # Fetch the results
        purchases = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"Error: {err}", 'error')
    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()

    return render_template('my_purchases.html', purchases=purchases)

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        # Fetch the logged-in username from the session
        username = session.get('username')  # This assumes the user is already logged in

        # Get form data
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # Fetch the user's current password from the database
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        # Check if user exists
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('change_password'))

        # Check if the old password matches
        if user['password'] != old_password:
            flash('Old password is incorrect.', 'error')
            return redirect(url_for('change_password'))

        # Check if new password and confirm password match
        if new_password != confirm_password:
            flash('New password and confirm password do not match.', 'error')
            return redirect(url_for('change_password'))

        # Update the password in the database
        cursor.execute("UPDATE users SET password = %s WHERE username = %s", (new_password, username))
        connection.commit()  # Save changes
        cursor.close()
        connection.close()

        flash('Password changed successfully!', 'success')
        return redirect(url_for('profile'))  # Redirect to the profile page or other location

    return render_template('change_password.html', user=user)

def get_account_id(cursor, username):
    cursor.execute("""SELECT accountID FROM accountinformation WHERE username = %s""", (username,))
    account_data = cursor.fetchone()
    return account_data[0] if account_data else None  # Adjust this based on your return logic

@app.route('/address', methods=['GET'])
def address():
    username = session.get('username')

    if not username:
        flash('You must be logged in to view this page.', 'error')
        return redirect(url_for('login'))

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        account_id = get_account_id(cursor, username)
        cursor.execute("SELECT addressID, addressLine1, addressLine2, city, state, zipCode, country, isdefault FROM addresses WHERE accountID = %s", (account_id,))
        addresses = cursor.fetchall()  # Fetch all addresses

        addresses = sorted(addresses, key=lambda address: address[7], reverse=True)
        
        return render_template('update_address.html', addresses=addresses)

    except Exception as e:
        flash(f'An error occurred while retrieving addresses: {str(e)}', 'error')
        return redirect(url_for('homepage'))

    finally:
        cursor.close()
        connection.close()

@app.route('/add_edit_address', methods=['GET'])
def show_address_form():
    address_id = request.args.get('addressID')  # Get addressID from query parameters if provided
    address = None

    if address_id:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT addressID, addressLine1, addressLine2, city, state, zipCode, country FROM addresses WHERE addressID = %s", (address_id,))
        address = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if not address:
            flash('Address not found.', 'error')
            return redirect(url_for('address'))

    return render_template('add_edit_address.html', title="Add/Edit Address", address=address)

@app.route('/add_or_update_address', methods=['POST'])
def add_or_update_address():
    username = session.get('username')

    if not username:
        flash('You must be logged in to add or update an address.', 'error')
        return redirect(url_for('login'))

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        account_id = get_account_id(cursor, username)

        if not account_id:
            flash('Account not found. Please log in again.', 'error')
            return redirect(url_for('login'))

        address_id = request.form.get('addressID')  # Get the addressID if updating
        address_data = {
            "address_line1": request.form.get('addressLine1'),
            "address_line2": request.form.get('addressLine2', ''),
            "city": request.form.get('city'),
            "state": request.form.get('state'),
            "zip_code": request.form.get('zipCode'),
            "country": request.form.get('country')
        }
        
        if not address_data["address_line1"] or not address_data["city"] or not address_data["state"] or not address_data["zip_code"] or not address_data["country"]:
            flash('Please fill in all required address fields.', 'error')
            return redirect(url_for('address'))

        if address_id:  # Update existing address
            cursor.execute("""UPDATE addresses 
                              SET addressLine1=%s, addressLine2=%s, city=%s, state=%s, 
                                  zipCode=%s, country=%s, updatedAt=NOW() 
                              WHERE addressID=%s AND accountID=%s""",
                           (address_data["address_line1"], address_data["address_line2"], address_data["city"],
                            address_data["state"], address_data["zip_code"], address_data["country"], address_id, account_id))
            flash('Address updated successfully.', 'success')
        else:  # Insert a new address
            cursor.execute("""INSERT INTO addresses (accountID, addressLine1, addressLine2, city, state, zipCode, country, isdefault)
                              VALUES (%s, %s, %s, %s, %s, %s, %s, FALSE)""",
                           (account_id, address_data["address_line1"], address_data["address_line2"],
                            address_data["city"], address_data["state"], address_data["zip_code"], address_data["country"]))
            flash('Address added successfully.', 'success')

        connection.commit()

    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('address'))

@app.route('/set_default_address', methods=['POST'])
def set_default_address():
    address_id = request.form.get('addressID')
    username = session.get('username')

    if not username:
        flash('You must be logged in to set a default address.', 'error')
        return redirect(url_for('login'))
    
    # First set all addresses for this account as non-default
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        # Fetch accountID using the username
        account_id = get_account_id(cursor, username)

        if not account_id:
            flash('Account not found. Please log in again.', 'error')
            return redirect(url_for('login'))
        
         # Set all addresses for this account as non-default
        cursor.execute("""UPDATE addresses SET isdefault = FALSE WHERE accountID = %s""", (account_id,))
        
        # Set the chosen address as default
        cursor.execute("""UPDATE addresses SET isdefault = TRUE WHERE addressID = %s AND accountID = %s""", (address_id, account_id))

        connection.commit()
        flash('Default address set successfully.', 'success')

    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('address'))
    
@app.route('/delete_address', methods=['POST'])
def delete_address():
    address_id = request.form.get('addressID')
    username = session.get('username')

    if not username:
        flash('You must be logged in to delete an address.', 'error')
        return redirect(url_for('login'))

    # Fetch accountID using the username
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        account_id = get_account_id(cursor, username)

        if not account_id:
            flash('Account not found. Please log in again.', 'error')
            return redirect(url_for('login'))

        # Delete the address
        cursor.execute("""DELETE FROM addresses WHERE addressID = %s AND accountID = %s""", (address_id, account_id))
        connection.commit()
        flash('Address deleted successfully.', 'success')

    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
    
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('address'))

@app.route('/update_address/<int:address_id>', methods=['GET', 'POST'])
def update_address(address_id):
    username = session.get('username')

    if not username:
        flash('You must be logged in to update an address.', 'error')
        return redirect(url_for('login'))

    connection = get_db_connection()
    cursor = connection.cursor()

    # Fetch the account_id based on username
    account_id = get_account_id(cursor, username)

    if not account_id:
        flash('Account not found. Please log in again.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Retrieve data from the form
        address_line1 = request.form['addressLine1']
        address_line2 = request.form.get('addressLine2', '')
        city = request.form['city']
        state = request.form['state']
        zipCode = request.form['zipCode']
        country = request.form['country']
        isdefault = request.form.get('isdefault', False)

        # Update the address in the database
        query = """UPDATE addresses 
                   SET addressLine1=%s, addressLine2=%s, city=%s, state=%s, 
                       zipCode=%s, country=%s, isdefault=%s, updatedAt=NOW() 
                   WHERE addressID=%s AND accountID=%s"""
        cursor.execute(query, (address_line1, address_line2, city, state, zipCode, country, isdefault, address_id, account_id))
        connection.commit()

        flash('Address updated successfully!', 'success')
        return redirect(url_for('address'))

    # Fetch the specific address to edit
    cursor.execute("SELECT * FROM addresses WHERE addressID = %s AND accountID = %s", (address_id, account_id))
    address = cursor.fetchone()

    if address:
        # Render the update address form with current data
        return render_template('update_address.html', address=address)
    else:
        flash('Address not found!', 'error')
        return redirect(url_for('address'))


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('logged_in', None)  # Clear the login session
    flash('Logout successful!')
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    # Check if the user is logged in
    if 'logged_in' in session and session['logged_in']:
        username = session.get('username')  # Get the username from session

        # Fetch user data from the database
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM accountinformation WHERE username = %s", (username,))
        user = cursor.fetchone()  # Get the user data

        address = None 

        if user:
            # Fetch the default address for the user
            cursor.execute("""
                SELECT * FROM addresses 
                WHERE accountID = %s AND isdefault = TRUE
            """, (user['accountID'],))  # Use addressID as accountID reference
            address = cursor.fetchone()  # Get the default address

        if request.method == 'POST':
            # Collect the updated form data
            firstName = request.form.get('firstName')
            lastName = request.form.get('lastName')
            email = request.form.get('email')
            phone = request.form.get('phone')
            gender = request.form.get('gender')
            dob = request.form.get('dob')

            # Update other user profile information
            cursor.execute("""
        UPDATE accountinformation
        SET firstName = %s, lastName = %s, email = %s, phoneNumber = %s, gender = %s, dob = %s
        WHERE accountID = %s
    """, (firstName, lastName, email, phone, gender, dob, user['accountID']))
    

        if request.method == 'POST':
            # Update user profile information (this part stays the same)

            if 'profile_image' in request.files:
                profile_image = request.files['profile_image']
                if profile_image:
                    save_directory = r"C:\Users\marka\Unimerce\static\savedimages"  # Adjust this path
                    os.makedirs(save_directory, exist_ok=True)  # Create directory if it doesn't exist

                    filename = secure_filename(profile_image.filename)
                    unique_filename = f"{user['accountID']}_{filename}"
                    image_path = os.path.join(save_directory, unique_filename)

                    try:
                        # Save the image
                        profile_image.save(image_path)

                        # Update the user profile picture in the database
                        cursor.execute("""
                            UPDATE accountinformation 
                            SET profilePic = %s 
                            WHERE accountID = %s
                        """, (f"static/savedimages/{unique_filename}", user['accountID']))
                        
                        connection.commit()

                        flash('Profile picture updated successfully!', 'success')  # Add success message

                    except Exception as e:
                        flash(f"Error saving image: {str(e)}", 'error')

            first_name = request.form['firstName']
            last_name = request.form['lastName']
            email = request.form['email']
            phone = request.form['phone']
            gender = request.form['gender']
            dob = request.form['dob']

            cursor.execute("""
                UPDATE accountinformation 
                SET firstName = %s, lastName = %s, email = %s, phoneNumber = %s, gender = %s, dob = %s 
                WHERE accountID = %s
            """, (first_name, last_name, email, phone, gender, dob, user['accountID']))

            connection.commit()
            flash('Profile and address updated successfully!', 'success')

        cursor.close()
        connection.close()

        no_address = address is None

        # Render the profile page with user data
        return render_template('profile.html', user=user, address=address, no_address=no_address)
    else:
        flash('Please log in to access your profile.', 'warning')  # Flash a message
        return redirect(url_for('login'))  # Redirect to the login page

def send_otp_email(recipient_email, otp, first_name):
    user = "unimerce.ecommerce@gmail.com"
    password = "osww rkmj kpjp tghl"  # Use an app-specific password if necessary

    subject = "Verify your email to create your UNIMERCE account"
    body = f"Hello, {first_name}, \n\nThanks for your interest in creating an UNIMERCE account. To create your account, please verify your email address by entering the one-time password below. \nYour OTP code is: {otp}"

    # Set up the server
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()  # Secure the connection
        server.login(user, password)
        message = f'Subject: {subject}\n\n{body}'
        server.sendmail(user, recipient_email, message)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Check if OTP is being verified
        if 'otp' in request.form:
            entered_otp = request.form['otp']
            if entered_otp == str(session.get('otp')):  # Validate OTP
                # Here you can process the registration
                user_data = session.get('user_data')

                # Insert user data into the database
                connection = get_db_connection()
                cursor = connection.cursor()

                try:
                    cursor.execute(""" 
                        INSERT INTO accountinformation (username, password, email, phoneNumber, userType, firstName, lastName)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (user_data['username'], user_data['password'], user_data['email'], 
                          user_data['phone_number'], user_data['user_type'], 
                          user_data['firstname'], user_data['lastname']))
                    connection.commit()
                    flash('Account created successfully!', 'success')
                    return redirect(url_for('success'))  # Redirect to success page
                except mysql.connector.Error as e:
                    flash(f'Error: {str(e)}', 'error')
                    return redirect(url_for('register'))
                finally:
                    cursor.close()
                    connection.close()
            else:
                flash('Invalid OTP. Please try again.', 'error')
                # Repopulate the registration form fields with user data from the session
                return render_template('register.html',
                                       firstname=session['user_data']['firstname'],
                                       lastname=session['user_data']['lastname'],
                                       username=session['user_data']['username'],
                                       phoneNumber=session['user_data']['phone_number'],
                                       email=session['user_data']['email'])

        else:  # This is for sending the OTP
            firstname = request.form['firstname']
            lastname = request.form['lastname']
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            confirm_password = request.form['confirm-password']
            phone_number = request.form['phoneNumber']
            
            # Validate password confirmation
            if password != confirm_password:
                flash('Passwords do not match', 'error')
                return redirect(url_for('register'))

            # Connect to the database and check for existing user data
            connection = get_db_connection()
            cursor = connection.cursor()

            try:
                # Check if username already exists
                cursor.execute("SELECT COUNT(*) FROM accountinformation WHERE username = %s", (username,))
                if cursor.fetchone()[0] > 0:
                    flash('Username already exists. Please choose a different one.', 'error')
                    return redirect(url_for('register'))

                # Check if email already exists
                cursor.execute("SELECT COUNT(*) FROM accountinformation WHERE email = %s", (email,))
                if cursor.fetchone()[0] > 0:
                    flash('Email already exists. Please use a different email.', 'error')
                    return redirect(url_for('register'))

                # Check if phone number already exists
                cursor.execute("SELECT COUNT(*) FROM accountinformation WHERE phoneNumber = %s", (phone_number,))
                if cursor.fetchone()[0] > 0:
                    flash('Phone number already exists. Please use a different number.', 'error')
                    return redirect(url_for('register'))

                # Generate and send OTP
                otp = random.randint(100000, 999999)  # Generate a random 6-digit OTP
                send_otp_email(email, otp, firstname)  # Pass firstname to the email function
                session['otp'] = otp  # Store OTP in session
                session['otp_sent'] = True  # Flag that OTP has been sent
                session['user_data'] = {
                    'firstname': firstname,
                    'lastname': lastname,
                    'username': username,
                    'email': email,
                    'password': password,  # Hash this before storing it
                    'phone_number': phone_number,
                    'user_type': 'buyer'
                }
                flash('An OTP has been sent to your email. Please enter it below to complete registration.', 'info')
                return redirect(url_for('register'))  # Stay on the same page and show OTP input

            except mysql.connector.Error as e:
                flash(f'Error: {str(e)}', 'error')
                return redirect(url_for('register'))
            finally:
                cursor.close()
                connection.close()
        
    # If method is GET, render the registration form
    return render_template('register.html', 
                           firstname=request.form.get('firstname', ''),
                           lastname=request.form.get('lastname', ''),
                           username=request.form.get('username', ''),
                           phoneNumber=request.form.get('phoneNumber', ''),
                           email=request.form.get('email', ''))


@app.route('/otp_verification', methods=['GET', 'POST'])
def otp_verification():
    if request.method == 'POST':
        entered_otp = request.form['otp']
        if entered_otp == str(session.get('otp')):  # Check if the entered OTP matches the stored OTP
            # Retrieve user data from session
            user_data = session['user_data']
            
            # Insert data into accountinformation table
            connection = get_db_connection()
            cursor = connection.cursor()

            try:
                cursor.execute(""" 
                    INSERT INTO accountinformation (username, password, email, phoneNumber, userType, firstName, lastName)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (user_data['username'], user_data['password'], user_data['email'], 
                      user_data['phone_number'], user_data['user_type'], 
                      user_data['firstname'], user_data['lastname']))
                connection.commit()
                flash('Account created successfully!', 'success')
                return redirect(url_for('success'))  # Redirect to success page
            except mysql.connector.Error as e:
                flash(f'Error: {str(e)}', 'error')
                return redirect(url_for('register'))
            finally:
                cursor.close()
                connection.close()
        else:
            flash('Invalid OTP. Please try again.', 'error')

    return render_template('otp_verification.html')  # Create this HTML template

@app.route('/success')
def success():
    return "Registration successful!"

# Homepage route
@app.route('/')
def homepage():
<<<<<<< HEAD
    return render_template('homepage.html')
=======
    current_date = datetime.now().date()
    top_sales = get_top_sales()  # Get your products
    categories = get_categories_and_subcategories()
    deals = fetch_deals()

    user = session.get('username')  # Retrieve username from the session
    
    return render_template('homepage.html', top_sales=top_sales, categories=categories, deals=deals, current_date=current_date, user=user)
>>>>>>> 81bccb2 (seller_dashboard edited)

if __name__ == '__main__':
    app.run(debug=True)