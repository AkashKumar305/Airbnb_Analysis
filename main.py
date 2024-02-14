# Import Necessary Libraries
import streamlit as st 
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster

# Constants
PRICE_MIN, PRICE_MAX, SCORE_MIN, SCORE_MAX = 0, 50000, 0, 100
ALL_COUNTRIES = 'All'

def home():
    # Display information about the project
    st.title('Airbnb Analysis')
    st.subheader('Technologies used:')
    streamlit_list = "1. Streamlit\n2. Pandas\n3. Plotly\n4. Folium"
    st.write(streamlit_list)
    st.subheader('Domain:')
    st.write('Travel Industry, Property Management and Tourism')
    st.subheader('About:')
    st.write('''This project aims to analyze Airbnb data using MongoDB Atlas, perform data cleaning
            and preparation, develop interactive geospatial visualizations, and create dynamic
            plots to gain insights into pricing variations, availability patterns, and location-based
            trends.''')

def filter_data(df, price_range, rating_range, selected_country):
    # Filter data based on user input (price range, rating range, country)
    with st.sidebar:

        if selected_country != ALL_COUNTRIES:
            filtered_data = df[
                (df['price'] >= price_range[0]) & (df['price'] <= price_range[1]) &
                (df['review_scores'] >= rating_range[0]) & (df['review_scores'] <= rating_range[1]) &
                (df['country'] == selected_country)
            ]
        else:
            filtered_data = df[
                (df['price'] >= price_range[0]) & (df['price'] <= price_range[1]) &
                (df['review_scores'] >= rating_range[0]) & (df['review_scores'] <= rating_range[1])
            ]
    return filtered_data

def sort_df(filtered_data):
    # Sort the filtered data based on user-selected criteria
    with st.sidebar:
        selected_state = st.selectbox(
            "Sort By",('Price (Low to High)', 'Price (High to Low)',
                      'Ratings (Low to High)', 'Ratings (High to Low)')
        )
        
        df_to_sort = filtered_data[['name','price','review_scores','property_type','room_type','bedrooms','bathrooms']]

        if selected_state == 'Price (Low to High)':
            df_sorted = df_to_sort.sort_values('price', ascending = True)
        elif selected_state == 'Price (High to Low)':
            df_sorted = df_to_sort.sort_values('price', ascending = False)
        elif selected_state == 'Ratings (Low to High)':
            df_sorted = df_to_sort.sort_values('review_scores', ascending = True)
        elif selected_state == 'Ratings (High to Low)':
            df_sorted = df_to_sort.sort_values('review_scores', ascending = False)

    return df_sorted

def world_map_func(filtered_data):
    # Create a World Map
    world_map = folium.Map()

    world_map = folium.Map(
                location = [filtered_data['latitude'].mean(), filtered_data['longitude'].mean()],
                zoom_start = 1,
        )
            
    marker_cluster = MarkerCluster().add_to(world_map)
            
    for index, row in filtered_data.iterrows():
        folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=f"Price: {row['price']}$, Rating: {row['review_scores']}",
                    icon=folium.Icon(color='blue')
        ).add_to(marker_cluster)

    return world_map

def bar_chart(df, x, y, color = None, title = None, labels = None, category_orders = None, color_sequence = None, xaxis_title = None, yaxis_title = None, hover_name = None, hover_data = None, legend_title = None):
    # Create a Bar Chart
    fig = px.bar(df, 
             x = x, 
             y = x,
             color = color ,
             title = title,
             labels = labels,
             category_orders = category_orders,
             color_discrete_sequence = color_sequence,
             hover_name = hover_name,
             hover_data = hover_data)
    fig.update_layout(xaxis_title = xaxis_title, yaxis_title = yaxis_title, legend_title = legend_title)
    return fig

def pie_chart(df, values, names, title):
    # Create a Pie Chart
    fig = px.pie(df, values = values,names = names, title = title)
    fig.update_traces(textposition = 'inside', textinfo = 'percent+label')
    return fig

def mapbox(df, lat, lon, color, size, hover_name, style, title, color_sequence, height, width, zoom):
    # Create a Scatter-Mapbox Plot
    fig = px.scatter_mapbox(df, 
                            lat = lat, lon = lon, 
                            color = color, size = size,
                            hover_name = hover_name, 
                            mapbox_style = style,
                            title = title,
                            color_continuous_scale = color_sequence,
                            height = height, 
                            width = width,
                            zoom = zoom )
    return fig

def main():
    # Load Airbnb data from CSV file
    df = pd.read_csv(r'your_path\airbnb.csv')

    # Configure page layout
    st.set_page_config(layout = 'wide')

    # Sidebar menu options
    with st.sidebar:
        options = option_menu('Menu',['Home','Map Viz', 'Data Insights'])

    if options == 'Home':
        home()
        
    if options == 'Map Viz':
        # Display Airbnb Listings Distribution Map
        st.title('Airbnb Listings Distribution Map')
        
        # User input for filtering and sorting
        with st.sidebar:
            price_range = st.slider('Select Price Range: ', min_value=PRICE_MIN, max_value=PRICE_MAX, step=1000,
                                value=(PRICE_MIN, PRICE_MAX))

            rating_range = st.slider('Select Rating Range: ', min_value=SCORE_MIN, max_value=SCORE_MAX, step=10,
                                 value=(SCORE_MIN, SCORE_MAX))

            selected_country = st.selectbox('Select a Country:', [ALL_COUNTRIES] + list(df['country'].unique()))

        # Filter and sort data based on user input
        filtered_data = filter_data(df, price_range, rating_range, selected_country)
        
        st.write(f'Displaying {len(filtered_data)} listings in the selected range')

        df_sorted = sort_df(filtered_data)
        
        # Display selected listing and world map
        st.subheader('Selected Listing:')

        if len(filtered_data) != 0:

            st.dataframe(df_sorted)

            world_map = world_map_func(filtered_data)
            
            folium_static(world_map,width = 1050, height = 600)
        else:
            st.warning('No Data to Display')
        

    if options == 'Data Insights':
        # Display data insights using charts
        st.title('Data Insights')
        col1,col2 = st.columns(2)
        
        with col1:
            # Display bar chart and pie chart in the first column
            st.plotly_chart(bar_chart(df,'country','price','market','Country-wise Prices',{'price':'Average Price'},{'country':df.groupby('country')['price'].mean().sort_values(ascending = False).index},px.colors.qualitative.Set1,'Country','Average Price'))

            st.plotly_chart(pie_chart(df,values = 'availability_365',names = 'property_type', title = 'Availability Distribution by Property Type'))

        with col2:
            # Display bar chart in the second column
            st.plotly_chart(bar_chart(df,'property_type','price',None,'Property Type Vs Price',{'price':'Average Price'},{'property_type': df.groupby('property_type')['price'].mean().sort_values(ascending = False).index},px.colors.qualitative.Set2,'Property Type','Average Price'))
            
            st.plotly_chart(bar_chart(df,'availability_30','accommodates',None,'Availability Patterns and Demand Fluctuations',{'availability_30': 'Availability in the Last 30 Days', 'accommodates': 'Accommodates'},None,px.colors.qualitative.Set2,'Availability in the Last 30 Days','Accommodates','accommodates',{'availability_30': ':.2f'},'Accommodates'))

        # Display mapbox visualization
        st.plotly_chart(mapbox(df,'latitude','longitude','availability_365','availability_365','name',"carto-positron",'Occupancy Rates on the Map',px.colors.sequential.Plasma,800,1000,1))

# Call the main function
if __name__ == '__main__':
    main()
