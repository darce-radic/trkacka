import json
import streamlit as st
import json
from supabase_integration import update_keywords, update_thresholds
from ml_model import retrain_model
from supabase_integration import update_keywords

# Load or initialize thresholds
try:
    with open("data/thresholds.json", "r") as f:
        RENEWAL_THRESHOLDS = json.load(f)
except FileNotFoundError:
    RENEWAL_THRESHOLDS = {
        "Daily": 1,
        "Weekly": 7,
        "Bi-Weekly": 15,
        "Monthly": 45,
        "Quarterly": 90,
        "Yearly": 370,
    }
    
    with open("data/keywords.json", "r") as f:
        CATEGORY_KEYWORDS = json.load(f)
except FileNotFoundError:
    CATEGORY_KEYWORDS = {
        "Entertainment": ["Netflix", "Spotify", "Hulu"],
        "Utilities": ["Electric", "Water", "Gas"],
        "Others": []
    }


def adjust_keywords():
    """
    Allow users to add new keywords dynamically.
    """
    st.title("Adjust Keywords")
    category = st.selectbox("Select a category:", ["Entertainment", "Utilities", "Others"])
    new_keyword = st.text_input("Enter a new keyword:")
    if st.button("Add Keyword"):
        update_keywords(category, new_keyword)
        st.success(f"Keyword '{new_keyword}' added to category '{category}'!")

def adjust_thresholds():
    """
    Allow users to refine thresholds for subscription patterns.
    """
    global RENEWAL_THRESHOLDS
    st.title("Adjust Renewal Thresholds")
    for pattern, threshold in RENEWAL_THRESHOLDS.items():
        new_threshold = st.number_input(f"Threshold for {pattern} (days)", value=threshold, min_value=1)
        RENEWAL_THRESHOLDS[pattern] = new_threshold

    update_thresholds(RENEWAL_THRESHOLDS)
    st.success("Thresholds updated!")
    


def gather_feedback(data):
    """
    Gather user feedback and retrain the ML model.
    """
    st.title("User Feedback for Categorization")

    for index, row in data.iterrows():
        new_category = st.text_input(f"Category for {row['Merchant']}:", value=row['Category'])
        data.at[index, 'Category'] = new_category

    if st.button("Submit Feedback"):
        train_model(data, features=['Merchant', 'Description'], target='Category')
        update_keywords(data['Category'].unique())
        st.success("Feedback submitted and model retrained!")
