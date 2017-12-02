# -*- coding:utf-8 -*-

from flask import Flask,Response
from flask import request
import os,json,sys
from spider import Spider


app=Flask(__name__)
data_path = os.path.abspath(os.curdir)+"/data";

@app.route('/api/book/upgrade',methods=['POST'])
def updateBooks():
    book_id = request.form['book_id'];
    book_name = request.form['book_name'];
    sp = Spider();
    sp.run(book_id,book_name);
    return Response("success", mimetype='application/json;charset=utf-8')

@app.route('/api/books',methods=['GET','POST'])
def getBooks():
    with open(data_path+"/books.json") as f:
        data = f.read()
    return Response(data, mimetype='application/json;charset=utf-8')

@app.route('/api/book/<book_id>',methods=['GET','POST'])
def getBook(book_id):
    with open(data_path+"/"+book_id+"/book.json") as f:
        data = f.read()
    r=Response(data, mimetype='application/json;charset=utf-8')
    return Response(data, mimetype='application/json;charset=utf-8')


@app.route('/api/book/<book_id>/chapters',methods=['GET','POST'])
def getChapters(book_id):
    with open(data_path+"/"+book_id+"/chapters.json") as f:
        data = f.read()
    r=Response(data, mimetype='application/json;charset=utf-8')
    return Response(data, mimetype='application/json;charset=utf-8')


@app.route('/api/book/<book_id>/chapter/<chapter_id>',methods=['GET','POST'])
def getChapterInfo(book_id,chapter_id):
    with open(data_path+"/"+book_id+"/"+chapter_id+"/chapter_info.json") as f:
        data = f.read()
    return Response(data, mimetype='application/json;charset=utf-8')



@app.route('/signin', methods=['GET'])
def signin_form():
    return '''<form action="/signin" method="post">
              <p><input name="username"></p>
              <p><input name="password" type="password"></p>
              <p><button type="submit">Sign In</button></p>
              </form>'''

@app.route('/signin', methods=['POST'])
def signin():
    if request.form['username'] == 'admin' and request.form['password'] == 'password':
        return  '<h3>Hello ,admin!</h3>'
    return '<h3>Bad username or password.</h3>'

if __name__ == '__main__':
    app.run()
