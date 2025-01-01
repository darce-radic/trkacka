import streamlit as st
from supabase_integration import fetch_uploaded_files, fetch_stored_subscriptions, fetch_organizations

def render_dashboard(user):
    """
    Render the dashboard page with user and organization information.
    """
    st.title("Dashboard")

    # Fetch organization information
    organization = fetch_organizations().loc[fetch_organizations()["id"] == user.organization_id].iloc[0]

    # Fetch number of files loaded
    files = fetch_uploaded_files(user.id)
    num_files = len(files)

    # Fetch subscriptions
    subscriptions = fetch_stored_subscriptions(user.id)
    num_subscriptions = len(subscriptions)

    # Display information
    st.subheader("User Information")
    st.write(f"Email: {user.email}")
    st.write(f"Organization: {organization['name']}")

    st.subheader("Statistics")
    st.metric("Number of Files Loaded", num_files)
    st.metric("Subscriptions Found", num_subscriptions)
    st.metric("Cancelled Subscriptions", len(subscriptions[subscriptions["status"] == "cancelled"]))
