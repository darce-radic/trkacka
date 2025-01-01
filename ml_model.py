import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
import pickle
from supabase_integration import fetch_organization_data

def load_validated_subscriptions(org_id):
    """
    Load validated subscriptions for an organization from Supabase.
    """
    return fetch_organization_data(org_id, "validated_subscriptions")

def train_model(org_id):
    """
    Train a machine learning model for transaction categorization using validated subscriptions.
    """
    # Load validated subscriptions
    data = load_validated_subscriptions(org_id)

    if data.empty:
        raise ValueError("No validated subscriptions available for training.")

    # Define a pipeline with a vectorizer and classifier
    pipeline = Pipeline([
        ('vectorizer', TfidfVectorizer()),
        ('classifier', RandomForestClassifier())
    ])

    # Prepare training data
    X = data['merchant'] + " " + data['description']
    y = data['category']

    # Train the model
    pipeline.fit(X, y)

    # Save the model to a file
    model_path = f"models/categorization_model_org_{org_id}.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(pipeline, f)

    return pipeline

def load_model(org_id):
    """
    Load a trained machine learning model for an organization.
    """
    model_path = f"models/categorization_model_org_{org_id}.pkl"
    try:
        with open(model_path, "rb") as f:
            model = pickle.load(f)
        return model
    except FileNotFoundError:
        raise ValueError(f"Model for organization {org_id} not found. Train the model first.")

def predict_categories(org_id, data):
    """
    Predict transaction categories using the trained model for an organization.
    """
    # Load the trained model
    model = load_model(org_id)

    # Prepare input data
    X = data['Merchant'] + " " + data['Description']

    # Predict categories
    data['Predicted Category'] = model.predict(X)
    return data
