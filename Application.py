#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st

def main():
    st.title("Folium Map Visualization")

    # Load the HTML file
    with open("map.html", "r") as f:
        html_content = f.read()

    # Display the HTML content
    st.components.v1.html(html_content, width=800, height=600)

if __name__ == "__main__":
    main()


# In[ ]:




