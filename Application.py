import streamlit as st
import pandas as pd
import json

# Set page config
st.set_page_config(
    page_title="prettymapp", 
    page_icon="🖼️", 
    initial_sidebar_state="collapsed",
    layout="wide"
)

def render_header():
    st.title("Visulaisations et Cartes")

def main():
    render_header()

    # Add France.jpg image in the sidebar
    st.sidebar.image("Image/Departement_Pas-de-Calais.png", use_column_width=True)

    # Define the list of tickers
    ticker_list = ['De valeurs foncières', 'Catastrophes naturelles']

    # Add a select box for choosing the ticker in the sidebar
    ticker = st.sidebar.selectbox("Choix donnés", ticker_list)

    # Determine which map HTML file to display based on the selected ticker
    if ticker == 'De valeurs foncières':
        map_html_file = "map_DVF_Adresse.html"
    elif ticker == 'Des catastrophes naturelles':
        map_html_file = "map_catnat.html"
        # Display another dropdown for selecting risks
        selected_risk = st.sidebar.selectbox("Select Risk", ['Inondation', 'Tempête', 'Sécheresse'])

    # Load and display the selected map HTML file
    with open(map_html_file, "r") as f:
        html_content = f.read()

    # Create a large container
    with st.container(height=600):
        # Display the HTML map
        st.components.v1.html(html_content, width=800, height=600)

if __name__ == "__main__":
    main()

# Green and grey colors
green_color = "#1b9e77"
grey_color = "#757575"

# Set background color
st.markdown(
    f"""
    <style>
    .reportview-container {{
        background-color: {grey_color};
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Set sidebar color
st.markdown(
    f"""
    <style>
    .sidebar. {{
        background-color: {green_color};
        color: white;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Set elements color
st.markdown(
    f"""
    <style>
    div.stButton > button:first-child {{
        background-color: {green_color};
    }}
    div.stSelectbox > div.stSelectbox-placeholder {{
        color: {grey_color};
    }}
    div.stSelectbox > div.stSelectbox-options {{
        color: black;
    }}
    </style>
    """,
    unsafe_allow_html=True
)


