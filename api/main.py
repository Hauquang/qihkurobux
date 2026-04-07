from flask import Flask, render_template, request, redirect
from supabase import create_client, Client
import os

app = Flask(_name_, template_folder='../templates')

# === BƯỚC QUAN TRỌNG: THAY THÔNG TIN CỦA BẠN VÀO ĐÂY ===
# Lấy từ mục Settings -> API trên Supabase
SUPABASE_URL = "https://awagntcuogwlqoztiwsu.supabase.com" 
SUPABASE_KEY = "sb_publishable_lUdWPefEo-h6GHCJ46orUg_T8c-hJA6"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/rut-robux', methods=['POST'])
def rut_robux():
    try:
        # Lấy dữ liệu từ form khách nhập
        username = request.form.get('username')
        amount = request.form.get('amount')
        gamepass_link = request.form.get('gamepass')
        
        # Đẩy dữ liệu vào bảng 'orders' trên Supabase
        data = {
            "username": username,
            "amount": int(amount),
            "gamepass_link": gamepass_link
        }
        supabase.table('orders').insert(data).execute()
        
        return "<h3>Gửi đơn thành công! Vui lòng chờ qihku duyệt đơn nhé.</h3><a href='/'>Quay lại</a>"
    except Exception as e:
        return f"Có lỗi xảy ra: {str(e)}"

@app.route('/qihku-admin')
def admin():
    try:
        # Lấy danh sách đơn hàng để bạn quản lý
        response = supabase.table('orders').select("*").order('created_at', desc=True).execute()
        return render_template('admin.html', orders=response.data)
    except Exception as e:
        return f"Lỗi truy cập Admin: {str(e)}"

# Để chạy local khi test
if _name_ == '_main_':
    app.run(debug=True)
