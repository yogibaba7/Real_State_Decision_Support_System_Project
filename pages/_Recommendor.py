
import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import os
import gdown

# =========================
# PAGE CONFIG
st.set_page_config(page_title="🏠 Property Recommendation System", page_icon="💰", layout="wide")
# =========================
st.title("🏠 Property Recommendation System")

def download_model(file_id, output):
    if not os.path.exists(output):
        url = f"https://drive.google.com/uc?id={file_id}"
        with st.spinner(f"Downloading {output}... ⏳"):
            gdown.download(url, output, quiet=False)


# =========================
# AREA SIM
# =========================
@st.cache_resource
def load_areasim():
    download_model("1puvxRV4Swbn2UrAAeMG4lu6ZKsfOgCta", "area_sim.joblib")
    model = joblib.load("area_sim.joblib")

    # safety check
    if hasattr(model, "shape"):
        st.write("Area sim shape:", model.shape)

    return model

area_sim = load_areasim()


# =========================
# PRICE SIM
# =========================
@st.cache_resource
def load_pricesim():
    download_model("1L-YjTIyQmks3WsMg8amNjh03v1XZfajz", "price_sim.joblib")
    model = joblib.load("price_sim.joblib")

    # safety check
    if hasattr(model, "shape"):
        st.write("Price sim shape:", model.shape)

    return model

price_sim = load_pricesim()


# =========================
# FACILITY SIM
# =========================
@st.cache_resource
def load_facilitysim():
    download_model("1wyKoIAi0dJaAajYjW365Ye1Z-nkSFTXn", "facility_sim.joblib")
    model = joblib.load("facility_sim.joblib")

    # safety check
    if hasattr(model, "shape"):
        st.write("Facility sim shape:", model.shape)

    return model

facility_sim = load_facilitysim()


# load data
df = pd.read_csv("data/missing_imputeted_df.csv")
# price_sim =joblib.load("models/price_sim.joblib")
# area_sim = joblib.load("models/area_sim.joblib")
# facility_sim = joblib.load("models/facility_sim.joblib")

# recommendation function
def recommend_properties(idx, sim1=price_sim,sim2=area_sim,sim3=facility_sim):
    print(sim1.shape,sim2.shape,sim3.shape)
    # combine similarity
    price_w = 0.9
    area_w = 0.6
    facility_w = 0.3

    combine_similarity = price_w*sim1 + area_w*sim2 + facility_w*sim3

    # Get the pairwise similarity scores with that property
    sim_scores = list(enumerate(combine_similarity[idx]))

    # Sort the properties based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the scores of the 10 most similar properties
    sim_scores = sim_scores[1:6]

    # Get the property indices
    property_indices = [i[0] for i in sim_scores]
    
    recommendations_df = df.iloc[property_indices]

    # Return the top 10 most similar properties
    return recommendations_df

# =========================
# UI - SELECT COLONY
# =========================
st.subheader("📍 Select Colony")

colony = st.selectbox("Choose Colony", df['colony'].dropna().unique())

filtered_df = df[df['colony'] == colony].reset_index()


# =========================
# SHOW TABLE (AGGRID)
# =========================
st.subheader("🏘️ Available Properties")

# gb = GridOptionsBuilder.from_dataframe(filtered_df)

# gb.configure_selection(
#     selection_mode="single",
#     use_checkbox=True
# )

# grid_response = AgGrid(
#     filtered_df,
#     gridOptions=gb.build(),
#     height=300
# )
gb = GridOptionsBuilder.from_dataframe(filtered_df)

# 🔥 IMPORTANT SETTINGS
gb.configure_selection(
    selection_mode="single",
    use_checkbox=True
)

# 👉 Make columns auto-fit
gb.configure_default_column(
    resizable=True,
    filter=True,
    sortable=True,
    flex=1,   # 🔥 THIS MAKES GRID RESPONSIVE
    minWidth=120
)

# 👉 Pagination (optional but clean)
gb.configure_pagination(paginationAutoPageSize=True)

grid_response = AgGrid(
    filtered_df,
    gridOptions=gb.build(),
    theme="streamlit",
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    height=400,
    fit_columns_on_grid_load=True,   # 🔥 KEY FIX
)



selected_rows = grid_response["selected_rows"]


# =========================
# SHOW RECOMMENDATIONS
# =========================
if selected_rows is not None and len(selected_rows) > 0:
    if isinstance(selected_rows, pd.DataFrame):
        selected_row = selected_rows.iloc[0]
    else:
        selected_row = selected_rows[0]

    selected_idx = selected_row["index"]

    st.success(f"✅ Selected: {selected_row['property_type']} in {selected_row['colony']}")

    st.markdown("---")
    st.subheader("🔍 Similar Properties")
    # selected_row = selected_rows[0]
    # selected_idx = selected_row["index"]

    # st.success(f"✅ Selected Property: {selected_row['property_type']} in {selected_row['colony']}")

    # st.markdown("---")
    # st.subheader("🔍 Similar Properties")

    recs = recommend_properties(selected_idx)


    for _, row in recs.iterrows():
        st.markdown(f"""
        <div style="
            padding:15px;
            border-radius:10px;
            background-color:#1e293b;
            margin-bottom:10px;
        ">
            <h4>🏠 {row['property_type']} in {row['colony']}</h4>
            <p>
            💰 Price: ₹{row['price_outer']} Lakh <br>
            📐 Area: {row['built_up_area']} sqft <br>
            🛏️ Bedrooms: {row['bedrooms']} <br>
            🛁 Bathrooms: {row['bathrooms']}
            </p>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("👉 Select a property from the table to see recommendations")
