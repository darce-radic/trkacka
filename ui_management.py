import streamlit as st
from mitosheet import sheet
from subscriptions import process_uploaded_file, validate_and_normalize, detect_recurring_charges
from supabase_integration import fetch_uploaded_files, fetch_file_data, fetch_stored_subscriptions
from supabase_integration import fetch_users, fetch_logs

from visual_analysis import visualize_feature_importance


def render_navigation():
    """
    Render the navigation sidebar.
    """
    return st.sidebar.radio(
        "Navigation",
        [
            "Upload Files",
            "Upload Bank Data (MitoSheet)",
            "Recurring Charge Detection",
            "Visual Analysis",
            "Feedback",
            "Run CrewAI Logic",
        ]
    )


def render_upload_page(user):
    """
    Render the upload page for general files.
    """
    st.title("Upload Files for Processing")

    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    if uploaded_file:
        st.write("Processing file...")
        try:
            processed_data = process_uploaded_file(uploaded_file, user)
            st.success("File processed successfully!")
            st.dataframe(processed_data)
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
            # Validate and normalize the file with MitoSheet
            edited_data = validate_and_normalize_with_mitosheet(uploaded_file)

            # Store edited data in Supabase
            response = process_uploaded_file(edited_data, user)
            if response.status_code == 201:
                st.success("Edited data uploaded successfully!")
            else:
                st.error("Failed to store data.")
        except Exception as e:
            st.error(f"Error processing file: {e}")


def render_recurring_charge_detection(user):
    """
    Render recurring charge detection results for uploaded data.
    """
    st.title("Recurring Charge Detection")

    files = fetch_uploaded_files(user["id"])
    if files.empty:
        st.warning("No uploaded files found.")
        return

    st.write("Uploaded Files:")
    file_id = st.selectbox("Select a file to analyze", files["id"])
    if file_id:
        file_data = fetch_file_data(file_id)

        # Detect recurring charges
        detected_data = detect_recurring_charges(file_data)

        st.write("Recurring Charges Analysis:")
        st.dataframe(detected_data)

        # Store recurring charges if confirmed by the user
        if st.button("Store Recurring Charges"):
            store_recurring_charges(user["id"], detected_data)
            st.success("Recurring charges stored successfully!")

from supabase_integration import fetch_logs, fetch_users, fetch_organizations, update_user, update_organization

def render_stored_subscriptions(user):
    """
    Render validated subscriptions for a user.
    """
    st.title("Stored Subscriptions")

    subscriptions = fetch_stored_subscriptions(user["id"])
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
