#!/bin/python
# -*- coding=utf-8 -*-
from flask import Flask,jsonify,request
from werkzeug import secure_filename
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from urine import Urine
import os
import cv2
import time
import json


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:vultr@45.77.3.10:3306/urine'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
CORS(app)
UPLOAD_FOLDER = './upload'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STATIC_URL'] = ''
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer,nullable=False,primary_key=True, autoincrement=True)
    phone = db.Column(db.String(255),nullable=True)
    age = db.Column(db.Integer,nullable=False)
    hypertension = db.relationship('Hypertension',backref=db.backref('users',lazy='dynamic'))
    diabete = db.relationship('Diabete',backref=db.backref('users',lazy='dynamic'))
    medicare =  db.relationship('Medicare',backref=db.backref('users',lazy='dynamic'))
    unionId = db.Column(db.String(1024))
    registerTime = db.Column(db.DateTime)
    nickname = db.Column(db.String(255))
    gender = db.Column(db.Integer)



    def __init__(self, phone,age,hypertension,diabete,medicare,unionId,registerTime,nickname,gender):
        self.nickname = nickname
        self.phone = phone
        self.age = age
        self.hypertension = hypertension
        self.diabete = diabete
        self.medicare = medicare
        self.unionId = unionId
        self.registerTime = registerTime
        self.nickname = nickname
        self.gender = gender

class Hypertension(db.Model):
    id = db.Column(db.Integer,nullable=False,primary_key=True, autoincrement=True)
    value = db.Column(db.String(255),nullable=False)
    name = db.Column(db.String(255),nullable=False)
    def __init__(self, value, name):
        self.value = value
        self.name = name

class Diabete(db.Model):
    id = db.Column(db.Integer,nullable=False,primary_key=True, autoincrement=True)
    value = db.Column(db.String(255),nullable=False)
    name = db.Column(db.String(255),nullable=False)

    def __init__(self, value, name):
        self.value = value
        self.name = name        

class Hospital(db.Model):
    id = db.Column(db.Integer,nullable=False,primary_key=True, autoincrement=True)
    name = db.Column(db.Integer,nullable=False)
    location = db.Column(db.String(255),nullable=False)
    longitude = db.Column(db.Float,nullable=False)
    latitude = db.Column(db.Float,nullable=False)
    province = db.Column(db.String(255))

class Medicare(db.Model):
    id = db.Column(db.Integer,nullable=False,primary_key=True, autoincrement=True)
    value = db.Column(db.String(255),nullable=False)
    name = db.Column(db.String(255),nullable=False)
    def __init__(self, value, name):
        self.value = value
        self.name = name  

    # def __repr__(self):
    #     return '<User%r>' % self.id

class Record(db.Model):

    id = db.Column(db.Integer,nullable=False,primary_key=True, autoincrement=True)
    image = db.Column(db.String(255),nullable=False)
    date = db.Column(db.DateTime)
    result = db.Column(db.String(4096))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User',backref=db.backref('records',lazy='dynamic'))


    def __init__(self,image,date,result,user):
        self.image = image
        self.date = date
        self.result = result
        self.user = user


    def __repr__(self):
        return '<User%r>' % self.id



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/urine/init',methods=['GET','POST'])
def db_init():
    db.create_all()
    return jsonify({'code':200})
@app.route('/urine/drop',methods=['GET','POST'])
def db_drop():
    db.drop_all()

@app.route('/urine/record/<id>',methods=['GET'])
def record(id):
    id = int(id)
    record = Record.query.filter_by(id=id).first()
    if not record:
        return jsonify({'code':'201111','msg':'记录不存在'})
    else:
        obj = {}
        obj['id'] = record.id
        obj['date'] = record.date
        obj['result'] = record.result
        obj['image'] = record.image

        return jsonify(obj)




@app.route('/urine/login',methods=['POST'])
def login():
    uid = request.values.get('uid')

    user = User.query.filter_by(id=uid).first()
    if not user:
        return json.dumps({'code':10001,'msg':'用户不存在'})

    return json.dumps({'id':user.id,'nickname':user.nickname})

@app.route('/urine/analyse',methods=['POST'])
def analyse():
    ifile = request.files['image']
    uid = request.values.get('id')
    # uid = 1
    user = User.query.filter_by(id=uid).first()
    if not user:
        return jsonify({'code':10002,'msg':'用户不存在'})

    if ifile and allowed_file(ifile.filename):
        filename = secure_filename(ifile.filename)
        output_path = os.path.join(app.config['UPLOAD_FOLDER'],uid,filename)
        ifile.save(output_path)
        image = cv2.imread(output_path)
        u = Urine(image)
        result = u.run()
        date = time.strftime("%Y-%m-%d", time.localtime())
        record = Record(output_path,date,json.dumps(result),user)
        db.session.add(record)
        db.session.commit()

        obj = {}
        obj['id'] = record.id
        obj['date'] = record.date
        obj['result'] = record.result
        obj['image'] = record.image
        return jsonify(obj)
    else:
        return jsonify({'code':10001,'msg':'文件格式不支持'})


@app.route('/urine/records',methods=['GET'])
def records():

    uid = request.values.get('id')
    user = User.query.filter_by(id=uid).first()
    if not user:
        return jsonify({'code':10002,'msg':'用户不存在'})
    records = user.records.all()
    result = []
    for record in records:
        obj = {}
        obj['id'] = record.id
        obj['date'] = record.date
        obj['result'] = record.result
        obj['image'] = record.image
        result.append(obj)
    return jsonify({'records':result})

    


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=9000,debug=True)