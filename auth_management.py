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
        response = None  # Initialize response variable
        try:
            st.write(f"Attempting to log in with email: {email}")  # Debugging information
            response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            st.write(f"Response: {response}")  # Debugging information
            if response and response.get('user'):
                st.success(f"Welcome, {response['user']['email']}!")
                return response['user']
            else:
                st.error("Invalid credentials.")
        except Exception as e:
            st.error(f"Error: {e}")
            st.write(f"Exception details: {e}")  # Detailed exception information
            st.write(f"Supabase response: {response}")  # Log the full response
            st.write(f"Supabase URL: {supabase_url}")  # Log Supabase URL
            st.write(f"Supabase Anon Key: {supabase_anon_key}")  # Log Supabase Anon Key
    return None

def signup_user():
    st.title("Sign Up")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    organization = st.text_input("Organization Name")

    if st.button("Sign Up"):
        try:
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
        except Exception as e:
            if "User already registered" in str(e):
                st.error("User already exists. Please log in.")
            else:
                st.error(f"Error: {e}")

def create_superuser():
    """
    Pre-create a superuser for the app.
    """
    email = st.secrets["superuser"]["email"]
    password = st.secrets["superuser"]["password"]

    # Check if the superuser already exists
    try:
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

    except Exception as e:
        print(f"Error during superuser creation: {e}")

    print("Failed to create superuser.")
    return None