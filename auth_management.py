import os
from supabase import create_client
import streamlit as st

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
            if response and response.user:
                user = response.user
                # Fetch additional user attributes
                user_data = supabase.table("auth.users").select("is_superuser, organization_id").eq("id", user.id).execute()
                if user_data.data:
                    user.is_superuser = user_data.data[0].get("is_superuser", False)
                    user.organization_id = user_data.data[0].get("organization_id", None)
                st.success(f"Welcome, {user.email}!")
                st.session_state.user = user  # Update session state
                return user
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
        response = None  # Initialize response variable
        try:
            response = supabase.auth.sign_up({"email": email, "password": password})
            if response and response.user:
                # Create organization record
                supabase.table("organizations").insert({
                    "name": organization,
                    "admin_user_id": response.user.id
                }).execute()
                st.success("Account created successfully! Please log in.")
            else:
                st.error("Error signing up. Please try again.")
        except Exception as e:
            if "User already registered" in str(e)):
                st.error("User already exists. Please log in.")
            else:
                st.error(f"Error: {e}")

def create_superuser():
    """
    Pre-create a superuser for the app.
    """
    email = "darko.radiceski@gmail.com"
    password = st.secrets["superuser"]["password"]

    # Debugging information
    print(f"Superuser Email: {email}")
    print(f"Superuser Password: {password}")

    # Check if the superuser already exists
    response = None  # Initialize response variable
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if response and response.user:
            user = response.user
            supabase.table("auth.users").update({"is_superuser": True}).eq("id", user.id).execute()
            print("Superuser already exists.")
        else:
            # Create a new superuser
            response = supabase.auth.sign_up({"email": email, "password": password})
            if response and response.user:
                user = response.user
                supabase.table("auth.users").update({"is_superuser": True}).eq("id", user.id).execute()
                print("Superuser created successfully!")

        # Create the "FitTech" organization and assign it to the superuser
        org_response = supabase.table("organizations").insert({
            "name": "FitTech",
            "admin_user_id": user.id
        }).execute()
        if org_response.data:
            supabase.table("auth.users").update({"organization_id": org_response.data[0]["id"]}).eq("id", user.id).execute()
            print("Organization 'FitTech' created and assigned to the superuser.")

        return user

    except Exception as e:
        print(f"Error during superuser creation: {e}")

    print("Failed to create superuser.")
    return None