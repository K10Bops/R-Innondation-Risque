import folium
from folium.plugins import MarkerCluster
import pandas as pd
import streamlit as st
import os
from streamlit.components.v1 import html

# Set page config
st.set_page_config(
    page_title="Data App",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Define a function to set the app's theme and aesthetics
def set_theme():
    # Define custom colors
    primary_color = "#1b9e77"
    background_color = "#f0f2f6"
    secondary_background_color = "#ffffff"
    text_color = "#333333"
    top_ranked_color = "#f63366"  # Streamlit pink for top-ranked predictions
    
    # Set the theme using Streamlit's custom CSS
    st.markdown(
        f"""
        <style>
        .reportview-container {{
            background-color: {background_color};
            color: {text_color};
        }}
        .sidebar .sidebar-content {{
            background-color: #f63366;  /* Change sidebar background color */
            color: white;
        }}
        .stTabs > .tabbable > .nav-tabs > li > a {{
            color: {text_color};
        }}
        .stTabs > .tabbable > .tab-content {{
            background-color: {secondary_background_color};
        }}
        .bar:hover {{
            fill: {top_ranked_color};  /* Change bar color on hover */
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Load the geo_data DataFrame from the CSV file
geo_data_file_path = os.path.join('tables', 'geo_data.csv')
geo_data = pd.read_csv(geo_data_file_path)

# Define the main function
def main():
    set_theme()  # Apply the custom theme

    # Create tabs for navigation
    tab1, tab2, tab3 = st.tabs(["Cartes", "Visualisations", "Commune_Sélectionner"])

    # Tab 1: Maps
    with tab1:
        st.header(f"Cartes de Inondation")
    
        # Function to create a risk map for selected years, departments, and insee_codes
        def create_risk_map_for_year_department_insee(geo_data, years, departments, insee_codes):
            """
            Create a risk map for selected years, departments, and insee_codes.
    
            Parameters:
            geo_data (DataFrame): DataFrame containing the geo data including latitude, longitude, year, department, and insee.
            years (list): The years for which to create the map.
            departments (list): The departments for which to create the map.
            insee_codes (list): The insee codes for the communes.
    
            Returns:
            folium.Map or None: A Folium map with markers for the selected years, departments, and insee_codes, or None if data is invalid.
            """
            # Filter the DataFrame for the selected years, departments, and insee_codes
            selected_data = geo_data[(geo_data['year'].isin(years)) & (geo_data['department'].isin(departments))]
    
            # Ensure the filtered data contains the necessary columns and no NaNs
            if selected_data.empty or selected_data[['latitude', 'longitude']].isnull().any().any():
                return None
    
            # Calculate the mean latitude and longitude for the selected insee_codes
            mean_lat = selected_data['latitude'].mean()
            mean_lon = selected_data['longitude'].mean()
    
            # Initialize a map centered around the mean location
            m1 = folium.Map(location=[mean_lat, mean_lon], zoom_start=10)
    
            # Use MarkerCluster to cluster the markers for better visualization
            marker_cluster = MarkerCluster().add_to(m1)
    
            # Check if multiple years are selected
            multiple_years = len(years) > 1
    
            # Add markers to the map with tooltips and customized popups
            for idx, row in selected_data.iterrows():
                # Create the popup content with commune name, risk score, and year if multiple years are selected
                popup_content = f"<strong>{row['nom_commune']}</strong><br>Risk Score: {row['risk_score']}"
                if multiple_years:
                    popup_content += f"<br>Year: {row['year']}"
                
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=folium.Popup(popup_content, max_width=300),
                    tooltip=row['nom_commune']
                ).add_to(marker_cluster)
    
            return m1
    
        # Set the theme and aesthetics
        set_theme()
    
        # Sidebar for filters
        st.sidebar.header("Filters")
    
        # Year filter with limit
        year_options = geo_data['year'].unique().tolist()
        selected_years = st.sidebar.multiselect("Select Year(s)", options=year_options, default=[2022])
        if len(selected_years) > 3:
            st.sidebar.warning("Choice of years limit reached. You can select up to 3 years.")
            selected_years = selected_years[:3]
    
        # Department filter
        department_options = geo_data['department'].unique().tolist()
        selected_departments = st.sidebar.multiselect("Select Department(s)", options=department_options, default=["Nord"])
    
        # Filter insee options based on selected departments
        if selected_departments:
            filtered_insee_options = geo_data.loc[geo_data['department'].isin(selected_departments), 'insee'].unique().tolist()
        else:
            filtered_insee_options = geo_data['insee'].unique().tolist()
    
        # Multiselect to choose communes
        selected_communes = st.sidebar.multiselect("Select Communes", options=filtered_insee_options, default=[])
    
        # Create the map with selected filters
        if selected_communes:
            filtered_geo_data = geo_data[geo_data['insee'].isin(selected_communes)]
        else:
            filtered_geo_data = geo_data
            
        # Display a message if no communes are selected (default state)
        if not selected_communes:
            st.sidebar.write("All Communes chosen by default")
            
    
        # Create the map with selected filters
        folium_map = create_risk_map_for_year_department_insee(filtered_geo_data, selected_years, selected_departments, selected_communes)
    
        # Display the map or a message if there are NaNs or no data
        if folium_map:
            html(folium_map._repr_html_(), width=1000, height=800, scrolling=True)
        else:
            st.write("Sorry either the values are Null, or this data does not exist.")


         
##################################################        
##################################################        
    # Tab 2: Visualisations
    with tab2:
        st.header(f"Visualisations de Inondation")
        
        # Define the function to display visualizations
        def display_visualization(disaster):
            # Maps the disaster type to its corresponding visualization files
            visualization_files = {
               'inondation': ['heatmap_inondation','monthly_distribution_2018_2013', 'top_10_nord','top_10_Pas_de_calais', 'top10_inondations_par_departement_map']
            }    
        
            # Define the directory containing the visualizations
            dir_path = '.'
        
            # Loop through each visualization file and display it
            for vis in visualization_files.get(disaster, []):
                try:
                    # Construct the full file path
                    file_path = os.path.join(dir_path, f"{vis}.html")
                    # Read the HTML content from the file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    # Display the HTML content
                    html(html_content, width=1200, height=500, scrolling=True)
                except FileNotFoundError:
                    # Handle the case when the file is not found
                    st.error(f"Le fichier de visualisation {vis} n'a pas été trouvé.")

        
        # Call the function to display visualizations
        display_visualization('inondation')
        
        
        # Load and display the table below all the visualizations
        st.header("Cout moyen des sinistres des principales régions inondées")
        table_path = os.path.join('tables', 'agg_filtered_df_grouped2.csv')
        df_table = pd.read_csv(table_path)
        st.write(df_table)
        
        
        
        
        
        
        
        
if __name__ == "__main__":
    main()
