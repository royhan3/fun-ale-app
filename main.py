import streamlit as st
import pandas as pd
from supabase import create_client

# 1. Koneksi Supabase
url = "https://jalezfpxljzsnrveatks.supabase.co"
key = "sb_publishable_Z8yQXpD6yPTGI11Z0hkN6A_c0cxqR_1"
supabase = create_client(url, key)

st.set_page_config(page_title="Fun Ale Hub | 2026", page_icon="🎬", layout="wide")

# --- CUSTOM STYLE ---
st.markdown("""
    <style>
    .stButton>button { border-radius: 20px; font-weight: bold; }
    [data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.1);
        padding: 15px; border-radius: 15px; border: 1px solid rgba(128, 128, 128, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/video-playlist.png")
    st.title("Fun Ale Center")
    menu = st.radio("Navigasi Utama", ["📊 Dashboard Utama", "➕ Tambah Rencana", "📤 Portal Editor", "👑 Panel Review Bos"])
    st.divider()
    st.caption("Production App v2.6 | 2026")

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
        df_p = df[df['status'] == 'Plan']
        if not df_p.empty:
            for i, row in df_p.iterrows():
                # Baris khusus untuk setiap judul konten agar bisa dihapus
                c_text, c_del = st.columns([4, 1])
                c_text.write(f"🔹 {row['concept']}")
                if c_del.button("🗑️", key=f"del_plan_{i}"):
                    supabase.table("content_plans").delete().eq("concept", row['concept']).execute()
                    st.rerun()
        else:
            st.write("Kosong")

    with col2:
        st.markdown("### ⏳ **WAITING REVIEW**")
        st.dataframe(df[df['status'] == 'Review'][['concept']], use_container_width=True, hide_index=True)

    with col3:
        st.markdown("### ✅ **COMPLETED**")
        st.dataframe(df[df['status'] == 'Done'][['concept']], use_container_width=True, hide_index=True)

# --- HALAMAN 2: TAMBAH RENCANA ---
elif menu == "➕ Tambah Rencana":
    st.title("➕ Tambah Ide Konten Baru")
    with st.container(border=True):
        new_concept = st.text_input("Judul / Konsep Konten:")
        if st.button("Simpan ke To-Do List", use_container_width=True):
            if new_concept:
                supabase.table("content_plans").insert({"concept": new_concept, "status": "Plan"}).execute()
                st.success("Berhasil ditambah!")
                st.rerun()

# --- HALAMAN 3: EDITOR ---
elif menu == "📤 Portal Editor":
    st.title("📤 Portal Upload Editor")
    df_u = df[df['status'] == 'Plan']
    if not df_u.empty:
        pilihan = st.selectbox("Pilih konten:", df_u['concept'].tolist())
        video_file = st.file_uploader("Upload MP4:", type=["mp4", "mov"])
        if st.button("🚀 Kirim ke Bos"):
            if video_file:
                path = f"{pilihan.replace(' ', '_')}.mp4"
                supabase.storage.from_("production-videos").upload(path, video_file.getvalue(), {"upsert":"true"})
                supabase.table("content_plans").update({"status": "Review"}).eq("concept", pilihan).execute()
                st.rerun()

# --- HALAMAN 4: BOS ---
elif menu == "👑 Panel Review Bos":
    st.title("👑 Ruang Review Bos")
    df_r = df[df['status'] == 'Review']
    if not df_r.empty:
        for i, row in df_r.iterrows():
            with st.container(border=True):
                st.subheader(f"🎬 {row['concept']}")
                url_v = f"{url}/storage/v1/object/public/production-videos/{row['concept'].replace(' ', '_')}.mp4"
                st.video(url_v)
                c1, c2, c3 = st.columns(3)
                if c1.button("✅ APPROVE", key=f"a_{i}"):
                    supabase.table("content_plans").update({"status": "Done"}).eq("concept", row['concept']).execute()
                    st.rerun()
                if c2.button("🗑️ HAPUS VIDEO", key=f"d_{i}"):
                    supabase.storage.from_("production-videos").remove([f"{row['concept'].replace(' ', '_')}.mp4"])
                    supabase.table("content_plans").update({"status": "Plan"}).eq("concept", row['concept']).execute()
                    st.rerun()
