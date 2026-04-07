from flask import Flask, render_template, request, redirect, session, url_for
from supabase import create_client, Client

app = Flask(_name_, template_folder='../templates')
app.secret_key = "qihku_bi_mat_2026" # Khóa để giữ phiên đăng nhập

# Thông tin kết nối Supabase
SUPABASE_URL = "https://awagntcuogwlqoztiwsu.supabase.co"
SUPABASE_KEY = "sbp_publishable_lUdwPeFeo-h6GHCJ46orUg_T8c-hJA6"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def index():
    user_info = None
    if 'user' in session:
        # Lấy số dư và thông tin user từ bảng 'users'
        res = supabase.table('users').select("*").eq("username", session['user']).single().execute()
        if res.data: 
            user_info = res.data
    return render_template('index.html', user=user_info)

# --- HỆ THỐNG TÀI KHOẢN ---
@app.route('/register', methods=['POST'])
def register():
    user = request.form.get('username')
    pwd = request.form.get('password')
    try:
        # Mặc định số dư khi đăng ký là 0đ
        supabase.table('users').insert({"username": user, "password": pwd, "balance": 0}).execute()
        return "<h3>Đăng ký thành công!</h3><a href='/'>Quay lại đăng nhập</a>"
    except:
        return "<h3>Tên tài khoản đã tồn tại!</h3><a href='/'>Thử lại</a>"

@app.route('/login', methods=['POST'])
def login():
    user = request.form.get('username')
    pwd = request.form.get('password')
    res = supabase.table('users').select("*").eq("username", user).eq("password", pwd).execute()
    if res.data:
        session['user'] = user
        return redirect('/')
    return "<h3>Sai tài khoản hoặc mật khẩu!</h3><a href='/'>Quay lại</a>"

# --- RÚT ROBUX (GIÁ 150đ/1RB) ---
@app.route('/rut-robux', methods=['POST'])
def rut_robux():
    if 'user' not in session: return redirect('/')
    
    amount = int(request.form.get('amount'))
    link = request.form.get('gamepass')
    price = amount * 150 # Giá 150đ theo yêu cầu của bro

    # Kiểm tra số dư khách
    user_res = supabase.table('users').select("balance").eq("username", session['user']).single().execute()
    if user_res.data and user_res.data['balance'] >= price:
        # 1. Trừ tiền khách
        new_balance = user_res.data['balance'] - price
        supabase.table('users').update({"balance": new_balance}).eq("username", session['user']).execute()
        
        # 2. Tạo đơn vào bảng 'order'
        supabase.table('order').insert({
            "username": session['user'], 
            "amount": amount, 
            "gamepass_link": link
        }).execute()
        return f"<h3>Thành công! Đã trừ {price}đ.</h3><a href='/'>Quay lại</a>"
    return "<h3>Số dư không đủ!</h3><a href='/'>Quay lại</a>"

# --- VƯỢT LINK NHẬN 0.5 ROBUX (75đ) ---
@app.route('/complete-link')
def complete_link():
    if 'user' not in session: return "Vui lòng đăng nhập!"
    
    # 0.5 Robux = 75đ (vì 1 Robux = 150đ)
    bonus = 75 
    user = session['user']

    res = supabase.table('users').select("balance").eq("username", user).single().execute()
    if res.data:
        new_bal = res.data['balance'] + bonus
        supabase.table('users').update({"balance": new_bal}).eq("username", user).execute()
        return f"<h3>Bạn nhận được 0.5 Robux ({bonus}đ).</h3><a href='/'>Về trang chủ</a>"
    return "Lỗi!"

# --- NẠP THẺ TỰ ĐỘNG (Gachthefast) ---
@app.route('/callback-card', methods=['POST'])
def card_callback():
    data = request.form 
    status = data.get('status')
    amount = int(data.get('value')) # Mệnh giá thẻ
    username = data.get('content') # Tên tài khoản khách nhập ở nội dung nạp
    
    if status == '1': # Thẻ đúng
        user_res = supabase.table('users').select("balance").eq("username", username).single().execute()
        if user_res.data:
            new_bal = user_res.data['balance'] + amount
            supabase.table('users').update({"balance": new_bal}).eq("username", username).execute()
    return "OK"

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')
