import pandas as pd 
import numpy as np 
import joblib 
from sklearn.preprocessing import StandardScaler
import streamlit as st
import statsmodels.api as sm
from sklearn.model_selection import KFold, cross_val_score
from sklearn.linear_model import LinearRegression,Ridge
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import OneHotEncoder, StandardScaler, OrdinalEncoder
import plotly.express as px
import shap
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

@st.cache_resource
def load_data1():
    if not os.path.exists("insight_df.joblib"):
        url = "https://drive.google.com/file/d/1hDGpVEenCaRy31PT_b9BHdg6XeLzUBIs/view?usp=drive_link"
        gdown.download(url, "insight_df.joblib", quiet=False)
    
    return joblib.load("insight_df.joblib")

df = load_data1()

@st.cache_resource
def load_data2():
    if not os.path.exists("top10features.joblib"):
        url = "https://drive.google.com/file/d/1iQbtYsE_1lWwLXGu6BRoXKabm7ORf9eg/view?usp=drive_link"
        gdown.download(url, "top10features.joblib", quiet=False)
    
    return joblib.load("top10features.joblib")

top20 = load_data2()

# df = joblib.load("models/insight_df.joblib")
# top20 = joblib.load("models/top10features.joblib")
inputs = df.drop(columns='price_outer')
output = df['price_outer']
output_log = np.log1p(output)
scaler = StandardScaler()

inputs_scaled = scaler.fit_transform(inputs)
inputs_df = pd.DataFrame(inputs_scaled,columns=inputs.columns)

# add constant
X_ols = sm.add_constant(inputs_df)

ols_model = sm.OLS(output_log, X_ols).fit()

summary_df = ols_model.summary2().tables[1]
summary_df = summary_df.reset_index().rename(columns={'index': 'feature'})


# sirf valid features (p < 0.05)
important_features = summary_df[summary_df['P>|t|'] < 0.05]

# constant hata do
important_features = important_features[important_features['feature'] != 'const']

valid_feature_list = important_features['feature'].tolist()

# print(valid_feature_list)

def get_insight(feature_name):

    idx = list(inputs_df.columns).index(feature_name)
    coef = important_features[important_features['feature']==feature_name]['Coef.']
    
    # coef = lr.coef_[idx]
    std = scaler.scale_[idx]

    real_coef = coef / std
    factor = np.exp(real_coef).values[0]
   

    base_price = df['price_outer'].median()

    rupee_change = base_price * (factor - 1)
    rupees = rupee_change * 100000

    percent = (factor - 1) * 100

    return rupees, percent

# =========================
# SIDEBAR (FEATURE SELECT)
# =========================
st.markdown("### ⚙️ Select Feature")

selected_feature = st.radio(
    "Choose Feature",
    valid_feature_list,
    horizontal=True
)


# =========================
# MAIN OUTPUT UI
# =========================
st.markdown("---")

col1, col2 = st.columns(2)

rupees, percent = get_insight(selected_feature)

# =========================
# CARD 1 (₹ IMPACT)
# =========================
with col1:
    st.markdown("### 💰 Price Impact")

    if rupees > 0:
        st.success(f"⬆️ Price increases by approx ₹{int(rupees):,}")
    else:
        st.error(f"⬇️ Price decreases by approx ₹{int(abs(rupees)):,}")

# =========================
# CARD 2 (% IMPACT)
# =========================
with col2:
    st.markdown("### 📊 Percentage Impact")

    if percent > 0:
        st.info(f"📈 +{round(percent,2)}% increase")
    else:
        st.warning(f"📉 {round(percent,2)}% decrease")

# =========================
# FEATURE STRENGTH
# =========================
st.markdown("---")

impact_strength = abs(percent)

if impact_strength > 20:
    strength = "🔥 High Impact"
elif impact_strength > 5:
    strength = "⚡ Medium Impact"
else:
    strength = "🟢 Low Impact"

st.markdown(f"### Impact Strength: {strength}")

st.dataframe(top20[['feature', 'coef']], use_container_width=True)


fig = px.scatter(df, x=selected_feature, y='price_outer',
                 trendline='ols',
                 title=f"{selected_feature} vs Price")

st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------------



# =========================
# LOAD DATA + PIPELINE
# =========================
df1 = pd.read_csv("data/missing_imputeted_df.csv")

pipeline = joblib.load("models/pipeline.joblib")

def luxury_category(row):
    if row>0 and row<=50:
        return 'Low'
    elif row>50 and row<=100:
        return 'Medium'
    else:
        return 'High'
    

df1['luxury_category'] = df1['luxury_score'].apply(luxury_category)

df1['furnishing_type'] = df1['furnishing_type'].map({0:"Unfurnished",1:"Semifurnished",2:"furnished"})

df1.drop(columns=['luxury_score','price_per_sqft'],inplace=True)


# =========================
# TABLE SELECT UI
# =========================
st.subheader("🏠 Select Property")

display_cols = [
    'colony', 'bedrooms', 'bathrooms',
    'built_up_area', 'price_outer'
]

grid_df = df1[display_cols]

gb = GridOptionsBuilder.from_dataframe(grid_df)
gb.configure_selection(selection_mode="single", use_checkbox=True)
gb.configure_pagination()

grid_response = AgGrid(
    grid_df,
    gridOptions=gb.build(),
    height=400,
    theme="streamlit"
)

selected_rows = grid_response["selected_rows"]

# =========================
# IF USER SELECTS ROW
# =========================
if selected_rows is not None and len(selected_rows) > 0:
    selected_row = selected_rows.iloc[0]

    # get index
    idx = df1[
        (df1['colony'] == selected_row['colony']) &
        (df1['bedrooms'] == selected_row['bedrooms']) &
        (df1['built_up_area'] == selected_row['built_up_area'])
    ].index[0]

    st.success(f"Selected Property Index: {idx}")

    # # =========================
    # # PREPARE INPUT
    # # =========================
    # df = df.drop(columns=['price_outer'])
    # input_data = df.iloc[[idx]]

    # # =========================
    # # PREDICTION
    # # =========================
    # pred_log = pipeline.predict(input_data)[0]
    # pred_price = np.exp(pred_log)

    # st.subheader(f"💰 Predicted Price: ₹{int(pred_price * 100000):,}")

    input_data = df1.drop(columns=['price_outer']).iloc[[idx]]
    # =========================
    # SHAP EXPLAINER
    # =========================
    model = pipeline.named_steps['model']
    preprocessor = pipeline.named_steps['preprocessor']
    feature_names = preprocessor.get_feature_names_out()

    input_transformed = preprocessor.transform(input_data)

    explainer = shap.TreeExplainer(model)
    shap_values = explainer(input_transformed)
    shap_values.feature_names = feature_names
    
    # =========================
    # WATERFALL
    # =========================
    st.subheader("📊 Feature Contribution")

    fig = plt.figure()
    shap.plots.waterfall(shap_values[0], show=False)
    st.pyplot(fig)

    # =========================
    # CONTRIBUTION TABLE
    # =========================
    contrib_df = pd.DataFrame({
        "Feature": feature_names,
        "Impact": shap_values.values[0]
    })

    base_price = df1['price_outer'].median()
    contrib_df["₹ Impact"] = contrib_df["Impact"] * base_price * 100000
    contrib_df["abs"] = contrib_df["₹ Impact"].abs()

    top = contrib_df.sort_values(by="abs", ascending=False).head(10)

    st.subheader("📋 Top Factors")
    st.dataframe(top[['Feature', '₹ Impact']], use_container_width=True)

    # =========================
    # POSITIVE / NEGATIVE
    # =========================
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🟢 Increasing Price")
        for _, row in top[top['₹ Impact'] > 0].iterrows():
            st.success(f"{row['Feature']} → +₹{int(row['₹ Impact']):,}")

    with col2:
        st.markdown("### 🔴 Decreasing Price")
        for _, row in top[top['₹ Impact'] < 0].iterrows():
            st.error(f"{row['Feature']} → ₹{int(row['₹ Impact']):,}")
