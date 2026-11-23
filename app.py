
import streamlit as st
import pandas as pd
import io
from pathlib import Path

# ==========================================
# KONFIGURASI HALAMAN
# ==========================================

st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# MEMUAT CSS
# ==========================================

css_path = Path(__file__).parent / "assets" / "style.css"

if css_path.exists():
    css = css_path.read_text(encoding="utf-8")
    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True
    )

# ==========================================
# DATA PENJUALAN BAWAAN
# ==========================================

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

# ==========================================
# SIDEBAR NAVIGASI
# ==========================================

st.sidebar.title("📊 Sales Dashboard")
st.sidebar.caption("Management & Analytics")
st.sidebar.divider()

menu = st.sidebar.radio(
    "MENU NAVIGASI",
    [
        "Overview",
        "Data Penjualan",
        "Analisis Penjualan",
        "Tentang Aplikasi"
    ]
)

st.sidebar.divider()

# ==========================================
# UPLOAD CSV / EXCEL
# ==========================================

st.sidebar.subheader("📂 Upload Data")

uploaded_file = st.sidebar.file_uploader(
    "Pilih file CSV atau Excel",
    type=["csv", "xlsx"],
    key="upload_data"
)

if uploaded_file is not None:
    try:
        if uploaded_file.name.lower().endswith(".csv"):
            upload_df = pd.read_csv(uploaded_file)
        else:
            upload_df = pd.read_excel(uploaded_file)

        kolom_wajib = [
            "Produk", "Kategori", "Jumlah", "Harga"
        ]

        if not all(kolom in upload_df.columns for kolom in kolom_wajib):
            st.sidebar.error(
                "Kolom wajib: Produk, Kategori, Jumlah, Harga."
            )
        else:
            upload_df = upload_df[kolom_wajib].copy()

            upload_df["Jumlah"] = pd.to_numeric(
                upload_df["Jumlah"], errors="coerce"
            )
            upload_df["Harga"] = pd.to_numeric(
                upload_df["Harga"], errors="coerce"
            )

            upload_df = upload_df.dropna(
                subset=kolom_wajib
            )

            upload_df = upload_df[
                (upload_df["Jumlah"] >= 0) &
                (upload_df["Harga"] >= 0)
            ]

            if not upload_df.empty:
                df = pd.concat(
                    [df, upload_df],
                    ignore_index=True
                )
                st.sidebar.success(
                    f"{len(upload_df)} data berhasil ditambahkan."
                )
            else:
                st.sidebar.warning("Tidak ada data valid.")

    except Exception as e:
        st.sidebar.error(f"Gagal membaca file: {e}")

# ==========================================
# PENGOLAHAN DATA
# ==========================================

df["Total"] = df["Jumlah"] * df["Harga"]

# ==========================================
# FILTER DATA
# ==========================================

st.sidebar.divider()
st.sidebar.subheader("Filter Data")

kategori = st.sidebar.multiselect(
    "Kategori Produk",
    options=sorted(df["Kategori"].unique()),
    default=sorted(df["Kategori"].unique())
)

harga_min = int(df["Harga"].min())
harga_max = int(df["Harga"].max())

rentang_harga = st.sidebar.slider(
    "Rentang Harga",
    min_value=harga_min,
    max_value=harga_max,
    value=(harga_min, harga_max)
)

filtered_df = df[
    (df["Kategori"].isin(kategori)) &
    (df["Harga"].between(
        rentang_harga[0],
        rentang_harga[1]
    ))
].copy()

# ==========================================
# EXPORT CSV / EXCEL
# ==========================================

st.sidebar.divider()
st.sidebar.subheader("📥 Export Data")

csv_data = filtered_df.to_csv(
    index=False
).encode("utf-8-sig")

st.sidebar.download_button(
    label="Download CSV",
    data=csv_data,
    file_name="laporan_penjualan.csv",
    mime="text/csv",
    use_container_width=True
)

excel_buffer = io.BytesIO()

with pd.ExcelWriter(
    excel_buffer,
    engine="openpyxl"
) as writer:
    filtered_df.to_excel(
        writer,
        index=False,
        sheet_name="Data Penjualan"
    )

st.sidebar.download_button(
    label="Download Excel",
    data=excel_buffer.getvalue(),
    file_name="laporan_penjualan.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True
)

st.sidebar.divider()
st.sidebar.caption("Python • Streamlit")
st.sidebar.caption("© 2026 Sales Dashboard")

# ==========================================
# MENU 1: OVERVIEW
# ==========================================


if menu == "Overview":

    st.title("Dashboard Overview")
    st.caption("Pantau performa dan ringkasan penjualan secara keseluruhan.")

    # ===== STATISTIK UTAMA =====
    total_transaksi = len(filtered_df)
    total_barang = filtered_df["Jumlah"].sum()
    total_penjualan = filtered_df["Total"].sum()
    total_produk = filtered_df["Produk"].nunique()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="🧾 Total Transaksi",
            value=f"{total_transaksi:,}"
        )

    with col2:
        st.metric(
            label="📦 Total Barang Terjual",
            value=f"{total_barang:,.0f}"
        )

    with col3:
        st.metric(
            label="💰 Total Penjualan",
            value=f"Rp {total_penjualan:,.0f}"
        )

    with col4:
        st.metric(
            label="🏷️ Jenis Produk",
            value=f"{total_produk:,}"
        )

    st.divider()

    # ===== GRAFIK PENJUALAN =====
    st.subheader("Visualisasi Penjualan")
    st.caption("Perbandingan pendapatan berdasarkan produk dan kategori.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Penjualan Berdasarkan Produk**")

        grafik_produk = (
            filtered_df.groupby("Produk")["Total"]
            .sum()
            .sort_values(ascending=False)
        )

        if not grafik_produk.empty:
            st.bar_chart(
                grafik_produk,
                color="#3B82F6"
            )
        else:
            st.info("Belum ada data penjualan produk.")

    with col2:
        st.markdown("**Penjualan Berdasarkan Kategori**")

        grafik_kategori = (
            filtered_df.groupby("Kategori")["Total"]
            .sum()
            .sort_values(ascending=False)
        )

        if not grafik_kategori.empty:
            st.bar_chart(
                grafik_kategori,
                color="#14B8A6"
            )
        else:
            st.info("Belum ada data penjualan kategori.")

    st.divider()

    # ===== RINGKASAN PRODUK =====
    st.subheader("Ringkasan Produk")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Produk dengan Penjualan Tertinggi**")

        if not grafik_produk.empty:
            produk_tertinggi = grafik_produk.idxmax()
            nilai_tertinggi = grafik_produk.max()

            st.metric(
                label=produk_tertinggi,
                value=f"Rp {nilai_tertinggi:,.0f}"
            )
        else:
            st.info("Belum tersedia data produk.")

    with col2:
        st.markdown("**Kategori dengan Penjualan Tertinggi**")

        if not grafik_kategori.empty:
            kategori_tertinggi = grafik_kategori.idxmax()
            nilai_kategori = grafik_kategori.max()

            st.metric(
                label=kategori_tertinggi,
                value=f"Rp {nilai_kategori:,.0f}"
            )
        else:
            st.info("Belum tersedia data kategori.")

    st.divider()

    # ===== DATA PENJUALAN =====
    st.subheader("Data Penjualan Terbaru")
    st.caption(f"Menampilkan {len(filtered_df)} data berdasarkan filter aktif.")

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )


# ==========================================
# MENU 2: DATA PENJUALAN
# ==========================================

elif menu == "Data Penjualan":

    st.title("Data Penjualan")
    st.caption("Informasi lengkap transaksi penjualan")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Jumlah Data", f"{len(filtered_df):,}")

    with col2:
        st.metric(
            "Total Pendapatan",
            f"Rp {filtered_df['Total'].sum():,.0f}"
        )

    st.divider()

    pencarian = st.text_input(
        "🔍 Cari Produk",
        placeholder="Masukkan nama produk..."
    )

    hasil = filtered_df[
        filtered_df["Produk"].str.contains(
            pencarian,
            case=False,
            na=False
        )
    ]

    st.dataframe(
        hasil,
        use_container_width=True,
        hide_index=True
    )

    st.caption(f"Menampilkan {len(hasil)} data")

# ==========================================
# MENU 3: ANALISIS PENJUALAN
# ==========================================


elif menu == "Analisis Penjualan":

    st.title("Analisis Penjualan")
    st.caption("Analisis performa produk dan kategori")

    if filtered_df.empty:

        st.warning("Tidak ada data untuk dianalisis.")

    else:

        # ===== PERHITUNGAN ANALISIS =====
        produk_terlaris = (
            filtered_df.groupby("Produk")["Jumlah"]
            .sum()
            .sort_values(ascending=False)
        )

        produk_pendapatan = (
            filtered_df.groupby("Produk")["Total"]
            .sum()
            .sort_values(ascending=False)
        )

        produk_tertinggi = produk_terlaris.idxmax()
        jumlah_tertinggi = produk_terlaris.max()

        pendapatan_tertinggi = produk_pendapatan.max()

        # ===== RINGKASAN STATISTIK =====
        st.subheader("Ringkasan Performa")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Produk Terlaris",
                produk_tertinggi
            )

        with col2:
            st.metric(
                "Jumlah Terjual",
                f"{jumlah_tertinggi:,.0f}"
            )

        with col3:
            st.metric(
                "Pendapatan Tertinggi",
                f"Rp {pendapatan_tertinggi:,.0f}"
            )

        st.divider()

        # ===== GRAFIK ANALISIS =====
        st.subheader("Visualisasi Performa Produk")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Produk Terlaris**")

            st.bar_chart(
                produk_terlaris,
                color="#3B82F6"
            )

        with col2:
            st.markdown("**Pendapatan Produk**")

            st.bar_chart(
                produk_pendapatan,
                color="#14B8A6"
            )

        st.divider()

        # ===== RINGKASAN PRODUK =====
        st.subheader("Ringkasan Performa Produk")

        analisis = (
            filtered_df.groupby("Produk")
            .agg(
                Total_Terjual=("Jumlah", "sum"),
                Total_Pendapatan=("Total", "sum")
            )
            .sort_values(
                by="Total_Pendapatan",
                ascending=False
            )
        )

        analisis.index.name = "Nama Produk"

        st.dataframe(
            analisis,
            use_container_width=True
        )


# ==========================================
# MENU 4: TENTANG APLIKASI
# ==========================================


elif menu == "Tentang Aplikasi":

    st.title("Tentang Aplikasi")
    st.caption("Informasi mengenai Sales Dashboard")

    # ===== DESKRIPSI APLIKASI =====
    st.subheader("📊 Sales Dashboard")

    st.write(
        """
        Sales Dashboard merupakan aplikasi berbasis web
        yang dirancang untuk membantu pengguna dalam
        mengelola, melihat, dan menganalisis data penjualan.

        Aplikasi ini menyediakan informasi berupa ringkasan
        statistik, visualisasi grafik, serta pengolahan data
        penjualan secara interaktif.
        """
    )

    st.divider()

    # ===== TEKNOLOGI =====
    st.subheader("🛠️ Teknologi yang Digunakan")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Python**")
        st.caption("Bahasa pemrograman utama aplikasi.")

    with col2:
        st.markdown("**Streamlit**")
        st.caption("Framework untuk membangun dashboard interaktif.")

    with col3:
        st.markdown("**Pandas**")
        st.caption("Library untuk pengolahan dan analisis data.")

    st.divider()

    # ===== FITUR APLIKASI =====
    st.subheader("✨ Fitur Aplikasi")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Pengelolaan Data**
        - Upload data CSV dan Excel.
        - Filter kategori dan harga produk.
        - Pencarian data penjualan.
        """)

    with col2:
        st.markdown("""
        **Analisis dan Laporan**
        - Ringkasan statistik penjualan.
        - Visualisasi grafik penjualan.
        - Analisis performa produk.
        - Export data CSV dan Excel.
        """)

    st.divider()

    # ===== INFORMASI APLIKASI =====
    st.subheader("Informasi Aplikasi")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Versi Aplikasi", "1.0.0")

    with col2:
        st.metric("Framework Utama", "Streamlit")

    st.caption("© 2026 Sales Dashboard | Developed with Python & Streamlit")

    st.info("Versi aplikasi: 1.0.0")
