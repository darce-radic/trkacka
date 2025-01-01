__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import streamlit as st
import ui_management
from subscriptions import process_uploaded_file, enrich_merchant_data
from supabase_integration import fetch_uploaded_files, upload_enriched_data
from ml_model import train_model
from crewai_workflow import run_crewai_workflow
from auth_management import authenticate_user, signup_user  # Import the necessary functions
import initialization  # Import the initialization module

def render_run_crewai_logic(user):
    """
    Run CrewAI logic on stored data and display enriched merchant data.
    """
    st.title("Run CrewAI Logic with Merchant Enrichment")

    files = fetch_uploaded_files(user["id"])
    if files.empty:
        st.warning("No files available for processing.")
        return

    st.write("Available Files:")
    file_id = st.selectbox("Select a file to process", files["id"])
    if file_id:
        file_data = fetch_uploaded_files(file_id)

        # Run CrewAI Workflow
        st.write("Processing CrewAI Workflow...")
        result = run_crewai_workflow(file_data)

        # Enrich and store data
        enriched_data = enrich_merchant_data(file_data)
        upload_enriched_data(user["id"], files.loc[file_id, 'file_name'], enriched_data)

        # Display results
        st.write("CrewAI Result:")
        st.json(result)
        ui_management.render_enriched_merchant_data(enriched_data)

def main():
    # Call initialization steps
    initialization.initialize_app()

    user = None
    auth_action = st.sidebar.selectbox("Choose Action", ["Login", "Sign Up"])

    if auth_action == "Login":
        user = authenticate_user()
    elif auth_action == "Sign Up":
        signup_user()

    if user:
        #st.write(f"User object: {user}")  # Debugging information
        if "is_superuser" in user and user["is_superuser"]:
            ui_management.render_superuser_dashboard()
        else:
            page = st.sidebar.radio(
                "Navigation",
                [
                    "Upload Files",
                    "Recurring Charge Detection",
                    "Subscription Validation",
                    "Cancelled Subscriptions",
                    "Organization Summary",
                    "Train Model",
                    "Run CrewAI Logic"
                ]
            )

            if page == "Upload Files":
                ui_management.render_upload_page(user)
            elif page == "Recurring Charge Detection":
                ui_management.render_recurring_charge_detection(user)
            elif page == "Subscription Validation":
                ui_management.render_subscription_validation(user["organization_id"], user)
            elif page == "Cancelled Subscriptions":
                ui_management.render_cancelled_subscriptions(user["organization_id"], user)
            elif page == "Organization Summary":
                ui_management.render_organization_summary(user["organization_id"])
            elif page == "Train Model":
                ui_management.render_train_model(user["organization_id"])
            elif page == "Run CrewAI Logic":
                render_run_crewai_logic(user)

if __name__ == "__main__":
    main()

