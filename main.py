import streamlit as st
import pandas as pd
from supabase import create_client

# 1. Koneksi Supabase
url = "https://jalezfpxljzsnrveatks.supabase.co"
key = "sb_publishable_Z8yQXpD6yPTGI11Z0hkN6A_c0cxqR_1"
supabase = create_client(url, key)

st.set_page_config(page_title="Fun Ale Hub | 2026", page_icon="🎬", layout="wide")

# --- CUSTOM STYLE (ADAPTIF) ---
st.markdown("""
    <style>
    .stButton>button {
        border-radius: 20px;
        font-weight: bold;
    }
    [data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.1);
        padding: 15px;
        border-radius: 15px;
        border: 1px solid rgba(128, 128, 128, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/video-playlist.png")
    st.title("Fun Ale Center")
    # Tambah menu "Tambah Rencana" di sini
    menu = st.radio("Navigasi Utama", ["📊 Dashboard Utama", "➕ Tambah Rencana", "📤 Portal Editor", "👑 Panel Review Bos"])
    st.divider()
    st.caption("Production App v2.5 | 2026")

# Ambil data terbaru
res = supabase.table("content_plans").select("*").execute()
df = pd.DataFrame(res.data)

# --- HALAMAN 1: DASHBOARD ---
if menu == "📊 Dashboard Utama":
    st.title("📊 Monitoring Produksi Fun Ale")
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Rencana", len(df[df['status'] == 'Plan']))
    m2.metric("Sedang Review", len(df[df['status'] == 'Review']))
    m3.metric("Selesai Produksi", len(df[df['status'] == 'Done']))
    
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 🛠️ **TO-DO LIST**")
        st.dataframe(df[df['status'] == 'Plan'][['concept']], use_container_width=True, hide_index=True)
    with col2:
        st.markdown("### ⏳ **WAITING REVIEW**")
        st.dataframe(df[df['status'] == 'Review'][['concept']], use_container_width=True, hide_index=True)
    with col3:
        st.markdown("### ✅ **COMPLETED**")
        st.dataframe(df[df['status'] == 'Done'][['concept']], use_container_width=True, hide_index=True)

# --- HALAMAN BARU: TAMBAH RENCANA ---
elif menu == "➕ Tambah Rencana":
    st.title("➕ Tambah Ide Konten Baru")
    with st.container(border=True):
        new_concept = st.text_input("Judul / Konsep Konten:", placeholder="Contoh: Ale main bola sama Asha")
        category = st.selectbox("Kategori:", ["FunArt", "FunGame", "FunSains", "FunDay"])
        target_week = st.number_input("Target Minggu Ke-:", min_value=1, max_value=52, value=1)
        
        if st.button("Simpan ke To-Do List", use_container_width=True):
            if new_concept:
                try:
                    # Masukkan data ke Supabase
                    data = {
                        "concept": new_concept,
                        "category": category,
                        "target_week": target_week,
                        "status": "Plan" # Otomatis jadi Plan
                    }
                    supabase.table("content_plans").insert(data).execute()
                    st.success(f"Berhasil menambahkan '{new_concept}' ke rencana!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Gagal simpan: {e}")
            else:
                st.warning("Isi dulu judul kontennya!")

# --- HALAMAN 2: EDITOR ---
elif menu == "📤 Portal Editor":
    st.title("📤 Portal Upload Editor")
    df_upload = df[df['status'] == 'Plan']
    if not df_upload.empty:
        pilihan = st.selectbox("Pilih konten:", df_upload['concept'].tolist())
        video_file = st.file_uploader("Upload MP4:", type=["mp4", "mov"])
        if st.button("🚀 Kirim ke Bos"):
            if video_file:
                clean_name = f"{pilihan.replace(' ', '_')}.mp4"
                supabase.storage.from_("production-videos").upload(path=clean_name, file=video_file.getvalue(), file_options={"content-type":"video/mp4", "upsert":"true"})
                supabase.table("content_plans").update({"status": "Review"}).eq("concept", pilihan).execute()
                st.success("Terkirim!")
                st.rerun()

# --- HALAMAN 3: BOS ---
elif menu == "👑 Panel Review Bos":
    st.title("👑 Ruang Review Bos")
    df_rev = df[df['status'] == 'Review']
    if not df_rev.empty:
        for i, row in df_rev.iterrows():
            with st.container(border=True):
                st.subheader(f"🎬 {row['concept']}")
                v_c1, v_c2, v_c3 = st.columns([1, 2, 1])
                with v_c2:
                    url_v = f"{url}/storage/v1/object/public/production-videos/{row['concept'].replace(' ', '_')}.mp4"
                    st.video(url_v)
                c1, c2, c3 = st.columns(3)
                if c1.button("✅ APPROVE", key=f"a_{i}", use_container_width=True):
                    supabase.table("content_plans").update({"status": "Done"}).eq("concept", row['concept']).execute()
                    st.rerun()
                if c2.button("✍️ REVISI", key=f"r_{i}", use_container_width=True):
                    st.warning("Catatan revisi terkirim!")
                if c3.button("🗑️ HAPUS", key=f"d_{i}", use_container_width=True):
                    supabase.storage.from_("production-videos").remove([f"{row['concept'].replace(' ', '_')}.mp4"])
                    supabase.table("content_plans").update({"status": "Plan"}).eq("concept", row['concept']).execute()
                    st.rerun()
    else:
        st.info("Belum ada video baru.")
