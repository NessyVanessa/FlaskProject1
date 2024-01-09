from flask import Flask, render_template, redirect, request, url_for, session, make_response
import mysql.connector
import sqlite3
from flask import flash
from flask import send_file
import io
import os

app = Flask(__name__)
# Konfigurasi basis data
db_config = {
 "host": "localhost",
 "user": "root",
 "password": "",
 "database": "project",
}
# Inisialisasi koneksi dan kursor
app.secret_key = 'secretkey'
connection = mysql.connector.connect(**db_config)
cursor = connection.cursor()
# Daftar pilihan untuk elemen <select>

@app.route("/")
def index():

    if 'is_logged_in' in session:
        cursor.execute("SELECT * FROM delivery")
        records = cursor.fetchall()
        return render_template('delivery.html', data=records)
    else:
        return redirect(url_for('login'))

@app.route("/login", methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute('SELECT * FROM account WHERE username = %s AND password = %s', (username, password))

        result = cursor.fetchone()

        if result:
            session['is_logged_in'] = True
            session['username']=result[1]

            return redirect(url_for('index'))
        
        else:
            return render_template('login.html')
        
    else:
        return render_template('login.html')
    
@app.route("/logout")
def logout():
    session.pop('is_logged_in', None)
    session.pop('username', None)

    return redirect(url_for('login'))

@app.route("/register", methods = ['GET', 'POST'], endpoint = 'register')
def register(id=None):
        
        if request.method == 'GET':
             return render_template('register.html')
        else:
            username = request.form['username']
            password = request.form['password']
            if id is None:
                    cursor.execute("INSERT INTO account (username,password) VALUES (%s,%s)",(username,password))
                    connection.commit()
                    flash('account successfully created')
            else:
                    
                    flash('account already registered') 

        return render_template('register.html')
        

@app.route("/delivery", methods=['GET', 'POST'])
@app.route("/update_delivery/<int:id>", methods=['GET', 'POST'])
def insert_or_update_delivery(id=None):
    if 'is_logged_in' in session:
        if request.method == 'POST':
            nama = request.form['driver']
            kategori = request.form['category']
            no_plat = request.form['license']
            tujuan = request.form['destination']
            jarak = request.form['distance']
            waktu_tempuh = int(jarak)/60

            if id is None:
                cursor.execute("INSERT INTO delivery (Driver_name, Category, License_plate, Destination, Distance, Est_arrival) VALUES (%s, %s, %s, %s,%s,%s)", (nama, kategori, no_plat,tujuan,jarak,waktu_tempuh))
                connection.commit()
            else:
                cursor.execute("UPDATE `delivery SET Driver_name = %s, Category = %s, License_plate = %s , Destination = %s , Distance = %s, Est_arrival = %s, WHERE id = %s", (nama, kategori, no_plat,tujuan,jarak,waktu_tempuh,id))
                connection.commit()
            return redirect(url_for('index'))
            
        if id is not None:
            cursor.execute("SELECT * FROM delivery WHERE id = %s", (id,))
            data = cursor.fetchone()
            return render_template('form.html',  default_value=data[6], data=data,url=url_for('insert_or_update_delivery', id=id))
        return render_template('form.html',  data=None)
    else:
        return redirect(url_for('login'))


@app.route("/delete_delivery/<int:id>")
def delete_delivery(id):
    if 'is_logged_in' in session:    
        cursor.execute("DELETE FROM delivery WHERE id = %s", (id,))
        connection.commit()
        return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))
