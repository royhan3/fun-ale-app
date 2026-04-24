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

# Ambil data terbaru dari database
res = supabase.table("content_plans").select("*").execute()
df = pd.DataFrame(res.data)

# --- HALAMAN 1: DAFTAR & PROGRES ---
if menu == "📋 Daftar & Progres":
    st.header("Status Produksi Fun Ale 2026")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🛠 Belum Digarap (Plan)")
        st.table(df[df['status'] == 'Plan'][['concept']])
    with col2:
        st.subheader("✅ Sudah Selesai (Done)")
        st.table(df[df['status'] == 'Done'][['concept']])

# --- HALAMAN 2: EDITOR (UPLOAD) ---
elif menu == "📤 Editor: Upload Video":
    st.header("Halaman Upload Editor")
    # Hanya pilih konten yang statusnya bukan 'Done'
    list_konten = df[df['status'] != 'Done']['concept'].tolist()
    pilihan = st.selectbox("Pilih judul konten yang sudah selesai diedit:", list_konten)
    
    video_file = st.file_uploader("Upload Hasil Edit (MP4)", type=["mp4", "mov"])
    
    if st.button("Kirim ke Bos"):
        if video_file and pilihan:
            with st.spinner("Sedang mengirim video ke gudang storage..."):
                # 1. Upload ke Supabase Storage
                nama_file = f"{pilihan.replace(' ', '_')}.mp4"
                res_storage = supabase.storage.from_("production-videos").upload(nama_file, video_file.getvalue(), {"content-type": "video/mp4"})
                
                # 2. Update status di tabel jadi 'Review'
                supabase.table("content_plans").update({"status": "Review"}).eq("concept", pilihan).execute()
                st.success(f"Mantap! Video '{pilihan}' sudah terkirim. Status sekarang: REVIEW.")
        else:
            st.warning("Pilih file videonya dulu ya!")

# --- HALAMAN 3: BOS (REVIEW) ---
elif menu == "👑 Bos: Review & Revisi":
    st.header("Halaman Persetujuan Bos")
    # Filter konten yang statusnya 'Review'
    df_review = df[df['status'] == 'Review']
    
    if not df_review.empty:
        for _, row in df_review.iterrows():
            with st.expander(f"Review Konten: {row['concept']}", expanded=True):
                # Ambil Link Video dari Storage
                nama_file_storage = f"{row['concept'].replace(' ', '_')}.mp4"
                url_video = f"{url}/storage/v1/object/public/production-videos/{nama_file_storage}"
                
                st.video(url_video)
                
                catatan = st.text_area("Catatan Revisi (Kosongkan jika oke):", key=f"txt_{row['concept']}")
                
                c1, c2 = st.columns(2)
                if c1.button("✅ APPROVE (Selesai)", key=f"app_{row['concept']}"):
                    supabase.table("content_plans").update({"status": "Done"}).eq("concept", row['concept']).execute()
                    st.rerun()
                
                if c2.button("❌ PERLU REVISI", key=f"rev_{row['concept']}"):
                    st.error(f"Catatan terkirim ke Editor: {catatan}")
                    # Di sini bisa ditambah logika update kolom revisi jika ada
    else:
        st.info("Belum ada kiriman video baru dari Editor. Santai dulu, Bos!")
