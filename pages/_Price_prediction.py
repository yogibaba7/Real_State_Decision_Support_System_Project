
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os 
import gdown

st.set_page_config(page_title="Price Prediction", page_icon="💰", layout="wide")

st.title("💰 Price Prediction Module")

@st.cache_resource
def load_model():
    if not os.path.exists("model.pkl"):
        url = "https://drive.google.com/file/d/1wr_2Y1gnnBkuiMqO2f1v-ALfZmnBHJSF/view?usp=drive_link"
        gdown.download(url, "model.pkl", quiet=False)
    
    return joblib.load("model.pkl")

model = load_model()

# @st.cache_resource
# def load_model():
#     return joblib.load("models/pipeline.joblib")

# model = load_model()

df = pd.read_csv("data/missing_imputeted_df.csv")

def luxury_category(row):
    if row>0 and row<=50:
        return 'Low'
    elif row>50 and row<=100:
        return 'Medium'
    else:
        return 'High'
    

df['luxury_category'] = df['luxury_score'].apply(luxury_category)

df['furnishing_type'] = df['furnishing_type'].map({0:"Unfurnished",1:"Semifurnished",2:"furnished"})

df.drop(columns=['luxury_score'],inplace=True)
st.markdown("Enter property details below 👇")

# -----------------------
# Inputs (you can modify)
# -----------------------
col1, col2, col3 = st.columns(3)

with col1:
    property_type = st.selectbox("Property Type", df['property_type'].unique())
    furnishing_type = st.selectbox("Furnishing Type", df['furnishing_type'].unique())
    bedrooms = st.number_input("Bedrooms", 1, 50, 1)

with col2:
    bathrooms = st.number_input("Bathrooms", 1, 50)
    balconies = st.number_input("Balconies", 0, 50)
    built_up_area = st.number_input("Built-up Area (sqft)", 200, 100000)

with col3:
    total_floors = st.number_input("Total Floors", 1, 60)
    property_age = st.selectbox("Property Age", df['Property Age'].unique())
    colony = st.selectbox("Colony / Location", df['colony'].unique())

luxury_category = st.selectbox("Luxury Category", df['luxury_category'].unique())
overlooking = st.selectbox("Overlooking Categories", df['Overlooking_Categories'].unique())

servant_room = st.selectbox("Servant Room", df['servant room'].unique())
store_room = st.selectbox("Store Room", df['store room'].unique())

# -----------------------
# Prediction
# -----------------------
if st.button("Predict Price 🚀"):
    input_data = pd.DataFrame([{
        "property_type": property_type,
        "furnishing_type": furnishing_type,
        "luxury_category": luxury_category,
        "Overlooking_Categories": overlooking,
        "Property Age": property_age,
        "colony": colony,
        "Total Floors": total_floors,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "balconies": balconies,
        "built_up_area": built_up_area,
        "servant room": servant_room,
        "store room": store_room
    }])

    # If your model was trained on log(price), then do expm1 after predict
    pred_log = model.predict(input_data)[0]
    pred_price = np.expm1(pred_log)

    min_price = pred_price - 15
    max_price = pred_price + 15
    st.success(f"Estimated Price Range: ₹ {min_price:,.0f} - ₹ {max_price:,.0f}")


