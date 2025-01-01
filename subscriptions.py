import pandas as pd
from supabase_integration import upload_bank_data


def validate_file(data, required_columns=None):
    """
    Validate the uploaded file for required columns.
    """
    if required_columns is None:
        required_columns = ["Date", "Amount", "Merchant", "Description"]

    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
    return data


def validate_and_normalize(file_path):
    """
    Validate and normalize the uploaded file.
    """
    data = pd.read_csv(file_path)

    # Normalize columns
    column_mappings = {
        "Date": "Date",
        "Amount": "Amount",
        "Merchant": "Merchant",
        "Description": "Description"
    }
    data.rename(columns=column_mappings, inplace=True)

    # Validate columns
    validate_file(data)

    # Normalize date format
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
    data.dropna(subset=["Date"], inplace=True)

    return data


def enrich_merchant_data(data):
    """
    Enrich merchant information using SerperDevTool.
    """
    from crewai_tools import SerperDevTool
    serper_tool = SerperDevTool()

    data["Merchant Info"] = data["Merchant"].apply(lambda x: serper_tool.run(x))
    return data


def detect_recurring_charges(data, historical_data=None):
    """
    Detect recurring charges by analyzing transaction intervals and comparing
    with historical subscriptions.
    """
    # Calculate intervals between transactions for each merchant
    data["Interval"] = data.groupby("Merchant")["Date"].diff().dt.days
    data["Is_Recurring"] = data["Interval"].apply(
        lambda x: "Yes" if x and x <= 30 else "No"
    )

    if historical_data is not None:
        # Compare with historical subscriptions to detect new recurring charges
        known_merchants = historical_data["Merchant"].unique()
        data["Is_New_Subscription"] = ~data["Merchant"].isin(known_merchants)
    else:
        data["Is_New_Subscription"] = "Unknown"

    return data


def detect_subscriptions(data):
    """
    Detect subscriptions by analyzing recurring charges and categories.
    """
    data = detect_recurring_charges(data)
    subscriptions = data[data["Is_Recurring"] == "Yes"]
    return subscriptions


def analyze_spending_trends(data):
    """
    Analyze spending trends over time.
    """
    data["Month"] = pd.to_datetime(data["Date"]).dt.to_period("M")
    spending_trends = data.groupby("Month")["Amount"].sum().reset_index()
    return spending_trends


def filter_others(data):
    """
    Filter transactions categorized as "Others".
    """
    others_data = data[data["Category"] == "Others"]
    return others_data


def calculate_savings(data):
    """
    Calculate potential savings based on cancelled subscriptions.
    """
    savings = []
    for _, row in data.iterrows():
        amount = row["amount"]
        frequency = row["frequency"]
        cancellation_date = pd.to_datetime(row["cancellation_date"])
        days_since_cancellation = (pd.Timestamp.now() - cancellation_date).days

        # Calculate savings based on frequency
        if frequency == "Daily":
            saved_amount = amount * days_since_cancellation
        elif frequency == "Weekly":
            saved_amount = amount * (days_since_cancellation // 7)
        elif frequency == "Monthly":
            saved_amount = amount * (days_since_cancellation // 30)
        elif frequency == "Yearly":
            saved_amount = amount * (days_since_cancellation // 365)
        else:
            saved_amount = 0  # Unknown frequency

        savings.append({"Merchant": row["merchant"], "Amount Saved": saved_amount})

    return pd.DataFrame(savings)


def process_uploaded_file(data, user):
    """
    Store uploaded files in Supabase.
    """
    response = upload_bank_data(user["id"], "uploaded_file.csv", data)
    return response
