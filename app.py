from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from flask_mysqldb import MySQL
import json

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Default WAMP MySQL username
app.config['MYSQL_PASSWORD'] = ''  # Default WAMP MySQL password (empty)
app.config['MYSQL_DB'] = 'flask_db'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.secret_key = 'your_secret_key'  # Required for session and flash messages

# Initialize MySQL
mysql = MySQL(app)

# Home Route (Login Page)
@app.route('/')
def login():
    return render_template('login.html')

# Handle Login Form Submission
@app.route('/login', methods=['POST'])
def handle_login():
    email = request.form.get('email')
    password = request.form.get('password')

    # Check if the user is the admin
    if email == 'admin@gmail.com' and password == 'admin123':
        session['logged_in'] = True
        session['username'] = 'Admin'
        return redirect(url_for('admin'))  # Redirect to admin.html

    # For regular users
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
    user = cur.fetchone()
    cur.close()

    if user:
        session['logged_in'] = True
        session['username'] = user['full_name']
        return redirect(url_for('home'))
    else:
        flash("Invalid credentials. Please try again.", "error")
        return redirect(url_for('login'))

# Handle Signup Form Submission
@app.route('/signup', methods=['POST'])
def handle_signup():
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    password = request.form.get('password')

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    existing_user = cur.fetchone()

    if existing_user:
        flash("Email already exists. Please use a different email.", "error")
        return redirect(url_for('login'))

    try:
        cur.execute("INSERT INTO users (full_name, email, password) VALUES (%s, %s, %s)", 
                    (full_name, email, password))
        mysql.connection.commit()
        flash("Registration successful! Please log in.", "success")
    except Exception as e:
        mysql.connection.rollback()
        flash("An error occurred. Please try again.", "error")
    finally:
        cur.close()

    return redirect(url_for('login'))

# Home Page (After Login)
@app.route('/home')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('home.html', username=session.get('username', 'Guest'))

# Admin Page
@app.route('/admin')
def admin():
    if not session.get('logged_in') or session.get('username') != 'Admin':
        return redirect(url_for('login'))

    # Fetch complaints from the database
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM complaints ORDER BY submitted_at DESC")
    complaints = cur.fetchall()
    cur.close()

    return render_template('admin.html', complaints=complaints)

# Handle Complaint Form Submission
@app.route('/submit_complaint', methods=['POST'])
def submit_complaint():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        # Insert the complaint into the database
        cur = mysql.connection.cursor()
        try:
            cur.execute(
                "INSERT INTO complaints (name, email, message) VALUES (%s, %s, %s)",
                (name, email, message)
            )
            mysql.connection.commit()
            flash("Your complaint has been submitted successfully!", "success")
        except Exception as e:
            mysql.connection.rollback()
            flash("An error occurred. Please try again.", "error")
        finally:
            cur.close()

    return redirect(url_for('home'))

# Handle Checkout
@app.route('/checkout', methods=['POST'])
def checkout():
    if request.method == 'POST':
        # Get the cart data from the request
        cart_data = request.json  # Expecting a JSON object with items and total price

        # Convert cart items to a JSON string
        items_json = json.dumps(cart_data['items'])

        # Insert the order into the database
        cur = mysql.connection.cursor()
        try:
            cur.execute(
                "INSERT INTO orders (items, total_price) VALUES (%s, %s)",
                (items_json, cart_data['total_price'])
            )
            mysql.connection.commit()
            return jsonify({"message": "Order placed successfully!"}), 200
        except Exception as e:
            mysql.connection.rollback()
            return jsonify({"error": "An error occurred while placing the order."}), 500
        finally:
            cur.close()

# Route to fetch items
@app.route('/get_items')
def get_items():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM items")
    items = cur.fetchall()
    cur.close()
    return jsonify(items)

# Route to add a new item
@app.route('/add_item', methods=['POST'])
def add_item():
    data = request.json
    name = data.get('name')
    category = data.get('category')
    price = data.get('price')
    quantity = data.get('quantity')
    image = data.get('image')

    cur = mysql.connection.cursor()
    try:
        cur.execute(
            "INSERT INTO items (name, category, price, quantity, image) VALUES (%s, %s, %s, %s, %s)",
            (name, category, price, quantity, image)
        )
        mysql.connection.commit()
        return jsonify({"message": "Item added successfully!"}), 200
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()

# Route to delete an item
@app.route('/delete_item', methods=['POST'])
def delete_item():
    data = request.json
    item_id = data.get('id')

    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM items WHERE id = %s", (item_id,))
        mysql.connection.commit()
        return jsonify({"message": "Item deleted successfully!"}), 200
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()

# Route to delete a complaint
@app.route('/delete_complaint/<int:complaint_id>', methods=['POST'])
def delete_complaint(complaint_id):
    if not session.get('logged_in') or session.get('username') != 'Admin':
        return redirect(url_for('login'))  # Ensure only the admin can delete complaints

    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM complaints WHERE id = %s", (complaint_id,))
        mysql.connection.commit()
        flash("Complaint deleted successfully!", "success")
    except Exception as e:
        mysql.connection.rollback()
        flash("An error occurred while deleting the complaint.", "error")
    finally:
        cur.close()

    return redirect(url_for('admin'))  # Redirect back to the admin page

# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Run the Application
if __name__ == '__main__':
    app.run(debug=True)