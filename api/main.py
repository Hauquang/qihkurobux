from flask import Flask, render_template, request, redirect, session, jsonify
from supabase import create_client, Client

app = Flask(_name_, template_folder='../templates')
app.secret_key = "qihku_bi_mat_123" # Khóa để giữ đăng nhập

# Thông tin kết nối
SUPABASE_URL = "https://awagntcuogwlqoztiwsu.supabase.co"
SUPABASE_KEY = "sbp_publishable_lUdwPeFeo-h6GHCJ46orUg_T8c-hJA6"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def index():
    user = session.get('user')
    balance = 0
    if user:
        # Lấy số dư mới nhất của khách
        res = supabase.table('users').select("balance").eq("username", user).single().execute()
        if res.data: balance = res.data['balance']
    return render_template('index.html', user=user, balance=balance)

# --- ĐĂNG KÝ / ĐĂNG NHẬP ---
@app.route('/register', methods=['POST'])
def register():
    user = request.form.get('username')
    pwd = request.form.get('password')
    try:
        supabase.table('users').insert({"username": user, "password": pwd, "balance": 0}).execute()
        return "Đăng ký xong! Quay lại đăng nhập nhé."
    except: return "Tên này có người dùng rồi bro!"

@app.route('/login', methods=['POST'])
def login():
    user = request.form.get('username')
    pwd = request.form.get('password')
    res = supabase.table('users').select("*").eq("username", user).eq("password", pwd).execute()
    if res.data:
        session['user'] = user
        return redirect('/')
    return "Sai tài khoản hoặc mật khẩu!"

# --- RÚT ROBUX & TRỪ TIỀN ---
@app.route('/rut-robux', methods=['POST'])
def rut_robux():
    if 'user' not in session: return "Phải đăng nhập mới rút được!"
    
    user = session['user']
    amount = int(request.form.get('amount'))
    link = request.form.get('gamepass')
    price = amount * 100 # Ví dụ: 100đ/1 Robux (Bro tự chỉnh giá)

    # 1. Check tiền
    res = supabase.table('users').select("balance").eq("username", user).single().execute()
    if res.data['balance'] < price: return "Không đủ tiền nạp thêm đi bro!"

    # 2. Trừ tiền và Tạo đơn
    new_balance = res.data['balance'] - price
    supabase.table('users').update({"balance": new_balance}).eq("username", user).execute()
    supabase.table('qihku').insert({"username": user, "amount": amount, "gamepass_link": link}).execute()
    
    return f"Đã trừ {price}đ. Chờ duyệt đơn nhé!"

# --- NẠP TIỀN TỰ ĐỘNG (WEBHOOK) ---
@app.route('/callback-card', methods=['POST'])
def card_callback():
    # Gachthefast gửi dữ liệu qua đây
    data = request.form 
    status = data.get('status')
    amount = int(data.get('value')) # Số tiền thẻ
    username = data.get('content') # Nội dung là tên tài khoản khách ghi
    
    if status == '1': # Thẻ đúng
        res = supabase.table('users').select("balance").eq("username", username).single().execute()
        if res.data:
            new_bal = res.data['balance'] + amount
            supabase.table('users').update({"balance": new_bal}).eq("username", username).execute()
    return "OK"

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

