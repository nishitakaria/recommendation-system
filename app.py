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
    df=pd.read_csv("recommend.csv")
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
    df.to_csv("recommend.csv")
    df1 = pd.read_csv("recommend.csv")
    df2=pd.read_csv("itemid2.csv")
    df2['pti'] = 0
   
#probability
    i=0
    while(i<250):
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
    df2.to_csv("itemid2_copy.csv")
    df6 = pd.read_csv("itemid2_copy")
    df6.sort_values(by='pti', ascending = False , inplace=True)
    df6.reset_index(drop=True, inplace=True)
    df6.to_csv("itemid2_copy.csv")
    df3 = pd.read_csv("Amazon2.csv")

#finding probability factor and sorting
    df4 = pd.read_csv("itemid3.csv")
    

#making set for titles
    global v
    v= set()
    x = literal_eval(df1.at[k,'product'])
    for item in x:
        print(item)
        i=0
        while(i<250):
            if int(item) == df3.at[i,'id']:
                v.add(df3.at[i,'title'])
                print(df3.at[i,'title'])
            i=i+1
    print(v)

    df4['pxm']=0
    i=0
    while(i<250):
        df4.loc[i,'pxm']=df2.at[i,'pti']*df3.at[i,'profit']
        i=i+1
   #print(type(df2['pxm']))
    df4.sort_values(by='pxm', ascending = False , inplace=True)
    df4.reset_index(drop=True, inplace=True)
    df4.to_csv("itemid3.csv")
    global recommended_images
    recommended_images = []
    global recommended_title 
    recommended_title = []
    global recommended_link 
    recommended_link = []
    global recommended_id 
    recommended_id = []
    if request.method == 'POST':
        gender = request.form['radio']

        #product without profitability
        global z
        z = set()
        t=0
        j=0
        while(t<250):
            i=0
            while(i<250):
                if(j==3):
                    break
                if  df6.at[t,'id'] == df3.at[i,'id']:
                    print(df6.at[t,'id'])
                    print(df3.at[i,'id'])
                    print(gender)
                    if(gender == 'Women'):
                        if (df6.at[t,'category2'] == 'Women' or df6.at[t,'category2'] == 'Unisex'):
                            z.add(df3.at[i,'title'])
                            j=j+1
                            print(df3.at[i,'title'])
                    if(gender == 'Men'):
                        print(df3.at[i,'category2'])
                        if (df3.at[i,'category2'] == 'Men' or df3.at[i,'category2'] == 'Unisex'):
                            print("hi")
                            z.add(df3.at[i,'title'])
                            j=j+1
                i=i+1
            t=t+1
            
        print("product w/o profit")
        print(z)

        #category wise 
        n=0
        i=0
        while(n<250):
            if(i==5):
                break
            print(gender)
            df4.reset_index(drop=True)
            df4.to_csv("itemid3.csv")

            if(gender =='Women'):
                if(df4.at[n,'category2']=='Women' or df4.at[n,'category2']=='Unisex'):
                    s = df4.at[n , 'id']
                    print(s)
                    f=0
                    while(f<250):
                        if(df3.at[f, 'id'] == s):
                            print(f)
                            recommended_images.append(df3.at[f,'imUrl'])
                            recommended_title.append(df3.at[f,'title'])
                            recommended_link.append(df3.at[f, 'link'])
                            recommended_id.append(s)

                        f=f+1
                    i=i+1

            if(gender =='Men'):
                if(df4.at[n,'category2']=='Men' or df4.at[n,'category2']=='Unisex'):
                    s = df4.at[n , 'id']
                    print(s)
                    f=0
                    while(f<250):
                        if(df3.at[f, 'id'] == s):
                            print(f)
                            recommended_images.append(df3.at[f,'imUrl'])
                            recommended_title.append(df3.at[f,'title'])
                            recommended_link.append(df3.at[f, 'link'])
                            recommended_id.append(s)
                        f=f+1
                    i=i+1
            n=n+1

   #print(a)
    return render_template('result.html', x = recommended_images[0] , y = recommended_images[1] , z = recommended_images[2], p = recommended_title[0], q = recommended_title[1], r = recommended_title[2], a = recommended_link[0], b = recommended_link[1], c = recommended_link[2], l = recommended_id[0], m = recommended_id[1], n = recommended_id[2], product = v, product1 = z)


@app.route('/update', methods=["GET", "POST"])
def update():
    print("hi")
    if request.method == 'POST':
        id1 = request.form['submit']
        print(id1)
        df5=pd.read_csv("recommend.csv")
        old = df5.at[k , 'product']
        old = set(literal_eval(old))
        old.add(str(id1))
        df5.at[k, 'product'] = old
        df5.to_csv("recommend.csv")

    return render_template('result.html' , x = recommended_images[0] , y = recommended_images[1] , z = recommended_images[2], p = recommended_title[0], q = recommended_title[1], r = recommended_title[2], a = recommended_link[0], b = recommended_link[1], c = recommended_link[2], l = recommended_id[0], m = recommended_id[1], n = recommended_id[2], product = v)



# if __name__ == '__main__':

app.secret_key = "^A%DJAJU^JJ123"
app.run(debug=True)


