import streamlit as st
import pandas as pd
from supabase import create_client

# 1. Koneksi Supabase
url = "https://jalezfpxljzsnrveatks.supabase.co"
key = "sb_publishable_Z8yQXpD6yPTGI11Z0hkN6A_c0cxqR_1"
supabase = create_client(url, key)

st.set_page_config(page_title="Fun Ale Production", layout="wide")

# --- SIDEBAR NAVIGASI ---
st.sidebar.title("🎬 Fun Ale Menu")
menu = st.sidebar.radio("Pilih Halaman:", ["📋 Daftar & Progres", "📤 Editor: Upload Video", "👑 Bos: Review & Revisi"])

# Ambil data terbaru
res = supabase.table("content_plans").select("*").execute()
df = pd.DataFrame(res.data)

# --- HALAMAN 1: DAFTAR & PROGRES ---
if menu == "📋 Daftar & Progres":
    st.header("Status Produksi Fun Ale 2026")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🛠 Belum Digarap")
        st.table(df[df['status'] == 'Plan'][['concept']])
    with c2:
        st.subheader("✅ Sudah Selesai")
        st.table(df[df['status'] == 'Done'][['concept']])

# --- HALAMAN 2: EDITOR (UPLOAD) ---
elif menu == "📤 Editor: Upload Video":
    st.header("Halaman Upload Editor")
    list_konten = df[df['status'] != 'Done']['concept'].tolist()
    pilihan = st.selectbox("Pilih judul konten:", list_konten)
    video_file = st.file_uploader("Upload Hasil Edit (MP4)", type=["mp4", "mov"])
    
    if st.button("Kirim ke Bos"):
        if video_file and pilihan:
            with st.spinner("Mengirim video..."):
                try:
                    clean_name = f"{pilihan.replace(' ', '_')}.mp4"
                    supabase.storage.from_("production-videos").upload(
                        path=clean_name, 
                        file=video_file.getvalue(), 
                        file_options={"content-type": "video/mp4", "upsert": "true"}
                    )
                    supabase.table("content_plans").update({"status": "Review"}).eq("concept", pilihan).execute()
                    st.success("Berhasil terkirim!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Gagal: {e}")

# --- HALAMAN 3: BOS (REVIEW) ---
elif menu == "👑 Bos: Review & Revisi":
    st.header("Halaman Persetujuan Bos")
    df_review = df[df['status'] == 'Review']
    
    if not df_review.empty:
        for i, row in df_review.iterrows():
            # Menggunakan ID atau Index unik agar tidak Duplicate Key Error
            with st.expander(f"Review: {row['concept']}", expanded=True):
                nama_file_storage = f"{row['concept'].replace(' ', '_')}.mp4"
                url_video = f"{url}/storage/v1/object/public/production-videos/{nama_file_storage}"
                st.video(url_video)
                
                catatan = st.text_area("Catatan Revisi:", key=f"revisi_{i}")
                
                col_btn1, col_btn2 = st.columns(2)
                if col_btn1.button("✅ APPROVE", key=f"approve_btn_{i}"):
                    supabase.table("content_plans").update({"status": "Done"}).eq("concept", row['concept']).execute()
                    st.success("Konten Selesai!")
                    st.rerun()
                
                if col_btn2.button("❌ REVISI", key=f"revisi_btn_{i}"):
                    st.warning(f"Revisi dikirim: {catatan}")
    else:
        st.info("Belum ada video baru.")
