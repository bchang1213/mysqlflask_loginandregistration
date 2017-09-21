from flask import Flask, render_template, redirect, request, session, flash
# import the Connector function
from mysqlconnection import MySQLConnector
import re
from flask.ext.bcrypt import Bcrypt
# create a regular expression object that we can use run operations on
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
PASSWORD_REGEX = re.compile(r'^([^0-9]*|[^A-Z]*)$')
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = 'secret103048580e8w7'

# connect and store the connection in "mysql"
# note that you pass the database name to the function
mysql=MySQLConnector(app,'fullfriends')

@app.route('/')
def index():
	if 'user_id' in session:
		return redirect('/submit')
	return render_template("index.html")

@app.route("/register", methods = ["POST"])
def register():
	form = request.form
	##########################
	# LIST OF ERRORS TO FLASH#
	##########################
	errors = []

	###########################
	#VALIDATING THE FIRST NAME#
	###########################
	if not len(form['first_name']):
		errors.append("Please enter your first name.")
	elif len(form['first_name']) < 2:
		errors.append("First name must contain at least two characters.")
	elif not form['first_name'].isalpha():
		errors.append("First name must only contain alphabetic letters.")

	##########################
	#VALIDATING THE LAST NAME#
	##########################
	if not len(form['last_name']):
		errors.append("Last name cannot be empty!")
	elif len(form['last_name']) < 2:
		errors.append("Last name must contain at least two characters.")
	elif not form['last_name'].isalpha():
		errors.append("Last name must only contain alphabetic letters.")

	######################
	#VALIDATING THE EMAIL#
	######################
	if not len(form['email']):
		errors.append("Please enter your e-mail address.")
	elif not EMAIL_REGEX.match(form['email']):
		errors.append("Please enter a valid e-mail address.")

	#########################
	#VALIDATING THE PASSWORD#
	#########################
	if  not  len(form['password']):
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
		if form['password'] != form['passconf']:
			errors.append('Password and confirmation fields must match.')

	##########################
	#IF THERE WERE ANY ERRORS#
	##########################
	if len(errors) > 0:
		for error in errors:
			flash(error, "error")
	else:
		check_email = mysql.query_db("SELECT email FROM users WHERE email = :email", {'email': form['email']})
		if len(check_email):
			flash("Account at that email address ({}) is already taken".format(form['email']), "error")
			return redirect('/')

		password = form['password']
		hashed_pw = bcrypt.generate_password_hash(password)

		data = {
			'first_name': request.form['first_name'],
			'last_name':  request.form['last_name'],
			'email': request.form['email'],
			'password': hashed_pw
		}

		query = """INSERT INTO users (users.first_name, users.last_name, 
			users.email, users.password, users.created_at, users.updated_at) 
		VALUES (:first_name,:last_name, :email,:password, NOW(), NOW())"""

		new_user = mysql.query_db(query, data)
		if new_user:
				flash('Registration was successful! Please sign-in to continue.',"success")
				return redirect('/')
		else:
			flash('something went wrong', 'error')


@app.route('/login', methods = ["POST"])
def login():
	form = request.form
	if not EMAIL_REGEX.match(form['email']) or len(form['password']) < 8:
		flash('Please enter valid credentials', "error")
	return redirect('/')

	encrypted_password = bcrypt.generate_password_hash(form['password'])

	data = {"email": form['email'], "password": encrypted_password}
	query = "SELECT * FROM users WHERE email = :email"

	users = mysql.query_db(query,data)

	if len(users):
		user = users[0]
		if not bcrypt.check_password_hash(user['password'],form['password']):
			flash('Account with those credentials could not be found.', 'error')
			return redirect('/')
		else:
			session['user_id'] = user['id']
			flash('Login successful!', 'success')
			return redirect('/submit')
	else:
		flash('Account with those credentials could not be found.','error')
	return redirect('/')

@app.route("/logout")
	def logout():
		session.clear()
		return redirect('/')


@app.route("/submit")
def submitted():
	if 'user_id' not in session:
		flash("You must be signed in to do that!", "error")
		return redirect('/')
	users = mysql.query_db('SELECT * FROM users WHERE id = :id', {'id':session['user_id']})
	if not len(users):
		flash("Something went wrong", 'error')
		return redirect('/')
	return	render_template("success.html", user = user[0])

@app.route("/submit/<user_id>/delete")
def delete_user(user_id):
	data = {'some_id': user_id}
	query = 'DELETE FROM users WHERE id = :some_id'
	mysql.query_db(query,data)
	return redirect("/submit")

app.run(debug=True)