
import streamlit as st
import pandas as pd

# Konfigurasi halaman
st.set_page_config(
    page_title="Dashboard Penjualan",
    page_icon="📊",
    layout="wide"
)

# Data penjualan
data = {
    "Produk": [
        "Laptop", "Mouse", "Keyboard", "Monitor",
        "Headset", "Webcam", "Laptop", "Mouse",
        "Monitor", "Keyboard"
    ],
    "Kategori": [
        "Komputer", "Aksesoris", "Aksesoris", "Komputer",
        "Aksesoris", "Aksesoris", "Komputer", "Aksesoris",
        "Komputer", "Aksesoris"
    ],
    "Jumlah": [5, 20, 15, 8, 12, 10, 7, 25, 6, 18],
    "Harga": [
        10000000, 150000, 300000, 2500000,
        500000, 750000, 10000000, 150000,
        2500000, 300000
    ]
}

df = pd.DataFrame(data)
df["Total"] = df["Jumlah"] * df["Harga"]

# Judul dashboard
st.title("📊 Dashboard Penjualan")
st.caption("Sistem Informasi Analisis Data Penjualan")

# Sidebar filter
st.sidebar.title("Filter Data")

kategori = st.sidebar.multiselect(
    "Pilih Kategori",
    options=df["Kategori"].unique(),
    default=df["Kategori"].unique()
)

# Filter data
filtered_df = df[df["Kategori"].isin(kategori)]

# Informasi utama
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Jumlah Transaksi", len(filtered_df))

with col2:
    st.metric("Total Barang", int(filtered_df["Jumlah"].sum()))

with col3:
    total = filtered_df["Total"].sum()
    st.metric("Total Penjualan", f"Rp {total:,.0f}")

st.divider()

# Grafik penjualan
st.subheader("📈 Grafik Penjualan Produk")

grafik = (
    filtered_df.groupby("Produk")["Total"]
    .sum()
    .sort_values(ascending=False)
)

st.bar_chart(grafik)

# Grafik kategori
st.subheader("📊 Penjualan Berdasarkan Kategori")

kategori_data = filtered_df.groupby("Kategori")["Total"].sum()

st.bar_chart(kategori_data)

# Tabel data
st.subheader("📋 Detail Data Penjualan")

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)

# Footer
st.divider()
st.caption("Dashboard dibuat menggunakan Python dan Streamlit")
