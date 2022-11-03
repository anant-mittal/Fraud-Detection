import mysql.connector
import numpy as np
import keras
from keras.models import load_model
from sklearn.externals import joblib
 

con = mysql.connector.connect(user='root', database='dell',host='localhost',password='')
con.autocommit = True
cur = con.cursor()
cur.execute("SELECT merch_id,trans_amt,is_declined,tnodecperday,aatd FROM transaction ORDER BY t_id DESC LIMIT 1")
data1 = cur.fetchall()

cur.execute("SELECT t_id FROM transaction ORDER BY t_id DESC LIMIT 1")
trans_id = cur.fetchall()

sc1 = joblib.load('scaler1.pkl')
classifier1 = load_model('model1.h5')
data1 = sc1.transform(data1)
fit1 = classifier1.predict(data1, verbose=1)
fit1 = int((fit1>0.5))

cur.execute("SELECT time,trans_amt,device_id FROM transaction ORDER BY t_id DESC LIMIT 1")
data2 = cur.fetchall()

sc2 = joblib.load('scaler2.pkl')
classifier2 = load_model('model2.h5')
data2 = sc2.transform(data2)
fit2 = classifier2.predict(data2, verbose=1)
fit2 = int((fit2>0.5))

cur.execute("SELECT trans_amt, isForeignTransaction, isHighRiskCountry FROM transaction ORDER BY t_id DESC LIMIT 1")
data3 = cur.fetchall()
sc3 = joblib.load('scaler3.pkl')
classifier3 = load_model('model3.h5')
data3 = sc3.transform(data3)
fit3 = classifier3.predict(data3, verbose=1)
fit3 = int((fit3>0.5))

result = (fit1+fit2+fit3)/3 * 100
cur.execute("UPDATE `transaction` SET `isFraud1` = %d, `isFraud2` = %d, `isFraud3` = %d, `result` = %f WHERE `t_id` = %d" % (fit1, fit2, fit3, result, trans_id[0][0]))
