import streamlit as st
import pandas as pd
from supabase import create_client

# 1. Koneksi Supabase (Pakai data yang lama)
url = "https://jalezfpxljzsnrveatks.supabase.co"
key = "sb_publishable_Z8yQXpD6yPTGI11Z0hkN6A_c0cxqR_1"
supabase = create_client(url, key)

st.set_page_config(page_title="Fun Ale Hub", layout="wide")
st.title("🎬 Fun Ale Production Hub")

# Menu Navigasi
menu = st.sidebar.selectbox("Pilih Menu", ["Daftar Konten", "Upload Video (Editor)", "Review Bos"])

if menu == "Daftar Konten":
    st.subheader("📋 Status Produksi Konten")
    res = supabase.table("content_plans").select("*").execute()
    df = pd.DataFrame(res.data)
    st.dataframe(df[['target_week', 'category', 'concept', 'status']], use_container_width=True)

# Sementara kita buat ini dulu untuk memastikan koneksi aman
