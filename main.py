import streamlit as st
import pandas as pd
from supabase import create_client

# 1. Koneksi Supabase
url = "https://jalezfpxljzsnrveatks.supabase.co"
key = "sb_publishable_Z8yQXpD6yPTGI11Z0hkN6A_c0cxqR_1"
supabase = create_client(url, key)

st.set_page_config(page_title="Fun Ale Hub | 2026", page_icon="🎬", layout="wide")

# --- CUSTOM STYLE (DARK MODE FRIENDLY) ---
st.markdown("""
    <style>
    .stButton>button { border-radius: 20px; font-weight: bold; }
    [data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.1);
        padding: 15px; border-radius: 15px; border: 1px solid rgba(128, 128, 128, 0.2);
    }
    .stWrite { font-size: 1.1rem; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/video-playlist.png")
    st.title("Fun Ale Center")
    menu = st.radio("Navigasi Utama", ["📊 Dashboard Utama", "➕ Tambah Rencana", "📤 Portal Editor", "👑 Panel Review Bos"])
    st.divider()
    st.caption("Production App v2.9 | 2026")

# Ambil data terbaru
res = supabase.table("content_plans").select("*").execute()
df = pd.DataFrame(res.data) if res.data else pd.DataFrame(columns=["concept", "status", "category", "platform", "target_week"])

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
                c_text, c_del = st.columns([4, 1])
                # --- DI SINI PERBAIKANNYA: Menambahkan Target Week & Platform ---
                info_label = f"{row.get('platform', 'Long')} | Week {row.get('target_week', '-')}"
                c_text.write(f"🔹 **{row['concept']}**")
                c_text.caption(f"📌 {info_label} | {row.get('category', 'General')}")
                
                if c_del.button("🗑️", key=f"del_plan_{i}"):
                    supabase.table("content_plans").delete().eq("concept", row['concept']).execute()
                    st.rerun()
                st.divider()
        else: st.write("Kosong")

    with col2:
        st.markdown("### ⏳ **WAITING REVIEW**")
        if not df[df['status'] == 'Review'].empty:
            st.dataframe(df[df['status'] == 'Review'][['concept', 'platform', 'target_week']], use_container_width=True, hide_index=True)
        else: st.write("Belum ada video.")

    with col3:
        st.markdown("### ✅ **COMPLETED**")
        if not df[df['status'] == 'Done'].empty:
            st.dataframe(df[df['status'] == 'Done'][['concept', 'platform', 'target_week']], use_container_width=True, hide_index=True)
        else: st.write("Belum ada yang selesai.")

# --- HALAMAN 2: TAMBAH RENCANA ---
elif menu == "➕ Tambah Rencana":
    st.title("➕ Tambah Ide Konten Baru")
    with st.container(border=True):
        new_concept = st.text_input("Judul / Konsep Konten:")
        c_a, c_b, c_c = st.columns(3)
        with c_a: category = st.selectbox("Kategori:", ["FunArt", "FunGame", "FunSains", "FunDay"])
        with c_b: platform = st.selectbox("Format Video:", ["Long", "Short"])
        with c_c: target_week = st.number_input("Target Minggu Ke-:", min_value=1, max_value=52, value=1)
        
        if st.button("🚀 Simpan ke To-Do List", use_container_width=True):
            if new_concept:
                supabase.table("content_plans").insert({
                    "concept": new_concept, 
                    "category": category, 
                    "platform": platform, 
                    "target_week": int(target_week), 
                    "status": "Plan"
                }).execute()
                st.success(f"Berhasil ditambah untuk Minggu ke-{target_week}!")
                st.rerun()

# --- HALAMAN 3: EDITOR --- (SAMA SEPERTI SEBELUMNYA)
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
    else: st.info("Tambahkan rencana dulu!")

# --- HALAMAN 4: BOS --- (DENGAN KOLOM REVISI)
elif menu == "👑 Panel Review Bos":
    st.title("👑 Ruang Review Bos")
    df_r = df[df['status'] == 'Review']
    if not df_r.empty:
        for i, row in df_r.iterrows():
            with st.container(border=True):
                st.subheader(f"🎬 {row['concept']} ({row.get('platform', 'Long')})")
                url_v = f"{url}/storage/v1/object/public/production-videos/{row['concept'].replace(' ', '_')}.mp4"
                v_c1, v_c2, v_c3 = st.columns([1, 2, 1])
                with v_c2: st.video(url_v)
                
                catatan = st.text_area("Catatan Revisi:", key=f"rev_{i}")
                c1, c2, c3 = st.columns(3)
                if c1.button("✅ APPROVE", key=f"a_{i}", use_container_width=True):
                    supabase.table("content_plans").update({"status": "Done"}).eq("concept", row['concept']).execute()
                    st.rerun()
                if c2.button("✍️ REVISI", key=f"r_{i}", use_container_width=True):
                    st.warning(f"Revisi: {catatan}")
                if c3.button("🗑️ HAPUS VIDEO", key=f"d_{i}", use_container_width=True):
                    supabase.storage.from_("production-videos").remove([f"{row['concept'].replace(' ', '_')}.mp4"])
                    supabase.table("content_plans").update({"status": "Plan"}).eq("concept", row['concept']).execute()
                    st.rerun()
