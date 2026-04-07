from flask import Flask, render_template, request
from supabase import create_client, Client
import os

app = Flask(_name_, template_folder='../templates')

# Điền thông tin từ mục Settings -> API trên Supabase của bạn
SUPABASE_URL = "https://awagntcuogwlqoztiwsu.supabase.co" 
SUPABASE_KEY = "sbp_publishable_lUdwPeFeo-h6GHCJ46orUg_T8c-hJA6" # Dùng Key Anon

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/rut-robux', methods=['POST'])
def rut_robux():
    try:
        # Lấy dữ liệu khách nhập từ form
        username = request.form.get('username')
        amount = request.form.get('amount')
        gamepass_link = request.form.get('gamepass')
        
        # Gửi dữ liệu vào bảng 'qihku'
        data = {
            "username": username,
            "amount": int(amount) if amount else 0,
            "gamepass_link": gamepass_link
        }
        supabase.table('qihku').insert(data).execute()
        
        return "<h3>Gửi đơn thành công! Vui lòng chờ qihku duyệt nhé.</h3><a href='/'>Quay lại</a>"
    except Exception as e:
        return f"Lỗi gửi đơn: {str(e)}"

@app.route('/qihku-admin')
def admin():
    try:
        # Lấy danh sách đơn hàng để admin xem
        res = supabase.table('qihku').select("*").order('created_at', desc=True).execute()
        return render_template('admin.html', orders=res.data)
    except Exception as e:
        return f"Lỗi Admin: {str(e)}"

if _name_ == '_main_':
    app.run(debug=True)
