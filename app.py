

import re
import bcrypt
from flask import Flask, Response, flash, redirect, render_template, request, session, url_for
from flask_bcrypt import Bcrypt
from flask_bootstrap import Bootstrap
from flask_mysqldb import MySQL, MySQLdb
from flask_login import UserMixin
from flask_login import login_user
from flask import jsonify, request
from vonage import Sms,Client, vonage;Sms

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'afya1'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)
bootstrap = Bootstrap(app)
bcrypt=Bcrypt(app)

admin_phone_number = '+254745805782'







class User(UserMixin):
    def __init__(self, email):
        self.email = email

    @staticmethod
    def get(email):
        # Implement a method to retrieve a user from the database based on the email
        return None








@app.route("/")
def hello_world():
    return render_template("home.html")


@app.route("/loan", methods=['GET', 'POST'])
def loan():
    user_qualifies = None 
    
    if request.method == "POST":
        profession = request.form['profession']
        email = session.get('email') 
   
        user_data, user_phone_number = check_loan_eligibility1(session['email'])
    
        if user_data and user_data['amount'] > 10:
            send_sms_notification(user_phone_number)
            user_qualifies=True
            #return render_template('loan.html', user_qualifies=True)
        else:
            user_qualifies=False
            #return render_template('loan.html', user_qualifies=False)
    return render_template('loan.html',user_qualifies=user_qualifies)
def check_loan_eligibility1(email):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user WHERE email = %s", (email,))
    user_data = cur.fetchone()
    user_phone_number = user_data['phone']  # Assuming phone number is stored in 'phone_number' column
    return user_data, user_phone_number

def send_sms_notification(user_phone_number):
       client = Client(key="44b618f4", secret="0dehetuX9n10Iehd")
       sms = Sms(client=client)
       
       response = sms.send_message(
         {
        "from": "Vonage APIs",
        "to": admin_phone_number,
        "text": 'User qualified for loan. Phone number: {}'.format(user_phone_number)
     })
       response = response["messages"][0]

       if response["status"] == "0":
        print("Message sent successfully.")
       else:
        print(f"Message failed with error: {response['error-text']}")
    
#     user_qualifies = None  # Set a default value
    
#     if request.method == "POST":
#         profession = request.form['profession']
#         email = session.get('email')  # Get the user's email from the session
        
#         if email:
#             user_qualifies = check_loan_eligibility(email)
#         else:
#             # Handle the case where the user's email is not in the session
#             user_qualifies = False

#     return render_template('loan.html', user_qualifies=user_qualifies)

# # Function to check loan eligibility
# def check_loan_eligibility(email):
#     cur = mysql.connection.cursor()
#     cur.execute("SELECT * FROM user WHERE email = %s", (email,))
#     user_data = cur.fetchone()
#     cur.close()

#     if user_data and user_data.get('amount', 0) > 10:  # Check if user_data is not None and amount is greater than 10
#         return True
#     else:
#         return False

@app.route('/details', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        phone1=request.form['phone1']
        phone2=request.form['phone2']
        amount=request.form['amount']
        password = request.form['password'].encode('utf-8')
        hash_password = bcrypt.generate_password_hash(password)
        
        cur = mysql.connection.cursor()
         #check if account exixts
        cur.execute('SELECT * FROM user WHERE email=%s',(email,))
        account=cur.fetchone()
        if account:
            flash("Account already exists!")
        elif not re.match(r'[^@]+@[^@]+\.[^@]+',email):
            flash('Invalid email Address')
        elif not email or not password or not first_name or  not last_name:
            flash('Please fill out the form')
        else:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO user(first_name,last_name,email,phone,phone1,phone2,amount,password) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",(first_name,last_name,email,phone,phone1,phone2,amount,hash_password,))
            mysql.connection.commit()
            session['first_name'] = first_name
            session['last_name']=last_name
            session['email']=email
            session['phone']=phone
            session['phone1']=phone1
            session['phone2']=phone2
            session['amount']=email
            
            cur.close()
           
            flash("Registerd successfully")
            return redirect(url_for("login"))
    
    return render_template('details.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM user WHERE email = %s", (email,))
        user_data = cur.fetchone()
     
        
        cur.close()
       
      
        
        
        
        if bcrypt.check_password_hash(user_data['password'], password):
            session['loggedin']=True
            session['email']=email
            flash('Login successful!')
            return redirect(url_for('loan'))
        else:
           
            flash('Invalid email or password')
            

    return render_template("login.html")
    
    # if request.method == 'POST':
    #     email = request.form['email']
    #     password = request.form['password']

    #     # Authenticate user (e.g., query database)
    #     user = authenticate_user(email, password)

    #     if user:
    #         login_user(user)
    #         flash('Login successful!')
    #         return redirect(url_for('loan'))
    #     else:
    #         flash('Invalid email or password')

    # return render_template('login.html')

# def authenticate_user(email, password):
#     # Query database to find user with given email
#     user_data = user(email)
    
    
#     if user_data and bcrypt.check_password_hash(user_data['password'], password):
        
#         return True
        
#     else:
#         return False
# def user(email):
#     cur = mysql.connection.cursor()
#     cur.execute("SELECT * FROM user WHERE email = %s", (email,))
#     user_data = cur.fetchone()
#     cur.close()
#     return user_data


# @app.route('/login', methods=["GET", "POST"])
# def login():
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']
#         cur = mysql.connection.cursor()
        
#         result = cur.execute("SELECT * FROM user WHERE email=%s ", [email])
#         print(result,flush=True)
        
#         if result > 0:
#             users = cur.fetchone()
#             Password1 = users['password']
#             if bcrypt.check_password_hash(Password1, password):
#                 session['loggedin'] = True
#                 session['first_name'] = users['first_name']
#                 session['last_name'] = users['last_name']
#                 session['email'] = users['email']
#                 print("User logged in successfully")
                
#                 flash("You have logged in successfully")
#                 return redirect(url_for("loan"))
#             else:
#                     flash("Incorrect username or password")
#         else:
#                 flash("User does not exist")
        
       
    
#         cur.close()
        
#     return render_template("login.html")

ELIGIBILITY_CRITERIA = {
    'Dental': {
         
        'minimum_income': 50  # Minimum annual income required
    },
    'Eye Exams/Eye Glasses': {
        
        'minimum_income': 40
    },
    'Hearing':{
        'minimum_income':20
    }
}
















if __name__ == "__main__":
    
    app.debug =True
    app.run(debug=True)
   