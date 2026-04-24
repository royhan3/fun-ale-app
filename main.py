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
    st.header("📊 Monitoring Produksi Fun Ale 2026")
    
    # Membuat 3 kolom untuk 3 status berbeda
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🛠 Belum Digarap")
        st.info("Status: Plan")
        df_plan = df[df['status'] == 'Plan']
        if not df_plan.empty:
            st.table(df_plan[['concept']])
        else:
            st.write("Kosong")

    with col2:
        st.subheader("⏳ Menunggu Review")
        st.warning("Status: Review")
        df_review = df[df['status'] == 'Review']
        if not df_review.empty:
            st.table(df_review[['concept']])
        else:
            st.write("Belum ada kiriman editor")

    with col3:
        st.subheader("✅ Sudah Selesai")
        st.success("Status: Done")
        df_done = df[df['status'] == 'Done']
        if not df_done.empty:
            st.table(df_done[['concept']])
        else:
            st.write("Belum ada yang selesai")

# --- HALAMAN 2: EDITOR (UPLOAD) ---
elif menu == "📤 Editor: Upload Video":
    st.header("📤 Kirim Video ke Bos")
    # Hanya tampilkan judul yang statusnya 'Plan'
    df_upload = df[df['status'] == 'Plan']
    
    if not df_upload.empty:
        list_konten = df_upload['concept'].tolist()
        pilihan = st.selectbox("Pilih konten yang mau diupload:", list_konten)
        video_file = st.file_uploader("Pilih file video (MP4)", type=["mp4", "mov"])
        
        if st.button("Kirim Sekarang"):
            if video_file:
                with st.spinner("Proses upload..."):
                    try:
                        clean_name = f"{pilihan.replace(' ', '_')}.mp4"
                        supabase.storage.from_("production-videos").upload(
                            path=clean_name, 
                            file=video_file.getvalue(), 
                            file_options={"content-type": "video/mp4", "upsert": "true"}
                        )
                        # Update status ke 'Review'
                        supabase.table("content_plans").update({"status": "Review"}).eq("concept", pilihan).execute()
                        st.success(f"Berhasil! '{pilihan}' sekarang masuk ke tabel Menunggu Review.")
                        st.balloons()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
    else:
        st.info("Semua konten sudah digarap atau sedang direview.")

# --- HALAMAN 3: BOS (REVIEW) ---
elif menu == "👑 Bos: Review & Revisi":
    st.header("👑 Persetujuan Bos")
    df_review_page = df[df['status'] == 'Review']
    
    if not df_review_page.empty:
        for i, row in df_review_page.iterrows():
            with st.expander(f"🎬 Review: {row['concept']}", expanded=True):
                # Tampilan video dikecilkan (proporsional)
                v_col1, v_col2, v_col3 = st.columns([1, 2, 1])
                with v_col2:
                    nama_file_storage = f"{row['concept'].replace(' ', '_')}.mp4"
                    url_video = f"{url}/storage/v1/object/public/production-videos/{nama_file_storage}"
                    st.video(url_video)
                
                st.divider()
                catatan = st.text_area("Catatan Revisi:", key=f"rev_text_{i}")
                
                c1, c2, c3 = st.columns(3)
                if c1.button("✅ APPROVE", key=f"btn_app_{i}", use_container_width=True):
                    # Jika di-approve, status jadi 'Done'
                    supabase.table("content_plans").update({"status": "Done"}).eq("concept", row['concept']).execute()
                    st.success("Konten dipindahkan ke tabel 'Sudah Selesai'!")
                    st.rerun()
                
                if c2.button("❌ REVISI", key=f"btn_rev_{i}", use_container_width=True):
                    st.warning(f"Catatan terkirim: {catatan}")
                
                if c3.button("🗑️ HAPUS", key=f"btn_del_{i}", use_container_width=True):
                    supabase.storage.from_("production-videos").remove([nama_file_storage])
                    supabase.table("content_plans").update({"status": "Plan"}).eq("concept", row['concept']).execute()
                    st.rerun()
    else:
        st.info("Belum ada video yang perlu direview.")
