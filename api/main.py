from flask import Flask, render_template, request, redirect, session, url_for
from supabase import create_client, Client

app = Flask(_name_, template_folder='../templates')
app.secret_key = "qihku_secure_2026"

# Thông tin Supabase
SUPABASE_URL = "https://awagntcuogwlqoztiwsu.supabase.co"
SUPABASE_KEY = "sbp_publishable_lUdwPeFeo-h6GHCJ46orUg_T8c-hJA6"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def index():
    user_info = None
    history = []
    if 'user' in session:
        # Lấy số dư khách
        res = supabase.table('users').select("*").eq("username", session['user']).single().execute()
        if res.data: user_info = res.data
        # Lấy lịch sử giao dịch (đơn rút Robux)
        hist_res = supabase.table('order').select("*").eq("username", session['user']).execute()
        if hist_res.data: history = hist_res.data
    return render_template('index.html', user=user_info, history=history)

# --- XỬ LÝ MUA ROBUX (GIÁ 150đ) ---
@app.route('/buy-robux', methods=['POST'])
def buy_robux():
    if 'user' not in session: return redirect('/')
    
    ingame = request.form.get('ingame_game') # Tên acc Roblox
    amount = int(request.form.get('amount'))
    link = request.form.get('gamepass_link')
    price = amount * 150 # 150đ/1RB

    # Check tiền
    user_res = supabase.table('users').select("balance").eq("username", session['user']).single().execute()
    if user_res.data and user_res.data['balance'] >= price:
        # Trừ tiền
        new_bal = user_res.data['balance'] - price
        supabase.table('users').update({"balance": new_bal}).eq("username", session['user']).execute()
        # Lưu đơn hàng
        supabase.table('order').insert({
            "username": session['user'],
            "ingame_game": ingame,
            "amount": amount,
            "gamepass_link": link,
            "status": "Đang xử lý"
        }).execute()
        return "<h3>Thành công! Đã trừ tiền và tạo đơn.</h3><a href='/'>Quay lại</a>"
    return "<h3>Số dư không đủ!</h3><a href='/'>Quay lại</a>"

# --- WEBHOOK NẠP THẺ (Gachthefast) ---
@app.route('/callback-card', methods=['POST'])
def card_callback():
    data = request.form 
    if data.get('status') == '1': # Thẻ đúng
        amount = int(data.get('value'))
        username = data.get('content') # Khách nhập tên web khi nạp
        user_res = supabase.table('users').select("balance").eq("username", username).single().execute()
        if user_res.data:
            new_bal = user_res.data['balance'] + amount
            supabase.table('users').update({"balance": new_bal}).eq("username", username).execute()
    return "OK"

@app.route('/login', methods=['POST'])
def login():
    u, p = request.form.get('username'), request.form.get('password')
    res = supabase.table('users').select("*").eq("username", u).eq("password", p).execute()
    if res.data:
        session['user'] = u
        return redirect('/')
    return "Sai tài khoản!"

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')
