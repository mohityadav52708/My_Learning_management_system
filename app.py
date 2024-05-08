from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from pymongo import MongoClient
import datetime
# import bcrypt
import os
import smtplib
import ssl
import random
import string
# from flask_mail import Mail, Message
from flask import request
from flask import Flask
from werkzeug.utils import secure_filename
import matplotlib.pyplot as plt
import io
import uuid
import numpy as np
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
# import plotly.graph_objs as go
import base64
from flask import Flask, render_template
from flask_pymongo import PyMongo
import plotly.graph_objs as go

app = Flask(__name__)

UPLOAD_FOLDER = '/path/to/upload/folder'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'your_secret_key'

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'sanjivinihealthcarecenter@gmail.com'  # Use the provided email
app.config['MAIL_PASSWORD'] = 'doszhhhwkuxdojsr'                    # Use the provided email password
app.config['MAIL_DEFAULT_SENDER'] = 'sanjivinihealthcarecenter@gmail.com'  # Use the provided email
app.config['MONGODB_URI'] = 'mongodb+srv://whitedevil7628:devil010@cluster0.gr1wse1.mongodb.net/'

# Initialize Flask-Mail
mail = Mail(app)

app.config['MONGO_URI'] = 'mongodb+srv://whitedevil7628:devil010@cluster0.gr1wse1.mongodb.net/'
uri = "mongodb+srv://whitedevil7628:devil010@cluster0.gr1wse1.mongodb.net/"
client = MongoClient(uri)
database = client["endsem"]  # Replace "your_database_name" with your actual database name
collection = database["book_list"]


mongo = PyMongo(app)
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
        return False

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
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
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
            flash('Registration successful!', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')
@app.route('/home', methods=['GET', 'POST'])
def home():
    collection = database["book_list"]
    
    # Fetch data from MongoDB
    data = collection.find()

    # Extracting data for the charts
    bar_x_data = []
    bar_y_data = []
    pie_labels = []
    pie_values = []
    line_x_data = []
    line_y_data = []

    for entry in data:
        bar_x_data.append(entry['name'])
        bar_y_data.append(int(entry['price']))
        pie_labels.append(entry['name'])
        pie_values.append(int(entry['price']))
        line_x_data.append(entry['name'])
        line_y_data.append(int(entry['price']))

    # Creating the bar chart
    bar_chart = go.Bar(
        x=bar_x_data,
        y=bar_y_data
    )

    # Creating the layout for the bar chart
    bar_layout = go.Layout(
        title='Book Prices (Bar Chart)',
        xaxis=dict(title='Book Name'),
        yaxis=dict(title='Price')
    )

    # Creating the pie chart
    pie_chart = go.Pie(
        labels=pie_labels,
        values=pie_values
    )

    # Creating the layout for the pie chart
    pie_layout = go.Layout(
        title='Book Prices (Pie Chart)'
    )

    # Creating the line graph
    line_graph = go.Scatter(
        x=line_x_data,
        y=line_y_data,
        mode='lines+markers'
    )

    # Creating the layout for the line graph
    line_layout = go.Layout(
        title='Book Prices (Line Graph)',
        xaxis=dict(title='Book Name'),
        yaxis=dict(title='Price')
    )

    # Combining data and layout into figures for all charts
    bar_fig = go.Figure(data=[bar_chart], layout=bar_layout)
    pie_fig = go.Figure(data=[pie_chart], layout=pie_layout)
    line_fig = go.Figure(data=[line_graph], layout=line_layout)

    # Convert the Plotly figures to JSON for rendering in the template
    bar_chart_json = bar_fig.to_json()
    pie_chart_json = pie_fig.to_json()
    line_chart_json = line_fig.to_json()

    return render_template('home.html', bar_chart=bar_chart_json, pie_chart=pie_chart_json, line_chart=line_chart_json)

@app.route('/generate-graph', methods=['POST'])
def generate_graph():
    if request.method == 'POST':
        # Example: Retrieving data from the form
        price = request.form['price']
        category = request.form['category']

        # Example: Generating a Plotly graph
        trace = go.Scatter(x=[1, 2, 3, 4], y=[10, 11, 12, 13], mode='markers')
        layout = go.Layout(title='Example Plotly Graph', xaxis=dict(title='X-axis'), yaxis=dict(title='Y-axis'))
        fig = go.Figure(data=[trace], layout=layout)
        
        # Convert the Plotly graph to HTML
        graph_html = fig.to_html(full_html=False)

        return graph_html
    else:
        return 'Method Not Allowed', 405

def generate_bar_chart(book_names, book_prices):
    # Generate a bar chart using Plotly
    trace = go.Bar(x=book_names, y=book_prices)
    layout = go.Layout(title='Prices of Books', xaxis=dict(title='Book Name'), yaxis=dict(title='Price'))
    fig = go.Figure(data=[trace], layout=layout)
    graph_html = fig.to_html(full_html=False)
    return graph_html

@app.route('/contact', methods=['GET'])
def contact():
    return render_template('contact.html')

@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        # Send an email to the user
        msg = Message(subject='Thank you for contacting us!',
                      sender=app.config['MAIL_USERNAME'],
                      recipients=[email])
        msg.body = f"Dear {name},\n\nThank you for contacting us. We have received your message:\n\n{message}\n\nWe will get back to you shortly.\n\nBest regards,\nThe Library Team"
        
        try:
            mail.send(msg)
        except Exception as e:
            flash('Failed to send email. Please try again later.', 'danger')
            return redirect(url_for('contact'))

        # You can handle the message here, such as storing it in the database, etc.

        flash('Your message has been received. We will get back to you soon. Thank you for reaching out.', 'success')
        return redirect(url_for('contact'))
    else:
        flash('Invalid request method.', 'danger')
        return redirect(url_for('contact')) 

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')


# Route for adding a book
# Route for adding a book
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

       
# Function to add book data to database
def add_book_to_database(sr, name, author, date, price, category):
    # For MongoDB, you can use PyMongo:
    collection.insert_one({'sr': sr, 'name': name, 'author': author, 'date': date, 'price': price, 'category': category})
    # return True if book is successfully added, else return False
    pass


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

# Route for viewing all books
# Route for viewing all books
def get_books():
    # Fetch books from the database, include required fields, and sort them based on serial number
    books = collection.find({}, {"_id": 0, "filename": 1, "serial number": 1, "name": 1, "author": 1, "date": 1, "price": 1, "category": 1, "available": 1}).sort("serial number", 1)
    return list(books)




@app.route('/view', methods=['GET'])
def view_book():
    # Fetch the list of books from the database
    collection = database["book_list"]
    books = get_books()
    books = collection.find({}, {"_id": 0})  # Exclude the _id field
    return render_template('view_book.html', books=books)

# Route for registering a new user contact
@app.route('/signup', methods=['POST'])
def signup():
    email = request.form['email']
    password = request.form['password']
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    if register_insert(email, hashed_password):
        return jsonify(message='User already exists'), 400
    else:
        verification_otp = generate_otp()
        verification_expiry = datetime.datetime.now() + datetime.timedelta(minutes=1)
        
        send_verification_email(email, verification_otp)
        return redirect(url_for('verification', email=email))

# Route for verifying OTP
@app.route('/verify-otp',methods=['GET', 'POST'])
def verify_otp():
    email = request.form['email']
    otp = request.form['otp']

    try:
        # Find the user by email
        user = database["login"].find_one({"username": email})

        if not user:
            # Display an alert and redirect to the signup page with an error message
            flash('User not found', 'error')
            return redirect(url_for('signup'))

        # Check if OTP is correct and not expired
        if user['verification_otp'] == otp and user['verification_expiry'] > datetime.datetime.now():
            # Update user as verified and clear OTP fields
            user['verified'] = True
            user['verification_otp'] = None
            user['verification_expiry'] = None
            database["login"].save(user)

            # Display an alert and redirect to the index page
            flash('Email verified successfully', 'success')
            return redirect(url_for('index'))
        else:
            # If OTP is invalid or expired, handle cleanup by removing the incomplete user
            cleanup_incomplete_user(user['_id'])

            # Display an alert and redirect to the signup page with an error message
            flash('Invalid or expired OTP', 'error')
            return redirect(url_for('signup'))
    except Exception as e:
        print('Error verifying OTP:', e)
        # Display an alert and redirect to the signup page with an error message
        flash('Internal server error', 'error')
        return redirect(url_for('signup'))

# Function to cleanup incomplete user
def cleanup_incomplete_user(user_id):
    # Perform cleanup logic here, such as deleting the user document from the database
    pass

# Route for the verification page
@app.route('/verification/<email>', methods=['GET'])
def verification(email):
    # Your verification logic goes here
    return render_template('verification.html')

# Function to send verification email
def send_verification_email(email, otp):
    port = 465
    smtp_server = "smtp.gmail.com"
    sender_email = "sanjivinihealthcarecenter@gmail.com"  # Enter your email address
    password = "doszhhhwkuxdojsr"  # Enter your password
    
    message = f"""\
    Subject: Email Verification

    Your OTP for email verification is: {otp}"""
    
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, email, message)

# Function to generate OTP
def generate_otp():
    digits = string.digits
    return ''.join(random.choice(digits) for i in range(6))

# Function to verify OTP
def validate_otp(email, otp):
    user = database["login"].find_one({"username": email})
    if user and user['verification_otp'] == otp and user['verification_expiry'] > datetime.datetime.now():
        return True
    else:
        return False
    
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        # Check if the email exists in the database
        collection = database["users"]  # Assuming you have a collection named "users"
        user = collection.find_one({"email": email})
        if user:
            # Generate a temporary password
            temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            # Update the user's password with the temporary password
            collection.update_one({"email": email}, {"$set": {"password": temp_password}})
            # Send an email with the temporary password (You need to implement this part)
            flash('Password reset instructions sent to your email', 'info')
            return redirect(url_for('login'))
        else:
            flash('Email not found', 'error')
            return redirect(url_for('forgot_password'))
    else:
        return render_template('forgot_password.html')


def generate_token():
    return str(uuid.uuid4())

def send_otp(email, otp):
    port = 587  # SMTP port
    smtp_server = "smtp.gmail.com"
    sender_email = app.config['MAIL_USERNAME']
    password = app.config['MAIL_PASSWORD']

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = email
    message["Subject"] = "OTP for Password Reset"

    body = f"Your OTP for password reset is: {otp}"
    message.attach(MIMEText(body, "plain"))

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls(context=context)
            server.login(sender_email, password)
            server.sendmail(sender_email, email, message.as_string())
            print("OTP sent successfully")
    except Exception as e:
        print("Error sending OTP:", e)
        


if __name__ == '__main__':
    app.run(debug=True)
