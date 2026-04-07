from flask import Flask, render_template, request, redirect, session
from supabase import create_client, Client

app = Flask(_name_, template_folder='../templates')
app.secret_key = "qihku_bi_mat_2026"

# Kết nối
SUPABASE_URL = "https://awagntcuogwlqoztiwsu.supabase.co"
SUPABASE_KEY = "sbp_publishable_lUdwPeFeo-h6GHCJ46orUg_T8c-hJA6"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def index():
    user_info = None
    history = []
    if 'user' in session:
        # Lấy thông tin user
        res = supabase.table('users').select("*").eq("username", session['user']).single().execute()
        if res.data: user_info = res.data
        # Lấy lịch sử giao dịch
        hist_res = supabase.table('order').select("*").eq("username", session['user']).order('created_at', desc=True).execute()
        if hist_res.data: history = hist_res.data
    return render_template('index.html', user=user_info, history=history)

# --- MUA / RÚT ROBUX ---
@app.route('/rut-robux', methods=['POST'])
def rut_robux():
    if 'user' not in session: return redirect('/')
    
    ingame = request.form.get('ingame_name') # Tên acc Roblox bắt buộc
    amount = int(request.form.get('amount'))
    link = request.form.get('gamepass')
    price = amount * 150 # Giá 150đ/1RB

    user_res = supabase.table('users').select("balance").eq("username", session['user']).single().execute()
    if user_res.data and user_res.data['balance'] >= price:
        # Trừ tiền
        new_bal = user_res.data['balance'] - price
        supabase.table('users').update({"balance": new_bal}).eq("username", session['user']).execute()
        # Lưu đơn hàng kèm tên acc Roblox
        supabase.table('order').insert({
            "username": session['user'],
            "ingame_name": ingame,
            "amount": amount,
            "gamepass_link": link,
            "status": "Chờ xử lý"
        }).execute()
        return "Đặt đơn thành công! Kiểm tra lịch sử nhé bro."
    return "Không đủ tiền rồi!"

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
