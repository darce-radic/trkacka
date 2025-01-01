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
    response = supabase.table("public.validated_subscriptions").select("*").eq("user_id", user_id).execute()
    return response.data

def upload_bank_data(user_id, file_name, data):
    """
    Store uploaded bank data in Supabase.
    """
    response = supabase.table("public.uploaded_files").insert({
        "user_id": user_id,
        "file_name": file_name,
        "data": data.to_json(orient="records"),
        "uploaded_at": pd.Timestamp.now().isoformat()
    }).execute()
    return response

def fetch_uploaded_files(user_id):
    """
    Fetch uploaded files for a specific user.
    """
    response = supabase.table("public.uploaded_files").select("*").eq("user_id", user_id).execute()
    return response.data

def fetch_file_data(file_id):
    """
    Retrieve file data by ID.
    """
    response = supabase.table("public.uploaded_files").select("data").eq("id", file_id).execute()
    if response.data:
        return pd.read_json(response.data[0]["data"])
    return pd.DataFrame()

def update_keywords(category, keyword):
    """
    Add a new keyword to Supabase.
    """
    response = supabase.table("public.keywords").insert({
        "category": category,
        "keyword": keyword
    }).execute()
    return response

def fetch_keywords():
    """
    Fetch all keywords from Supabase.
    """
    response = supabase.table("public.keywords").select("*").execute()
    return response["data"]

def fetch_thresholds():
    """
    Fetch all thresholds from Supabase.
    """
    response = supabase.table("public.thresholds").select("*").execute()
    return response["data"]

def upload_enriched_data(user_id, file_name, data):
    """
    Store enriched merchant data in Supabase.
    """
    response = supabase.table("public.enriched_data").insert({
        "user_id": user_id,
        "file_name": file_name,
        "data": data.to_json(orient="records"),
        "uploaded_at": pd.Timestamp.now().isoformat()
    }).execute()
    return response

def fetch_enriched_data(user_id, file_name):
    """
    Fetch enriched merchant data by file name.
    """
    response = supabase.table("public.enriched_data").select("data").eq("user_id", user_id).eq("file_name", file_name).execute()
    if response.data:
        return pd.read_json(response.data[0]["data"])
    return pd.DataFrame()

def log_action(action, user_id, organization_id=None, details=None):
    """
    Log an action in the app.
    """
    response = service_supabase.table("public.app_logs").insert({
        "action": action,
        "user_id": user_id,
        "organization_id": organization_id,
        "details": details or {},
        "created_at": pd.Timestamp.now().isoformat()
    }).execute()
    return response

def fetch_logs():
    """
    Fetch all logs from the app_logs table.
    """
    response = supabase.table("public.app_logs").select("*").execute()
    return pd.DataFrame(response.data)

def fetch_users():
    """
    Fetch all users from the auth.users table.
    """
    response = supabase.table("auth.users").select("*").execute()
    return pd.DataFrame(response.data)

def update_user(user_id, updates):
    """
    Update user information securely using the service role key.
    """
    response = service_supabase.table("auth.users").update(updates).eq("id", user_id).execute()
    return response

def fetch_organizations():
    """
    Fetch all organizations from the public.organizations table.
    """
    response = supabase.table("public.organizations").select("*").execute()
    return pd.DataFrame(response.data)

def update_organization(org_id, updates):
    """
    Update organization information.
    """
    response = supabase.table("public.organizations").update(updates).eq("id", org_id).execute()
    return response

def fetch_organization_data(org_id, table_name):
    """
    Fetch data for a specific organization from the specified table.
    """
    response = supabase.table(f"public.{table_name}").select("*").eq("organization_id", org_id).execute()
    if response.get("data"):
        return response["data"]
    else:
        raise ValueError(f"No data found in table {table_name} for organization ID {org_id}")
