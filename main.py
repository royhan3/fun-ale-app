import streamlit as st
import pandas as pd
from supabase import create_client

# 1. Koneksi Supabase
url = "https://jalezfpxljzsnrveatks.supabase.co"
key = "sb_publishable_Z8yQXpD6yPTGI11Z0hkN6A_c0cxqR_1"
supabase = create_client(url, key)

# Set halaman agar lebih lebar dan punya ikon tab
st.set_page_config(page_title="Fun Ale Hub | 2026", page_icon="🎬", layout="wide")

# --- CUSTOM STYLE (ADAPTIF TEMA TERANG/GELAP) ---
st.markdown("""
    <style>
    /* Mengatur radius tombol agar lebih modern */
    .stButton>button {
        border-radius: 20px;
        font-weight: bold;
    }
    
    /* Perbaikan Kotak Metrik agar Transparan & Adaptif */
    [data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.1); /* Abu-abu sangat transparan */
        padding: 15px;
        border-radius: 15px;
        border: 1px solid rgba(128, 128, 128, 0.2); /* Garis tipis pembatas */
    }

    /* Memastikan teks metrik tetap terbaca */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
    }
    
    /* Styling Container untuk Review Video */
    .stElementContainer {
        border-radius: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/video-playlist.png") # Ikon pemanis
    st.title("Fun Ale Center")
    menu = st.radio("Navigasi Utama", ["📊 Dashboard Utama", "📤 Portal Editor", "👑 Panel Review Bos"])
    st.divider()
    st.caption("Production App v2.0 | 2026")

# Ambil data terbaru
res = supabase.table("content_plans").select("*").execute()
df = pd.DataFrame(res.data)

# --- HALAMAN 1: DASHBOARD ---
if menu == "📊 Dashboard Utama":
    st.title("📊 Monitoring Produksi Fun Ale")
    
    # Bagian Metrik (Ringkasan Angka)
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Rencana", len(df[df['status'] == 'Plan']), delta="Konten")
    m2.metric("Sedang Review", len(df[df['status'] == 'Review']), delta="Waiting", delta_color="inverse")
    m3.metric("Selesai Produksi", len(df[df['status'] == 'Done']), delta="Final", delta_color="normal")
    
    st.divider()
    
    # 3 Kolom Tabel
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🛠️ **TO-DO LIST**")
        df_p = df[df['status'] == 'Plan'][['concept']]
        if not df_p.empty:
            st.dataframe(df_p, use_container_width=True, hide_index=True)
        else:
            st.write("Semua beres! ✅")

    with col2:
        st.markdown("### ⏳ **WAITING REVIEW**")
        df_r = df[df['status'] == 'Review'][['concept']]
        if not df_r.empty:
            st.dataframe(df_r, use_container_width=True, hide_index=True)
        else:
            st.write("Belum ada video masuk ☕")

    with col3:
        st.markdown("### ✅ **COMPLETED**")
        df_d = df[df['status'] == 'Done'][['concept']]
        if not df_d.empty:
            st.dataframe(df_d, use_container_width=True, hide_index=True)
        else:
            st.write("Ayo semangat! 💪")

# --- HALAMAN 2: EDITOR ---
elif menu == "📤 Portal Editor":
    st.title("📤 Portal Upload Editor")
    st.info("Silakan pilih konten yang sudah selesai diedit dan kirim ke Bos.")
    
    df_upload = df[df['status'] == 'Plan']
    if not df_upload.empty:
        with st.container(border=True):
            pilihan = st.selectbox("Judul Konten:", df_upload['concept'].tolist())
            video_file = st.file_uploader("Upload MP4 (Max 200MB):", type=["mp4", "mov"])
            
            if st.button("🚀 Kirim Hasil Edit", use_container_width=True):
                if video_file:
                    with st.spinner("Mengompres dan mengirim video..."):
                        try:
                            clean_name = f"{pilihan.replace(' ', '_')}.mp4"
                            supabase.storage.from_("production-videos").upload(
                                path=clean_name, file=video_file.getvalue(), 
                                file_options={"content-type": "video/mp4", "upsert": "true"}
                            )
                            supabase.table("content_plans").update({"status": "Review"}).eq("concept", pilihan).execute()
                            st.success(f"Berhasil! '{pilihan}' sudah mendarat di meja Bos.")
                            st.balloons()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                else:
                    st.warning("Pilih file dulu dong!")
    else:
        st.success("Semua rencana konten sudah diproses!")

# --- HALAMAN 3: BOS ---
elif menu == "👑 Panel Review Bos":
    st.title("👑 Ruang Review Bos")
    df_rev = df[df['status'] == 'Review']
    
    if not df_rev.empty:
        for i, row in df_rev.iterrows():
            with st.container(border=True):
                st.subheader(f"🎬 Konten: {row['concept']}")
                
                v_col1, v_col2, v_col3 = st.columns([1, 2, 1])
                with v_col2:
                    url_v = f"{url}/storage/v1/object/public/production-videos/{row['concept'].replace(' ', '_')}.mp4"
                    st.video(url_v)
                
                catatan = st.text_input("Pesan untuk Editor:", key=f"t_{i}")
                
                c1, c2, c3 = st.columns(3)
                if c1.button("✅ TERIMA", key=f"a_{i}", use_container_width=True):
                    supabase.table("content_plans").update({"status": "Done"}).eq("concept", row['concept']).execute()
                    st.rerun()
                
                if c2.button("✍️ REVISI", key=f"r_{i}", use_container_width=True):
                    st.warning(f"Revisi dikirim: {catatan}")
                
                if c3.button("🗑️ TOLAK/HAPUS", key=f"d_{i}", use_container_width=True):
                    supabase.storage.from_("production-videos").remove([f"{row['concept'].replace(' ', '_')}.mp4"])
                    supabase.table("content_plans").update({"status": "Plan"}).eq("concept", row['concept']).execute()
                    st.rerun()
    else:
        st.balloons()
        st.info("Santai, Bos! Belum ada video baru yang perlu dicek.")
