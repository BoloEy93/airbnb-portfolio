import streamlit as st
import pandas as pd
from snowflake.snowpark import Session
from snowflake.ml.registry import Registry
import json 

st.set_page_config(page_title="Price Predictor", page_icon="💰", layout="wide")

st.title("💰 Airbnb Price Predictor")
st.markdown("This tool uses a Random Forest model registered in Snowflake Model Registry to predict the nightly price of an NYC listing.")

# Single shared session for everything
@st.cache_resource
def get_session():
    return Session.builder.configs(st.secrets["snowflake"]).create()

session = get_session()

# UI Form
with st.form("prediction_form"):
    st.subheader("Listing Details")
    col1, col2 = st.columns(2)
    
    with col1:
        room_type = st.selectbox("Room Type", ["Entire home/apt", "Private room", "Shared room", "Hotel room"])
        borough = st.selectbox("Borough", ["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"])
        accommodates = st.slider("Accommodates (Guests)", 1, 10, 2)
        bedrooms = st.slider("Bedrooms", 0.0, 5.0, 1.0)
        
    with col2:
        beds = st.slider("Beds", 0.0, 5.0, 1.0)
        bathrooms = st.slider("Bathrooms", 0.0, 5.0, 1.0)
        min_nights = st.number_input("Minimum Nights", value=30)
        avail_365 = st.number_input("Availability (Days per year)", value=180)
        
    st.subheader("Neighbourhood & Host Details")
    col3, col4 = st.columns(2)
    with col3:
        neigh_median = st.number_input("Neighbourhood Median Price ($)", value=150.0)
        review_rating = st.slider("Review Rating", 0.0, 5.0, 4.5)
    with col4:
        host_listings = st.number_input("Host Total Listings", value=1)
        
    submit = st.form_submit_button("Predict Price")

if submit:
    with st.spinner("Calculating..."):
        # Build the SQL directly — most stable for warehouse models
        sql = f"""
        SELECT MODEL(AIRBNB_PORTFOLIO.ANALYTICS.AIRBNB_PRICE_PREDICTOR, v3)!predict(
            ACCOMMODATES => {accommodates},
            BEDROOMS => {bedrooms},
            BEDS => {beds},
            BATHROOMS => {bathrooms},
            ROOM_TYPE => '{room_type}',
            BOROUGH => '{borough}',
            NEIGHBOURHOOD_MEDIAN_PRICE => {neigh_median},
            REVIEW_SCORES_RATING => {review_rating},
            MINIMUM_NIGHTS => {min_nights},
            AVAILABILITY_365 => {avail_365},
            HOST_LISTING_COUNT => {host_listings}
        ) AS PREDICTED_PRICE
        """
        
        try:
            result = session.sql(sql).collect()
            raw_value = result[0]["PREDICTED_PRICE"]
            
            # Parse the JSON string
            parsed = json.loads(raw_value)
            predicted_price = parsed["output_feature_0"]
            
            st.success(f"### Predicted Nightly Price: **${predicted_price:.2f}**")
            st.info("Note: This is a machine learning estimate based on historical NYC data. Actual prices may vary based on seasonality and amenities.")
        except Exception as e:
            st.error(f"Prediction failed: {e}")

        #result = session.sql(sql).collect()
        #raw_value = result[0]["PREDICTED_PRICE"]
        #st.write(f"Raw value: {raw_value} (type: {type(raw_value)})")
        #try:
        #    predicted_price = float(raw_value)
        #    st.success(f"### Predicted Nightly Price: **${predicted_price:.2f}**")
        #except (ValueError, TypeError):
        #    st.error(f"Could not convert to float: {raw_value}")

        #try:
        #    result = session.sql(sql).collect()
        #    #predicted_price = result[0]["PREDICTED_PRICE"]
        #    raw_value = result[0]["PREDICTED_PRICE"]
        #    predicted_price = float(raw_value)  # <-- Cast to float
        #    st.success(f"### Predicted Nightly Price: **${predicted_price:.2f}**")
        #    st.info("Note: This is a machine learning estimate based on historical NYC data. Actual prices may vary based on seasonality and amenities.")
        #except Exception as e:
        #    st.error(f"Prediction failed: {e}")