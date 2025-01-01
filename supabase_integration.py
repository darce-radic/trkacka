import json
import pandas as pd
import streamlit as st
from supabase import create_client

# Load credentials from st.secrets
supabase_url = st.secrets["supabase"]["url"]
supabase_key = st.secrets["supabase"]["key"]
supabase = create_client(supabase_url, supabase_key)



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
    return response


def fetch_uploaded_files(user_id):
    """
    Retrieve uploaded files from Supabase for a specific user.
    """
    response = supabase.table("uploaded_files").select("*").eq("user_id", user_id).execute()
    return pd.DataFrame(response.data)


def fetch_file_data(file_id):
    """
    Retrieve file data by ID.
    """
    response = supabase.table("uploaded_files").select("data").eq("id", file_id).execute()
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
    return response


def fetch_keywords():
    """
    Fetch all keywords from Supabase.
    """
    response = supabase.table("keywords").select("*").execute()
    return response["data"]


def fetch_thresholds():
    """
    Fetch all thresholds from Supabase.
    """
    response = supabase.table("thresholds").select("*").execute()
    return response["data"]

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
    return response


def fetch_enriched_data(user_id, file_name):
    """
    Fetch enriched merchant data by file name.
    """
    response = supabase.table("enriched_data").select("data").eq("user_id", user_id).eq("file_name", file_name).execute()
    if response.data:
        return pd.read_json(response.data[0]["data"])
    return pd.DataFrame()

def log_action(action, user_id, organization_id=None, details=None):
    """
    Log an action in the app.
    """
    response = supabase.table("app_logs").insert({
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
    response = supabase.table("app_logs").select("*").execute()
    return pd.DataFrame(response.data)

def fetch_users():
    """
    Fetch all users from the auth.users table.
    """
    response = supabase.table("auth.users").select("*").execute()
    return pd.DataFrame(response.data)


def update_user(user_id, updates):
    """
    Update user information (e.g., activate/deactivate).
    """
    response = supabase.table("auth.users").update(updates).eq("id", user_id).execute()
    return response

def fetch_organizations():
    """
    Fetch all organizations from the organizations table.
    """
    response = supabase.table("organizations").select("*").execute()
    return pd.DataFrame(response.data)


def update_organization(org_id, updates):
    """
    Update organization information.
    """
    response = supabase.table("organizations").update(updates).eq("id", org_id).execute()
    return response
