
from flask import session
from helpers.database import get_db_connection
from helpers.formatting import time_ago

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

def get_product_reviews(product_id):
    """Fetch all reviews for a specific product."""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        query = """
            SELECT 
                r.reviewID, 
                r.productID, 
                r.accountID, 
                r.rating, 
                r.reviewText, 
                r.reviewHeading,
                r.dateCreated, 
                r.dateUpdated,
                COALESCE(CONCAT(a.firstName, ' ', a.lastName), 'Anonymous') AS user,
                a.profilePic
            FROM product_reviews r
            LEFT JOIN accountinformation a ON r.accountID = a.accountID
            WHERE productID = %s
            ORDER BY dateCreated DESC
        """
        cursor.execute(query, (product_id,))
        reviews = cursor.fetchall()
        return reviews

    except Exception as e:
        print(f"Error fetching product reviews: {e}")
        return []

    finally:
        cursor.close()
        connection.close()

# Helper: Get product count for a seller
def get_product_count(seller_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS productsNum FROM products WHERE sellerID = %s", (seller_id,))
    product_count = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if product_count:  # Check if product_count is not None
        return product_count['productsNum']
    return 0

# Helper: Get average rating for seller's products
def get_average_rating(seller_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT AVG(r.rating) AS totalRating
        FROM product_reviews r
        JOIN products p ON r.productID = p.productID
        WHERE p.sellerID = %s
    """, (seller_id,))
    rating_data = cursor.fetchone()
    cursor.close()
    conn.close()
    return round(float(rating_data['totalRating'] or 0), 2)

# Helper: Get follower count for a seller
def get_follower_count(seller_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) AS totalFollowers FROM followers WHERE sellerID = %s", (seller_id,))
    followers_data = cursor.fetchone()
    cursor.close()
    conn.close()
    return followers_data['totalFollowers']

def get_seller_info(seller_id):
    """Fetch seller details by seller ID."""
    connection = get_db_connection()
    
    if not connection:
        return None  # Handle connection failure gracefully

    try:
        cursor = connection.cursor(dictionary=True)

        # Query to get seller information based on seller_id
        query = """
            SELECT 
                s.sellerID, 
                s.shopName, 
                s.imgURL, 
                s.join_date AS joinedDate, 
                s.isVerified, 
                COUNT(p.productID) AS productsNum, 
                COALESCE(AVG(r.rating), 0) AS totalRating, 
                COUNT(f.followerID) AS totalFollowers 
            FROM sellers s
            LEFT JOIN products p ON s.sellerID = p.sellerID
            LEFT JOIN product_reviews r ON p.productID = r.productID
            LEFT JOIN followers f ON s.sellerID = f.sellerID
            WHERE s.sellerID = %s
            GROUP BY s.sellerID
        """

        cursor.execute(query, (seller_id,))
        seller_info = cursor.fetchone()  # Get the first result
        print("Sasfas: ", seller_info)
        # Check if the seller exists
        if not seller_info:
            return None

        # Convert isVerified to a boolean
        seller_info['isVerified'] = bool(seller_info['isVerified'])
        seller_info['totalRating'] = get_average_rating(seller_info['sellerID'])

        return seller_info

    except Exception as e:
        print(f"Error fetching seller info: {e}")
        return None

    finally:
        cursor.close()
        connection.close()

def get_seller_id(cursor, username):
    """Fetch seller ID based on the account's username."""

    cursor.execute("""
        SELECT s.sellerID 
        FROM sellers s
        JOIN accountinformation a ON s.accountID = a.accountID
        WHERE a.accountID = %s
    """, (username,))
    
    result = cursor.fetchone()
    if result:
        seller_id = result['sellerID']  # Extract the sellerID correctly
    else:
        seller_id = None  # Handle case where no seller is found

def get_seller_id_by_username(username):
    """Fetch the seller ID based on the provided username."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT s.sellerID 
            FROM sellers s
            JOIN accountinformation a ON s.accountID = a.accountID
            WHERE a.username = %s
        """, (username,))

        result = cursor.fetchone()
        if result:
            return result['sellerID']
        else:
            print(f"No seller ID found for username: {username}")
            return None
    except Exception as e:
        print(f"Error fetching seller ID: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def fetch_all_products(seller_id):
    """Fetch all products, optionally filtered by seller ID."""

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        if seller_id:
            # Fetch products for the specific seller
            print(f"Fetching products for seller ID: {seller_id}")
            cursor.execute(
                """SELECT p.productID, 
                    p.productName, 
                    p.productDesc, 
                    p.productPrice, 
                    p.imgURL, 
                    p.categoryID,
                    p.subcategoryID,
                    p.stock_quantity,
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
                    GROUP_CONCAT(i.imageURL) AS imageURLs
                FROM products p
                LEFT JOIN productimages i ON p.productID = i.productID
                WHERE sellerID = %s
                GROUP BY p.productID""",
                (seller_id,)
            )
        else:
            # Fetch all products if no seller ID is provided
            cursor.execute(
                """SELECT p.productID, 
                    p.productName, 
                    p.productDesc, 
                    p.productPrice, 
                    p.categoryID,
                    p.subcategoryID,
                    p.stock_quantity,
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
                    GROUP_CONCAT(i.imageURL) AS imageURLs
                FROM products p
                LEFT JOIN productimages i ON p.productID = i.productID
                GROUP BY p.productID
                """
            )

        products = cursor.fetchall()
        print(f"Fetched {len(products)} products.")
        return products
        
    except Exception as e:
        print(f"Error fetching products: {e}")
        products = []
    finally:
        cursor.close()
        connection.close()


def fetch_all_categories():
    """Fetch all product categories from the database."""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT categoryID, categoryName as name, imgURL FROM categories")
        categories = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching categories: {e}")
        categories = []  # Return an empty list if an error occurs
    finally:
        cursor.close()
        connection.close()

    return categories

def fetch_subcategories_by_category(category_id):
    """Fetch subcategories for a given category."""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    print(f"Category ID IS KK: {category_id}")
    try:
        query = """
            SELECT subcategoryID, subcategoryName 
            FROM subcategories 
            WHERE categoryID = %s
        """
        cursor.execute(query, (category_id,))
        subcategories = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching subcategories: {e}")
        subcategories = []  # Return an empty list on error
    finally:
        cursor.close()
        connection.close()

    return subcategories

def get_categories_and_subcategories():
    """Fetch categories and subcategories from the database."""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Query to fetch categories and their corresponding subcategories
        query = """
            SELECT 
                c.categoryID, c.categoryName, 
                s.subcategoryID, s.subcategoryName
            FROM 
                categories c
            LEFT JOIN 
                subcategories s ON c.categoryID = s.categoryID
        """
        cursor.execute(query)
        results = cursor.fetchall()

        # Organize data: Group subcategories under their respective categories
        categories = {}
        for row in results:
            category_id = row['categoryID']

            # Initialize category if not already present
            if category_id not in categories:
                categories[category_id] = {
                    'categoryID': category_id,
                    'categoryName': row['categoryName'],
                    'subcategories': []
                }

            # Add subcategory if present
            if row['subcategoryID']:
                categories[category_id]['subcategories'].append({
                    'subcategoryID': row['subcategoryID'],
                    'subcategoryName': row['subcategoryName']
                })

        return list(categories.values())  # Convert to a list for rendering

    except Exception as e:
        print(f"Error fetching categories: {e}")
        return []
    finally:
        cursor.close()
        connection.close()

def fetch_all_variation_types():
    """Fetch all variation types from the database."""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT variationTypeID, variationType FROM variation_types")
        variation_types = cursor.fetchall()
        return variation_types
    except Exception as e:
        print(f"Error fetching variation types: {str(e)}")
        return []
    finally:
        cursor.close()
        connection.close()

def fetch_userdetails(username):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT * FROM accountinformation WHERE username = %s""", (username,))
        user = cursor.fetchone()

        if user:
            return user
        else:
            print(f"No seller ID found for username: {username}")
            return None
        
    except Exception as e:
        print(f"Error fetching seller ID: {e}")
        return None
    finally:
        cursor.close()
        conn.close()