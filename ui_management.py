import streamlit as st
import pandas as pd  # Import pandas
# from mitosheet import sheet  # Comment out the Mito component import
from subscriptions import process_uploaded_file, validate_and_normalize, detect_recurring_charges, enrich_merchant_data
from supabase_integration import fetch_uploaded_files, fetch_file_data, fetch_stored_subscriptions, upload_enriched_data
from supabase_integration import fetch_users, fetch_logs, fetch_organizations, update_user, update_organization
from visual_analysis import visualize_feature_importance

def render_navigation():
    """
    Render the navigation sidebar.
    """
    return st.sidebar.radio(
        "Navigation",
        [
            "Dashboard",
            "Upload Files",
            "Upload Bank Data (MitoSheet)",
            "Recurring Charge Detection",
            "Visual Analysis",
            "Feedback",
            "Run CrewAI Logic",
        ]
    )

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

def render_upload_page(user):
    """
    Render the upload page for general files.
    """
    st.title("Upload Files for Processing")

    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    if uploaded_file:
        st.write("Processing file...")
        try:
            # Read the content of the uploaded file into a DataFrame
            data = pd.read_csv(uploaded_file)
            # Display a preview of the data
            st.write("Data Preview:")
            st.dataframe(data.head())
            # sheet(data)  # Comment out the MitoSheet component
            if st.button("Save and Process"):
                processed_data = process_uploaded_file(data, user)
                if processed_data is not None:
                    st.success("File processed successfully!")
                    st.dataframe(processed_data)
                    st.session_state.user = user  # Update session state
                else:
                    st.error("Error processing file: processed_data is None")
        except Exception as e:
            st.error(f"Error: {e}")

def render_upload_with_mitosheet(user):
    """
    Render the upload page with MitoSheet integration and guide users.
    """
    st.title("Upload Bank Transaction Files with MitoSheet")

    st.write("""
        **How to Use MitoSheet:**
        - Upload your bank transaction CSV file.
        - Use the MitoSheet editor to clean and normalize your data.
        - Ensure required columns are present: `Date`, `Amount`, `Merchant`, `Description`.
        - Save changes, and the normalized data will be stored in the system.
    """)

    uploaded_file = st.file_uploader("Upload Bank File (CSV)", type=["csv"])
    if uploaded_file:
        st.write("Opening MitoSheet for editing...")
        try:
            # Read the content of the uploaded file into a DataFrame
            data = pd.read_csv(uploaded_file)
            # Validate and normalize the file with MitoSheet
            # sheet(data)  # Comment out the MitoSheet component
            st.write("Data Preview:")
            st.dataframe(data.head())

            # Store edited data in Supabase
            response = process_uploaded_file(data, user)
            if response.status_code == 201:
                st.success("Edited data uploaded successfully!")
                st.session_state.user = user  # Update session state
            else:
                st.error("Failed to store data.")
        except Exception as e:
            st.error(f"Error processing file: {e}")

def render_recurring_charge_detection(user):
    """
    Render recurring charge detection results for uploaded data.
    """
    st.title("Recurring Charge Detection")

    files = fetch_uploaded_files(user.id)
    if not files:
        st.warning("No uploaded files found.")
        return

    st.write("Uploaded Files:")
    file_id = st.selectbox("Select a file to analyze", [file["id"] for file in files])
    if file_id:
        file_data = fetch_file_data(file_id)

        # Enrich merchant data if the 'Merchant' column is missing
        if "Merchant" not in file_data.columns:
            file_data = enrich_merchant_data(file_data)

        # Detect recurring charges
        detected_data = detect_recurring_charges(file_data)

        st.write("Recurring Charges Analysis:")
        st.dataframe(detected_data)

        # Store recurring charges if confirmed by the user
        if st.button("Store Recurring Charges"):
            upload_enriched_data(user.id, file_id, detected_data)
            st.success("Recurring charges stored successfully!")
            st.session_state.user = user  # Update session state

def render_stored_subscriptions(user):
    """
    Render validated subscriptions for a user.
    """
    st.title("Stored Subscriptions")

    subscriptions = fetch_stored_subscriptions(user.id)
    if subscriptions:
        st.write("Stored Validated Subscriptions:")
        st.dataframe(subscriptions)
    else:
        st.warning("No subscriptions found.")

def render_superuser_dashboard():
    """
    Render the superuser dashboard for managing the app.
    """
    st.title("Superuser Dashboard")

    section = st.sidebar.radio(
        "Superuser Actions",
        ["View Logs", "Manage Users", "Manage Organizations", "App Statistics"]
    )

    if section == "View Logs":
        st.subheader("App Logs")
        logs = fetch_logs()
        st.dataframe(logs)

    elif section == "Manage Users":
        st.subheader("Manage Users")
        users = fetch_users()
        st.dataframe(users)

        user_id = st.selectbox("Select User to Update", users["id"])
        is_active = st.selectbox("Active Status", [True, False])
        if st.button("Update User"):
            update_user(user_id, {"is_active": is_active})
            st.success("User updated successfully!")

    elif section == "Manage Organizations":
        st.subheader("Manage Organizations")
        organizations = fetch_organizations()
        st.dataframe(organizations)

        org_id = st.selectbox("Select Organization to Update", organizations["id"])
        is_active = st.selectbox("Active Status", [True, False])
        if st.button("Update Organization"):
            update_organization(org_id, {"is_active": is_active})
            st.success("Organization updated successfully!")

    elif section == "App Statistics":
        st.subheader("App Statistics")
        users = fetch_users()
        organizations = fetch_organizations()

        st.metric("Total Users", len(users))
        st.metric("Total Organizations", len(organizations))

def render_enriched_merchant_data(data):
    """
    Render the enriched merchant data.
    """
    st.title("Enriched Merchant Data")
    st.dataframe(data)
