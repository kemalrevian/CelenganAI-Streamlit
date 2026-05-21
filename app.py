import streamlit as st
import pandas as pd
import altair as alt
import sqlite3
import hashlib
import datetime
from ai_agent import ask_financial_assistant
from multimodal_agent import transcribe_audio, parse_receipt_image

# --- FUNGSI HELPER UNTUK DATABASE & AUTH ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_login(email, password):
    conn = sqlite3.connect('database/Celengan_AI_st_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, password_hash FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        user_id, name, db_password = user
        if db_password == hash_password(password) or db_password == password:
            return user_id, name
    return None, None

def register_user(name, email, password):
    conn = sqlite3.connect('database/Celengan_AI_st_database.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)", 
                       (name, email, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False 
    finally:
        conn.close()

# --- FUNGSI HELPER UNTUK UI ---
MONTH_NAMES = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

def get_total_expense(user_id, date_obj):
    conn = sqlite3.connect('database/Celengan_AI_st_database.db')
    cursor = conn.cursor()
    month_str = date_obj.strftime("%Y-%m")
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE user_id = ? AND type = 'expense' AND strftime('%Y-%m', created_at) = ?", (user_id, month_str))
    expense = cursor.fetchone()[0] or 0
    conn.close()
    return expense

def change_month(delta):
    month = st.session_state.current_date.month - 1 + delta
    year = st.session_state.current_date.year + month // 12
    month = month % 12 + 1
    st.session_state.current_date = datetime.date(year, month, 1)

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Celengan.AI", 
    page_icon="🪙",
    layout="centered"
)

# --- INISIALISASI SESSION STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.user_name = None
    st.session_state.messages = []
    st.session_state.auto_prompt = None # Untuk menampung hasil teks dari suara/gambar

if "current_date" not in st.session_state:
    now = datetime.datetime.now()
    st.session_state.current_date = datetime.date(now.year, now.month, 1)


# ===========================
# HALAMAN 1: LOGIN & REGISTER
# ===========================
if not st.session_state.logged_in:
    st.title("🪙 Celengan.AI")
    st.caption("Asisten Keuangan Pribadi Gen Z - Silakan Login")
    
    tab_login, tab_register = st.tabs(["🔒 Login", "📝 Register Akun Baru"])
    
    with tab_login:
        st.subheader("Login ke Akun Anda")
        login_email = st.text_input("Email", key="login_email")
        login_pass = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Login", type="primary", use_container_width=True):
            uid, uname = verify_login(login_email, login_pass)
            if uid:
                st.session_state.logged_in = True
                st.session_state.user_id = uid
                st.session_state.user_name = uname
                st.success(f"Berhasil login sebagai {uname}!")
                st.rerun()
            else:
                st.error("Email atau Password salah!")
                
    with tab_register:
        st.subheader("Buat Akun Baru")
        reg_name = st.text_input("Nama Panggilan")
        reg_email = st.text_input("Email")
        reg_pass = st.text_input("Password", type="password")
        
        if st.button("Daftar Sekarang", use_container_width=True):
            if reg_name and reg_email and reg_pass:
                if register_user(reg_name, reg_email, reg_pass):
                    st.success("Akun berhasil dibuat! Silakan login di tab sebelah.")
                else:
                    st.error("Pendaftaran Gagal: Email sudah terdaftar!")
            else:
                st.warning("Mohon isi semua form pendaftaran.")


# ================
# HALAMAN 2: UTAMA
# ================
else:
    # Membungkus semua elemen atas ke dalam satu Container
    header_container = st.container()
    
    with header_container:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"### Celengan.ai\nHi, {st.session_state.user_name}!")
        with col2:
            st.write("") 
            if st.button("Keluar", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.user_id = None
                st.session_state.user_name = None
                st.session_state.messages = []
                st.rerun()

        # Navigasi Bulan & Kartu Pengeluaran
        expense = get_total_expense(st.session_state.user_id, st.session_state.current_date)
        month_name = f"{MONTH_NAMES[st.session_state.current_date.month - 1]} {st.session_state.current_date.year}"

        c1, c2, c3 = st.columns([1, 4, 1])
        with c1:
            st.button("❮", key="prev_month", on_click=change_month, args=(-1,), use_container_width=True)
        with c2:
            st.markdown(f"<h5 style='text-align: center; margin-top: 5px;'>Bulan Ini • {month_name}</h5>", unsafe_allow_html=True)
        with c3:
            st.button("❯", key="next_month", on_click=change_month, args=(1,), use_container_width=True)

        st.info(f"💳 **Total Pengeluaran:** \n\n# Rp {expense:,.0f}")

    if len(st.session_state.messages) == 0:
        greeting = "Halo! Saya adalah Celengan.ai, asisten keuangan pribadi kamu. Ada yang mau dicatat atau dihitung hari ini?"
        st.session_state.messages.append({"role": "assistant", "content": greeting})


    # --------------
    # CHAT INTERFACE
    # --------------
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if isinstance(msg["content"], dict) and msg["content"].get("type") == "chart":
                chart_data = msg["content"]
                st.write(f"**{chart_data.get('title', 'Grafik')}**")
                df = pd.DataFrame(chart_data.get("data", []))
                if not df.empty:
                    df.set_index("name", inplace=True)
                    c_type = chart_data.get("chart_type")
                    if c_type == "bar":
                        st.bar_chart(df)
                    elif c_type == "line":
                        st.line_chart(df)
                    elif c_type == "pie":
                        df_pie = df.reset_index()
                        pie = alt.Chart(df_pie).mark_arc().encode(
                            theta=alt.Theta(field="value", type="quantitative"),
                            color=alt.Color(field="name", type="nominal"),
                            tooltip=['name', 'value']
                        )
                        st.altair_chart(pie, use_container_width=True)
                else:
                    st.info("Tidak ada data untuk grafik ini.")
            else:
                st.markdown(msg["content"])


    # --------------------------------
    # MULTIMODAL INPUTS (Kamera & Mic)
    # --------------------------------
    _, col_cam, col_mic, _ = st.columns([1, 2, 2, 1])
    
    # Fitur Vision
    with col_cam:
        with st.popover("📷 Unggah Struk", use_container_width=True):
            uploaded_image = st.file_uploader("Upload foto struk", type=['png', 'jpg', 'jpeg'], key="vision_uploader")
            if uploaded_image:
                if st.button("Catat Struk Ini", key="btn_vision", use_container_width=True):
                    with st.spinner("Membaca struk dengan AI..."):
                        try:
                            extracted_data = parse_receipt_image(uploaded_image)
                            st.session_state.auto_prompt = f"Tolong catat pengeluaran dari struk: {extracted_data['description']} kategori {extracted_data['category']} sebesar Rp {extracted_data['amount']}."
                            st.rerun() 
                        except Exception as e:
                            st.error(f"Gagal membaca struk: {e}")

    # Fitur Voice
    with col_mic:
        with st.popover("🎤 Rekam Suara", use_container_width=True):
            audio_data = st.audio_input("Rekam perintah suara", key="voice_uploader")
            if audio_data:
                if st.button("Kirim Suara", key="btn_voice", use_container_width=True):
                    with st.spinner("Mendengarkan..."):
                        try:
                            transcribed_text = transcribe_audio(audio_data)
                            st.session_state.auto_prompt = transcribed_text
                            st.rerun() 
                        except Exception as e:
                            st.error(f"Gagal memproses suara: {e}")

    # ----------------
    # PENGIRIMAN PESAN
    # ----------------
    user_input = st.chat_input("Ketik pengeluaran atau pertanyaan...")
    
    # Prioritasin pesan dari auto_prompt (Voice/Vision) jika ada
    prompt = None
    if st.session_state.auto_prompt:
        prompt = st.session_state.auto_prompt
        st.session_state.auto_prompt = None 
    elif user_input:
        prompt = user_input

    # Jika ada prompt yang masuk, jalankan AI
    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("assistant"):
            with st.spinner("Sedang Berpikir..."):
                try:
                    history_for_ai = [
                        {"role": m["role"], "content": m["content"]} 
                        for m in st.session_state.messages 
                        if isinstance(m["content"], str)
                    ]
                    
                    response = ask_financial_assistant(
                        user_message=prompt, 
                        user_id=st.session_state.user_id, 
                        history=history_for_ai[:-1]
                    )
                    
                    if isinstance(response, dict) and response.get("type") == "chart":
                        st.write(f"**{response.get('title', 'Grafik')}**")
                        df = pd.DataFrame(response.get("data", []))
                        if not df.empty:
                            df.set_index("name", inplace=True)
                            c_type = response.get("chart_type")
                            if c_type == "bar":
                                st.bar_chart(df)
                            elif c_type == "line":
                                st.line_chart(df)
                            elif c_type == "pie":
                                df_pie = df.reset_index()
                                pie = alt.Chart(df_pie).mark_arc().encode(
                                    theta=alt.Theta(field="value", type="quantitative"),
                                    color=alt.Color(field="name", type="nominal"),
                                    tooltip=['name', 'value']
                                )
                                st.altair_chart(pie, use_container_width=True)
                        else:
                            st.info("Tidak ada data untuk grafik ini.")
                    else:
                        st.markdown(response)
                        
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    st.rerun() 
                    
                except Exception as e:
                    st.error(f"Waduh, ada error nih: {e}")
