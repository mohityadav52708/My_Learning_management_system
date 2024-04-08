from flask import Flask, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Access the MongoDB URI from the environment variables
MONGODB_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGODB_URI)
database = client["endsem"]

app = Flask(__name__)
app.secret_key = 'your_secret_key'


# Functions for database operations
def register_insert(username, password):
    collection = database["login"]
    user_data = collection.find_one({"username": username})
    if user_data:
        return True  # User already exists
    else:
        collection.insert_one({"username": username, "password": password})
        return False  # User registered successfully

def login_data(username, password):
    collection = database["login"]
    user_data = collection.find_one({"username": username, "password": password})
    return bool(user_data)  # True if login successful, False otherwise

def add_book(sr, name, author, date, price, category, status="yes"):
    collection = database["book_list"]
    book_data = collection.find_one({"serial number": sr})
    if not book_data:
        collection.insert_one({"serial number": sr, "name": name, "author": author, "date": date,
                               "price": price, "category": category, "available": status})
        return True  # Book added successfully
    else:
        return False  # Book with the same serial number already exists

def delete_book(sr):
    collection = database["book_list"]
    result = collection.delete_one({"serial number": sr})
    return bool(result.deleted_count)  # True if book deleted successfully, False otherwise

# Route for login
@app.route('/', methods=['GET'])
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if login_data(username, password):
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            return jsonify({"message": "Invalid username or password"}), 401
    else:
        return render_template('login.html')

# Route for registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if register_insert(username, password):
            flash('Username already exists', 'danger')
        else:
            return jsonify({"message": "User registered successfully"}), 201
    return render_template('register.html')

# Route for home page
@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Handle form submission or other POST requests here
        pass
    return render_template('home.html')

# Route for adding a book
@app.route('/add', methods=['GET', 'POST'])
def add_book_route():
    if request.method == 'POST':
        sr = request.form['book_id']
        name = request.form['book_name']
        author = request.form['author_name']
        date = request.form['date_name']
        price = request.form['price_name']
        category = request.form['category_name']
        if add_book(sr, name, author, date, price, category):
            flash('Book added successfully', 'success')
        else:
            flash('Failed to add book. Please try again', 'danger')
        return redirect(url_for('home'))
    else:
        return render_template('add_book.html')

# Route for deleting a book
@app.route('/delete', methods=['GET', 'POST'])
def delete_book_route():
    if request.method == 'POST':
        sr = request.form['book_id']
        if delete_book(sr):
            flash('Book deleted successfully', 'success')
        else:
            flash('Failed to delete book. Book does not exist', 'danger')
        return redirect(url_for('home'))
    else:
        return render_template('delete_book.html')
    
@app.route('/view', methods=['GET'])
def view_book():
    # Fetch the list of books from the database
    collection = database["book_list"]
    books = collection.find({}, {"_id": 0})  # Exclude the _id field
    return render_template('view_book.html', books=books)

# Route for viewing the defaulter identification
@app.route('/defaulter-identification')
def defaulter_identification():
    return render_template('defaulter-identification.html')

if __name__ == '__main__':
    app.run(debug=True)
