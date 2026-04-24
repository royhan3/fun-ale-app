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
    .revisi-card {
        background-color: rgba(255, 75, 75, 0.1);
        border: 1px solid #ff4b4b;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/video-playlist.png")
    st.title("Fun Ale Center")
    menu = st.radio("Navigasi", ["📊 Dashboard Utama", "➕ Tambah Rencana", "📤 Portal Editor", "👑 Panel Review Bos"])
    st.divider()
    st.caption("v3.1 | Clean Workflow")

# Ambil data terbaru
res = supabase.table("content_plans").select("*").execute()
df = pd.DataFrame(res.data) if res.data else pd.DataFrame(columns=["concept", "status", "notes", "platform", "target_week"])

# --- HALAMAN 1: DASHBOARD ---
if menu == "📊 Dashboard Utama":
    st.title("📊 Monitoring Produksi Fun Ale")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Rencana Baru", len(df[(df['status'] == 'Plan') & (df['notes'] == "")]))
    m2.metric("Perlu Revisi", len(df[(df['status'] == 'Plan') & (df['notes'] != "")]))
    m3.metric("Sedang Review", len(df[df['status'] == 'Review']))
    
    st.divider()
    
    # SEKARANG ADA 4 KOLOM
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown("### 🛠️ **TO-DO LIST**")
        # Hanya yang status Plan dan TIDAK ada catatan revisi
        df_new = df[(df['status'] == 'Plan') & ((df['notes'] == "") | (df['notes'].isna()))]
        if not df_new.empty:
            for i, row in df_new.iterrows():
                st.write(f"🔹 **{row['concept']}**")
                st.caption(f"{row.get('platform', 'Long')} | Week {row.get('target_week', '-')}")
                st.divider()
        else: st.write("Kosong")

    with c2:
        st.markdown("### ✍️ **REVISI LIST**")
        # Hanya yang status Plan dan ADA catatan revisi
        df_rev_todo = df[(df['status'] == 'Plan') & (df['notes'] != "") & (df['notes'].notna())]
        if not df_rev_todo.empty:
            for i, row in df_rev_todo.iterrows():
                st.markdown(f"""<div class='revisi-card'>
                    <b>{row['concept']}</b><br>
                    <small>💬 {row['notes']}</small>
                </div>""", unsafe_allow_html=True)
        else: st.write("Aman, gaada revisi! ✨")

    with c3:
        st.markdown("### ⏳ **WAITING**")
        df_wait = df[df['status'] == 'Review']
        if not df_wait.empty:
            st.dataframe(df_wait[['concept', 'platform']], use_container_width=True, hide_index=True)
        else: st.write("Kosong")

    with c4:
        st.markdown("### ✅ **DONE**")
        df_done = df[df['status'] == 'Done']
        if not df_done.empty:
            st.dataframe(df_done[['concept']], use_container_width=True, hide_index=True)
        else: st.write("Belum ada")

# --- HALAMAN 2: TAMBAH RENCANA --- (TETAP SAMA)
elif menu == "➕ Tambah Rencana":
    st.title("➕ Tambah Ide")
    with st.container(border=True):
        new_concept = st.text_input("Judul:")
        c_a, c_b, c_c = st.columns(3)
        with c_a: cat = st.selectbox("Kategori:", ["FunArt", "FunGame", "FunSains", "FunDay"])
        with c_b: plat = st.selectbox("Format:", ["Long", "Short"])
        with c_c: week = st.number_input("Minggu Ke-:", 1, 52, 1)
        if st.button("🚀 Simpan", use_container_width=True):
            if new_concept:
                supabase.table("content_plans").insert({"concept":new_concept, "category":cat, "platform":plat, "target_week":int(week), "status":"Plan", "notes":""}).execute()
                st.rerun()

# --- HALAMAN 3: PORTAL EDITOR ---
elif menu == "📤 Portal Editor":
    st.title("📤 Portal Upload")
    # Editor bisa pilih dari To-Do maupun Revisi List (semua yang statusnya Plan)
    df_u = df[df['status'] == 'Plan']
    if not df_u.empty:
        pilihan = st.selectbox("Pilih konten yang mau diupload:", df_u['concept'].tolist())
        video_file = st.file_uploader("Upload MP4:", type=["mp4", "mov"])
        if st.button("🚀 Kirim ke Bos", use_container_width=True):
            if video_file:
                path = f"{pilihan.replace(' ', '_')}.mp4"
                supabase.storage.from_("production-videos").upload(path, video_file.getvalue(), {"upsert":"true"})
                # Reset notes jadi kosong karena sudah diperbaiki
                supabase.table("content_plans").update({"status": "Review", "notes": ""}).eq("concept", pilihan).execute()
                st.success("Terkirim! Judul ini sekarang pindah ke Waiting Review.")
                st.rerun()
    else: st.info("Tidak ada konten yang perlu digarap.")

# --- HALAMAN 4: PANEL REVIEW BOS ---
elif menu == "👑 Panel Review Bos":
    st.title("👑 Ruang Review")
    df_r = df[df['status'] == 'Review']
    if not df_r.empty:
        for i, row in df_r.iterrows():
            with st.container(border=True):
                st.subheader(f"🎬 {row['concept']}")
                url_v = f"{url}/storage/v1/object/public/production-videos/{row['concept'].replace(' ', '_')}.mp4"
                v_c1, v_c2, v_c3 = st.columns([1, 2, 1])
                with v_c2: st.video(url_v)
                
                catatan = st.text_area("Catatan Revisi:", key=f"rev_{i}")
                c1, c2, c3 = st.columns(3)
                if c1.button("✅ APPROVE", key=f"a_{i}", use_container_width=True):
                    supabase.table("content_plans").update({"status": "Done", "notes": ""}).eq("concept", row['concept']).execute()
                    st.rerun()
                if c2.button("✍️ REVISI", key=f"r_{i}", use_container_width=True):
                    if catatan:
                        # Balikkan ke Plan dan isi notes-nya
                        supabase.table("content_plans").update({"status": "Plan", "notes": catatan}).eq("concept", row['concept']).execute()
                        st.rerun()
                    else: st.error("Isi catatan dulu!")
                if c3.button("🗑️ HAPUS", key=f"d_{i}", use_container_width=True):
                    supabase.storage.from_("production-videos").remove([f"{row['concept'].replace(' ', '_')}.mp4"])
                    supabase.table("content_plans").update({"status": "Plan", "notes": ""}).eq("concept", row['concept']).execute()
                    st.rerun()
