import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
from func import DataAnalyzer, BrazilMapPlotter


# Set styling
sns.set(style='dark')
import matplotlib as mpl
mpl.rcParams.update(mpl.rcParamsDefault)

# Membaca dataset dengan low_memory=False
datetime_cols = [
    "order_approved_at", "order_delivered_carrier_date", 
    "order_delivered_customer_date", "order_estimated_delivery_date", 
    "order_purchase_timestamp", "shipping_limit_date"
]

# Membaca CSV
try:
    all_df = pd.read_csv("/Users/vanillatte/Downloads/Streamlit/all_data.csv", low_memory=False)
except FileNotFoundError:
    st.error("File tidak ditemukan. Pastikan path file CSV benar.")
    st.stop()

# Sorting dan reset index
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(drop=True, inplace=True)

# Dataset Geolocation
geolocation = all_df.drop_duplicates(subset='customer_unique_id')

# Mengonversi kolom datetime dan menangani nilai yang tidak valid
for col in datetime_cols:
    all_df[col] = pd.to_datetime(all_df[col], errors='coerce')  # Mengganti nilai yang tidak valid dengan NaT

# Tanggal Minimum dan Maksimum
min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()

# Sidebar
with st.sidebar:
    st.title("Rizky Asmi Fadillah")
    # Cek jika gambar ada
    try:
        st.image("for_sidebar.png")
    except Exception as e:
        st.error(f"Gambar tidak ditemukan: {e}")

    start_date, end_date = st.date_input(
        label="Select Date Range",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

# Data Utama
main_df = all_df[(all_df["order_approved_at"] >= pd.to_datetime(start_date)) & 
                 (all_df["order_approved_at"] <= pd.to_datetime(end_date))]

# Menganalisis Data
function = DataAnalyzer(main_df)

# Menciptakan DataFrames analisis
daily_orders_df = function.create_daily_orders_df()
sum_spend_df = function.create_sum_spend_df()
sum_order_items_df = function.create_sum_order_items_df()
review_score, common_score = function.review_score_df()
state, most_common_state = function.create_bystate_df()
order_status, common_status = function.create_order_status()

# Judul Dashboard
st.header("E-Commerce Dashboard :convenience_store:")

# Pesanan Harian
st.subheader("Daily Orders")
col1, col2 = st.columns(2)

with col1:
    total_order = daily_orders_df["order_count"].sum()
    st.markdown(f"Total Order: **{total_order}**")

with col2:
    total_revenue = format_currency(daily_orders_df["revenue"].sum(), "IDR", locale="id_ID")
    st.markdown(f"Total Revenue: **{total_revenue}**")

# Grafik Pesanan Harian
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(
    daily_orders_df["order_approved_at"],
    daily_orders_df["order_count"],
    marker="o",
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis="x", rotation=45)
ax.tick_params(axis="y", labelsize=15)
st.pyplot(fig)

# Item Pesanan
st.subheader("Order Items")
col1, col2 = st.columns(2)

with col1:
    total_items = sum_order_items_df["product_count"].sum()
    st.markdown(f"Total Items: **{total_items}**")

with col2:
    avg_items = sum_order_items_df["product_count"].mean()
    st.markdown(f"Average Items: **{avg_items:.2f}**")

# Grafik Item Pesanan
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(20, 8))

colors = ["#068DA9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

# Produk paling banyak terjual
sns.barplot(x="product_count", y="product_category_name_english", hue="product_category_name_english", 
            data=sum_order_items_df.head(5), palette=colors, ax=ax[0], legend=False)
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=15)
ax[0].set_title("Produk paling banyak terjual", loc="center", fontsize=20)
ax[0].tick_params(axis='y', labelsize=12)
ax[0].tick_params(axis='x', labelsize=12)

# Produk paling sedikit terjual
sns.barplot(x="product_count", y="product_category_name_english", hue="product_category_name_english", 
            data=sum_order_items_df.sort_values(by="product_count", ascending=True).head(5), palette=colors, ax=ax[1], legend=False)
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=15)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Produk paling sedikit terjual", loc="center", fontsize=20)
ax[1].tick_params(axis='y', labelsize=12)
ax[1].tick_params(axis='x', labelsize=12)

st.pyplot(fig)

# Skor Ulasan
st.subheader("Review Score")
col1, col2 = st.columns(2)

with col1:
    avg_review_score = review_score.mean()
    st.markdown(f"Average Review Score: **{avg_review_score:.2f}**")

with col2:
    most_common_review_score = review_score.value_counts().index[0]
    st.markdown(f"Most Common Review Score: **{most_common_review_score}**")

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x=review_score.index, 
            y=review_score.values, 
            hue=review_score.index, 
            palette=["#068DA9" if score == common_score else "#D3D3D3" for score in review_score.index], 
            legend=False)

plt.title("Rating by customers for service", fontsize=15)
plt.xlabel("Rating")
plt.ylabel("Count")
plt.xticks(fontsize=12)
st.pyplot(fig)

# Demografi Pelanggan
st.subheader("Customer Demographic")
tab1, tab2 = st.tabs(["State", "Order Status"])

# Tab : State
with tab1:
    most_common_state = state.customer_state.value_counts().index[0]
    st.markdown(f"Most Common State: **{most_common_state}**")

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=state.customer_state.value_counts().index,
                y=state.customer_count.values, 
                hue=state.customer_state.value_counts().index,
                palette=["#068DA9" if score == most_common_state else "#D3D3D3" for score in state.customer_state.value_counts().index],
                legend=False)

    plt.title("Number customers from State", fontsize=15)
    plt.xlabel("State")
    plt.ylabel("Number of Customers")
    plt.xticks(fontsize=12)
    st.pyplot(fig)

# Tab : Order Status
with tab2:
    common_status_ = order_status.value_counts().index[0]
    st.markdown(f"Most Common Order Status: **{common_status_}**")

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=order_status.index,
                y=order_status.values,
                hue=order_status.index,
                palette=["#068DA9" if score == common_status else "#D3D3D3" for score in order_status.index],
                legend=False)
    
    plt.title("Order Status", fontsize=15)
    plt.xlabel("Status")
    plt.ylabel("Count")
    plt.xticks(fontsize=12)
    st.pyplot(fig)

# Footer
st.caption('Copyright (C) Rizky Asmi Fadillah. 2024')
