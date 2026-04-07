from flask import Flask, render_template, request, redirect, url_for
import pymongo

app = Flask(_name_, template_folder='../templates')

# Dán link MongoDB Atlas của bạn vào đây
client = pymongo.MongoClient("MONGODB_URI_CUA_BAN")
db = client.qihkudb
orders = db.orders

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/rut-robux', methods=['POST'])
def rut_robux():
    name = request.form.get('username')
    amount = request.form.get('amount')
    link = request.form.get('gamepass')
    orders.insert_one({"user": name, "amount": amount, "link": link, "status": "Pending"})
    return "Đơn hàng đã được gửi! Chờ qihku duyệt nhé."

@app.route('/qihku-admin')
def admin():
    all_orders = list(orders.find())
    return render_template('admin.html', orders=all_orders)