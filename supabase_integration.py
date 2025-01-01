import json
import pandas as pd
import streamlit as st
from supabase import create_client

# Load credentials from st.secrets
supabase_url = st.secrets["supabase"]["url"]
supabase_anon_key = st.secrets["supabase"]["anon_key"]
supabase_service_role_key = st.secrets["supabase"]["service_role_key"]

# Anonymous client for regular operations
supabase = create_client(supabase_url, supabase_anon_key)

# Service role client for admin operations
service_supabase = create_client(supabase_url, supabase_service_role_key)

def fetch_stored_subscriptions(user_id):
    """
    Fetch stored validated subscriptions for a specific user.
    """
    response = supabase.table("validated_subscriptions").select("*").eq("user_id", user_id).execute()
    if response.error:
        st.error(f"Error fetching subscriptions: {response.error}")
        return []
    return response.data if response.data else []

def upload_bank_data(user_id, file_name, data):
    """
    Store uploaded bank data in Supabase.
    """
    response = supabase.table("uploaded_files").insert({
        "user_id": user_id,
        "file_name": file_name,
        "data": data.to_json(orient="records"),
        "uploaded_at": pd.Timestamp.now().isoformat()
    }).execute()
    if response.error:
        st.error(f"Error uploading bank data: {response.error}")
    return response

def fetch_uploaded_files(user_id):
    """
    Fetch uploaded files for a specific user.
    """
    response = supabase.table("uploaded_files").select("*").eq("user_id", user_id).execute()
    if response.error:
        st.error(f"Error fetching uploaded files: {response.error}")
        return []
    return response.data if response.data else []

def fetch_file_data(file_id):
    """
    Retrieve file data by ID.
    """
    response = supabase.table("uploaded_files").select("data").eq("id", file_id).execute()
    if response.error:
        st.error(f"Error fetching file data: {response.error}")
        return pd.DataFrame()
    if response.data:
        return pd.read_json(response.data[0]["data"])
    return pd.DataFrame()

def update_keywords(category, keyword):
    """
    Add a new keyword to Supabase.
    """
    response = supabase.table("keywords").insert({
        "category": category,
        "keyword": keyword
    }).execute()
    if response.error:
        st.error(f"Error adding keyword: {response.error}")
    return response

def fetch_keywords():
    """
    Fetch all keywords from Supabase.
    """
    response = supabase.table("keywords").select("*").execute()
    if response.error:
        st.error(f"Error fetching keywords: {response.error}")
        return []
    return response.data if response.data else []

def fetch_thresholds():
    """
    Fetch all thresholds from Supabase.
    """
    response = supabase.table("thresholds").select("*").execute()
    if response.error:
        st.error(f"Error fetching thresholds: {response.error}")
        return []
    return response.data if response.data else []

def upload_enriched_data(user_id, file_name, data):
    """
    Store enriched merchant data in Supabase.
    """
    response = supabase.table("enriched_data").insert({
        "user_id": user_id,
        "file_name": file_name,
        "data": data.to_json(orient="records"),
        "uploaded_at": pd.Timestamp.now().isoformat()
    }).execute()
    if response.error:
        st.error(f"Error uploading enriched data: {response.error}")
    return response

def fetch_enriched_data(user_id, file_name):
    """
    Fetch enriched merchant data by file name.
    """
    response = supabase.table("enriched_data").select("data").eq("user_id", user_id).eq("file_name", file_name).execute()
    if response.error:
        st.error(f"Error fetching enriched data: {response.error}")
        return pd.DataFrame()
    if response.data:
        return pd.read_json(response.data[0]["data"])
    return pd.DataFrame()

def log_action(action, user_id, organization_id=None, details=None):
    """
    Log an action in the app.
    """
    response = service_supabase.table("app_logs").insert({
        "action": action,
        "user_id": user_id,
        "organization_id": organization_id,
        "details": details or {},
        "created_at": pd.Timestamp.now().isoformat()
    }).execute()
    if response.error:
        st.error(f"Error logging action: {response.error}")
    return response

def fetch_logs():
    """
    Fetch all logs from the app_logs table.
    """
    response = supabase.table("app_logs").select("*").execute()
    if response.error:
        st.error(f"Error fetching logs: {response.error}")
        return pd.DataFrame()
    return pd.DataFrame(response.data) if response.data else pd.DataFrame()

def fetch_users():
    """
    Fetch all users from the auth.users table.
    """
    response = service_supabase.table("auth.users").select("*").execute()
    if response.error:
        st.error(f"Error fetching users: {response.error}")
        return pd.DataFrame()
    return pd.DataFrame(response.data) if response.data else pd.DataFrame()

def update_user(user_id, updates):
    """
    Update user information securely using the service role key.
    """
    response = service_supabase.table("auth.users").update(updates).eq("id", user_id).execute()
    if response.error:
        st.error(f"Error updating user: {response.error}")
    return response

def update_organization(org_id, updates):
    """
    Update organization information.
    """
    response = supabase.table("organizations").update(updates).eq("id", org_id).execute()
    if response.error:
        st.error(f"Error updating organization: {response.error}")
    return response

def fetch_organizations():
    """
    Fetch all organizations from the public.organizations table.
    """
    response = supabase.table("organizations").select("*").execute()
    if response.error:
        st.error(f"Error fetching organizations: {response.error}")
        return pd.DataFrame()
    return pd.DataFrame(response.data) if response.data else pd.DataFrame()