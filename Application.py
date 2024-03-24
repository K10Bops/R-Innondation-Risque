import streamlit as st
import os

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
    
    # Set the theme using Streamlit's custom CSS
    st.markdown(
        f"""
        <style>
        .reportview-container {{
            background-color: {background_color};
            color: {text_color};
        }}
        .sidebar .sidebar-content {{
            background-color: {primary_color};
            color: white;
        }}
        .stTabs > .tabbable > .nav-tabs > li > a {{
            color: {text_color};
        }}
        .stTabs > .tabbable > .tab-content {{
            background-color: {secondary_background_color};
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Define the main function
def main():
    set_theme()  # Apply the custom theme

    # Sidebar selections for disasters
    disaster = st.sidebar.selectbox(
        "Sélectionner le type de catastrophe", 
        ['Inondation', 'Sécheresse'],
        index=0
    )

    # Create tabs for navigation
    tab1, tab2 = st.tabs(["Cartes", "Visualisations"])

    # Tab 1: Maps
    with tab1:
        st.header(f"Cartes de {disaster}")

        # Define the list of levels
        levels = ['Commune', 'Adresse']
        level = st.sidebar.selectbox("Sélectionner le niveau de la carte", levels)
        
        # Determine the map file based on the selections
        map_html_file = f"{level} level {disaster.lower()} map.html"
        # Display the map
        display_map(map_html_file)

    # Tab 2: Visualisations
    with tab2:
        st.header(f"Visualisations de {disaster}")
        # Determine the visualization files based on the disaster
        display_visualization(disaster.lower())

# Function to display the map
def display_map(map_html_file):
    try:
        with open(map_html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        st.components.v1.html(html_content, width=1400, height=800, scrolling=True)
    except FileNotFoundError:
        st.error("Le fichier de la carte n'a pas été trouvé.")

# Function to display visualizations
def display_visualization(disaster):
    # Maps the disaster type to its corresponding visualization files
    visualization_files = {
        'inondation': ['heatmap_inondation', 'barchart_inondation', 'top10_inondation'],
        'sécheresse': ['heatmap_secheresse', 'barchart_secheresse', 'top10_secheresse']
    }
    
    for vis in visualization_files.get(disaster, []):
        try:
            file_path = f"{vis}.html" #Update with correct file path
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            st.components.v1.html(html_content, width=1200, height=500, scrolling=True)
        except FileNotFoundError:
            st.error(f"Le fichier de visualisation {vis} n'a pas été trouvé.")

if __name__ == "__main__":
    main()


