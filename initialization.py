from auth_management import create_superuser

def initialize_app():
    """
    Perform all necessary initialization tasks for the app.
    """
    print("Initializing the app...")

    # Step 1: Create the superuser
    print("Ensuring superuser exists...")
    try:
        create_superuser()
    except Exception as e:
        print(f"Error during superuser creation: {e}")


    # Add other initialization steps if needed
    print("Initialization complete.")
