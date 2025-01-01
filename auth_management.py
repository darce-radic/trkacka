import os
from supabase import create_client
import streamlit as st
from supabase import create_client

# Load credentials from st.secrets
supabase_url = st.secrets["supabase"]["url"]
supabase_anon_key = st.secrets["supabase"]["anon_key"]
supabase = create_client(supabase_url, supabase_anon_key)

def authenticate_user():
    st.title("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if response and response.get('user'):
            st.success(f"Welcome, {response['user']['email']}!")
            return response['user']
        else:
            st.error("Invalid credentials.")
    return None

def signup_user():
    st.title("Sign Up")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    organization = st.text_input("Organization Name")

    if st.button("Sign Up"):
        response = supabase.auth.sign_up({"email": email, "password": password})
        if response and response.get('user'):
            # Create organization record
            supabase.table("organizations").insert({
                "name": organization,
                "user_id": response['user']['id']
            }).execute()
            st.success("Account created successfully! Please log in.")
        else:
            st.error("Error signing up. Please try again.")

def create_superuser():
    """
    Pre-create a superuser for the app.
    """
    email = st.secrets["superuser"]["email"]
    password = st.secrets["superuser"]["password"]

    # Check if the superuser already exists
    response = supabase.auth.sign_in_with_password({"email": email, "password": password})
    if response and "user" in response:
        user = response["user"]
        supabase.table("auth.users").update({"is_superuser": True}).eq("id", user["id"]).execute()
        print("Superuser already exists.")
        return user

    # Create a new superuser
    response = supabase.auth.sign_up({"email": email, "password": password})
    if response and "user" in response:
        user = response["user"]
        supabase.table("auth.users").update({"is_superuser": True}).eq("id", user["id"]).execute()
        print("Superuser created successfully!")
        return user

    print("Failed to create superuser.")
    return None