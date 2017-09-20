from flask import Flask, render_template, redirect, request, session, flash
# import the Connector function
from mysqlconnection import MySQLConnector
import re
import os, binascii
import md5
# create a regular expression object that we can use run operations on
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
PASSWORD_REGEX = re.compile(r'^([^0-9]*|[^A-Z]*)$')
app = Flask(__name__)
app.secret_key = 'secret103048580e8w7'

# connect and store the connection in "mysql"
# note that you pass the database name to the function
mysql=MySQLConnector(app,'fullfriends')

@app.route('/')
def index():
	return render_template("index.html")

@app.route("/result", methods = ["POST"])
def posting():
	form = request.form
	##########################
	# LIST OF ERRORS TO FLASH#
	##########################
	errors = []

	###########################
	#VALIDATING THE FIRST NAME#
	###########################
	if len(request.form['first_name']) == 0:
		errors.append("Please enter your first name.")
	elif request.form['first_name'].isalpha() != True:
		errors.append("First name must only contain alphabetic letters.")

	##########################
	#VALIDATING THE LAST NAME#
	##########################
	if len(request.form['last_name']) == 0:
		errors.append("Last name cannot be empty!") 
	elif request.form['last_name'].isalpha() != True:
		errors.append("Last name must only contain alphabetic letters.")

	######################
	#VALIDATING THE EMAIL#
	######################
	if len(request.form['email']) == 0:
		errors.append("Email cannot be blank!")
	elif not EMAIL_REGEX.match(request.form['email']):
		errors.append("Invalid Email Address!")

	#########################
	#VALIDATING THE PASSWORD#
	#########################
	if len(form['password']) == 0:
		errors.append("Please enter a password")
	else:
		if len(form['password']) < 8:
			errors.append("Password must be at least 8 characters.")
		if not any([letter.isupper() for letter in form['password']]):
			errors.append("Password must contain at least one uppercase letter.")
		if not any([letter.isdigit() for letter in form['password']]):
			errors.append("Password must contain at least one number.")
		if not any([letter in "!@#$%^&*()-_=+~`\"'<>,.?/:;\}{][|" for letter in form['password']]):
			errors.append("Password must contain at least one special character.")
		if form['password'] != form['password_2']:
			errors.append('Password and confirmation fields must match.')

	##########################
	#IF THERE WERE ANY ERRORS#
	##########################
	if len(errors) > 0:
		for error in errors:
			flash(error)
	else:
		password = request.form['password']
		salt = binascii.b2a_hex(os.urandom(15))
		hashed_pw = md5.new(password + salt).hexdigest()

		data = {
			'first_name': request.form['first_name'],
			'last_name':  request.form['last_name'],
			'email': request.form['email'],
			'password': hashed_pw
		}

		query = "INSERT INTO users (users.first_name, users.last_name, users.email, users.password, users.created_at, users.updated_at) VALUES (:first_name,:last_name, :email,:password, NOW(), NOW())"

		mysql.query_db(query, data)

		return redirect('/submit')

@app.route("/submit")
def submitted():
	users = mysql.query_db('SELECT * FROM users')
	return	render_template("success.html", users=users)

@app.route("/submit/<user_id>/delete")
def delete_user(user_id):
	data = {'some_id': user_id}
	query = 'DELETE FROM users WHERE id = :some_id'
	mysql.query_db(query,data)
	return redirect("/submit")

app.run(debug=True)