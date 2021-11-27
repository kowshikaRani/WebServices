# -*- coding: utf-8 -*-
"""
Created on Sat Oct 16 10:07:20 2021

@author: user
"""

from flask import Flask,jsonify,request,redirect,url_for,render_template,session
from flaskext.mysql import MySQL
from flask_session import Session
from flask_session.__init__ import Session
import re
import os

#C:\kowshika\sem9\webservices\templates\colorlib-search-12

app = Flask(__name__,template_folder='templates')
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'akr'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

mysql.init_app(app)

conn = mysql.connect()
cursor =conn.cursor()


# A route to return all of the available entries in our catalog.
@app.route('/')
def home():
    return render_template("home.html")

@app.route('/api')
def homee():
    return render_template("Homee.html")

@app.route('/api/signin')
def signin():
    return render_template("signin.html")

@app.route('/api/login', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        
        con = mysql.connect()
        c = con.cursor()        
        #fetch the customer id from the email got as input
        q="select customername from customer where emailid = %s"
        val=(username)
        
        c.execute(q,val)
        customername=str(c.fetchone())
        
        session["name"] = customername[2:-3]
        
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM customer WHERE emailId = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        if account:
            # Create session data, we can access this data in other routes
            #session['loggedin'] = True
            #session['id'] = account['id']
            #session['username'] = account['username']
            # Redirect to home page
            return render_template("Homee.html")
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
            return render_template('home.html')
        conn.commit()
        conn.close()
    return render_template("Homee.html")

@app.route('/api/logout')
def logout():
    # Remove session data, this will log the user out
    session["name"] = None
    return redirect("/")
   

@app.route('/api/signup')
def signup():
    return render_template("signup.html")

@app.route('/api/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'phonenumber' in request.form: 
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        phonenumber=request.form['phonenumber']
        
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM customer WHERE emailid = %s', (email,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z]+', username):
            msg = 'Name must contain only characters !'
        elif not re.match(r'[0-9]+',phonenumber):
            msg = 'Phone number must contain only numbers'
        elif not username or not password or not email or not phonenumber :
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO customer(customername,emailid,mobilenumber,password) VALUES (%s, %s, %s, %s)', (username,email,phonenumber, password,))
            msg = 'You have successfully registered!'
            conn.commit()
        conn.close()
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        return render_template('signup.html')        
    # Show registration form with message (if any)
    return render_template('signin.html')

@app.route('/api/displaymenu')
def displaymenu():
    return render_template("displaymenu.html")

@app.route('/api/menu')
def display_menu():
    return render_template("displaysmenu.html")

@app.route('/api/all', methods=['GET'])
def api_all():
    cursor.execute("SELECT * from customer")
    keys=['customerid','customername','emailid','mobilenumber','review','reservationid']
    r=cursor.fetchall()
    r=list(r)
                
        
    d=[]
    for i in range(len(r)):
        temp_D=dict()
        for j in range(len(r[i])):
            temp_D[keys[j]]=r[i][j]
        d.append(temp_D)
    
    print(d)
    #li=[jsonify(customerid=r[0],customername=r[1],emailid=r[2],mobilenumber=r[3],review=r[4],reservationid=r[5])]
    
    return jsonify(data=d)

@app.route('/api/booking')
def book():
    return render_template("colorlib-search-12/booking.html")

@app.route('/api/add', methods=['POST'])
def booking():
        conn = mysql.connect()
        c = conn.cursor()
        mail =  request.form['ml']
        date=request.form['dt']
        time=request.form['tm'].lower()
        NoOfGuests=request.form['ng']
        
        #fetch the customer id from the email got as input
        q="select customerid from customer where emailid = %s"
        val=(mail)
        
        c.execute(q,val)
        customerID=list(c.fetchone())[0]   
        
        tablesbooked=conn.cursor()
        query="select dinetableid from reservationtable where rdate =%s and mealtime=%s"
        value = (date,time)
        tablesbooked.execute(query,value)
        
        if tablesbooked.rowcount > 0:
            
            bookedtableID= [list[0] for list in tablesbooked.fetchall()]
            bookedtableID.append(0)
            bookedtablesID = tuple(bookedtableID)  
            dinetableID=-1
            
            c1=conn.cursor()
            query="select dinetableid from dinetable where capacity >= %s and dinetableid not in {} order by capacity".format(bookedtablesID)
            value = (NoOfGuests)
            c1.execute(query,value)
            dinetableID= c1.fetchone()
            
        else:
            c1=conn.cursor()
            query="select dinetableid from dinetable where capacity >= %s order by capacity"
            value = (NoOfGuests)
            c1.execute(query,value)
            dinetableID= c1.fetchone()
        
        reservationId=list()
        if dinetableID:   
            #get new unique reservation ID
            dinetableID = list(dinetableID)
            dinetableID = dinetableID[0]
            r=conn.cursor()
            qu="select ReservationTableid from reservationtable order by reservationTableid desc"
            r.execute(qu)        
            reservationId= list(r.fetchone())[0]
            reservationId=int(reservationId)+1
        else:
            return "Sorry! No tables are available..book for another meal time"
            
        #Insert the reservation
        #reservation beeing noted in the table
        reservation_cursor = conn.cursor()
        query ="insert into reservationtable(reservationTableid,rdate,mealtime,numberofguests,dinetableid,customerid) values(%s,%s,%s,%s,%s,%s)"
        param = (reservationId,date,time,NoOfGuests,dinetableID,customerID)
        reservation_cursor.execute(query,param)
        conn.commit()
        conn.close()
        return render_template("Homee.html")
        
@app.route('/api/cancelbooking')
def cancelbook():
    return render_template("colorlib-search-12/cancelbooking.html")

#cancel booking various options like cancel all or cancel all bookings in a day or cancel in particular
@app.route('/api/cancel', methods=['POST'])
def cancel_booking():
        conn = mysql.connect()
        c = conn.cursor()
        mail =  request.form['ml']
        date=request.form['dt']
        time=request.form['tm']
        q="select customerid from customer where emailid = %s"
        val=(mail)
        #get customer id from mail to delete the entry from the table
        c.execute(q,val)
        customerID=list(c.fetchone())[0]   
        
        #cancel in the reservation table
        cancel_cursor = conn.cursor()
        
        if time == '' and date =='':
            #get reservation id
            q="delete from reservationtable where customerid=%s"
            v=(customerID)
            cancel_cursor.execute(q,v)
            
            
        elif time=='':
            #if this condition is true then date is empty
            q="delete from reservationtable where customerid=%s and rdate=%s"
            v=(customerID,date)
            cancel_cursor.execute(q,v)
            
        elif date=='':
            return "time alone is not suffecient,please enter the date aswell"
        
        # cancellation of reservation when given all fields.
        else:
            q="delete from reservationtable where customerid=%s and rdate=%s and mealtime=%s"
            v=(customerID,date,time)
            cancel_cursor.execute(q,v)
        conn.commit()
        conn.close()
        return render_template("Homee.html")

#view menu


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5006, debug=True)
#cursor.execute("insert into akr.customer(customerid,customername,emailid,mobilenumber,review,reservationid) values(6,'MSD','dhoni@csk.com',7777777777,'super',null)")


"""
cursor.execute("SELECT * from akr.customer")
for i in cursor:
    print(i)
"""
    
conn.commit()
cursor.close()
