
import streamlit as st

st.set_page_config(page_title="Overview", page_icon="🏠", layout="wide")

st.title("🏠 Project Overview")

st.markdown("""
### 🎯 Goal
This web app helps users make better real estate decisions by providing:

- **Property price prediction**
- **Property recommendation**
- **Market analytics**
""")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Modules", "4")
with col2:
    st.metric("ML Models", "ExtraTrees / XGBoost")
with col3:
    st.metric("Dataset", "Cleaned Real Estate Data")

st.markdown("---")

st.subheader("📌 How to Use")
st.markdown("""
1. Go to **Price Prediction** → enter property details → get predicted price  
2. Go to **Recommendation** → choose preferences → get best matches  
3. Go to **Analytics** → explore insights and graphs  
""")
