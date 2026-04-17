import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm

st.title("📊 Analytics Module")

# Load your data
zone_df = pd.read_csv("data/zona_analytics_df.csv")
zone_df1 = pd.read_csv("data/zone_analytics1.csv")
zone_df1['area_per_bedroom'] = zone_df1['built_up_area'] /( zone_df1['Total Floors'] * zone_df1['bedrooms'])
zone_df1 = zone_df1.sort_values('area_per_bedroom',ascending=False).iloc[2:]


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


# Now use state instead of button
if st.session_state.view == "zone":
    st.subheader("📍 Zone-wise Analysis")

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



    
    # price and build up size distibution in zones
    zone_avg = zone_df.groupby(["zone","latitude","longitude"]).agg(
    avg_price_per_sqft=("price_outer","median"),
    avg_build_up_area=("area","median"),
    total_listings=("price_per_sqft","count")
    ).reset_index()


    # Plot map
    fig = px.scatter_mapbox(
        zone_avg,
        lat="latitude",
        lon="longitude",
        size="avg_build_up_area",
        color="avg_price_per_sqft",
        hover_name="zone",
        hover_data={
            "avg_price_per_sqft": True,
            "avg_build_up_area": True,
            "total_listings": True,
            "latitude": False,
            "longitude": False
        },
        zoom=11,
        height=600,
        size_max=80
    )

    fig.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig, use_container_width=True)

    # property prices distribution in zones
    fig = px.box(zone_df1, x='price_outer',y='zone',color='zone',title='property price distribution in zones')
    st.plotly_chart(fig,use_container_width=True)

    # PPS distribution in zones
    fig = px.box(zone_df1, x='price_per_sqft',y='zone',color='zone',title='PPS distribution in zones')
    st.plotly_chart(fig,use_container_width=True)

    # Avg PPS in Zones
    # price per sqft comparision
    grps = zone_df1.groupby('zone')
    temp = grps['price_per_sqft'].mean().reset_index()
    fig = px.bar(temp,y='zone',x='price_per_sqft',title='Avg_PPS_In_Zones',color='price_per_sqft')
    st.plotly_chart(fig, use_container_width=True)

    # Build up area Distribuiton in zones
    fig = px.box(zone_df1, x='built_up_area',y='zone',color='zone',title='Built up area distribution acroos zones')
    st.plotly_chart(fig,use_container_width=True)

    # Properties Age Distribution in zones
    age_df = pd.crosstab(zone_df1['zone'],zone_df1['Property Age'],normalize='index').reset_index()
    fig = px.bar(
    age_df,
    y="zone",
    x=age_df.columns[1:],  # all age columns
    title="Property Age Distribution by Zone",
    )
    st.plotly_chart(fig, use_container_width=True)

    # Properties Furnishing type across zones
    age_df = pd.crosstab(index=zone_df1['zone'],columns=zone_df1['furnishing_type'],normalize='index').reset_index()
    fig = px.bar(
        age_df,
        y="zone",
        x=age_df.columns[1:],  # all age columns
        title="Furnishing type across  Zone",
    )
    st.plotly_chart(fig, use_container_width=True)

    # Overlooking categories distribution across zones
    temp = round(pd.crosstab(zone_df1['zone'],zone_df1['Overlooking_Categories'],normalize='index')*100,2)
    # sns.heatmap(temp, annot=True,fmt=".0f",cmap="coolwarm",cbar_kws={'label': 'Distribution in %'}  )
    
    # st.pyplot(plt)
    fig = px.imshow(
        temp,
        text_auto=True,
        color_continuous_scale="RdBu"
    )

    fig.update_layout(
        title="Overlooking Categories Distribution (In %) Across Zone",
        height=800,
        width=2000
    )

    st.plotly_chart(fig, use_container_width=True)

    # Luxiery score distribution across zones
    trp1 = zone_df1.groupby('zone')['luxury_score'].median().reset_index()
    fig = px.bar(trp1,y='zone',x='luxury_score',color='luxury_score',title='luxury_by_zone')

    st.plotly_chart(fig, use_container_width=True)
   
    # price vs built up area in zones
    fig = px.scatter(
        zone_df1,
        x="built_up_area",
        y="price_outer",
        facet_col="zone",
        facet_col_wrap=3,
        title="Area vs Price per Zone"
    )

    st.plotly_chart(fig)

    fig = px.scatter(zone_df1,x='price_outer',y='area_per_bedroom',facet_col="zone",
        facet_col_wrap=3,
        title="Area vs Price per Zone")
    st.plotly_chart(fig, use_container_width=True)

    # mean vs median property price 
    bar_df = zone_df.groupby(['zone','latitude','longitude']).agg(avg_property_price=('price_outer','mean'),median_property_price=('price_outer','median')).reset_index()
    fig = px.bar(
    bar_df,
    y="zone",
    x=["avg_property_price", "median_property_price"],
    barmode="group",
    title="Mean vs Median Property Price by Zone"
    )
    st.plotly_chart(fig, use_container_width=True,width=800,height=600)

    # heatmap for price based on property age across zones
    pivot = zone_df1.pivot_table(
        values="price_outer",
        index="zone",
        columns="Property Age",
        aggfunc="median"
    )

    sns.heatmap(pivot, annot=True,fmt=".0f",cmap="coolwarm",cbar_kws={'label': 'Price (in Lakhs)'}  )
    plt.title("Median Price based on Property Age across Zones")
    st.pyplot(plt)

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

    zone_df1['bedroom_group'] = zone_df1['bedrooms'].apply(bedroom_group)

    bedroom_price = zone_df1.groupby(['bedroom_group','zone'])['price_outer'].median().reset_index()
    order = ["1 BHK","2 BHK", "3 BHK", "4 BHK", "5 BHK", "6+ BHK"]

    bedroom_price['bedroom_group'] = pd.Categorical(
        bedroom_price['bedroom_group'],
        categories=order,
        ordered=True
    )

    bedroom_price = bedroom_price.sort_values('bedroom_group')

    fig = px.bar(
        bedroom_price,
        y="bedroom_group",
        x="price_outer",
        text="price_outer",
        title="Median Price by Bedroom Type",
        facet_col="zone",
        facet_col_wrap=3
    )

    fig.update_traces(textposition='outside')

    st.plotly_chart(fig, use_container_width=True)

    # property price based on furnishing type across zones
    temp = zone_df1.groupby(['zone','furnishing_type'])['price_outer'].median().reset_index()
    fig = px.bar(
        temp,
        y="zone",
        x="price_outer",
        text="price_outer",
        facet_col="furnishing_type",
        facet_col_wrap=3,
        title="Median Price by Furnishing Type across Zones"
    )

    fig.update_traces(textposition='outside')

    st.plotly_chart(fig, use_container_width=True)

    # Property price based on overlooking categories across zones
    temp = zone_df1.groupby(['zone','Overlooking_Categories'])['price_outer'].median().reset_index()
    fig = px.bar(
        temp,
        y="zone",
        x="price_outer",
        text="price_outer",
        title="Property Price Based on Overlooking Categories across Zones",
        facet_col="Overlooking_Categories",
        facet_col_wrap=2
    )

    fig.update_traces(textposition='outside')

    st.plotly_chart(fig, use_container_width=True)


elif st.session_state.view == "colony":
    st.subheader("📍 Colony-wise Analysis")

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

    # Property Prices
    temp = round(zone_df1.groupby('colony')['price_outer'].median().sort_values(ascending=False).reset_index(),0)
    fig = px.bar(temp,y='price_outer',x='colony',color='price_outer',text='price_outer',title='Median Property Price by Colony')
    fig.update_traces(textposition='outside')
    st.plotly_chart(fig, use_container_width=True)
    
    # Price per sqft
    temp = round(zone_df1.groupby('colony')['price_per_sqft'].median().sort_values(ascending=False).reset_index(),0)
    fig = px.bar(temp,y='price_per_sqft',x='colony',color='price_per_sqft',text='price_per_sqft',title='Median Price per Sqft by Colony')
    fig.update_traces(textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

    # Built_UP_area
    temp = zone_df1[zone_df1['built_up_area']<6000]

    order = (
    temp.groupby('colony')['built_up_area']
    .median()
    .sort_values(ascending=False)   # highest first
    .index
)
    # temp = round(zone_df1.groupby('colony')['built_up_area'].median().sort_values(ascending=False).reset_index(),0)
    fig = px.box(temp,x='colony',y='built_up_area',category_orders={'colony': order},title='Median Built-up Area by Colony')
    # fig = px.box(temp,y='built_up_area',x='colony',color='built_up_area',text='built_up_area',title='Median Built-up Area by Colony')
    # fig.update_traces(textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

    # Bedroom Categories distribution across colonies
    plt.figure(figsize=(6,8))
    temp = pd.crosstab(zone_df1['colony'],zone_df1['bedrooms_categories'],normalize='index') *100
    sns.heatmap(temp,annot=True,cmap="coolwarm",cbar_kws={'label': 'Distribution in %'})
    plt.title("Bedroom Categories distribution across Colonies")
    st.pyplot(plt)

    # Furnishing type distribution across colonies
    zone_df1['furnishing_type_categories'] = zone_df1['furnishing_type'].map({0:"Unfurnished",1:"Semifurnished",2:"Furnished"})
    plt.figure(figsize=(6,8))
    temp = pd.crosstab(zone_df1['colony'],zone_df1['furnishing_type_categories'],normalize='index') *100
    sns.heatmap(temp,annot=True,fmt="0.1f",cmap="coolwarm",cbar_kws={'label': 'Distribution in %'})
    plt.title("Furnished Properties distribution across Colonies")
    st.pyplot(plt)


    # Property Age
    plt.figure(figsize=(6,8))
    temp = pd.crosstab(zone_df1['colony'],zone_df1['Property Age'],normalize='index') *100
    sns.heatmap(temp,annot=True,fmt="0.1f",cmap="coolwarm",cbar_kws={'label': 'Distribution in %'})
    plt.title("Property Age distribution across Colonies")
    st.pyplot(plt)

    # Overlooking category
    plt.figure(figsize=(6,8))
    temp = pd.crosstab(zone_df1['colony'],zone_df1['Overlooking_Categories'],normalize='index') *100
    sns.heatmap(temp,annot=True,fmt="0.1f",cmap="coolwarm",cbar_kws={'label': 'Distribution in %'})
    plt.title("Overlooking Categories distribution across Colonies")
    st.pyplot(plt)

    # Median Property Price in colonies based on property age
    temp = pd.pivot_table(data=zone_df1,index='colony',columns='Property Age',values='price_outer',aggfunc='median').fillna(0)
    plt.figure(figsize=(6,8))
    sns.heatmap(temp,annot=True,fmt="0.1f",cmap="coolwarm",cbar_kws={'label': 'Median Price'})
    plt.title("Median Property Price in colonies based on property age")
    st.pyplot(plt)

    # Bedrooms category
    temp = pd.pivot_table(data=zone_df1,index='colony',columns='bedrooms_categories',values='price_outer',aggfunc='median').fillna(0)
    plt.figure(figsize=(6,8))
    sns.heatmap(temp,annot=True,fmt="0.1f",cmap="coolwarm",cbar_kws={'label': 'Median Price'})
    plt.title("Median Property Price in colonies based on bedrooms category")
    st.pyplot(plt)

    st.subheader("Property Price Trend Based on Built-up Area ")
    colony = st.selectbox("Select Colony", options=zone_df1['colony'].dropna().unique())

    temp = zone_df1[zone_df1['colony'] == colony]
    fig = px.scatter(temp, y='price_outer', x='built_up_area', trendline='ols',title=f'Price vs Built-up Area in {colony}')
    st.plotly_chart(fig, use_container_width=True)


    # price increase per unit area in colonies
    results = []

    for colony in zone_df1['colony'].unique():
        df = zone_df1[zone_df1['colony'] == colony]

        X = df['built_up_area']
        y = df['price_outer']

        X = sm.add_constant(X)  # adds intercept

        model = sm.OLS(y, X).fit()

        slope = model.params['built_up_area']

        results.append({
            'colony': colony,
            'price_increase_per_unit_area': slope
        })


    slope_df = pd.DataFrame(results).sort_values(by='price_increase_per_unit_area', ascending=False)

    fig = px.bar(
    slope_df,
    x='colony',
    y='price_increase_per_unit_area',
    title='Price Increase per Unit Area (Colony-wise)',
    color='price_increase_per_unit_area'
    )
    st.plotly_chart(fig, use_container_width=True)

    # furnishing type price 
    temp = pd.pivot_table(data=zone_df1,index='colony',columns='furnishing_type_categories',values='price_outer',aggfunc='median').fillna(0)
    plt.figure(figsize=(6,8))
    sns.heatmap(temp,annot=True,fmt="0.1f",cmap="coolwarm",cbar_kws={'label': 'Median Price'})
    plt.title("Median Property Price in colonies based on furnishing type")
    st.pyplot(plt)

else:
    st.markdown("### 📊 Quick Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("🏠 Total Properties", len(zone_df1))
    col2.metric("📍 Zones", zone_df1['zone'].nunique())
    col3.metric("🏘️ Colonies", zone_df1['colony'].nunique())

    st.markdown("---")

    st.markdown("### 💡 What you can explore")

    st.info("""
    🔹 Zone-wise Analytics → Understand price trends, area distribution, amenities  
    🔹 Colony-wise Analytics → Compare colonies, identify best locations  
    """)

    st.markdown("---")

    st.markdown("### 📈 Sample Insight")

    import plotly.express as px

    fig = px.histogram(
        zone_df1,
        x="price_outer",
        nbins=50,
        title="Overall Price Distribution"
    )

    st.plotly_chart(fig, use_container_width=True)




    # word cloud for each zone
    # remove nulls
#     t1 = zone_df.dropna(subset=['features'])
#     # convert list/string to clean text
#     t1['features_clean'] = t1['features'].astype(str)
#     t1['features_clean'] = t1['features_clean'].str.replace("[","").str.replace("]","").str.replace("/","").str.replace("'","").str.replace(",","")

#     zones = zone_df['zone'].dropna().unique()

# # Loop in chunks of 4 (for 4 columns)
# for i in range(0, len(zones), 4):
#     cols = st.columns(4)

#     for j, col in enumerate(cols):
#         if i + j < len(zones):
#             zone = zones[i + j]
#             zone_df_subset = t1[t1['zone'] == zone]

#             text = " ".join(t1['features_clean'])

#             with col:
#                 st.markdown(f"**{zone}**")

#                 if text.strip() == "":
#                     st.write("No data")
#                 else:
#                     wordcloud = WordCloud(
#                         width=1400,
#                         height=1200,
#                         background_color='white'
#                     ).generate(text)

#                     fig, ax = plt.subplots(figsize=(8,6))
#                     ax.imshow(wordcloud, interpolation='bilinear')
#                     ax.axis("off")
                    

#                     st.pyplot(fig)



# elif colony_btn:
#     st.subheader("🏘️ Colony-wise Analysis")

#     colony_data = df.groupby("colony")["price"].mean().reset_index()
#     st.write(colony_data)
#     st.bar_chart(colony_data.set_index("colony"))