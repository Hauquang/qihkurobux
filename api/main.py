from flask import Flask, render_template, request, redirect, session
from supabase import create_client, Client

app = Flask(_name_, template_folder='../templates')
app.secret_key = "qihku_secure_2026"

# Thông tin kết nối Supabase
SUPABASE_URL = "https://awagntcuogwlqoztiwsu.supabase.co"
SUPABASE_KEY = "sbp_publishable_lUdwPeFeo-h6GHCJ46orUg_T8c-hJA6"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def index():
    user_info = None
    history = []
    if 'user' in session:
        # Lấy thông tin số dư người dùng
        res = supabase.table('users').select("*").eq("username", session['user']).single().execute()
        if res.data: 
            user_info = res.data
        
        # Lấy lịch sử đơn hàng từ bảng 'order'
        hist_res = supabase.table('order').select("*").eq("username", session['user']).order('created_at', desc=True).execute()
        if hist_res.data: 
            history = hist_res.data
            
    return render_template('index.html', user=user_info, history=history)

# --- XỬ LÝ MUA ROBUX (Giá 150đ/1RB) ---
@app.route('/buy-robux', methods=['POST'])
def buy_robux():
    if 'user' not in session: 
        return redirect('/')
    
    # Lấy dữ liệu từ form (Bắt buộc khớp tên cột trên Supabase)
    ingame = request.form.get('ingame_game') 
    amount = int(request.form.get('amount'))
    link = request.form.get('gamepass_link')
    price = amount * 150 

    # Kiểm tra số dư khách
    user_res = supabase.table('users').select("balance").eq("username", session['user']).single().execute()
    
    if user_res.data and user_res.data['balance'] >= price:
        # 1. Trừ tiền khách
        new_bal = user_res.data['balance'] - price
        supabase.table('users').update({"balance": new_bal}).eq("username", session['user']).execute()
        
        # 2. Tạo đơn vào bảng 'order'
        supabase.table('order').insert({
            "username": session['user'],
            "ingame_game": ingame,
            "amount": amount,
            "gamepass_link": link,
            "status": "Đang xử lý"
        }).execute()
        
        return "<h3>Thành công! Đã tạo đơn rút Robux.</h3><a href='/'>Quay lại</a>"
    
    return "<h3>Số dư của bạn không đủ!</h3><a href='/'>Quay lại</a>"

# --- HỆ THỐNG TÀI KHOẢN ---
@app.route('/register', methods=['POST'])
def register():
    u = request.form.get('username')
    p = request.form.get('password')
    try:
        supabase.table('users').insert({"username": u, "password": p, "balance": 0}).execute()
        return "<h3>Đăng ký thành công!</h3><a href='/'>Đăng nhập ngay</a>"
    except:
        return "<h3>Tên tài khoản đã tồn tại!</h3><a href='/'>Thử lại</a>"

@app.route('/login', methods=['POST'])
def login():
    u = request.form.get('username')
    p = request.form.get('password')
    res = supabase.table('users').select("*").eq("username", u).eq("password", p).execute()
    if res.data:
        session['user'] = u
        return redirect('/')
    return "<h3>Sai tài khoản hoặc mật khẩu!</h3><a href='/'>Quay lại</a>"

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

# Chạy app (Sửa lỗi _name_ bro gặp phải)
if _name_ == '_main_':
    app.run(debug=True)
