from flask import Flask, request, jsonify, flash, redirect, url_for, render_template
from pymongo import MongoClient
import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Access the MongoDB URI from the environment variables
MONGODB_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGODB_URI)
database = client["endsem"]

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def register_user(username, password):
    collection = database["login"]
    user_data = collection.find_one({"username": username})
    if user_data:
        return jsonify({"message": "User already exists"}), 409
    else:
        collection.insert_one({"username": username, "password": password})
        return jsonify({"message": "User registered successfully"}), 201

def login_user(username, password):
    collection = database["login"]
    user_data = collection.find_one({"username": username, "password": password})
    if user_data:
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message": "Invalid username or password"}), 401

def add_book(sr, name, author, date, price, category, status="yes"):
    collection = database["book_list"]
    book_data = collection.find_one({"serial number": sr})
    if not book_data:
        collection.insert_one({"serial number": sr, "name": name, "author": author, "date": date,
                               "price": price, "category": category, "available": status})
        return jsonify({"message": "Book added successfully"}), 201
    else:
        return jsonify({"message": "Book with the same serial number already exists"}), 409

def delete_book(sr):
    collection = database["book_list"]
    result = collection.delete_one({"serial number": sr})
    if result.deleted_count:
        return jsonify({"message": "Book deleted successfully"}), 200
    else:
        return jsonify({"message": "Book not found"}), 404

def get_all_books():
    collection = database["book_list"]
    books = collection.find({}, {"_id": 0})  # Exclude the _id field
    return jsonify(books), 200

def get_book_by_serial_number(sr):
    collection = database["book_list"]
    book_data = collection.find_one({"serial number": sr}, {"_id": 0})
    if book_data:
        return jsonify(book_data), 200
    else:
        return jsonify({"message": "Book not found"}), 404

# Routes for user management
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400
    return register_user(username, password)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400
    return login_user(username, password)

# Routes for book management
@app.route('/books', methods=['POST'])
def add_book_route():
    data = request.get_json()
    sr = data.get('serial_number')
    name = data.get('name')
    author = data.get('author')
    date = data.get('date')
    price = data.get('price')
    category = data.get('category')
    if not sr or not name or not author or not date or not price or not category:
        return jsonify({"message": "Missing required fields"}), 400
    return add_book(sr, name, author, date, price, category)

@app.route('/books/<sr>', methods=['DELETE'])
def delete_book_route(sr):
    return delete_book(sr)

@app.route('/books', methods=['GET'])
def get_books():
    return get_all_books()

@app.route('/books/<sr>', methods=['GET'])
def get_book(sr):
    return get_book_by_serial_number(sr)

if __name__ == '__main__':
    app.run(debug=True)
