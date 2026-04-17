import pandas as pd
import numpy as np
import joblib
import streamlit as st
import statsmodels.api as sm
import plotly.express as px
import matplotlib.pyplot as plt
from st_aggrid import AgGrid, GridOptionsBuilder
import os
import gdown

# =========================

# PAGE CONFIG

# =========================

st.set_page_config(page_title="Insight Module", page_icon="📊", layout="wide")

st.title("🏠 Smart Real Estate Insight Module")
st.markdown("### Understand how each feature impacts property price")

# =========================

# LOAD DATA (CACHED)

# =========================

@st.cache_resource
def load_data1():
    if not os.path.exists("insight_df.joblib"):
        url = "https://drive.google.com/uc?id=1hDGpVEenCaRy31PT_b9BHdg6XeLzUBIs"
        gdown.download(url, "insight_df.joblib", quiet=False)
    df = joblib.load("insight_df.joblib")
    return df.astype("float32")

@st.cache_resource
def load_data2():
    if not os.path.exists("top10features.joblib"):
        url = "https://drive.google.com/uc?id=1iQbtYsE_1lWwLXGu6BRoXKabm7ORf9eg"
        gdown.download(url, "top10features.joblib", quiet=False)
    return joblib.load("top10features.joblib")

df = load_data1()
top20 = load_data2()

# =========================

# OLS (CACHED)

# =========================

@st.cache_resource
def compute_ols(df):
    inputs = df.drop(columns='price_outer')
    output = df['price_outer']
    output_log = np.log1p(output)


    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    inputs_scaled = scaler.fit_transform(inputs)

    inputs_df = pd.DataFrame(inputs_scaled, columns=inputs.columns)
    X_ols = sm.add_constant(inputs_df)

    model = sm.OLS(output_log, X_ols).fit()
    summary_df = model.summary2().tables[1]
    summary_df = summary_df.reset_index().rename(columns={'index': 'feature'})

    important = summary_df[summary_df['P>|t|'] < 0.05]
    important = important[important['feature'] != 'const']

    return important, scaler, inputs_df


important_features, scaler, inputs_df = compute_ols(df)

valid_feature_list = important_features['feature'].tolist()

# =========================

# INSIGHT FUNCTION

# =========================

def get_insight(feature_name):
    idx = list(inputs_df.columns).index(feature_name)
    coef = important_features[important_features['feature'] == feature_name]['Coef.']
    std = scaler.scale_[idx]

    real_coef = coef / std
    factor = np.exp(real_coef).values[0]

    base_price = df['price_outer'].median()
    rupee_change = base_price * (factor - 1)
    rupees = rupee_change * 100000
    percent = (factor - 1) * 100

    return rupees, percent


# =========================

# UI

# =========================

st.markdown("### ⚙️ Select Feature")

selected_feature = st.radio("Choose Feature", valid_feature_list, horizontal=True)

st.markdown("---")
col1, col2 = st.columns(2)

rupees, percent = get_insight(selected_feature)

with col1:
    st.markdown("### 💰 Price Impact")
    if rupees > 0:
        st.success(f"⬆️ Price increases by approx ₹{int(rupees):,}")
    else:
        st.error(f"⬇️ Price decreases by approx ₹{int(abs(rupees)):,}")

with col2:
    st.markdown("### 📊 Percentage Impact")
    if percent > 0:
        st.info(f"📈 +{round(percent,2)}% increase")
    else:
        st.warning(f"📉 {round(percent,2)}% decrease")

# =========================

# SCATTER

# =========================

fig = px.scatter(df, x=selected_feature, y='price_outer', trendline='ols')
st.plotly_chart(fig, use_container_width=True)

# =========================

# LOAD MODEL (CACHED)

# =========================

@st.cache_resource
def load_model():
    if not os.path.exists("model.joblib"):
        url = "https://drive.google.com/uc?id=1wr_2Y1gnnBkuiMqO2f1v-ALfZmnBHJSF"
        gdown.download(url, "model.joblib", quiet=False)
    return joblib.load("model.joblib")

pipeline = load_model()

# =========================

# LOAD SECOND DATA

# =========================

df1 = pd.read_csv("data/missing_imputeted_df.csv")
df1 = df1.astype("float32")

def luxury_category(row):
    if row <= 50:
        return 'Low'
    elif row <= 100:
        return 'Medium'
    else:
        return 'High'

df1['luxury_category'] = df1['luxury_score'].apply(luxury_category)
df1['furnishing_type'] = df1['furnishing_type'].map({0: "Unfurnished", 1: "Semifurnished", 2: "furnished"})
df1.drop(columns=['luxury_score', 'price_per_sqft'], inplace=True)

# =========================

# TABLE

# =========================

st.subheader("🏠 Select Property")

display_cols = ['colony', 'bedrooms', 'bathrooms', 'built_up_area', 'price_outer']
grid_df = df1[display_cols]

gb = GridOptionsBuilder.from_dataframe(grid_df)
gb.configure_selection(selection_mode="single", use_checkbox=True)

grid_response = AgGrid(grid_df, gridOptions=gb.build(), height=400)
selected_rows = grid_response["selected_rows"]

# =========================

# SHAP (LAZY + CACHED)

# =========================

@st.cache_resource
def get_explainer(model):
    import shap
    return shap.TreeExplainer(model)

if selected_rows is not None and len(selected_rows) > 0:
    selected_row = selected_rows.iloc[0]


    idx = df1[
        (df1['colony'] == selected_row['colony']) &
        (df1['bedrooms'] == selected_row['bedrooms']) &
        (df1['built_up_area'] == selected_row['built_up_area'])
    ].index[0]

    st.success(f"Selected Property Index: {idx}")

    input_data = df1.drop(columns=['price_outer']).iloc[[idx]]

    model = pipeline.named_steps['model']
    preprocessor = pipeline.named_steps['preprocessor']
    feature_names = preprocessor.get_feature_names_out()

    input_transformed = preprocessor.transform(input_data)

    explainer = get_explainer(model)
    shap_values = explainer(input_transformed)

    st.subheader("📊 Feature Contribution")

    fig = plt.figure()
    import shap
    shap.plots.waterfall(shap_values[0], show=False)
    st.pyplot(fig)

