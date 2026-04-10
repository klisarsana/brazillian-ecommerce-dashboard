import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Config Halaman Dashboard
st.set_page_config(
    page_title='Brazilian E-Commerce Dashboard',
    layout='wide'
)

# Fungsi untuk menyiapkan dataframe

@st.cache_data
def create_monthly_sales_df(df):
    monthly_sales_df = df.groupby(by='purchase_month').agg({
        'order_id': 'nunique',
        'payment_value': 'sum'
    }).reset_index()
    monthly_sales_df.rename(columns={
        'order_id': 'order_count',
        'payment_value': 'revenue'
    }, inplace=True)
    return monthly_sales_df


def create_delivery_review_df(df):
    delivery_review_df = df.groupby('review_score').agg({
        'delivery_time_days': 'mean'
    }).reset_index()
    return delivery_review_df


def create_day_hour_df(df):
    day_hour_df = df.groupby(['purchase_day', 'purchase_hour']).agg({
        'order_id': 'nunique'
    }).reset_index()
    return day_hour_df


def create_installments_trend_df(df):
    # Membuat binning lagi agar reaktif terhadap filter
    df['payment_category'] = pd.qcut(df['payment_value'], q=3, labels=[
                                     'Low', 'Medium', 'High'])
    installments_trend_df = df.groupby('payment_category', observed=True).agg({
        'payment_installments': 'mean'
    }).reset_index()
    return installments_trend_df


def create_rfm_df(df):
    recent_date = df['order_purchase_timestamp'].max() + pd.Timedelta(days=1)
    rfm_df = df.groupby('customer_id').agg({
        'order_purchase_timestamp': lambda x: (recent_date - x.max()).days,
        'order_id': 'nunique',
        'payment_value': 'sum'
    }).reset_index()
    rfm_df.columns = ['customer_id', 'recency', 'frequency', 'monetary']
    
    # Memangkas ID Pelanggan (ambil 5 karakter terakhir) agar rapih di dashboard
    rfm_df['customer_id'] = rfm_df['customer_id'].str[:5]
    return rfm_df


def create_state_orders_df(df):
    state_orders_df = df.groupby(
        'customer_state').order_id.nunique().reset_index()
    state_orders_df.rename(columns={
        'order_id': 'total_orders'
    }, inplace=True)
    return state_orders_df


# Load Data
all_df = pd.read_csv('all_df.csv')
all_df['order_purchase_timestamp'] = pd.to_datetime(
    all_df['order_purchase_timestamp'])

# Dataframe untuk visualisasi
monthly_sales_df = create_monthly_sales_df(all_df)
delivery_review_df = create_delivery_review_df(all_df)
day_hour_df = create_day_hour_df(all_df)
installments_df = create_installments_trend_df(all_df)
rfm_df = create_rfm_df(all_df)
state_df = create_state_orders_df(all_df)

# Membuat Sidebar
with st.sidebar:
    st.title('Brazilian E-Commerce Dashboard')
    st.markdown('---')
    
    # Filter Tanggal
    min_date = all_df['order_purchase_timestamp'].min()
    max_date = all_df['order_purchase_timestamp'].max()
    
    start_date = st.date_input(
    "Tanggal Mulai:",
    value=min_date,
    min_value=min_date,
    max_value=max_date
    )
    
    end_date = st.date_input(
    "Tanggal Akhir:",
    value=max_date,
    min_value=min_date,
    max_value=max_date
    )
    
    st.markdown('---')
    st.markdown('**Muchlis Ar Wicaksana**')
    st.markdown('**CDCC009D6Y2743**')

# Filter Data Berdasarkan input tanggal
main_df = all_df[(all_df['order_purchase_timestamp'] >= str(start_date)) &
                 (all_df['order_purchase_timestamp'] <= str(end_date))]

# Main Dashboard
st.header('Brazilian E-Commerce Dashboard')
st.caption(f'Periode: {start_date} s/d {end_date}')
st.markdown('---')

# Metric KPI
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_orders = all_df.order_id.nunique()
    st.metric("Total Orders", value=total_orders)

with col2:
    total_revenue = all_df.payment_value.sum()
    st.metric('Total Revenue', value=f'R$ {total_revenue:,.2f}')

with col3:
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    st.metric('Avg Order Value (AOV)', value=f'R$ {avg_order_value:,.2f}')

with col4:
    avg_review_score = round(main_df.review_score.mean(), 2)
    st.metric('Avg Review Score', value=f'{avg_review_score} / 5')

with col5:
    avg_delivery_time = round(all_df.delivery_time_days.mean(), 1)
    st.metric('Avg Delivery Time', value=f'{avg_delivery_time} Days')

st.markdown('---')

# Performa penjualan (Revenue)
st.subheader('Performa Penjualan & Revenue per Bulan')
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    monthly_sales_df['purchase_month'],
    monthly_sales_df['revenue'],
    marker='o',
    color='#ff4b4b'
)
plt.xticks(rotation=45)
st.pyplot(fig)

st.markdown('---')

# Analisis Review Score & Installment (cicilan)
col_left, col_right = st.columns(2)
with col_left:
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        x='review_score',
        y='delivery_time_days',
        data=delivery_review_df,
        palette=['#d3d3d3', '#d3d3d3', '#d3d3d3', '#d3d3d3', '#ff4b4b'],
        ax=ax
    )
    ax.set_title('Pengaruh Lama Pengiriman terhadap Review Score', fontsize=16, fontweight='bold')
    ax.set_xlabel('Review Score (Bintang)')
    ax.set_ylabel('Rata-rata Waktu Pengiriman (Hari)')
    st.pyplot(fig)

with col_right:
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        x='payment_category',
        y='payment_installments',
        data=installments_df,
        palette=['#d3d3d3', '#d3d3d3', '#ff4b4b'],
        ax=ax
    )
    ax.set_title('Rata-rata Jumlah Cicilan Berdasarkan Kategori Belanja (Binning)', fontsize=16, fontweight='bold')
    ax.set_xlabel('Kategori Pembayaran')
    ax.set_ylabel('Rata-rata Jumlah Cicilan')
    st.pyplot(fig)

st.markdown('---')

# Heatmap aktivitas transaksi pelanggan
st.subheader('Aktivitas Transaksi Pelanggan (Hari vs Jam)')
heatmap_data = day_hour_df.pivot(index='purchase_day', columns='purchase_hour', values='order_id').fillna(0)
days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
heatmap_data = heatmap_data.reindex(days_order)
fig, ax = plt.subplots(figsize=(16, 6))
sns.heatmap(heatmap_data, cmap='YlOrRd',ax=ax)
ax.set_xlabel('Jam Transaksi')
ax.set_ylabel('Hari Transaksi')
st.pyplot(fig)

st.markdown('---')

# RFM Parameter
st.subheader('Customer Terbaik berdasarkan Parameter RFM')

# KPI avg RFM
col1, col2, col3 = st.columns(3)
with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric('Avg Recency (Hari)', value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric('Avg Frequency', value=avg_frequency)

with col3:
    avg_monetary = rfm_df.monetary.mean()
    st.metric('Avg Monetary', value=f'R$ {avg_monetary:,.2f}')

# Visual RFM
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))

# Recency
sns.barplot(
    x='customer_id',
    y='recency',
    data=rfm_df.sort_values(by='recency', ascending=True).head(5),
    palette='Reds_r',
    ax=ax[0]
)
ax[0].set_ylabel(None)
ax[0].set_xlabel('customer_id', fontsize=30)
ax[0].set_title('By Recency (Hari)', loc='center', fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=30)

# Frequnecy
sns.barplot(
    x='customer_id',
    y='frequency',
    data=rfm_df.sort_values(by='frequency', ascending=False).head(5),
    palette='Reds_r',
    ax=ax[1]
)
ax[1].set_ylabel(None)
ax[1].set_xlabel('customer_id', fontsize=30)
ax[1].set_title('By Frequnecy', loc='center', fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=30)

# Monetary
sns.barplot(
    x='customer_id',
    y='monetary',
    data=rfm_df.sort_values(by='monetary', ascending=False).head(5),
    palette='Reds_r',
    ax=ax[2]
)
ax[2].set_ylabel(None)
ax[2].set_xlabel('customer_id', fontsize=30)
ax[2].set_title('By Monetary', loc='center', fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=30)

st.pyplot(fig)

st.markdown('---')
st.caption('Muchlis Ar Wicaksana | CDCC009D6Y2743')