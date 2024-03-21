import streamlit as st
import pandas as pd
import json

# Set page config
st.set_page_config(
    page_title="PerilMapp", 
    page_icon="🖼️", 
    initial_sidebar_state="collapsed",
    layout="wide"
)

def render_header():
    st.title("Visulaisations et Cartes")

def main():
    render_header()
    with open("map_catnat.html", "r") as f:
        html_content = f.read()

    # Create a large container
    with st.container(height=600):
        # Create two columns
        col1, col2 = st.columns([3, 2])

        # Display the HTML map in the first column
        with col1:
            st.components.v1.html(html_content, width=800, height=600)

        # Write the description in the second column
        with col2:
            st.write("## Map Description")
            st.write("Our newly developed interactive map provides valuable insights into flood risk based on frequency. Whether you’re a homeowner, insurer, or policy decision-maker, this map empowers you to make informed choices")

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

# Additional content goes here
st.sidebar.markdown("# Risque Selection")
_list = ['Innondation', 'Tempête', 'Sécheresse']
ticker = st.sidebar.selectbox("Choose Your Risk", _list)

# Add images in the sidebar
st.sidebar.image("IMAGE/credit-agricole-nord-de-france.jpg", width=150)
st.sidebar.image("IMAGE/IESEG.png", width=150)



