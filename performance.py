import streamlit as st
import pandas as pd

@st.cache
def cache_data(data):
    """
    Cache frequently accessed data for performance.
    """
    return data

def paginate_data(data, page_size=10):
    """
    Paginate large datasets.
    """
    total_pages = (len(data) - 1) // page_size + 1
    page = st.number_input("Page", min_value=1, max_value=total_pages, step=1)
    start = (page - 1) * page_size
    end = start + page_size
    return data.iloc[start:end]
