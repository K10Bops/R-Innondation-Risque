import streamlit as st
import pandas as pd
import json
import zipfile
import os

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
    st.sidebar.image("Image/France.jpg", use_column_width=True)

    # Define the list of tickers
    ticker_list = ['DVF', 'CATNET']

    # Add a select box for choosing the ticker in the sidebar
    ticker = st.sidebar.selectbox("Choix donnés", ticker_list)

    # Determine which map HTML file to display based on the selected ticker
    map_html_file = None  # Initialize map_html_file variable
    if ticker == 'DVF':
        # Unzip the HTML file if it's in a zip archive
        map_zip_file = "map_DVF_Adresse.zip"
        with zipfile.ZipFile(map_zip_file, 'r') as zip_ref:
            zip_ref.extractall("map_DVF_Adresse")
        map_html_file = "map_DVF_Adresse/map_DVF_Adresse.html"
    elif ticker == 'CATNET':
        map_html_file = "map_catnat.html"
        # Display another dropdown for selecting risks
        selected_risk = st.sidebar.selectbox("Select Risk", ['Inondation', 'Tempête', 'Sécheresse'])

    if map_html_file:
        # Load and display the selected map HTML file
        with open(map_html_file, "r") as f:
            html_content = f.read()

        # Create a large container with custom CSS for height
        st.markdown(
            """
            <style>
            .custom-container {
                height: 600px;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        # Display the HTML map within the custom container
        st.markdown(
            f'<div class="custom-container">{html_content}</div>',
            unsafe_allow_html=True
        )

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

if __name__ == "__main__":
    main()
