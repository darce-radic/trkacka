from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd
import streamlit as st

def cluster_transactions(data):
    """
    Cluster transactions based on amount and frequency.
    """
    scaler = StandardScaler()
    clustering_features = data[['Amount', 'Frequency']].fillna(0)
    scaled_data = scaler.fit_transform(clustering_features)

    kmeans = KMeans(n_clusters=5, random_state=42)
    data['Cluster'] = kmeans.fit_predict(scaled_data)

    return data

def display_cluster_analysis(data):
    """
    Display cluster analysis results.
    """
    st.title("Transaction Clusters")
    st.write(data[['Merchant', 'Cluster']].groupby('Cluster').count())
    st.write("Cluster Visualization Coming Soon!")


def perform_dynamic_clustering(data, max_clusters=10):
    """
    Perform dynamic clustering using KMeans.
    """
    scaler = StandardScaler()
    clustering_data = data[['Amount', 'Frequency']].fillna(0)
    scaled_data = scaler.fit_transform(clustering_data)

    inertia = []
    for k in range(1, max_clusters + 1):
        kmeans = KMeans(n_clusters=k)
        kmeans.fit(scaled_data)
        inertia.append(kmeans.inertia_)

    plt.figure(figsize=(10, 6))
    plt.plot(range(1, max_clusters + 1), inertia, marker='o')
    plt.title("Elbow Method for Optimal Clusters")
    plt.xlabel("Number of Clusters")
    plt.ylabel("Inertia")
    st.pyplot(plt)

    optimal_k = inertia.index(min(inertia[1:])) + 1
    kmeans = KMeans(n_clusters=optimal_k)
    data['Cluster'] = kmeans.fit_predict(scaled_data)

    return data
