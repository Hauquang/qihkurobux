from flask import Flask, render_template, request, redirect, session
from supabase import create_client, Client

app = Flask(_name_, template_folder='../templates')
app.secret_key = "qihku_secret_key_123" 

# Kết nối Supabase
SUPABASE_URL = "https://awagntcuogwlqoztiwsu.supabase.co"
SUPABASE_KEY = "sbp_publishable_lUdwPeFeo-h6GHCJ46orUg_T8c-hJA6"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def index():
    user_info = None
    if 'user' in session:
        # Lấy số dư và tên khách từ bảng users
        res = supabase.table('users').select("*").eq("username", session['user']).single().execute()
        if res.data: user_info = res.data
    return render_template('index.html', user=user_info)

# Logic Đăng ký & Đăng nhập
@app.route('/login', methods=['POST'])
def login():
    u, p = request.form.get('username'), request.form.get('password')
    res = supabase.table('users').select("*").eq("username", u).eq("password", p).execute()
    if res.data:
        session['user'] = u
        return redirect('/')
    return "Sai thông tin rồi bro!"

# Logic Rút Robux và Trừ tiền
@app.route('/rut-robux', methods=['POST'])
def rut_robux():
    if 'user' not in session: return redirect('/')
    amount = int(request.form.get('amount'))
    price = amount * 100 # Giá 100đ/1 Robux
    
    # Check tiền trong bảng users
    res = supabase.table('users').select("balance").eq("username", session['user']).single().execute()
    if res.data and res.data['balance'] >= price:
        # 1. Trừ tiền
        new_bal = res.data['balance'] - price
        supabase.table('users').update({"balance": new_bal}).eq("username", session['user']).execute()
        # 2. Lưu đơn vào bảng order
        supabase.table('order').insert({
            "username": session['user'], 
            "amount": amount, 
            "gamepass_link": request.form.get('gamepass')
        }).execute()
        return "Rút thành công, chờ shop duyệt đơn nhé!"
    return "Không đủ tiền rồi!"

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')
