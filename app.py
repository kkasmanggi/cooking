import streamlit as st
import google.generativeai as genai
import os

# ==============================================================================
# PENGATURAN API KEY DAN MODEL
# ==============================================================================

# Mengambil API key dari secrets di Streamlit Cloud
API_KEY = st.secrets["gemini_api_key"]

# Nama model Gemini yang akan digunakan.
MODEL_NAME = 'gemini-1.5-flash'

# ==============================================================================
# KONTEKS AWAL CHATBOT
# ==============================================================================

# Definisikan peran chatbot Anda di sini.
INITIAL_CHATBOT_CONTEXT = [
    {
        "role": "user",
        "parts": ["Saya adalah Ahli Masak. Saya akan memberikan berbagai macam jenis resep masakan yang Anda inginkan. Jawaban singkat dan jelas. Tolak pertanyaan selain tentang masakan."]
    },
    {
        "role": "model",
        "parts": ["Baik! Saya akan memberikan resep yang Anda inginkan."]
    }
]

# ==============================================================================
# APLIKASI STREAMLIT
# ==============================================================================

# Mengatur judul halaman dan ikon
st.set_page_config(page_title="Ahli Masak 👨‍🍳", page_icon="🍳")
st.title("👨‍🍳 Ahli Masak")
st.caption("Aplikasi chatbot yang hanya bisa memberikan resep masakan. Dibuat dengan Google Gemini.")

# Inisialisasi Gemini API
try:
    genai.configure(api_key=API_KEY)
except Exception as e:
    st.error(f"Kesalahan saat mengkonfigurasi API Key: {e}")
    st.stop()

# Inisialisasi model
try:
    model = genai.GenerativeModel(
        MODEL_NAME,
        generation_config=genai.types.GenerationConfig(
            temperature=0.4,
            max_output_tokens=500
        )
    )
except Exception as e:
    st.error(f"Kesalahan saat inisialisasi model '{MODEL_NAME}': {e}")
    st.stop()

# Inisialisasi riwayat chat di Streamlit session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    # Tambahkan konteks awal ke riwayat chat
    for chat_entry in INITIAL_CHATBOT_CONTEXT:
        st.session_state.chat_history.append(chat_entry)

# Tampilkan riwayat chat yang sudah ada, kecuali konteks awal
for message in st.session_state.chat_history:
    if message["role"] == "user":
        with st.chat_message("user", avatar="🙋‍♂️"):
            st.write(message["parts"][0])
    elif message["role"] == "model" and message["parts"][0] != "Baik! Saya akan memberikan resep yang Anda inginkan.":
        with st.chat_message("assistant", avatar="👨‍🍳"):
            st.write(message["parts"][0])
            
# Tangani input dari pengguna
user_prompt = st.chat_input("Tanyakan resep masakan...")

if user_prompt:
    # Tampilkan input pengguna di chat
    with st.chat_message("user", avatar="🙋‍♂️"):
        st.write(user_prompt)
    
    # Tambahkan input pengguna ke riwayat
    st.session_state.chat_history.append({"role": "user", "parts": [user_prompt]})
    
    # Buat sesi chat baru dengan riwayat dari session state
    chat_session = model.start_chat(history=st.session_state.chat_history)
    
    # Kirim pesan ke model dan dapatkan respons
    try:
        response = chat_session.send_message(user_prompt, request_options={"timeout": 60})
        model_response = response.text
    except Exception as e:
        model_response = f"Maaf, terjadi kesalahan: {e}"
        
    # Tampilkan respons dari model
    with st.chat_message("assistant", avatar="👨‍🍳"):
        st.write(model_response)
        
    # Tambahkan respons model ke riwayat
    st.session_state.chat_history.append({"role": "model", "parts": [model_response]})
