import streamlit as st
import pandas as pd
import datetime
import joblib
import os

# ==========================================
# 1. KONFIGURASI & CSS HALAMAN
# ==========================================
st.set_page_config(page_title="HVAC Predictor", page_icon="🏢", layout="wide")

st.markdown("""
<style>
    .metric-container { background-color: white; border-radius: 10px; padding: 20px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); text-align: center; margin-bottom: 15px;}
    .metric-value { font-size: 2.5rem; font-weight: bold; color: #1f77b4; }
    .metric-label { font-size: 1.2rem; color: #555; }
    .stButton>button { width: 100%; background-color: #4CAF50; color: white; font-weight: bold; border-radius: 5px; padding: 10px 24px; font-size: 18px; }
    .stButton>button:hover { background-color: #45a049; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. FUNGSI INTI (MODEL & DATA)
# ==========================================
@st.cache_resource
def load_model():
    try:
        return joblib.load('model_rico_final.pkl')
    except Exception as e:
        st.error(f"❌ Error model: {e}")
        return None

def process_time_index(df):
    """FUNGSI ANTI-GAGAL: Mencari kolom waktu dan mengubahnya menjadi format string persis seperti CSV."""
    df.columns = df.columns.str.strip()
    
    target_col = None
    for col in df.columns:
        if str(col).lower() in ['_time', 'time', 'waktu', 'date', 'timestamp', 'unnamed: 0']:
            target_col = col
            break
            
    if target_col is None:
        target_col = df.columns[0]

    try:
        df[target_col] = pd.to_datetime(df[target_col], errors='coerce')
        df = df.dropna(subset=[target_col])
        df.set_index(target_col, inplace=True)
        # Menjaga tipe indeks tetap DatetimeIndex agar line_chart bisa memvisualisasikannya
    except:
        pass
        
    return df

@st.cache_data
def get_local_data_fresh():
    csv_file = 'data_B.RTD6_Clean.csv'
    if os.path.exists(csv_file):
        try:
            df = pd.read_csv(csv_file)
            return process_time_index(df)
        except Exception as e:
            st.error(f"Gagal memuat {csv_file}: {e}")
            return None
    return None

def smart_hvac_controller(predicted_temp):
    if predicted_temp > 24.5: return "🔴 Matikan Pemanas (Mencegah Overheating)"
    elif predicted_temp < 20: return "🔵 Nyalakan Pemanas (Menjaga Kenyamanan)"
    else: return "🟢 Standby (Suhu Optimal)"

FITUR_AI = ['B.RTD6', 'WS1_Solar_radiation', 'WS1_Temperature', 'pid.SB47.setpoint', 
            'lag_temp_1', 'lag_temp_5', 'lag_temp_10', 'lag_temp_15', 'lag_temp_30']

# ==========================================
# 3. HEADER APLIKASI
# ==========================================
st.title("🏢 Smart Building HVAC Predictor")
st.markdown("Mensimulasikan sistem kontrol gedung pintar berbasis Machine Learning untuk memprediksi inersia termal 30 menit ke depan.")
st.divider()

model_hvac = load_model()
df_local = get_local_data_fresh()

# ==========================================
# 4. SISTEM TAB MENU
# ==========================================
tab1, tab2 = st.tabs([
    "🎛️ TAB 1: MODE EKSPLORASI (Manual & Upload CSV)", 
    "📊 TAB 2: MODE EVALUASI (Dataset B.RTD6 Asli)"
])

# ---------------------------------------------------------
# TAB 1: MODE EKSPLORASI
# ---------------------------------------------------------
with tab1:
    st.header("🎛️ Eksplorasi Data Bebas")
    mode_input = st.radio("Pilih Metode Input Data:", ["🕹️ Input Manual (Slider)", "📂 Upload CSV Custom"])
    st.markdown("---")

    col_input, col_output = st.columns([1, 1.5])
    
    if mode_input == "🕹️ Input Manual (Slider)":
        with col_input:
            st.info("Ketik langsung atau geser nilai sensor di bawah ini.")
            waktu_str = st.text_input("📝 Input Waktu Mandiri (Format: YYYY-MM-DD HH:MM)", value=datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
            
            temp_now = st.number_input(" Suhu Saat Ini (°C)", value=25.0, step=0.1)
            solar    = st.number_input(" Matahari (W/m²)", value=100.0, step=10.0)
            temp_out = st.number_input(" Suhu Luar (°C)", value=10.0, step=0.1)
            setpoint = st.number_input(" Setpoint (°C)", value=40.0, step=0.5)
            
            with st.expander("⚙️ Mode Lanjutan (Riwayat Suhu/Lags)"):
                stable_mode = st.checkbox("Asumsikan suhu historis stabil", value=True)
                if stable_mode:
                     lag_1 = lag_5 = lag_10 = lag_15 = lag_30 = temp_now
                else:
                    lag_1 = st.number_input("1m lalu", value=float(temp_now))
                    lag_5 = st.number_input("5m lalu", value=float(temp_now))
                    lag_10 = st.number_input("10m lalu", value=float(temp_now))
                    lag_15 = st.number_input("15m lalu", value=float(temp_now))
                    lag_30 = st.number_input("30m lalu", value=float(temp_now))

            btn_manual = st.button("🚀 PREDIKSI SUHU MANUAL", use_container_width=True)

        with col_output:
            if btn_manual and model_hvac:
                try:
                    waktu_sekarang = datetime.datetime.strptime(waktu_str, '%Y-%m-%d %H:%M')
                    input_df = pd.DataFrame([[temp_now, solar, temp_out, setpoint, lag_1, lag_5, lag_10, lag_15, lag_30]], columns=FITUR_AI)
                    prediksi_ai = model_hvac.predict(input_df)[0]
                    
                    st.success("✅ Prediksi Selesai!")
                    c1, c2 = st.columns(2)
                    c1.metric(f"Suhu Aktual ({waktu_sekarang.strftime('%H:%M')})", f"{temp_now:.2f} °C")
                    c2.metric("🔮 Tebakan AI (30m ke depan)", f"{prediksi_ai:.2f} °C", delta=f"{prediksi_ai - temp_now:.2f} °C", delta_color="inverse")
                    st.markdown(f"### 🤖 Tindakan HVAC Otomatis: {smart_hvac_controller(prediksi_ai)}")
                except ValueError:
                    st.error("❌ Format waktu salah! Pastikan formatnya YYYY-MM-DD HH:MM")

    else:
        uploaded_file = st.file_uploader("Upload File CSV Anda", type=['csv'])
        
        st.caption("📌 **Penting:** Pastikan file CSV Anda memiliki 9 fitur wajib berikut agar AI dapat bekerja:")
        st.code("B.RTD6, WS1_Solar_radiation, WS1_Temperature, pid.SB47.setpoint, lag_temp_1, lag_temp_5, lag_temp_10, lag_temp_15, lag_temp_30", language="text")
        
        if uploaded_file is not None:
            df_custom = pd.read_csv(uploaded_file)
            df_custom = process_time_index(df_custom)
            
            st.success("File CSV berhasil diupload!")
            
            pilihan_waktu = st.selectbox(
                "📝 Ketik atau Pilih Waktu Observasi dari CSV:", 
                options=df_custom.index,
                help="Klik kotak ini lalu langsung ketik jam/tanggal yang Anda cari."
            )
            
            current_data_custom = df_custom.loc[pilihan_waktu]
            
            if isinstance(current_data_custom, pd.DataFrame):
                current_data_custom = current_data_custom.iloc[0]
            
            st.info(f"📍 **Waktu Terpilih:** {pilihan_waktu}")
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Suhu", f"{current_data_custom.get('B.RTD6', 0):.2f} °C")
            c2.metric("Matahari", f"{current_data_custom.get('WS1_Solar_radiation', 0):.2f} W/m²")
            c3.metric("Suhu Luar", f"{current_data_custom.get('WS1_Temperature', 0):.2f} °C")
            c4.metric("Setpoint", f"{current_data_custom.get('pid.SB47.setpoint', 0)} °C")

            if st.button(" PREDIKSI DARI CSV UPLOAD", use_container_width=True) and model_hvac:
                try:
                    input_df = pd.DataFrame([current_data_custom[FITUR_AI].values], columns=FITUR_AI)
                    prediksi_ai = model_hvac.predict(input_df)[0]
                    fakta = current_data_custom.get('target', "Tidak ada data target")
                    
                    st.markdown("---")
                    col_a, col_b = st.columns(2)
                    col_a.metric(" Tebakan AI (30m)", f"{prediksi_ai:.2f} °C")
                    if isinstance(fakta, (int, float)):
                        col_b.metric(" Fakta Lapangan", f"{fakta:.2f} °C", delta=f"Error: {abs(prediksi_ai - fakta):.4f} °C", delta_color="inverse")
                    else:
                        col_b.metric(" Fakta Lapangan", "N/A")
                        
                    st.markdown(f"### 🤖 Tindakan HVAC Otomatis: {smart_hvac_controller(prediksi_ai)}")
                except KeyError:
                    st.error("❌ File CSV yang diupload tidak memiliki 9 kolom fitur yang dibutuhkan model!")
            
            # --- PERBAIKAN GRAFIK TAB 1 ---
            st.markdown("---")
            st.markdown("### 📈 Visualisasi Tren (Dataset CSV)")
            baris_terakhir = 500
            df_plot_custom = df_custom.tail(baris_terakhir).copy()
            if 'B.RTD6' in df_plot_custom.columns:
                # Trik agar grafik muncul: ubah sementara index teks menjadi datetime
                df_plot_custom.index = pd.to_datetime(df_plot_custom.index, errors='coerce')
                st.line_chart(df_plot_custom['B.RTD6'], color="#1f77b4", use_container_width=True)

# ---------------------------------------------------------
# TAB 2: MODE EVALUASI (Otomatis Baca CSV di VS Code)
# ---------------------------------------------------------
with tab2:
    st.header("📊 Validasi Model pada Dataset Asli (B.RTD6)")
    st.write("Sistem otomatis membaca file `data_B.RTD6_Clean.csv` dari folder proyek Anda.")
    
    if df_local is not None:
        
        pilihan_waktu_asli = st.selectbox(
            "📝 Ketik atau Pilih Waktu Observasi (Dataset Asli):", 
            options=df_local.index,
            index=len(df_local)-100 if len(df_local) > 100 else 0,
            help="Klik kotak ini lalu langsung ketik jam/tanggal yang Anda cari."
        )
        
        current_data = df_local.loc[pilihan_waktu_asli]
        
        if isinstance(current_data, pd.DataFrame):
            current_data = current_data.iloc[0]
            
        st.info(f"📍 **Sistem Terkunci Pada Waktu:** {pilihan_waktu_asli}")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Suhu Ruangan", f"{current_data.get('B.RTD6', 0):.2f} °C")
        c2.metric("Intensitas Matahari", f"{current_data.get('WS1_Solar_radiation', 0):.2f} W/m²")
        c3.metric("Suhu Luar", f"{current_data.get('WS1_Temperature', 0):.2f} °C")
        c4.metric("Setpoint", f"{current_data.get('pid.SB47.setpoint', 0)} °C")
        
        if st.button(" JALANKAN PREDIKSI (Otomatis)", use_container_width=True):
            if model_hvac:
                try:
                    input_df = pd.DataFrame([current_data[FITUR_AI].values], columns=FITUR_AI)
                    prediksi_ai = model_hvac.predict(input_df)[0]
                    fakta = current_data.get('target', 0) 
                    
                    st.markdown("---")
                    col_a, col_b, col_c = st.columns(3)
                    col_a.metric(" Tebakan AI (30m)", f"{prediksi_ai:.2f} °C")
                    col_b.metric(" Fakta Sebenarnya", f"{fakta:.2f} °C")
                    col_c.metric(" Selisih Error", f"{abs(prediksi_ai - fakta):.4f} °C", delta="-Akurasi Maksimal", delta_color="inverse")
                    
                    st.markdown(f"###  Tindakan HVAC Otomatis: {smart_hvac_controller(prediksi_ai)}")
                except Exception as e:
                    st.error(f"Error prediksi dataset: {e}")
        
       