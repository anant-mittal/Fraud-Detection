print("Content-type: text/html")
print ("") 
from flask import Flask
from flask import flash,redirect,render_template,request,session,abort,url_for
import os
import pymysql
import json
import urllib
import datetime
import tensorflow as tf
from flask_mail import Mail, Message
import mysql.connector
import numpy as np
import keras
from keras.models import load_model
from sklearn.externals import joblib
from twilio.rest import Client
import hashlib

global graph, classifier1, classifier2, classifier3
graph = tf.get_default_graph

conn=pymysql.connect(host="localhost",user="root",password="",db="dell")
c=conn.cursor()

from pymysql import escape_string as thwart
app=Flask(__name__) #Root Path of Website Folder
mail=Mail(app)
@app.route('/')

def index():
    if not session.get('logged_in'):
        return render_template('adminlogin.html')
        
    else:
        return redirect(url_for('success'))

@app.route('/checkuser', methods=['POST'])
def do_admin_login():
    chkuser = request.form['uname']
    c.execute("SELECT `password` FROM `login`WHERE `username`=%s",chkuser)
    psw = c.fetchall()
    print(psw)
    entpsw = request.form['psw']
    textUtf8 = entpsw.encode("utf-8")
    hash = hashlib.md5(textUtf8)
    chkpsw = hash.hexdigest()
    print(chkpsw)
    if chkpsw == psw[0][0]:
        session['logged_in'] = True
        flash('You are now logged in!')
        return redirect(url_for('success'))
    else:
        flash('Please check your credentials again!')
        return redirect(url_for('index'))
       
    
@app.route('/success')
def success():
   return  render_template('userpage.html')

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return index()

@app.route("/cost1",methods=['GET','POST'])
def showtrans1():
    epoch = datetime.datetime.now()
    epoch = epoch.timestamp()
    epoch = int(epoch)
    lapprice=request.form['laptop']
    c.execute("Insert into transaction(time,device_id,merch_id,aatd,trans_amt,is_declined,tnodecperday,isForeignTransaction,isHighRiskCountry) values(%s, %s, %s, %s, %s, %s, %s, %s, %s)", (epoch,4,1644890473,30000,76000,1,5,0,1))
    conn.commit()
    return render_template('paymentpage.html')

@app.route("/cost2",methods=['GET','POST'])
def showtrans2():
    epoch = datetime.datetime.now()
    epoch = epoch.timestamp()
    epoch = int(epoch)
    serverprice=request.form['server']
    c.execute("Insert into transaction(time,device_id,merch_id,aatd,trans_amt,is_declined,tnodecperday,isForeignTransaction,isHighRiskCountry) values(%s, %s, %s, %s, %s, %s, %s, %s, %s)", (epoch,4,1644890473,250,800000,0,5,1,1))
    conn.commit()
    return render_template('paymentpage.html')

@app.route("/cost3",methods=['GET','POST'])
def showtrans3():
    epoch = datetime.datetime.now()
    epoch = epoch.timestamp()
    epoch = int(epoch)
    mouseprice=request.form['mouse']
    c.execute("Insert into transaction(time,device_id,merch_id,aatd,trans_amt,is_declined,tnodecperday,isForeignTransaction,isHighRiskCountry) values(%s, %s, %s, %s, %s, %s, %s, %s, %s)", (epoch,2,1644890473,250,6000,0,5,1,1))
    conn.commit()
    return render_template('paymentpage.html')

@app.route("/callme")
def callme():
    c.execute("Select * from transaction order by t_id desc limit 5")
    data=c.fetchall()
    return render_template("nextpage.html", data = data)

@app.route("/saveval", methods=['GET','POST'])
def saveval():
            #Prediction Code
            keras.backend.clear_session()
            c.execute("SELECT merch_id,trans_amt,is_declined,tnodecperday,aatd FROM transaction ORDER BY t_id DESC LIMIT 1") #Model
            data1 = c.fetchall()

            c.execute("SELECT t_id FROM transaction ORDER BY t_id DESC LIMIT 1")
            trans_id = c.fetchall()

            sc1 = joblib.load('scaler1.pkl')
            classifier1 = load_model('model1.h5')
            data1 = sc1.transform(data1)
            fit1 = classifier1.predict(data1, verbose=1)
            fit1 = int((fit1>0.5))

            c.execute("SELECT time,trans_amt,device_id FROM transaction ORDER BY t_id DESC LIMIT 1")
            data2 = c.fetchall()

            sc2 = joblib.load('scaler2.pkl')
            classifier2 = load_model('model2.h5')
            data2 = sc2.transform(data2)
            fit2 = classifier2.predict(data2, verbose=1)
            fit2 = int((fit2>0.5))

            c.execute("SELECT trans_amt, isForeignTransaction, isHighRiskCountry FROM transaction ORDER BY t_id DESC LIMIT 1")
            data3 = c.fetchall()
            sc3 = joblib.load('scaler3.pkl')
            classifier3 = load_model('model3.h5')
            data3 = sc3.transform(data3)
            fit3 = classifier3.predict(data3, verbose=1)
            fit3 = int((fit3>0.5))

            op = (fit1+fit2+fit3)
            if(op==0):
            	out = 'Not Fraud'
            elif(op==1):
                out = 'Less Risky'
                app.config['MAIL_SERVER']='smtp.gmail.com'
                app.config['MAIL_PORT'] = 465
                app.config['MAIL_USERNAME'] = 'akshat.rhcp16@gmail.com'
                app.config['MAIL_PASSWORD'] = 'dell@1234'
                app.config['MAIL_USE_TLS'] = False
                app.config['MAIL_USE_SSL'] = True
                mail = Mail(app)
                msg = Message('Fraud Detected', sender = 'akshat.rhcp16@gmail.com', recipients = ['ankit.dhall97@gmail.com'])
                msg.body = "Fraudulent transaction has been detected on your Dell account."
                mail.send(msg)
            elif(op==2):
            	out = 'Moderately Risky'
            	account_sid = 'ACaac489e4dbb591556a9f30fd8db3456f'
            	auth_token  = '1422fee3f2892669dfe59656031e8370'
            	client = Client(account_sid, auth_token)
            	message = client.messages.create(
                              body='Fraudulent transaction has been detected on your Dell account.',
                              from_='+18319206231',	
                              to='+917073572015'
                          )

            elif(op==3):
                out = 'Highly Risky'
                account_sid = 'ACaac489e4dbb591556a9f30fd8db3456f'
                auth_token  = '1422fee3f2892669dfe59656031e8370'
                client = Client(account_sid, auth_token)
                call = client.calls.create(
                        url='http://demo.twilio.com/docs/voice.xml',
                        to='+917073572015',
                        from_='+18319206231'
                    )
                print(call.sid)    			 			 
            c.execute("UPDATE `transaction` SET `isFraud1` = %s, `isFraud2` = %s, `isFraud3` = %s, `result` = %s WHERE `t_id` = %s" ,(fit1, fit2, fit3, out, trans_id[0][0]))
            conn.commit()
            c.execute("Select * from transaction order by t_id desc limit 5")
            data=c.fetchall()
            return render_template('nextpage.html',data=data)

if __name__=="__main__":
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)

