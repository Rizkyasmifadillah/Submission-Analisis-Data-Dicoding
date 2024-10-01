from typing import Self  # Biarkan ini jika Anda memerlukannya di Python 3.11+


class DataAnalyzer:
    def __init__(self, df):
        self.df = df

    def create_daily_orders_df(self):
        daily_orders_df = self.df.resample(rule='D', on='order_approved_at').agg({
            "order_id": "nunique",
            "payment_value": "sum"
        })
        daily_orders_df = daily_orders_df.reset_index()
        daily_orders_df.rename(columns={
            "order_id": "order_count",
            "payment_value": "revenue"
        }, inplace=True)
        
        return daily_orders_df
    
    def create_sum_spend_df(self):
        sum_spend_df = self.df.resample(rule='D', on='order_approved_at').agg({
            "payment_value": "sum"
        })
        sum_spend_df = sum_spend_df.reset_index()
        sum_spend_df.rename(columns={
            "payment_value": "total_spend"
        }, inplace=True)

        return sum_spend_df

    def create_sum_order_items_df(self):
        sum_order_items_df = self.df.groupby("product_category_name_english")["product_id"].count().reset_index()
        sum_order_items_df.rename(columns={
            "product_id": "product_count"
        }, inplace=True)
        sum_order_items_df = sum_order_items_df.sort_values(by='product_count', ascending=False)

        return sum_order_items_df

    def review_score_df(self):
        review_scores = self.df['review_score'].value_counts().sort_values(ascending=False)
        most_common_score = review_scores.idxmax()

        return review_scores, most_common_score

    def create_bystate_df(self):
        bystate_df = self.df.groupby(by="customer_state").customer_id.nunique().reset_index()
        bystate_df.rename(columns={
            "customer_id": "customer_count"
        }, inplace=True)
        most_common_state = bystate_df.loc[bystate_df['customer_count'].idxmax(), 'customer_state']
        bystate_df = bystate_df.sort_values(by='customer_count', ascending=False)

        return bystate_df, most_common_state

    def create_order_status(self):
        order_status_df = self.df["order_status"].value_counts().sort_values(ascending=False)
        most_common_status = order_status_df.idxmax()

        return order_status_df, most_common_status


import pydeck as pdk

class BrazilMapPlotter:
    def __init__(self, data, st):
        self.data = data
        self.st = st

    def plot(self):
        # Buat layer untuk titik geolocation
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=self.data,
            get_position='[geolocation_lng, geolocation_lat]',
            get_radius=2000,  # radius dalam meter
            get_fill_color=[255, 0, 0],
            pickable=True
        )

        # Pusatkan peta di Brazil
        view_state = pdk.ViewState(
            latitude=self.data["geolocation_lat"].mean(),
            longitude=self.data["geolocation_lng"].mean(),
            zoom=4,
            pitch=50
        )

        # Buat peta dengan Deck
        brazil_map = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "Lat: {geolocation_lat}\nLng: {geolocation_lng}"})

        # Tampilkan peta di Streamlit
        self.st.pydeck_chart(brazil_map)


