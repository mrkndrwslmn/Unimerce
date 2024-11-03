from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from helpers.database import get_db_connection
from routes.user import get_account_id  # Correct path to import the function

# Create Blueprint
address_bp = Blueprint('address', __name__)

# Routes and Functions for Address Management

@address_bp.route('/', methods=['GET'])
def address():
    """Retrieve and display addresses for the logged-in user."""
    username = session.get('username')
    if not username:
        flash('You must be logged in to view this page.', 'error')
        return redirect(url_for('user.login'))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        account_id = get_account_id(cursor, username)
        cursor.execute(
            """
            SELECT addressID, addressLine1, addressLine2, city, state, zipCode, country, isDefault 
            FROM addresses WHERE accountID = %s
            """, (account_id,)
        )
        addresses = cursor.fetchall()

        addresses = sorted(addresses, key=lambda x: x['isDefault'], reverse=True)
    
        return render_template('update_address.html', addresses=addresses)
    
    except Exception as e:
        flash(f'An error occurred while retrieving addresses: {str(e)}', 'error')
        return redirect(url_for('homepage'))
    finally:
        cursor.close()
        connection.close()

@address_bp.route('/addresses')
def fetch_addresses():
    """Retrieve and display user addresses."""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)  # Ensure dictionary cursor

        account_id = session.get('userID')  # Assuming userID is stored in session
        cursor.execute("""
            SELECT addressID, addressLine1, addressLine2, city, state, zipCode, country 
            FROM addresses 
            WHERE accountID = %s AND isDefault = TRUE
        """, (account_id,))
        
        address = cursor.fetchone()  # Fetch a single address
        cursor.close()
        connection.close()

        if address:
            return render_template('address.html', address=address)
        else:
            flash('No default address found.', 'info')
            return render_template('address.html', address=None)
    
    except Exception as e:
        flash(f"An error occurred while retrieving addresses: {str(e)}", 'error')
        return render_template('error.html')

@address_bp.route('/add_edit', methods=['GET'])
def show_address_form():
    """Show form to add or edit an address."""
    address_id = request.args.get('addressID')
    address = None

    if address_id:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT addressID, addressLine1, addressLine2, city, state, zipCode, country FROM addresses WHERE addressID = %s", 
            (address_id,)
        )
        address = cursor.fetchone()
        cursor.close()
        connection.close()

        if not address:
            flash('Address not found.', 'error')
            return redirect(url_for('address.address'))

    return render_template('add_edit_address.html', title="Add/Edit Address", address=address)


@address_bp.route('/add_or_update', methods=['POST'])
def add_or_update_address():
    """Add or update an address."""
    username = session.get('username')
    if not username:
        flash('You must be logged in.', 'error')
        return redirect(url_for('user.login'))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        account_id = get_account_id(cursor, username)
        print(f"Account ID: {account_id}")  # Debugging

        if not account_id:
            flash('Account not found. Please log in again.', 'error')
            return redirect(url_for('user.login'))

        address_id = request.form.get('addressID')
        print(f"Received Address ID: {address_id}")  # Debugging

        address_data = {
            "address_line1": request.form.get('addressLine1'),
            "address_line2": request.form.get('addressLine2', ''),
            "city": request.form.get('city'),
            "state": request.form.get('state'),
            "zip_code": request.form.get('zipCode'),
            "country": request.form.get('country')
        }
        print(f"Address Data: {address_data}")  # Debugging

        if not address_data["address_line1"] or not address_data["city"]:
            flash('Address Line 1 and City are required.', 'error')
            return redirect(url_for('address.address'))

        # SQL Execution Debugging
        if address_id:
            query = """
                UPDATE addresses 
                SET addressLine1=%s, addressLine2=%s, city=%s, state=%s, zipCode=%s, country=%s, updatedAt=NOW() 
                WHERE addressID=%s AND accountID=%s
            """
            params = (*address_data.values(), address_id, account_id)
            print(f"Executing SQL: {query} with {params}")  # Debugging

            cursor.execute(query, params)
            print("Address updated successfully.")
            flash('Address updated successfully.', 'success')
        else:
            query = """
                INSERT INTO addresses (accountID, addressLine1, addressLine2, city, state, zipCode, country, isdefault) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, FALSE)
            """
            params = (account_id, *address_data.values())
            print(f"Executing SQL: {query} with {params}")  # Debugging

            cursor.execute(query, params)
            print("Address added successfully.")
            flash('Address added successfully.', 'success')

        connection.commit()
        print("Database commit successful!")

    except Exception as e:
        print(f'Error: {str(e)}')  # Debugging
        flash(f'An error occurred: {str(e)}', 'error')

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('address.address'))


@address_bp.route('/set_default', methods=['POST'])
def set_default_address():
    """Set an address as the default address."""
    address_id = request.form.get('addressID')
    username = session.get('username')

    if not username:
        flash('You must be logged in.', 'error')
        return redirect(url_for('user.login'))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        account_id = get_account_id(cursor, username)
        if not account_id:
            flash('Account not found.', 'error')
            return redirect(url_for('user.login'))

        # Set all addresses to non-default
        cursor.execute("""UPDATE addresses SET isDefault = FALSE WHERE accountID = %s""", (account_id,))
        # Set selected address as default
        cursor.execute("UPDATE addresses SET isDefault = TRUE WHERE addressID = %s AND accountID = %s", 
                       (address_id, account_id))
        connection.commit()
        flash('Default address set successfully.', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('address.address'))


@address_bp.route('/delete', methods=['POST'])
def delete_address():
    """Delete an address."""
    address_id = request.form.get('addressID')
    username = session.get('username')

    if not username:
        flash('You must be logged in.', 'error')
        return redirect(url_for('user.login'))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        account_id = get_account_id(cursor, username)
        if not account_id:
            flash('Account not found.', 'error')
            return redirect(url_for('user.login'))

        # Delete the address
        cursor.execute("DELETE FROM addresses WHERE addressID = %s AND accountID = %s", 
                       (address_id, account_id))
        connection.commit()
        flash('Address deleted successfully.', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('address.address'))


@address_bp.route('/update/<int:address_id>', methods=['GET', 'POST'])
def update_address(address_id):
    """Update a specific address."""
    username = session.get('username')
    if not username:
        flash('You must be logged in.', 'error')
        return redirect(url_for('user.login'))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        account_id = get_account_id(cursor, username)
        if not account_id:
            flash('Account not found.', 'error')
            return redirect(url_for('user.login'))

        if request.method == 'POST':
            # Update address details
            address_data = (
                request.form['addressLine1'],
                request.form.get('addressLine2', ''),
                request.form['city'],
                request.form['state'],
                request.form['zipCode'],
                request.form['country'],
                request.form.get('isdefault', False),
                address_id, 
                account_id
            )
            cursor.execute(
                """
                UPDATE addresses 
                SET addressLine1=%s, addressLine2=%s, city=%s, state=%s, zipCode=%s, country=%s, 
                    isdefault=%s, updatedAt=NOW() 
                WHERE addressID=%s AND accountID=%s
                """, 
                address_data
            )
            connection.commit()
            flash('Address updated successfully!', 'success')
            return redirect(url_for('address.address'))

        # Fetch address to edit
        cursor.execute("SELECT * FROM addresses WHERE addressID = %s AND accountID = %s", 
                       (address_id, account_id))
        address = cursor.fetchone()

        if address:
            return render_template('update_address.html', address=address)
        else:
            flash('Address not found.', 'error')
            return redirect(url_for('address.address'))
    finally:
        cursor.close()
        connection.close()
