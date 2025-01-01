from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import pickle
import shap

def train_model(data, features, target):
    """
    Train a machine learning model for categorization.
    """
    text_vectorizer = TfidfVectorizer()
    scaler = StandardScaler()
    classifier = RandomForestClassifier()

    pipeline = Pipeline([
        ('vectorizer', text_vectorizer),
        ('scaler', scaler),
        ('classifier', classifier)
    ])

    X = data[features]
    y = data[target]
    pipeline.fit(X, y)

    with open("data/categorization_model.pkl", "wb") as f:
        pickle.dump(pipeline, f)

    return pipeline

def predict_categories(data, model):
    """
    Predict categories using the trained model.
    """
    X = data[['Merchant', 'Description']]
    data['Predicted Category'] = model.predict(X)
    return data

def explain_predictions(model, data):
    """
    Explain model predictions using SHAP.
    """
    explainer = shap.Explainer(model.named_steps['classifier'], data)
    shap_values = explainer(data)
    shap.summary_plot(shap_values, data)
