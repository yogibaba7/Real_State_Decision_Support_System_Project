import streamlit as st


st.set_page_config(page_title="Real Estate DSS", layout="wide")

# 🎯 Title
st.markdown("""
<h1 style='text-align: center; color: white;'>
🏡 Real Estate Decision Support System
</h1>
<p style='text-align: center; color: gray;'>
Make smarter property decisions with data-driven insights
</p>
""", unsafe_allow_html=True)

st.markdown("---")

# 🔥 KPI Cards
col1, col2, col3, col4 = st.columns(4)

col1.metric("📍 Zones Covered", "8")
col2.metric("🏠 Properties", "1500+")
col3.metric("📊 Features", "20+")
col4.metric("🤖 Models", "3")

st.markdown("---")

# 🔥 Modules Section
st.subheader("🚀 Explore Modules")

col1, col2 = st.columns(2)

with col1:
    st.info("📊 **Analytics Module**\n\nExplore trends, insights, and patterns in real estate data.")

    st.info("💰 **Price Prediction**\n\nPredict property prices using machine learning.")

with col2:
    st.info("🎯 **Recommendation System**\n\nGet best property suggestions based on your needs.")

    st.info("📌 **Overview Dashboard**\n\nUnderstand overall market distribution and stats.")

st.markdown("---")


# 🧠 PROJECT DESCRIPTION
st.subheader("🏠 Project Overview")

st.markdown("""
This application helps users make **data-driven real estate decisions**:

- 🔍 Analyze market trends  
- 💰 Predict property prices  
- 🎯 Get personalized recommendations  
""")

# ⚡ HOW TO USE
st.subheader("📌 How to Use")

st.markdown("""
1️⃣ Go to **Price Prediction** → Enter property details  
2️⃣ Go to **Recommendation** → Get best matches  
3️⃣ Go to **Analytics** → Explore insights  
""")

st.markdown("---")

# 🎯 CTA
st.success("👉 Use the sidebar to navigate between modules")

# 🎉 Small animation
st.toast("Welcome to your Real Estate Dashboard 🚀")



