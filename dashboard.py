import streamlit as st
import pandas as pd
from supabase_integration import fetch_uploaded_files, fetch_stored_subscriptions, fetch_organizations

def render_dashboard(user):
    """
    Render the dashboard page with user and organization information.
    """
    st.title("Dashboard")

    # Fetch organization information
    organizations_df = fetch_organizations()
    st.write("Organizations DataFrame:", organizations_df)  # Debugging information
    if "id" not in organizations_df.columns:
        st.error("The 'id' column is missing from the organizations DataFrame.")
        return

    organization = organizations_df.loc[organizations_df["id"] == user.organization_id].iloc[0]

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

    # Visualization options
    st.subheader("Visualizations")

    # Example: Line chart of subscriptions over time
    if not subscriptions.empty:
        subscriptions["Date"] = pd.to_datetime(subscriptions["Date"])
        subscriptions.set_index("Date", inplace=True)
        st.line_chart(subscriptions["Amount"])

    # Example: Bar chart of subscriptions by category
    if "Category" in subscriptions.columns:
        category_counts = subscriptions["Category"].value_counts()
        st.bar_chart(category_counts)

    # Example: Area chart of spending trends
    if not subscriptions.empty:
        subscriptions["Month"] = subscriptions.index.to_period("M")
        monthly_spending = subscriptions.groupby("Month")["Amount"].sum()
        st.area_chart(monthly_spending)
