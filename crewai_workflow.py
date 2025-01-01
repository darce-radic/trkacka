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
    verbose=True
)

pattern_analyzer_agent = Agent(
    role="Pattern Analyzer",
    goal="Identify recurring subscription patterns in the data.",
    tools=[csv_tool],
    verbose=True
)

categorizer_agent = Agent(
    role="Categorizer",
    goal="Categorize transactions into predefined subscription categories.",
    tools=[rag_tool],
    verbose=True
)

enrichment_agent = Agent(
    role="Enrichment Agent",
    goal="Enrich merchant data with additional context using SerperDevTool.",
    tools=[serper_tool],
    verbose=True
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
    result = crew.kickoff(inputs={"data": data.to_dict(orient="records")})
    return result
