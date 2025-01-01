import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import pandas as pd


def visualize_feature_importance(feature_names, importances):
    """
    Visualize feature importance as a bar chart.
    """
    plt.figure(figsize=(10, 6))
    sns.barplot(x=importances, y=feature_names, palette="viridis")
    plt.xlabel("Importance")
    plt.ylabel("Feature")
    plt.title("Feature Importance")
    st.pyplot(plt)


def plot_spending_trends(trends):
    """
    Plot spending trends over time.
    """
    plt.figure(figsize=(10, 6))
    trends.plot(kind='line')
    plt.title("Spending Trends Over Time")
    plt.xlabel("Month")
    plt.ylabel("Total Amount")
    st.pyplot(plt)



def filter_transactions_by_cluster(data, cluster_id):
    """
    Filter transactions by cluster.
    """
    return data[data['Cluster'] == cluster_id]



def visualize_cluster_data(data):
    """
    Visualize cluster data.
    """
    plt.figure(figsize=(10, 6))
    sns.countplot(data=data, x='Cluster', palette="viridis")
    plt.title("Transaction Count by Cluster")
    plt.xlabel("Cluster")
    plt.ylabel("Count")
    st.pyplot(plt)

def render_cluster_insights(data):
    """
    Render insights for clusters.
    """
    st.title("Cluster Insights")
    st.write(data.groupby('Cluster')['Amount'].mean())
    visualize_cluster_data(data)
