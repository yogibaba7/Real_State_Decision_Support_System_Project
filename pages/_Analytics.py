
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import ast
from collections import Counter

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="📊 Analytics Module", page_icon="", layout="wide")

st.title("👋 Welcome to Analytics Module")
st.markdown("### Understand Bhopal Property Market Trends and Insights")


# =========================
# LOAD DATA (CACHED)
# =========================
@st.cache_data
def load_data():
    df1 = pd.read_csv("data/zone_analytics1.csv")
    df2 = pd.read_csv("data/zona_analytics_df.csv")
    return df1, df2

zone_df1, zone_df = load_data()

# calculating area per bedroom and removing outliers
zone_df1['area_per_bedroom'] = zone_df1['built_up_area'] /( zone_df1['Total Floors'] * zone_df1['bedrooms'])
zone_df1 = zone_df1.sort_values('area_per_bedroom',ascending=False).iloc[2:]

# recreate furnishing type categories
zone_df1['furnishing_type'] = zone_df1['furnishing_type'].replace({0:'Unfurnished', 
                                                                   1:'Semi-Furnished', 2:'Furnished'})


# bedrooms price distribution across zones
def bedroom_group(x):
    if x ==1:
        return "1 BHK"
    elif x == 2:
        return "2 BHK"
    elif x == 3:
        return "3 BHK"
    elif x == 4:
        return "4 BHK"
    elif x == 5:
        return "5 BHK"
    elif x >= 6:
        return "6+ BHK"
    else:
        return "Others"

zone_df1['bedrooms_categories'] = zone_df1['bedrooms'].apply(bedroom_group)

# FUNCTION TO GENERATE TEXT
# =========================
def get_text(data):
    all_features = []
    for row in data['features']:
        if isinstance(row, list):
            all_features.extend(row)
    text = " ".join(all_features)
    text = text.replace("/", " ")
    return text

# Initialize session state
if "view" not in st.session_state:
    st.session_state.view = None

col1, col2 = st.columns(2)

with col1:
    if st.button("Zone-wise Analytics"):
        st.session_state.view = "zone"

with col2:
    if st.button("Colony-wise Analytics"):
        st.session_state.view = "colony"

if st.session_state.view == None:
    
    st.info("""
    👉 Select an analysis type to explore real estate insights

    🔹 Zone-wise Analytics → Compare areas, prices, trends  
    🔹 Colony-wise Analytics → Deep dive into specific locations  
    """)

    st.markdown("---")

    # Preview cards
    col1, col2, col3 = st.columns(3)

    col1.metric("🏠 Total Properties", len(zone_df1))
    col2.metric("📍 Zones", zone_df1['zone'].nunique())
    col3.metric("🏘️ Colonies", zone_df1['colony'].nunique())

    st.markdown("---")

    # Sample visualization (teaser)
    st.markdown("### 📈 Market Overview")

    fig = px.histogram(
        zone_df1,
        x="price_outer",
        nbins=40,
        title="Property Price Distribution"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.caption("💡 Tip: Click on 'Zone-wise Analytics' or 'Colony-wise Analytics' to explore deeper insights")

elif st.session_state.view == "zone":
    st.subheader("📍 Zone-wise Analysis")

    # =========================
    # ZONE MAP + CONTEXT
    # =========================

    st.markdown("### 🗺️ Bhopal Zone Classification")

    st.image("assets/zone_classification.png", use_container_width=True)

    st.caption("""
    This zone division is created manually based on domain understanding, 
    location patterns, and market trends. Minor variations may exist.
    """)

    st.info("👇 Now explore detailed analytics below")

    # filtering based on property type
    selected_option = st.selectbox(
        "Select Property Type",
        options=["Overall","Flats","Independent Houses"]
    )

    if selected_option == "Flats":
        zone_df = zone_df[zone_df['property_type']=='Flat']
        zone_df1 = zone_df1[zone_df1['property_type']=='Flat']

    elif selected_option == "Independent Houses":
        zone_df = zone_df[zone_df['property_type']=='House']
        zone_df1 = zone_df1[zone_df1['property_type']=='House']
    


    section = st.radio(
    "Choose Analysis",
    ["Overview", "Price Analysis", "Area Analysis", "Amenities", "Advanced"],
    horizontal=True
)
    if section == "Overview":
            col1, col2, col3, col4 = st.columns(4)

            col1.metric("🏠 Properties", len(zone_df1))
            col2.metric("💰 Median Price", f"₹{int(zone_df1['price_outer'].median())}L")
            col3.metric("📐 Avg Area", f"{int(zone_df1['built_up_area'].mean())} sqft")
            col4.metric("📊 Avg PPS", f"{int(zone_df1['price_per_sqft'].mean())}")

            st.markdown("### 📈 Price Distribution")

            fig = px.histogram(zone_df1, x="price_outer", nbins=40)
            st.plotly_chart(fig, use_container_width=True)


            st.markdown("### 📊 Price vs Area")

            fig = px.scatter(
                zone_df1,
                x="built_up_area",
                y="price_outer",
                trendline="ols"
            )

            st.plotly_chart(fig, use_container_width=True)

            st.markdown("### 🏙️ Zone-wise Price Comparison")

            temp = zone_df1.groupby("zone")["price_outer"].median().reset_index()

            fig = px.bar(temp, x="zone", y="price_outer", color="price_outer")
            st.plotly_chart(fig, use_container_width=True)

            top_zone = temp.loc[temp['price_outer'].idxmax(), 'zone']
            cheap_zone = temp.loc[temp['price_outer'].idxmin(), 'zone']

            st.info(f"""
            🏆 Most Expensive Zone: {top_zone}  
            💸 Most Affordable Zone: {cheap_zone}  
            📊 Price varies significantly across zones  
            """)

            st.caption("💡 Tip: Use other sections to explore deeper insights like area trends and amenities")
    
    elif section == "Price Analysis":
        st.markdown("### 💰 Price Analysis")
        st.caption("Understand how property prices vary across zones and areas")

        st.markdown("#### 📊 Price Distribution Across Zones")

        fig = px.box(
            zone_df1,
            x="price_outer",
            y="zone",
            color="zone"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### 📐 Price per Sqft Comparison")

        temp = zone_df1.groupby("zone")["price_per_sqft"].median().reset_index()

        fig = px.bar(
            temp,
            x="price_per_sqft",
            y="zone",
            color="price_per_sqft",
            text="price_per_sqft"
        )

        fig.update_traces(textposition="outside")

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### 🏘️ Price Increase per Unit Area in Each Zone")
        results = []
        for zone in zone_df1['zone'].unique():
            df = zone_df1[zone_df1['zone'] == zone]

            X = df['built_up_area']
            y = df['price_outer']

            X = sm.add_constant(X)  # adds intercept

            model = sm.OLS(y, X).fit()

            slope = model.params['built_up_area']

            results.append({
                'zone': zone,
                'price_increase_per_unit_area': slope*100000
            })


        slope_df = pd.DataFrame(results).sort_values(by='price_increase_per_unit_area', ascending=False)

        fig = px.bar(
            slope_df,
            x='zone',
            y='price_increase_per_unit_area',
            color='price_increase_per_unit_area',
            text='price_increase_per_unit_area'
        )

        fig.update_traces(texttemplate='₹%{text:.0f}', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

        st.caption("""
    📌 Note: This analysis is based on a simple linear regression model applied separately to each zone.  
                The values represent estimated price sensitivity (₹ per sqft) and may vary depending on property characteristics.  
                Use this as a directional insight rather than an exact price rule.
        """)

        st.markdown("#### 🏘️ Price vs Area by Zone")
        fig = px.scatter(
        zone_df1,
        x="built_up_area",
        y="price_outer",
        color="zone",
        trendline="ols",
        opacity=0.7
    )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### 🏙️ Age based Price Comparision in Zones")

        temp = zone_df1.pivot_table(
            values="price_outer",
            index="zone",
            columns="Property Age",
            aggfunc="median"
        )

        fig = px.imshow(
        temp,
        text_auto=True,
        color_continuous_scale="RdBu"
    )

        fig.update_layout(
            height=800,
            width=2000
        )

        st.plotly_chart(fig, use_container_width=True)

        # price by bedroom categories in zones
        st.markdown("#### 💰 Median Property Price by BHK Across Zones")

        bedroom_price = zone_df1.groupby(['bedrooms_categories','zone'])['price_outer'].median().reset_index()
        order = ["1 BHK","2 BHK", "3 BHK", "4 BHK", "5 BHK", "6+ BHK"]

        bedroom_price['bedrooms'] = pd.Categorical(
            bedroom_price['bedrooms_categories'],
            categories=order,
            ordered=True
        )

        bedroom_price = bedroom_price.sort_values('bedrooms')

        fig = px.bar(
            bedroom_price,
            y="bedrooms",
            x="price_outer",
            text="price_outer",
            color="bedrooms",
            title="Median Price by Bedroom Type",
            facet_col="zone",
            facet_col_wrap=3
        )

        fig.update_traces(textposition='outside')

        st.plotly_chart(fig, use_container_width=True)

        # furnishing type price distribution
        st.markdown("#### 🪑 Median Price by Furnishing Type across Zones")
        temp = zone_df1.groupby(['zone','furnishing_type'])['price_outer'].median().reset_index()
        fig = px.bar(
            temp,
            y="zone",
            x="price_outer",
            text="price_outer",
            facet_col="furnishing_type",
            facet_col_wrap=3,
            color="furnishing_type",
        )

        fig.update_traces(textposition='outside')

        st.plotly_chart(fig, use_container_width=True)

        # heatmap for price based on property age across zones
        pivot = zone_df1.pivot_table(
            values="price_outer",
            index="zone",
            columns="Overlooking_Categories",
            aggfunc="median"
        )

        upper_limit = np.percentile(pivot.values.flatten(), 95)

        pivot_clipped = pivot.clip(upper=upper_limit)

        fig = px.imshow(
        pivot_clipped,
        text_auto=True,
        color_continuous_scale='YlGnBu',
        title="💰 Median Price by Overlooking Type Across Zones",
        aspect="auto"
    )

        fig.update_layout(
            height=800, margin=dict(l=200, r=50, t=60, b=50)
        )
        st.plotly_chart(fig, use_container_width=True)

        # sns.heatmap(pivot, annot=True,fmt=".0f",cmap="coolwarm",cbar_kws={'label': 'Price (in Lakhs)'}  )
        # plt.title("Median Price based on Property Age across Zones")
        # st.pyplot(plt)

    elif section == "Area Analysis":
        st.markdown("### 📐 Area Analysis")
        st.caption("Understand property size distribution and its impact across zones")

        st.markdown("#### 📊 Overall Built-Up Area Distribution")
        fig = px.histogram(
            zone_df1,
            x="built_up_area",
            nbins=40
        )

        st.plotly_chart(fig, use_container_width=True)

        # area per bedroom distribution
        st.markdown("#### 🛏️ Area per Bedroom Distribution")
        fig = px.histogram(
            zone_df1,
            x="area_per_bedroom",
            nbins=40
        )   
        st.plotly_chart(fig, use_container_width=True)

        # Build up area Distribuiton in zones
        st.markdown("#### 🏙️ Zone-wise Built-Up Area Comparison")
        fig = px.box(zone_df1, x='built_up_area',y='zone',color='zone')
        st.plotly_chart(fig,use_container_width=True)

        # avg area per bedroom
        st.markdown("#### 🏘️ Average Area per Bedroom by Zone")
        temp = zone_df1.groupby("zone")["area_per_bedroom"].median().reset_index()    
        fig = px.bar(
            temp,
            x="zone",
            y="area_per_bedroom",
            color="area_per_bedroom",
            text="area_per_bedroom"
        )   
        fig.update_traces(texttemplate='%{text:.0f} sqft', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)


        # area category distribution
        st.markdown("#### 🏘️ Area Category Distribution")
        temp = zone_df1.copy()

        def area_category(x):
            if x < 1000:
                return "Small"
            elif x < 2000:
                return "Medium"
            else:
                return "Large"

        temp['area_type'] = temp['built_up_area'].apply(area_category)

        # count per zone + area_type
        agg = temp.groupby(['zone', 'area_type']).size().reset_index(name='count')


        fig = px.pie(
            agg,
            names='area_type',
            values='count',
            facet_col='zone',
            facet_col_wrap=3
        )

        fig.update_traces(textinfo='percent')
        fig.update_layout(height=800)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 📏 Area Classification Logic")

        st.info("""
        We categorize properties based on built-up area:

        • 🟢 Small → < 1000 sqft  
        • 🔵 Medium → 1000 – 2000 sqft  
        • 🔴 Large → > 2000 sqft  
        """)

    elif section == "Amenities":
        st.markdown("### 🛠️ Amenities Analysis")

        # Top amenities distribution
        st.markdown("#### 🏘️ Top Amenities Distribution")
        t1 = zone_df.dropna(subset=['features'])
        t1['features'] = t1['features'].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) else []
        )

        all_features = []

        for row in t1['features']:
            all_features.extend(row)

        counter = Counter(all_features)
        top_amenities = counter.most_common(20)

        top_df = pd.DataFrame(top_amenities, columns=['Amenity', 'Count'])

            # 🔥 BAR CHART
        fig = px.bar(
            top_df,
            x='Count',
            y='Amenity',
            orientation='h',
            text='Count',
            color='Count'
        )

        fig.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            title="🏆 Top Amenities Overall"
        )

        st.plotly_chart(fig, use_container_width=True)


        # =========================
        # INSIGHTS
        # =========================
        top1 = top_df.iloc[0]
        st.success(f"🔥 Most common amenity: {top1['Amenity']} ({top1['Count']} listings)")

        # Rare amenities
        rare = counter.most_common()[-5:]

        st.warning("⚠️ Rare Amenities:")
        for r in rare:
            st.write(f"{r[0]} → {r[1]} listings")

        st.markdown("### ☁️ Amenities Word Cloud")

        # =========================
        # TOGGLE (Overall / Zone)
        # =========================
        wc_option = st.radio(
            "Select WordCloud View",
            ["Overall", "Zone-wise"],
            horizontal=True
        )
        t2 = zone_df.dropna(subset=['features'])
        t2['features'] = t2['features'].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) else []
        )
        if wc_option == "Overall":

            text = get_text(t2)
            wordcloud = WordCloud(
                width=800,
                height=400,
                background_color='black',
                colormap='viridis'
            ).generate(text)

            fig, ax = plt.subplots()
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis("off")

            st.pyplot(fig)

            st.caption("💡 Bigger words = more frequent amenities in listings")

            # Furnishing type distribution
            st.markdown("### 🪑 Furnishing Type Distribution")

            furnish_counts = zone_df1['furnishing_type'].value_counts().reset_index()
            furnish_counts.columns = ['Furnishing', 'Count']

            fig = px.pie(
                furnish_counts,
                names='Furnishing',
                values='Count',
                title="Overall Furnishing Distribution",
                hole=0.4  # donut style (looks better)
            )
            fig.update_traces(textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)

            st.info("💡 Shows proportion of Unfurnished, Semi-furnished, and Furnished properties")
            st.caption("""
            💡 Furnishing types are not manually assigned. They are generated using clustering on 
            amenities like AC, wardrobe, kitchen, etc. The model grouped properties into 3 categories 
            based on similarity patterns in the data , so there may be slight variations.
            """)
            # insight
            top = furnish_counts.iloc[0]
            st.success(f"🔥 Most common: {top['Furnishing']} ({top['Count']} listings)")


            # Overlooking category distribution
            st.subheader("🌇 Overlooking Distribution")

            counts = zone_df1['Overlooking_Categories'].value_counts().reset_index()
            counts.columns = ['Type', 'Count']

            fig = px.pie(counts, names='Type', values='Count', hole=0.2)
            fig.update_traces(textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)

            # insight
            top = counts.iloc[0]
            st.success(f"🔥 Most common: {top['Type']} ({top['Count']} listings)")

        
        # =========================
        # ZONE-WISE WORD CLOUD
        # =========================
        else:
            zones = t2['zone'].dropna().unique()
            selected_zone = st.selectbox("Select Zone", zones)

            zone_df = t2[t2['zone'] == selected_zone]
            text = get_text(t2)

            wordcloud = WordCloud(
                width=800,
                height=400,
                background_color='black',
                colormap='plasma'
            ).generate(text)

            fig, ax = plt.subplots()
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis("off")

            st.pyplot(fig)

            st.caption("💡 Bigger words = more frequent amenities in listings")

            # Furnishing type distribution
            st.markdown("### 🪑 Furnishing Type Distribution")

            temp1 = zone_df1[zone_df1['zone'] == selected_zone]

            furnish_counts = temp1['furnishing_type'].value_counts().reset_index()
            furnish_counts.columns = ['Furnishing', 'Count']

            fig = px.pie(
                furnish_counts,
                names='Furnishing',
                values='Count',
                title=f" {selected_zone} Furnishing Distribution",
                hole=0.4  # donut style (looks better)
            )
            fig.update_traces(textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)

            st.info("💡 Shows proportion of Unfurnished, Semi-furnished, and Furnished properties")
            st.caption("""
💡 Furnishing types are not manually assigned. They are generated using clustering on 
amenities like AC, wardrobe, kitchen, etc. The model grouped properties into 3 categories 
based on similarity patterns in the data , so there may be slight variations.
""")
            # insight
            top = furnish_counts.iloc[0]
            st.success(f"🔥 Most common: {top['Furnishing']} ({top['Count']} listings)")


            # Overlooking category distribution
            st.subheader("🌇 Overlooking Distribution")

            temp = zone_df1.groupby(['zone', 'Overlooking_Categories']).size().reset_index(name='count')

            # convert to %
            temp['percentage'] = temp.groupby('zone')['count'].transform(lambda x: x / x.sum() * 100)

            
            fig = px.bar(
                temp,
                x='zone',
                y='percentage',
                color='Overlooking_Categories',
                barmode='stack',
                text_auto='.1f'
            )

        
            zone_order = zone_df1.groupby('zone')['price_outer'].mean().sort_values(ascending=False).index

            fig.update_layout(xaxis={'categoryorder':'array', 'categoryarray':zone_order},yaxis_title="Percentage (%)")
            st.plotly_chart(fig, use_container_width=True)

            top_view = temp.loc[temp.groupby('zone')['percentage'].idxmax()]

            st.subheader("🔥 Dominant View per Zone")

            for _, row in top_view.iterrows():
                st.write(f"{row['zone']} → {row['Overlooking_Categories']} ({row['percentage']:.1f}%)")

    elif section == "Advanced":
        st.markdown("### 🧠 Advanced Analytics")
        st.info("This section is under development. Stay tuned for more insights and interactive tools to explore the Bhopal real estate market!")


elif st.session_state.view == "colony":

    st.subheader("📍 Colony-wise Analysis")

    # =========================
    # FILTER
    # =========================
    selected_option = st.selectbox(
        "Select Property Type",
        options=["Overall","Flats","Independent Houses"]
    )

    df = zone_df1.copy()

    if selected_option == "Flats":
        df = df[df['property_type']=='Flat']

    elif selected_option == "Independent Houses":
        df = df[df['property_type']=='House']

    # =========================
    # KPIs
    # =========================
    col1, col2, col3 = st.columns(3)

    col1.metric("🏘️ Total Colonies", df['colony'].nunique())
    col2.metric("💰 Avg Price", f"₹{int(df['price_outer'].median())} L")
    col3.metric("📏 Avg Area", f"{int(df['built_up_area'].median())} sqft")

    st.markdown("---")

    # =========================
    # TOP COLONIES (PRICE)
    # =========================
    st.markdown("### 💰 Top Expensive Colonies")

    temp = df.groupby('colony')['price_outer'].median().sort_values(ascending=False).head(15).reset_index()

    fig = px.bar(
        temp,
        y='colony',
        x='price_outer',
        color='price_outer',
        text='price_outer',
        orientation='h'
    )

    fig.update_layout(height=500)
    fig.update_traces(textposition='outside')

    st.plotly_chart(fig, use_container_width=True)

    # =========================
    # PRICE PER SQFT
    # =========================
    st.markdown("### 📏 Price per Sqft Comparison")

    temp = df.groupby('colony')['price_per_sqft'].median().sort_values(ascending=False).head(15).reset_index()

    fig = px.bar(
        temp,
        y='colony',
        x='price_per_sqft',
        color='price_per_sqft',
        text='price_per_sqft',
        orientation='h'
    )

    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

    # =========================
    # AREA DISTRIBUTION
    # =========================
    st.markdown("### 📐 Built-up Area Distribution")

    temp = df[df['built_up_area'] < 6000]

    fig = px.box(
        temp,
        x='colony',
        y='built_up_area',
        title="Area Spread by Colony"
    )

    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)

    # =========================
    # BEDROOM HEATMAP (PLOTLY)
    # =========================
    st.markdown("### 🛏️ Bedroom Distribution")

    temp = round(pd.crosstab(df['colony'], df['bedrooms_categories'], normalize='index') * 100,2)

    fig = px.imshow(
        temp,
        text_auto=True,
        color_continuous_scale='RdBu',
        aspect="auto"
        
    )

    fig.update_layout(height=800,      margin=dict(l=200, r=50, t=60, b=50))
    st.plotly_chart(fig, use_container_width=True)

    # =========================
    # PRICE vs AREA (INTERACTIVE)
    # =========================
    st.markdown("### 📊 Price vs Area (Interactive)")

    colony = st.selectbox("Select Colony", df['colony'].dropna().unique())

    temp = df[df['colony'] == colony]

    fig = px.scatter(
        temp,
        x='built_up_area',
        y='price_outer',
        trendline='ols',
        title=f"{colony} Price Trend"
    )

    st.plotly_chart(fig, use_container_width=True)

    # =========================
    # PRICE SENSITIVITY (🔥 GOLD FEATURE)
    # =========================
    st.markdown("### 📈 Price Increase per sqft (Colony-wise)")

    results = []

    for c in df['colony'].unique():
        temp = df[df['colony'] == c]

        if len(temp) < 5:
            continue

        X = temp['built_up_area']
        y = temp['price_outer']

        X = sm.add_constant(X)

        model = sm.OLS(y, X).fit()

        slope = model.params['built_up_area']

        results.append({
            'colony': c,
            'price_increase': slope
        })

    slope_df = pd.DataFrame(results).sort_values(by='price_increase', ascending=False).head(15)

    fig = px.bar(
        slope_df,
        x='price_increase',
        y='colony',
        orientation='h',
        color='price_increase',
        title="₹ Increase per sqft"
    )

    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

    # =========================
    # INSIGHTS (🔥 VERY IMPORTANT)
    # =========================
    st.markdown("### 🧠 Insights")

    if not slope_df.empty:
        best = slope_df.iloc[0]
        worst = slope_df.iloc[-1]

        st.success(f"🔥 Highest appreciation: {best['colony']} (₹{int(best['price_increase'])}/sqft)")
        st.warning(f"⚠️ Lowest appreciation: {worst['colony']} (₹{int(worst['price_increase'])}/sqft)")

    # Furnishing type distribution across colonies
    st.markdown("### 🪑 Furnishing Type Distribution across Colonies")
    # zone_df1['furnishing_type_categories'] = zone_df1['furnishing_type'].map({0:"Unfurnished",1:"Semifurnished",2:"Furnished"})
    
    temp = round(pd.crosstab(zone_df1['colony'],zone_df1['furnishing_type'],normalize='index') *100, 2)
    fig = px.imshow(
        temp,
        text_auto=True,
        color_continuous_scale='RdBu',
        aspect="auto"
        
    )

    fig.update_layout(height=800,      margin=dict(l=200, r=50, t=60, b=50))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Property Age Distribution across Colonies")
    temp = round(pd.crosstab(zone_df1['colony'],zone_df1['Property Age'],normalize='index') *100, 2)
    fig = px.imshow(
        temp,
        text_auto=True,
        color_continuous_scale='RdBu',
        aspect="auto"
        
    )

    fig.update_layout(height=800,      margin=dict(l=200, r=50, t=60, b=50))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Overlooking Distribution across Colonies")
    temp = round(pd.crosstab(zone_df1['colony'],zone_df1['Overlooking_Categories'],normalize='index') *100, 2)
    fig = px.imshow(
        temp,
        text_auto=True,
        color_continuous_scale='RdBu',
        aspect="auto"
        
    )

    fig.update_layout(height=800,      margin=dict(l=200, r=50, t=60, b=50))
    st.plotly_chart(fig, use_container_width=True)

