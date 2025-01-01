import pandas as pd
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
import os

# Load OpenAI API key (if needed for CrewAI tools like SerperDevTool)
os.environ["OPENAI_API_KEY"] = "your_openai_api_key_here"

# Initialize SerperDevTool for enrichment
serper_tool = SerperDevTool()

# Step 1: Normalize Data
def normalize_data(data):
    """
    Prepare the data for processing by cleaning and standardizing columns.
    """
    # Drop unnamed columns
    data = data.loc[:, ~data.columns.str.contains('^Unnamed')]

    # Ensure necessary columns
    required_columns = ["Date", "Amount", "Description"]
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        raise ValueError(f"The following required columns are missing: {', '.join(missing_columns)}")

    # Convert date column to datetime for easier grouping
    data["Date"] = pd.to_datetime(data["Date"])

    return data

# Step 2: Detect Recurring Charges
def detect_recurring_charges(data):
    """
    Detect potential recurring charges by grouping descriptions and amounts.
    """
    # Group by description and amount to find recurring charges
    recurring = (
        data.groupby(["Description", "Amount"])
        .size()
        .reset_index(name="Frequency")
    )

    # Filter for transactions that occur more than once
    recurring = recurring[recurring["Frequency"] > 1]

    # Merge back to include original details
    recurring_data = data.merge(
        recurring, on=["Description", "Amount"], how="inner"
    ).sort_values(by=["Description", "Date"])

    return recurring_data

def enrich_merchant_data(data):
    """
    Enrich recurring transactions by inferring merchant details from descriptions.
    """
    # Ensure the 'Merchant' column exists
    if "Merchant" not in data.columns:
        data["Merchant"] = data["Description"].apply(lambda desc: infer_merchant_from_description(desc))

    # Add enrichment context (e.g., category)
    data["Category"] = data["Merchant"].apply(
        lambda merchant: "Subscription" if merchant != "Unknown Merchant" else "Unknown"
    )

    return data

def infer_merchant_from_description(description):
    """
    Infer merchant information based on transaction description.
    This function uses simple keyword matching; replace with actual enrichment logic.
    """
    # Mocked logic for now; replace with tool/API calls
    if "Netflix" in description:
        return "Netflix"
    elif "Spotify" in description:
        return "Spotify"
    elif "Gym" in description:
        return "Local Gym"
    else:
        return "Unknown Merchant"


# Step 4: Full Workflow
def run_subscription_detection(data):
    """
    Full workflow to detect recurring transactions and enrich them.
    """
    try:
        # Step 1: Normalize data
        normalized_data = normalize_data(data)

        # Step 2: Detect recurring charges
        recurring_data = detect_recurring_charges(normalized_data)

        if recurring_data.empty:
            print("No recurring transactions detected.")
            return None

        # Step 3: Enrich recurring transactions
        enriched_data = enrich_recurring_charges(recurring_data)

        return enriched_data
    except Exception as e:
        print(f"Error detecting recurring subscriptions: {e}")
        return None

# Step 5: Integration with CrewAI
# Define CrewAI agents and tasks
normalizer_agent = Agent(
    role="Data Normalizer",
    goal="Prepare and standardize transaction data for processing.",
    tools=[],
    verbose=True,
    backstory="Responsible for ensuring clean and consistent data for analysis."
)

recurring_detector_agent = Agent(
    role="Recurring Charge Detector",
    goal="Identify potential recurring transactions indicative of subscriptions.",
    tools=[],
    verbose=True,
    backstory="Skilled in detecting patterns in financial transactions."
)

enrichment_agent = Agent(
    role="Enrichment Agent",
    goal="Enrich transaction data by identifying merchants and subscription details.",
    tools=[serper_tool],
    verbose=True,
    backstory="Uses advanced tools to enrich transaction details for better insights."
)

normalization_task = Task(
    description="Normalize and prepare transaction data.",
    expected_output="Cleaned and standardized data ready for analysis.",
    agent=normalizer_agent
)

recurring_detection_task = Task(
    description="Analyze data to detect potential recurring transactions.",
    expected_output="A list of recurring transactions and their frequencies.",
    agent=recurring_detector_agent
)

enrichment_task = Task(
    description="Enrich recurring transactions with merchant and category details.",
    expected_output="Recurring transactions enriched with merchant and subscription data.",
    agent=enrichment_agent
)

# Define Crew
crew = Crew(
    agents=[normalizer_agent, recurring_detector_agent, enrichment_agent],
    tasks=[normalization_task, recurring_detection_task, enrichment_task],
    process=Process.sequential  # Sequential execution of tasks
)

