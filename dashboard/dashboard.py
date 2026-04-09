import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime

st.set_page_config(
    layout="wide"
)

# Load Data


def load_data():
    df = pd.read_csv("all_data.csv")
    datetime_cols = [
        "order_purchase_timestamp", "order_approved_at",
        "order_delivered_carrier_date", "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]
    for col in datetime_cols:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    df["order_month_year"] = df["order_purchase_timestamp"].dt.to_period(
        "M").astype(str)
    days_order = ["Monday", "Tuesday", "Wednesday",
                  "Thursday", "Friday", "Saturday", "Sunday"]
    df["purchase_day"] = pd.Categorical(
        df["purchase_day"], categories=days_order, ordered=True)
    return df


df = load_data()

# Sidebar
st.sidebar.title("E-Commerce Dashboard")
st.sidebar.markdown("**Brazilian E-Commerce — Olist Dataset**")
st.sidebar.markdown("---")

min_date = df["order_purchase_timestamp"].min().date()
max_date = datetime.date(2018, 8, 31)

st.sidebar.markdown("## Filter Tanggal")
start_date = st.sidebar.date_input(
    "Tanggal Mulai:",
    value=min_date,
    min_value=min_date,
    max_value=max_date
)
end_date = st.sidebar.date_input(
    "Tanggal Akhir:",
    value=max_date,
    min_value=min_date,
    max_value=max_date
)

if start_date > end_date:
    st.sidebar.error(
        "Tanggal mulai tidak boleh lebih besar dari tanggal akhir!")

st.sidebar.markdown("---")
st.sidebar.markdown("Dibuat oleh: **Muchlis Ar Wicaksana**")
st.sidebar.markdown("ID: CDCC009D6Y2743")

# Filter
mask = (
    (df["order_purchase_timestamp"].dt.date >= start_date) &
    (df["order_purchase_timestamp"].dt.date <= end_date)
)
filtered = df[mask].copy()

# Header
st.title("Brazilian E-Commerce Analytics Dashboard")
st.caption(
    f"Periode: {start_date} s/d {end_date}")
st.markdown("---")

# Metric KPI
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Revenue", f"R$ {filtered['payment_value'].sum():,.0f}")
c2.metric("Total Orders", f"{filtered['order_id'].nunique():,}")
c3.metric("Avg Review Score", f"{filtered['review_score'].mean():.2f}")
c4.metric("Avg Delivery (Hari)",
          f"{filtered['delivery_time_days'].mean():.1f}")
avg_val = filtered.groupby("order_id")["payment_value"].sum().mean()
c5.metric("Avg Order Value", f"R$ {avg_val:.0f}")

st.markdown("---")

# Revenue per Bulan
st.subheader("Performa Penjualan & Revenue per Bulan")

monthly_rev = (
    filtered
    .groupby("order_month_year")["payment_value"]
    .sum()
    .reset_index()
    .sort_values("order_month_year")
)

fig1, ax1 = plt.subplots(figsize=(14, 4))
ax1.plot(
    monthly_rev["order_month_year"],
    monthly_rev["payment_value"],
    marker="o", linewidth=2.5, color="#FF9F9F", markersize=7
)
ax1.fill_between(range(len(monthly_rev)),
                 monthly_rev["payment_value"], alpha=0.15, color="#FF9F9F")
ax1.set_xticks(range(len(monthly_rev)))
ax1.set_xticklabels(monthly_rev["order_month_year"], rotation=45, ha="right")
ax1.set_title("Total Revenue Penjualan per Bulan",
              fontsize=14, fontweight="bold")
ax1.set_xlabel("Bulan")
ax1.set_ylabel("Total Revenue (R$)")
st.pyplot(fig1)
st.info('Insight : Terdapat peningkatan pesat revenue hingga titik tertinggi di bulan November 2017, dan performa tersebut relatif stabil sepanjang tahun 2018.')

st.markdown('---')

# Hubungan Pengiriman dan Review Score
st.subheader('Pengaruh Lama Pengiriman terhadap Review Score')
avg_delivery_by_score = (filtered.groupby('review_score')[
                         'delivery_time_days'].mean().reset_index())

col_a, col_b = st.columns(2)
with col_a:
    fig2, ax2 = plt.subplots(figsize=(7, 4))
    bar_colors = ["#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#FF9F9F"]
    bars = ax2.bar(
        avg_delivery_by_score['review_score'].astype(str),
        avg_delivery_by_score['delivery_time_days'],
        color=bar_colors
    )
    ax2.set_title('Rata-rata Lama Pengiriman per Review Score',
                  fontsize=12, fontweight='bold')
    ax2.set_xlabel("Review Score (Bintang)")
    ax2.set_ylabel('Rata-rata Hari Pengiriman')
    st.pyplot(fig2)

with col_b:
    review_dist = filtered['review_score'].value_counts().sort_index()
    fig3, ax3 = plt.subplots(figsize=(7, 4))
    ax3.pie(review_dist.values, labels=[
            f"★ {s}"for s in review_dist.index], autopct='%1.1f%%')
    ax3.set_title('Distribusi Review Score', fontsize=12, fontweight='bold')
    st.pyplot(fig3)
st.info('Insight : Keterlambatan pengiriman berbanding lurus dengan kepuasan. Rating bintang 1 rata-rata mengalami waktu pengiriman sampai 20 hari, dan pelanggan yang memberikan bintang 5 rata-rata mengalami waktu pengiriman 10 hari atau kurang.')

st.markdown('---')

# Heatmap aktivitas transaksi pelanggan
st.subheader('Kapan Pelanggan Paling Aktif Melakukan Transaksi ?')
days_order = ['Monday', 'Tuesday', 'Wednesday',
              'Thursday', 'Friday', 'Saturday', 'Sunday']
heatmap_data = filtered.groupby(
    ['purchase_day', 'purchase_hour']).size().unstack(fill_value=0)
fig4, ax4 = plt.subplots(figsize=(16, 5))
sns.heatmap(
    heatmap_data,
    cmap='YlOrRd',
    annot=False,
    ax=ax4,
)
ax4.set_title("Heatmap Aktivitas Transaksi Pelanggan (Hari vs Jam)",
              fontsize=14, fontweight='bold')
ax4.set_xlabel('Jam Pembelian (0-23)')
ax4.set_ylabel('Hari Pembelian')
st.pyplot(fig4)

col_c, col_d = st.columns(2)
with col_c:
    orders_by_day = filtered.groupby(
        'purchase_day', observed=True).size().reset_index(name='count')
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    bar_colors_day = [
        '#FF9F9F' if d in weekdays else '#D3D3D3' for d in orders_by_day['purchase_day']]
    fig5, ax5 = plt.subplots(figsize=(7, 3))
    ax5.bar(orders_by_day['purchase_day'],
            orders_by_day['count'], color=bar_colors_day)
    ax5.set_title('Total Transaksi per Hari', fontsize=12, fontweight='bold')
    ax5.set_xlabel('Hari')
    ax5.set_ylabel('Jumlah Transaksi')
    ax5.set_xticklabels(orders_by_day['purchase_day'], rotation=25)
    st.pyplot(fig5)

with col_d:
    orders_by_hour = filtered.groupby(
        'purchase_hour').size().reset_index(name='count')
    peak_mask = orders_by_hour['purchase_hour'].between(
        10, 16) | orders_by_hour['purchase_hour'].between(20, 22)
    bar_colors_hour = ["#FF9F9F" if p else '#D3D3D3' for p in peak_mask]
    fig6, ax6 = plt.subplots(figsize=(7, 3))
    ax6.bar(orders_by_hour['purchase_hour'],
            orders_by_hour['count'], color=bar_colors_hour)
    ax6.set_title('Total Transaksi per Jam', fontsize=12, fontweight='bold')
    ax6.set_xlabel('Jam')
    ax6.set_ylabel('Jumlah Transaksi')
    ax6.set_xticks(range(0, 24))
    st.pyplot(fig6)
st.info('Mayoritas aktivitas transaksi berpusat pada hari senin hingga jumat selama jam 10.00 - 16.00 dan malah hari jam 20.00 - 22.00, ini menandakan bahwa konsumen lebih suka belanja di sela sela aktivitas mereka, bukan di akhir pekan.')

st.markdown('---')

# Cicilan untuk nominal besar
st.subheader('Apakah Pelanggan Cenderung Mencicil untuk Nominal Besar ?')

payments_valid = filtered[filtered['payment_installments'] > 0].copy()
payments_valid['is_installment'] = payments_valid['payment_installments'].apply(
    lambda x: 'Cicilan (>1x)' if x > 1 else 'Lunas (1x)')

col_e, col_f = st.columns(2)
with col_e:
    fig7, ax7 = plt.subplots(figsize=(7, 4))
    sns.boxplot(
        data=payments_valid,
        x='is_installment', 
        y='payment_value',
        hue='is_installment',
        palette={'Lunas (1x)': '#6495ED', 'Cicilan (>1x)': "#FF9F9F"},
        showfliers=False,
        legend=False,
    )
    ax7.set_title('Nilai Transaksi: Bayar Lunas vs Cicilan',
                  fontsize=12, fontweight='bold')
    ax7.set_xlabel('Metode Pembayaran')
    ax7.set_ylabel('Nilai Pembayaran (R$)')
    st.pyplot(fig7)

with col_f:
    st.markdown('**Ringkasan Statistik Nilai Transaksi**')
    summary = payments_valid.groupby('is_installment')['payment_value'].agg(
        jumlah='count',
        rata_rata='mean',
        median='median',
        std='std'
    ).round(2)
    summary.index.name = 'Metode'
    st.dataframe(summary, use_container_width=True)
    avg_inst = payments_valid[payments_valid['is_installment'] == 'Cicilan (>1x)']['payment_installments'].mean()
    st.metric('Rata-rata Jumalah Cicilan', f'{avg_inst:.1f}x')
    
st.info('Pelanggan memiliki keccenderungan yang sangat jelas untuk memanfaatkan fitur installments ketika mereka membeli barang dengan nominal yang tinggi. Rata-rata pemayaran pada transaksi installments jauh lebih tinggi dibandingkan transaksi yang dibayar lunas langusng')

st.markdown('---')

st.subheader('Analisis Tambahan')
col_g, col_h, col_i = st.columns([1, 2, 1])
with col_h:
    payments_types = filtered['payment_type'].value_counts()
    fig8, ax8 = plt.subplots(figsize=(5, 5))
    ax8.pie(
        payments_types.values,
        autopct='%1.1f%%',
    )
    ax8.legend(payments_types.index, bbox_to_anchor=(1, 1))
    ax8.set_title('Presentase Tipe Pembayaran', fontsize=12, fontweight='bold')
    st.pyplot(fig8)

st.info('mayoritas pelanggan sangat bergantung pada penggunaan credit card sebagai metode transaksi utama. Hal ini menandakan bahwa perusahaan harus menjadikan credit card sebagai prioritas operasional agar tidak terjadi failed transaction. Selain itu, integrasi pembayaran Boleto tetap harus dipertahankan karena berhasil menjangkau segemen pelanggan yang mungkin belum memilii akses perbankan digital.')

st.markdown('---')
st.caption('Brazilian E-Commerce Dashboard | Muchlis Ar Wicaksana')
