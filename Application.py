import folium
import pandas as pd
import streamlit as st
from streamlit.components.v1 import html
import os
import plotly.graph_objs as go
import plotly.offline as pyo
import datetime
import plotly.express as px
from folium.plugins import MarkerCluster
import time
import geopandas as gpd

from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)


# Get the directory of the current script
current_dir = os.path.join('tables')




# File paths relative to the current script
file_names = [
    'test_set_modarate_scenario.csv',
    'test_set_optimist_scenario.csv',
    'test_set_pessimist_scenario.csv'
]

# Construct the full file paths
file_paths = [os.path.join(current_dir, file_name) for file_name in file_names]

# Reading CSV files
dataframes = [pd.read_csv(file) for file in file_paths]

# Accessing individual dataframes
moderate_scenario_df = dataframes[0]
optimist_scenario_df = dataframes[1]
pessimist_scenario_df = dataframes[2]

# Load the geo_data DataFrame from the CSV file
geo_data_file_path = os.path.join('tables', 'geo_data.csv')
geo_data = pd.read_csv(geo_data_file_path)

dvf_path = os.path.join('tables', 'dvf_yearly.csv')
dvf_yearly = pd.read_csv(dvf_path)

basetable_path = os.path.join('tables', 'basetable.csv')
basetable = pd.read_csv(basetable_path)
# =============================================================================



# DATA Mutation
# =============================================================================
# Merge moderate_scenario_df with geo_data on 'insee'
moderate_scenario_df = pd.merge(moderate_scenario_df, geo_data[['insee', 'nom_commune']], on='insee', how='left')
moderate_scenario_df.rename(columns={'nom_commune': 'id_nom'}, inplace=True)

# Merge optimist_scenario_df with geo_data on 'insee'
optimist_scenario_df = pd.merge(optimist_scenario_df, geo_data[['insee', 'nom_commune']], on='insee', how='left')
optimist_scenario_df.rename(columns={'nom_commune': 'id_nom'}, inplace=True)

# Merge pessimist_scenario_df with geo_data on 'insee'
pessimist_scenario_df = pd.merge(pessimist_scenario_df, geo_data[['insee', 'nom_commune']], on='insee', how='left')
pessimist_scenario_df.rename(columns={'nom_commune': 'id_nom'}, inplace=True)
# Merge moderate_scenario_df with geo_data on 'insee'
basetable = pd.merge(basetable, geo_data[['insee', 'nom_commune']], on='insee', how='left')

# Preprocess the 'last_occurrence' column to keep only the date part
geo_data['last_occurrence'] = geo_data['last_occurrence'].astype(str).str[:10]
geo_data['risk_score'] = geo_data['risk_score'].astype(int)
dvf_yearly['risk_score'] = dvf_yearly['risk_score'].astype(int)

moderate_scenario_df['risk_score'] = moderate_scenario_df['risk_score'].astype(int)
optimist_scenario_df['risk_score'] = optimist_scenario_df['risk_score'].astype(int)
pessimist_scenario_df['risk_score'] = pessimist_scenario_df['risk_score'].astype(int)


# =============================================================================
# FUNCTIONS
# =============================================================================
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
# Set page config
st.set_page_config(
    page_title="Data App",
    layout="wide",
    initial_sidebar_state="collapsed"
)
# =============================================================================
# Define the main function
def main():
    set_theme()  # Apply the custom theme

    # Create tabs for navigation
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Cartes", "Visualisations", "Risk Analysis", "Scenario", "Demandes de valeurs"])
    
    # Tab 1: Maps
    with tab1:
        st.header("Cartes de Inondation")

        # Function to create a risk map for selected year, departments, and insee_codes
        def create_risk_map_for_year_department_insee(geo_data, year, departments, insee_codes, selected_risk_scores):
            # Create a new column 'id_nom' by merging 'insee' and 'nom_commune'
            geo_data['id_nom'] = geo_data['insee'].astype(str) + ' : ' + geo_data['nom_commune']
            
            # Filter the DataFrame for the selected year, departments, risk_scores, and id_nom
            selected_data = geo_data[(geo_data['year'] == year) & 
                                     (geo_data['department'].isin(departments)) & 
                                     (geo_data['risk_score'].isin(selected_risk_scores)) &
                                     (geo_data['id_nom'].isin(insee_codes))]
            
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
            
            # Add markers to the map with tooltips and customized popups
            for idx, row in selected_data.iterrows():
                # Calculate the sum of 'num_cours_deau' and 'num_plan_deau'
                sum_value = row['num_cours_deau'] + row['num_plan_deau']
            
                # Get the corresponding last_occurrence for the commune
                last_occurrence = selected_data[selected_data['id_nom'] == row['id_nom']]['last_occurrence'].values[0]
            
                # Handle special case for 'last_occurrence'
                if last_occurrence == '1900-01-01':
                    last_occurrence_display = "No Occurrence within selected year"
                else:
                    last_occurrence_display = last_occurrence
            
                # Create the popup content with commune name, risk score, and the sum of 'num_cours_deau' and 'num_plan_deau'
                popup_content = (f"<strong>{row['nom_commune']}</strong><br>"
                                 f"Risk Score: {row['risk_score']}<br>"
                                 f"Sum of Water Sources: {sum_value}<br>"
                                 f"Last Occurrence: {last_occurrence_display}")
            
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=folium.Popup(popup_content, max_width=300),
                    tooltip=row['id_nom']
                ).add_to(marker_cluster)
            
            # Sample GeoDataFrame with mixed geometry types
            gdf = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
            
            # Filter the GeoDataFrame to include only France
            france_geometry = gdf[gdf['name'] == 'France']
            
            # Add the geometry for France to the map
            for idx, row in france_geometry.iterrows():
                folium.GeoJson(row['geometry']).add_to(m1)
            
            return m1
        
        # Function to create a filtered plot
        def create_filtered_plot(geo_data, department, selected_year_range):
            # Filter data for the specified department
            department_data = geo_data[geo_data['department'] == department]
        
            # Group by commune and calculate mean 'is_at_risk_Inondation'
            commune_risk_scores = department_data.groupby('nom_commune')['is_at_risk_Inondation'].mean()
        
            # Sort communes by mean risk score in descending order and select top 5
            top_communes = commune_risk_scores.sort_values(ascending=False).head(5).index.tolist()
        
            # Filter data for the top 5 communes
            filtered_df = department_data[department_data['nom_commune'].isin(top_communes)]
        
            # Filter data for the selected year range
            filtered_df = filtered_df[filtered_df['year'].between(selected_year_range[0], selected_year_range[1])]
        
            # Group by 'nom_commune' and 'year', calculate mean 'risk_score'
            grouped_df = filtered_df.groupby(['nom_commune', 'year'])['risk_score'].mean().reset_index()
        
            # Plot
            fig = px.line(grouped_df, x='year', y='risk_score', color='nom_commune', title=f'Change in Risk Score by Commune - {department}',
                          labels={'risk_score': 'Mean Risk Score', 'year': 'Year', 'nom_commune': 'Commune'})
        
            return fig
        
        # Define the default year range for the plot
        default_plot_year_range = (1990, 2000)
        
        # Determine the range of years in the dataset
        min_year = int(geo_data['year'].min())
        max_year = int(geo_data['year'].max())
        
        # Year filter with a dropdown
        col1, col2, col3 = st.columns(3)
        with col1:
            year_options = sorted(geo_data['year'].unique().tolist(), reverse=True)
            selected_year = st.selectbox("Select Year on Map", options=year_options)
        
        # Department filter
        with col2:
            department_options = geo_data['department'].unique().tolist()
            selected_departments = st.multiselect("Select Department(s)", options=department_options, default=["Nord"])
        
        # Multiselect to choose communes
        with col3:
            geo_data['id_nom'] = geo_data['insee'].astype(str) + ' : ' + geo_data['nom_commune']
            if selected_departments:
                filtered_insee_options = geo_data.loc[geo_data['department'].isin(selected_departments), 'id_nom'].unique().tolist()
            else:
                filtered_insee_options = geo_data['id_nom'].unique().tolist()
            
            if selected_departments:
                selected_communes = st.multiselect("Select Communes", options=filtered_insee_options, default=filtered_insee_options if not selected_departments else [])
                if not selected_communes:
                    st.caption("All Communes chosen by default")
        
        # Risk score checkboxes in horizontal format
        st.subheader("Select Risk Scores")
        
        
        risk_score_labels = {0: "Absent", 1: "Faible", 2: "Moyen", 3: "Élevé"}
        selected_risk_scores = []
        risk_score_cols = st.columns(len(risk_score_labels))
        for idx, (score, label) in enumerate(risk_score_labels.items()):
            if risk_score_cols[idx].checkbox(f"Risk Score: {label}", value=True):
                selected_risk_scores.append(score)
        
        # Ensure all communes are selected by default if none are selected
        if not selected_communes:
            selected_communes = filtered_insee_options

        # Create the map with selected filters
        filtered_geo_data = geo_data[
            (geo_data['id_nom'].isin(selected_communes)) & 
            (geo_data['risk_score'].isin(selected_risk_scores)) & 
            (geo_data['year'] == selected_year)
        ]
        
        # Progress bar for map loading
        progress_text = "MAP loading. Please wait."
        my_bar = st.progress(0, text=progress_text)
        
        for percent_complete in range(100):
            time.sleep(0.01)
            my_bar.progress(percent_complete + 1, text=progress_text)
        
        # Load the map
        folium_map = create_risk_map_for_year_department_insee(filtered_geo_data, selected_year, selected_departments, selected_communes, selected_risk_scores)
        
        st.divider() # a horizontal rule
        
        # Display the map or a message if there are NaNs or no data
        if folium_map:
            st.components.v1.html(folium_map._repr_html_(), width=1350, height=600, scrolling=True)
        else:
            st.write("Sorry either the values are Null, or this data does not exist.")
        
        my_bar.empty()
        # Add the "Reset Page" button with a unique key
        if st.button("Reset Page", key="reset_tab2"):
            st.experimental_rerun()
        
        
        st.divider() # a horizontal rule
        
        


         
            
            
        
        






         
##################################################        
##################################################        
    # Tab 2: Visualisations
    with tab2:
        st.header(f"Visualisations de Inondation")
        
        # Define the function to display visualizations
        def display_visualization(disaster):
            # Maps the disaster type to its corresponding visualization files
            visualization_files = {
               'inondation': ['heatmap_inondation','monthly_distribution_2018_2023', 'top_10_nord','top_10_Pas_de_calais', ]
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


##################################################        
##################################################        
     # Tab 2: Visualisations
###############################################################################
    with tab3:
### 4 RISK VISAUALISATIONS
        
        # Slider for plot year range
        st.caption("Filter Range of Risk Year(s) for Plot")
        selected_plot_year_range = st.slider(
            "Select Year Range",
            min_value=min_year,
            max_value=max_year,
            value=default_plot_year_range,
            step=1,
            format="%d"
        )
        
        # Load the plot for "Nord"
        fig_nord = create_filtered_plot(geo_data, "Nord", selected_plot_year_range)
        
        # Load the plot for "Pas_De_Calais"
        fig_pas_de_calais = create_filtered_plot(geo_data, "Pas_De_Calais", selected_plot_year_range)
        
        # Display plots side by side
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig_nord, use_container_width=True, height=600)
                
        with col2:
            st.plotly_chart(fig_pas_de_calais, use_container_width=True, height=600)
        
        # Generate and display heatmaps
        top_communes_Nord = geo_data[geo_data['department'] == 'Nord'].nlargest(10, 'risk_score')
        top_communes_Pas_De_Calais = geo_data[geo_data['department'] == 'Pas_De_Calais'].nlargest(10, 'risk_score')

        top_communes_Nord_mean = top_communes_Nord.groupby('nom_commune')['risk_score'].mean()
        top_communes_Pas_De_Calais_mean = top_communes_Pas_De_Calais.groupby('nom_commune')['risk_score'].mean()

        top_communes_Nord_data = geo_data[geo_data['nom_commune'].isin(top_communes_Nord_mean.index)]
        top_communes_Pas_De_Calais_data = geo_data[geo_data['nom_commune'].isin(top_communes_Pas_De_Calais_mean.index)]

        heatmap_data_Nord = top_communes_Nord_data.pivot_table(values='risk_score', index='nom_commune', columns='year', fill_value=0)
        heatmap_data_Pas_De_Calais = top_communes_Pas_De_Calais_data.pivot_table(values='risk_score', index='nom_commune', columns='year', fill_value=0)

        colorscale = [
            [0, '#e0f3f8'],
            [1.0 / 1000, '#abd9e9'],
            [1.0 / 10, '#4dac26'],
            [1.0, '#08589e']
        ]

        fig_Nord = px.imshow(heatmap_data_Nord, aspect='auto',
                             title='Risk Score Intensity Over Time for Top Communes (Department Nord)',
                             labels={'color': 'risk_score'},
                             color_continuous_scale=colorscale)

        fig_Pas_De_Calais = px.imshow(heatmap_data_Pas_De_Calais, aspect='auto',
                                      title='Risk Score Intensity Over Time for Top Communes (Department Pas-de-Calais)',
                                      labels={'color': 'risk_score'},
                                      color_continuous_scale=colorscale)

        # Display heatmaps in Streamlit
        st.plotly_chart(fig_Nord, use_container_width=True, height=600)
        st.plotly_chart(fig_Pas_De_Calais, use_container_width=True, height=600)

        if st.button("Reset Page", key="reset_tab3"):
            st.experimental_rerun()        
        



# =============================================================================

    
    # Tab 4: Scenarios
    with tab4:
        st.subheader("Analyze Different Scenarios")
    
        # Default selected dataframe
        selected_df = st.selectbox("Select DataFrame", ["Moderate", "Optimistic", "Pessimistic"], index=1)
    
        # Get the selected dataframe and set the default descriptive text
        if selected_df == "Moderate":
            df = moderate_scenario_df
            scenario_name = "moderate"
            scenario_description = "moderate risk"
            expenditure_change = "wouldn’t change from"
            percentage_change = ""
        elif selected_df == "Optimistic":
            df = optimist_scenario_df
            scenario_name = "optimistic"
            scenario_description = "no expected flood risk"
            expenditure_change = "would decrease by 25% to reach"
            percentage_change = "decrease"
        else:
            df = pessimist_scenario_df
            scenario_name = "pessimistic"
            scenario_description = "low risk"
            expenditure_change = "would increase by 25% to reach"
            percentage_change = "increase"
        
        # Create default descriptive text for each scenario
        default_texts = {
            "Moderate": f"""
                - **Moderate Scenario Description**:
                  - Decrease risk score by 1 level except for 0 for 2024
                  - Increase the average claims expenditure by 25% for 2024
                """,
            "Optimistic": f"""
                - **Optimistic Scenario Description**:
                  - Decrease risk score by 1 level except for 0 for 2024
                  - Reduce the average claims expenditure by 25% for 2024
                """,
            "Pessimistic": f"""
                - **Pessimistic Scenario Description**:
                  - Keep the same risk score as 2023
                  - Keep the same average claims expenditure for 2023
                """
        }
    
        # Display the default descriptive text
        st.markdown(default_texts[selected_df])
    
        # Create filters
        with st.container():
            # Filter by 'id_nom'
            selected_id_nom = st.selectbox("Select an 'id_nom'", df["id_nom"].unique())
             
            # Filter the DataFrame based on the selected 'id_nom' and the year 2024
            selected_data = df[(df['id_nom'] == selected_id_nom) & (df['year'] == 2024)]
            
            # Check if the filtered data is not empty
            if not selected_data.empty:
                # Extract the relevant values
                risk_score = selected_data['risk_score'].values[0]
                estimated_expenditure = selected_data['Estimated Expenditure (€k)'].values[0]
                property_depreciation = selected_data['depreciation'].values[0]
            
                # Define risk description based on risk score
                if risk_score == 0:
                    risk_description = "no expected flood risk"
                elif risk_score == 1:
                    risk_description = "low risk"
                elif risk_score == 2:
                    risk_description = "moderate risk"
                else:
                    risk_description = "high risk"
            
                # Generate the dynamic text with bold fonts based on the selected scenario
                dynamic_text = {
                    "Moderate": f"""
                    In an **moderate** scenario, **{selected_id_nom}** would have a risk score of **{risk_score}**, indicating 
                    **{risk_description}**. The average expenditure **{expenditure_change}** **€{estimated_expenditure:,.2f}k**. 
                    In this situation, the average price of meter squared would change by **€{property_depreciation:,.2f}k** in 2024.
                    """,
                    "Optimistic": f"""
                    In an **optimistic** scenario, **{selected_id_nom}** would have a risk score of **{risk_score}**, indicating 
                    **{risk_description}**. The average expenditure **{expenditure_change}** **€{estimated_expenditure:,.2f}k**. 
                    In this situation, the average price of meter squared would change by **€{property_depreciation:,.2f}k** in 2024.
                    """,
                    "Pessimistic": f"""
                    In an **pessimistic** scenario, **{selected_id_nom}** would have a risk score of **{risk_score}**, indicating 
                    **{risk_description}**. The average expenditure **{expenditure_change}** **€{estimated_expenditure:,.2f}k**. 
                    In this situation, the average price of meter squared would change by **€{property_depreciation:,.2f}k** in 2024.
                    """
                }
            
                # Display the dynamic text based on the selected scenario
                st.markdown(dynamic_text[selected_df])
            else:
                st.write("No data available for the selected ID NOM and year 2024.")
    
            if st.button("Reset Page", key="reset_tab4"):
                st.experimental_rerun()
        
                st.divider()


        st.subheader("Historical Depreciation information")
############################    
        # Create pivot table
        pivot_df = basetable.pivot_table(index='year', columns='nom_commune', values='depreciation')
        # Plotting for Depreciation Since Last Year Over Time by INSEE Code
        fig1 = go.Figure()
    
        for column in pivot_df.columns:
            fig1.add_trace(go.Scatter(
                x=pivot_df.index,
                y=pivot_df[column],
                mode='lines+markers',
                name=f'Nom: {column}'
            ))
    
        fig1.update_layout(
            title='Depreciation by Commune',
            xaxis_title='Year',
            yaxis_title='Depreciation Since Last Year',
            legend_title='INSEE Nom',
            template='plotly_white',
            width = 1200
        )
    
        st.plotly_chart(fig1)
############################               
        # Calculating the average depreciation for each year
        average_depreciation = basetable.groupby('year')['depreciation'].mean()
    
        # Plotting for Average Depreciation Since Last Year Over Time
        fig2 = go.Figure()
    
        fig2.add_trace(go.Scatter(
            x=average_depreciation.index,
            y=average_depreciation.values,
            mode='lines+markers',
            name='Average Depreciation',
            line=dict(color='blue', width=2),
            marker=dict(symbol='circle', size=8, color='blue'),
        ))
    
        fig2.update_layout(
            title='Average Depreciation',
            xaxis_title='Year',
            yaxis_title='Average Depreciation',
            template='plotly_white',
            width = 1200
        )
    
        st.plotly_chart(fig2)
        
# =============================================================================        
    with tab5:
        st.header("2014-2023 valeurs")
        
        # Grouped data by 'risk_score'
        grouped_data = dvf_yearly.groupby('risk_score')
    
        # Plotting for Change in Average Prixm2Moyen by Risk Score Over the Years
        fig1 = go.Figure()
    
        # Iterate over each group
        for name, group in grouped_data:
            fig1.add_trace(go.Scatter(
                x=group['year'],
                y=group['Prixm2Moyen'],
                mode='lines+markers',
                name=f'Risk Score {name}'
            ))
    
        fig1.update_layout(
            title='Change in Average Prixm2Moyen by Risk Score Over the Years',
            xaxis_title='Year',
            yaxis_title='Average Prixm2Moyen',
            template='plotly_white',
            width = 1200
        )
    
        st.plotly_chart(fig1)
    
        # Compute the average Prixm2Moyen for risk scores other than 0
        average_other_risk = dvf_yearly[dvf_yearly['risk_score'] != 0].groupby('year')['Prixm2Moyen'].mean()
    
        # Grouped data by 'risk_score' including only risk score 0
        average_zero_risk = dvf_yearly[dvf_yearly['risk_score'] == 0].groupby('year')['Prixm2Moyen'].mean()
    
        # Plotting for Average Prixm2Moyen Over the Years for Different Risk Scores
        fig2 = go.Figure()
    
        # Plotting line for risk score = 0
        fig2.add_trace(go.Scatter(
            x=average_zero_risk.index,
            y=average_zero_risk.values,
            mode='lines',
            name='Average for risk score = 0',
            line=dict(color='blue')
        ))
    
        # Plotting line for other risk scores
        fig2.add_trace(go.Scatter(
            x=average_other_risk.index,
            y=average_other_risk.values,
            mode='lines',
            name='Average for other risk scores',
            line=dict(color='red')
        ))
    
        fig2.update_layout(
            title='Average Prixm2Moyen Over the Years for Different Risk Scores',
            xaxis_title='Year',
            yaxis_title='Average Prixm2Moyen',
            template='plotly_white',
            width = 1200
        )
    
        st.plotly_chart(fig2)    
        
if __name__ == "__main__":
    main()

