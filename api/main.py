from flask import Flask, render_template, request, redirect, session, url_for
from supabase import create_client, Client

app = Flask(_name_, template_folder='../templates')
app.secret_key = "qihku_bi_mat_123" 

# Kết nối Supabase
SUPABASE_URL = "https://awagntcuogwlqoztiwsu.supabase.co"
SUPABASE_KEY = "sbp_publishable_lUdwPeFeo-h6GHCJ46orUg_T8c-hJA6"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def index():
    user_info = None
    if 'user' in session:
        # Lấy thông tin user và số dư
        res = supabase.table('users').select("*").eq("username", session['user']).single().execute()
        if res.data: user_info = res.data
    return render_template('index.html', user=user_info)

@app.route('/register', methods=['POST'])
def register():
    user = request.form.get('username')
    pwd = request.form.get('password')
    try:
        supabase.table('users').insert({"username": user, "password": pwd, "balance": 0}).execute()
        return "<h3>Đăng ký xong!</h3><a href='/'>Quay lại đăng nhập</a>"
    except: return "<h3>Tên này đã có người dùng!</h3><a href='/'>Thử lại</a>"

@app.route('/login', methods=['POST'])
def login():
    user = request.form.get('username')
    pwd = request.form.get('password')
    res = supabase.table('users').select("*").eq("username", user).eq("password", pwd).execute()
    if res.data:
        session['user'] = user
        return redirect('/')
    return "<h3>Sai tài khoản hoặc mật khẩu!</h3><a href='/'>Quay lại</a>"

@app.route('/rut-robux', methods=['POST'])
def rut_robux():
    if 'user' not in session: return redirect('/')
    
    amount = int(request.form.get('amount'))
    link = request.form.get('gamepass')
    price = amount * 100 # Ví dụ 100đ/1 Robux. Bạn có thể tự chỉnh giá này.

    # Kiểm tra số dư khách
    user_res = supabase.table('users').select("balance").eq("username", session['user']).single().execute()
    if user_res.data and user_res.data['balance'] >= price:
        # 1. Trừ tiền khách
        new_balance = user_res.data['balance'] - price
        supabase.table('users').update({"balance": new_balance}).eq("username", session['user']).execute()
        # 2. Tạo đơn vào bảng order
        supabase.table('order').insert({"username": session['user'], "amount": amount, "gamepass_link": link}).execute()
        return f"<h3>Thành công! Đã trừ {price}đ.</h3><a href='/'>Quay lại</a>"
    return "<h3>Không đủ tiền nạp thêm đi bro!</h3><a href='/'>Quay lại</a>"

# --- WEBHOOK NẠP THẺ (Gachthefast) ---
@app.route('/callback-card', methods=['POST'])
def card_callback():
    data = request.form # Nhận từ Gachthefast
    status = data.get('status')
    amount = int(data.get('value')) # Mệnh giá thẻ
    username = data.get('content') # Nội dung là tên tài khoản khách ghi khi nạp
    
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
