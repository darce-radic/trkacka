import streamlit as st
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool, RagTool, CSVSearchTool
import os

# Load OpenAI API key from st.secrets
os.environ["OPENAI_API_KEY"] = st.secrets["openai"]["api_key"]

# Initialize tools
csv_tool = CSVSearchTool()
rag_tool = RagTool()
serper_tool = SerperDevTool()

# Define Agents
normalizer_agent = Agent(
    role="Data Normalizer",
    goal="Clean and standardize uploaded transaction data.",
    tools=[csv_tool],
    verbose=True,
    backstory="Responsible for ensuring data consistency and cleanliness."
)

pattern_analyzer_agent = Agent(
    role="Pattern Analyzer",
    goal="Identify recurring subscription patterns in the data.",
    tools=[csv_tool],
    verbose=True,
    backstory="Analyzes data to find recurring patterns and trends."
)

categorizer_agent = Agent(
    role="Categorizer",
    goal="Categorize transactions into predefined subscription categories.",
    tools=[rag_tool],
    verbose=True,
    backstory="Classifies transactions into specific categories for better organization."
)

enrichment_agent = Agent(
    role="Enrichment Agent",
    goal="Enrich merchant data with additional context using SerperDevTool.",
    tools=[serper_tool],
    verbose=True,
    backstory="Adds contextual information to merchant data for enhanced insights."
)

# Define Tasks
normalization_task = Task(
    description="Normalize uploaded data into a consistent format.",
    expected_output="Normalized data with standardized columns.",
    agent=normalizer_agent
)

pattern_analysis_task = Task(
    description="Analyze the normalized data to detect recurring transactions.",
    expected_output="List of recurring transactions with patterns identified.",
    agent=pattern_analyzer_agent
)

categorization_task = Task(
    description="Categorize recurring transactions into predefined categories.",
    expected_output="Categorized transactions with corresponding labels.",
    agent=categorizer_agent
)

enrichment_task = Task(
    description="Use SerperDevTool to enrich merchant information for each transaction.",
    expected_output="Merchant data enriched with additional contextual information.",
    agent=enrichment_agent
)

# Define Crew
crew = Crew(
    agents=[
        normalizer_agent,
        pattern_analyzer_agent,
        categorizer_agent,
        enrichment_agent
    ],
    tasks=[
        normalization_task,
        pattern_analysis_task,
        categorization_task,
        enrichment_task
    ],
    process=Process.sequential  # Execute tasks sequentially
)

def run_crewai_workflow(data):
    """
    Run CrewAI workflow on the given data.
    """
    print("Running CrewAI workflow...")
    try:
        result = crew.kickoff(inputs={"data": data.to_dict(orient="records")})
        print("CrewAI workflow result:", result)  # Debugging information
        return result
    except Exception as e:
        print(f"Error running CrewAI workflow: {e}")
        return None

def display_crewai_results(result):
    """
    Display the results of the CrewAI workflow.
    """
    if result is None:
        st.error("No results to display. The workflow may have encountered an error.")
        return

    st.write("CrewAI Workflow Results:")
    for task_result in result:
        st.subheader(task_result["task"])
        if "output" in task_result:
            st.write(task_result["output"])
        if "error" in task_result:
            st.error(task_result["error"])

def render_run_crewai_logic(user):
    """
    Run CrewAI logic on stored data and display enriched merchant data.
    """
    st.title("Run CrewAI Logic with Merchant Enrichment")

    # Access user ID correctly
    user_id = user.id  # Correctly access the user ID

    files = fetch_uploaded_files(user_id)
    if not files:
        st.warning("No files available for processing.")
        return

    st.write("Available Files:")
    file_id = st.selectbox("Select a file to process", [file["id"] for file in files])
    if file_id:
        file_data = fetch_file_data(file_id)

        # Run CrewAI Workflow
        st.write("Processing CrewAI Workflow...")
        result = run_crewai_workflow(file_data)

        # Display CrewAI results
        display_crewai_results(result)

        # Enrich and store data
        enriched_data = enrich_merchant_data(file_data)
        upload_enriched_data(user_id, file_id, enriched_data)

        # Display enriched data
        st.write("Enriched Merchant Data:")
        st.dataframe(enriched_data)
