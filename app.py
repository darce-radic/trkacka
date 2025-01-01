__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import streamlit as st
from supabase import create_client, Client
import ui_management  # Ensure this module exists and is correctly named
from subscriptions import process_uploaded_file, enrich_merchant_data
from supabase_integration import fetch_uploaded_files, fetch_stored_subscriptions, fetch_organizations, fetch_file_data, upload_enriched_data
from ml_model import train_model
from crewai_workflow import run_crewai_workflow  # Ensure this function is correctly defined and imported
from auth_management import authenticate_user, signup_user
import initialization
from dashboard import render_dashboard
import os

# Disable telemetry by setting an environment variable
os.environ["POSTHOG_DISABLE_TELEMETRY"] = "true"

# Load credentials from st.secrets
supabase_url = st.secrets["supabase"]["url"]
supabase_anon_key = st.secrets["supabase"]["anon_key"]
supabase: Client = create_client(supabase_url, supabase_anon_key)

# Service role client for admin operations
supabase_service_role_key = st.secrets["supabase"]["service_role_key"]
service_supabase = create_client(supabase_url, supabase_service_role_key)

# Set SERPER_API_KEY
os.environ["SERPER_API_KEY"] = "ebc89a77abd19b5367010c4a9470685832e547ef"

def render_run_crewai_logic(user):
    """
    Run CrewAI logic on stored data and display enriched merchant data.
    """
    st.title("Run CrewAI Logic with Merchant Enrichment")

    # Access user ID correctly
    user_id = user.id  # Correctly access the user ID

    files = fetch_uploaded_files(user_id)
    if not files:
        st.warning("No files available for processing.")
        return

    st.write("Available Files:")
    file_id = st.selectbox("Select a file to process", [file["id"] for file in files])
    if file_id:
        file_data = fetch_file_data(file_id)

        # Check for required columns before running the workflow
        required_columns = ["Date", "Amount", "Description"]
        missing_columns = [col for col in required_columns if col not in file_data.columns]
        if missing_columns:
            st.error(f"The following required columns are missing from the data: {', '.join(missing_columns)}")
            return

        # Convert data to JSON format
        data_json = file_data.to_json(orient="records")

        # Run CrewAI Workflow
        st.write("Processing CrewAI Workflow...")
        result = run_crewai_workflow(data_json)

        # Enrich and store data
        try:
            enriched_data = enrich_merchant_data(file_data)
            upload_enriched_data(user_id, file_id, enriched_data)

            # Display results
            st.write("CrewAI Result:")
            st.json(result)
            ui_management.render_enriched_merchant_data(enriched_data)
        except ValueError as e:
            st.error(f"Error enriching merchant data: {e}")

def main():
    # Call initialization steps
    initialization.initialize_app()

    if "user" not in st.session_state:
        st.session_state.user = None

    auth_action = st.sidebar.selectbox("Choose Action", ["Login", "Sign Up"])

    if auth_action == "Login":
        user = authenticate_user()
        if user:
            st.session_state.user = user
            st.experimental_set_query_params(rerun="true")
    elif auth_action == "Sign Up":
        signup_user()
        st.experimental_set_query_params(rerun="true")

    user = st.session_state.user

    if user:
        st.write(f"User object: {user}")  # Debugging information
        if hasattr(user, "is_superuser") and user.is_superuser:
            ui_management.render_superuser_dashboard()
        else:
            page = st.sidebar.radio(
                "Navigation",
                [
                    "Dashboard",
                    "Upload Files",
                    "Recurring Charge Detection",
                    "Subscription Validation",
                    "Cancelled Subscriptions",
                    # "Organization Summary",  # Comment out this line
                    "Train Model",
                    "Run CrewAI Logic"
                ]
            )

            if page == "Dashboard":
                render_dashboard(user)
            elif page == "Upload Files":
                ui_management.render_upload_page(user)
            elif page == "Recurring Charge Detection":
                ui_management.render_recurring_charge_detection(user)
            elif page == "Subscription Validation":
                ui_management.render_stored_subscriptions(user)  # Use the correct function
            elif page == "Cancelled Subscriptions":
                ui_management.render_cancelled_subscriptions(user.organization_id, user)
            # elif page == "Organization Summary":  # Comment out this line
            #     ui_management.render_organization_summary(user.organization_id)  # Comment out this line
            elif page == "Train Model":
                ui_management.render_train_model(user.organization_id)
            elif page == "Run CrewAI Logic":
                render_run_crewai_logic(user)

if __name__ == "__main__":
    main()

