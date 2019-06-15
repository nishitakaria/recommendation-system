from flask import Flask,render_template,url_for,request
#import nltk 
from functools import wraps
import pandas as pd
#from rake_nltk import Rake
import numpy as np
#from sklearn.metrics.pairwise import cosine_similarity
#from sklearn.feature_extraction.text import CountVectorizer
import pickle
#from sklearn.externals import joblib
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL,MySQLdb
import bcrypt
import random
import csv
from ast import literal_eval


k=16
s=5
app = Flask(__name__)


app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'fashionpoint'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/login',methods=["GET","POST"])
def login():
    if request.method == 'POST':
        cid = request.form['cid']
        password = request.form['password']

        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM customer WHERE cid=%s",(cid,))
        user = curl.fetchone()
        print(user['cid'], user['num'], user['password'])
        global k
        k = user['num']
        curl.close()

        if user is not None:
            if password== user["password"]:
                session['cid'] = user['cid']
                session['num'] = user['num']
                return render_template("my.html")
            else:
                return "Error password and customer id not match"
        else:
            return "Error user not found"
    else:
        return render_template("login.html")

@app.route('/logout', methods=["GET", "POST"])
def logout():
    session.clear()
    return render_template("home.html")
    

@app.route('/my')
def my():
    return render_template('my.html')


def jaccard_index(first_set, second_set):
    index = 1.0
    first_set=set(literal_eval(first_set))
    second_set=set(literal_eval(second_set))

    if first_set or second_set:
        index = (float(len(first_set.intersection(second_set))) / len(first_set.union(second_set)))
    return index   


@app.route('/recommend', methods=["GET", "POST"])
def recommend():

   #print(k)
#jaccard
    df=pd.read_csv("recommend1.csv")
    df['jaccard']=''
    i=0
    while (i<500):
        first_set = df.at[k,'product']
        if(i==k):
            i=i+1
        second_set = df.at[i,'product']
        index = jaccard_index(first_set, second_set)
        df.at[i, 'jaccard'] = index
        i=i+1
    df.to_csv("recommend1.csv")
    df1 = pd.read_csv("recommend1.csv")
    df2=pd.read_csv("itemid2.csv")
    df2['pti'] = 0
   
#probability
    i=0
    while(i<99):
     #print(i)
        j=0
        while(j<500):
            if(j==k):
                j=j+1
            first_set=df1.at[j,'product']
            #print(j)
            item = df2.at[i,'id']
           # print(df2.at[i,'pti'])
            #print(df1.at[j, 'jaccard'])
            if str(item) in first_set:
                df2.loc[i,'pti']=df2.at[i,'pti']+df1.at[j, 'jaccard']
            j=j+1
        i=i+1
    df2.to_csv("itemid2.csv")

#finding probability factor and sorting
    df4 = pd.read_csv("itemid3.csv")
    df3 = pd.read_csv("Amazon1.csv")
    df4['pxm']=0
    i=0
    while(i<99):
        df4.loc[i,'pxm']=df2.at[i,'pti']*df3.at[i,'profit']
        i=i+1
   #print(type(df2['pxm']))
    df4.sort_values(by='pxm', ascending = False , inplace=True)
    df4.to_csv("itemid3.csv")
    recommended_clothes = []
    if request.method == 'POST':
        gender = request.form['radio']
        n=0
        i=0
        while(n<99):
            if(i==5):
                break
            print(gender)
            if(gender =='Women'):
                if(df4.at[n,'category2']=='Women' or df4.at[n,'category2']=='Unisex'):
                    global s
                    s=n
                    print(s)
                    recommended_clothes.append(df3.at[s,'title'])
                    #print( recommended_clothes[i])
                    i=i+1
            n=n+1

   #print(a)
    return render_template('result.html', x = recommended_clothes[0] , y = recommended_clothes[1] , z = recommended_clothes[2], a=13064  )


@app.route('/update', methods=["GET", "POST"])
def update(id1):
    print("hi")


        #id1 = request.form("id")
    print(id1)
    df5=pd.read_csv("recommend1.csv")
    old = df5.at[k , 'product']
    old = set(literal_eval(old))
    # old.add()
    df5.at[k, 'product'] = old
    df5.to_csv("recommend1.csv")




# if __name__ == '__main__':

app.secret_key = "^A%DJAJU^JJ123"
app.run(debug=True)


