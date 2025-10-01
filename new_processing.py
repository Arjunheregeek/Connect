import pandas as pd
import json

# Define the input and output file paths
# Make sure to update this path to where your file is located
input_file = "Data/People for People Table v1 (1).csv"
output_file = "Data/Processed_People_Knowledge_Graph.csv"

# Read the original CSV file
try:
    data = pd.read_csv(input_file)
except FileNotFoundError:
    print(f"Error: The input file was not found at '{input_file}'")
    exit()

def extract_knowledge_graph_data(row):
    """
    Parses the raw JSON data from the 'coresignal_raw' column to extract
    structured fields for the knowledge graph.
    """
    try:
        # Load the JSON string into a Python dictionary
        # The raw data might be inside another string, so we handle that.
        raw_data = row["coresignal_raw"]
        if isinstance(raw_data, str):
            parsed_data = json.loads(raw_data)
        else:
            # If data is already parsed or not a string, use it directly
            parsed_data = raw_data

        # --- Extract Experience History ---
        # We extract specific, clean fields from each job experience
        experience_history = []
        if parsed_data.get("experience") and isinstance(parsed_data["experience"], list):
            for job in parsed_data["experience"]:
                experience_history.append({
                    "company_name": job.get("company_name"),
                    "company_linkedin_url": job.get("company_linkedin_url"),
                    "title": job.get("position_title"),
                    "description": job.get("description"),
                    "start_date": job.get("date_from"),
                    "end_date": job.get("date_to"),
                    "duration_months": job.get("duration_months"),
                    "location": job.get("location")
                })

        # --- Extract Education History ---
        education_history = []
        if parsed_data.get("education") and isinstance(parsed_data["education"], list):
            for edu in parsed_data["education"]:
                education_history.append({
                    "institution_name": edu.get("institution_name"),
                    "institution_url": edu.get("institution_url"),
                    "degree": edu.get("degree"),
                    "start_year": edu.get("date_from_year"),
                    "end_year": edu.get("date_to_year")
                })
        
        # --- Assemble all the data points ---
        return {
            # Core Identity (Person Node)
            "id": parsed_data.get("id"),
            "name": row.get("name", parsed_data.get("full_name")),
            "linkedin_profile": row.get("linkedin_profile", parsed_data.get("linkedin_url")),
            "email": parsed_data.get("primary_professional_email", row.get("email")),
            "phone": row.get("phone"),
            "location": parsed_data.get("location_full"),
            "headline": parsed_data.get("headline"),
            "summary": parsed_data.get("summary"),
            "followers_count": parsed_data.get("followers_count"),
            
            # Key Attributes for Filtering (Person Node Properties)
            "total_experience_months": parsed_data.get("total_experience_duration_months"),
            "skills": json.dumps(parsed_data.get("inferred_skills", [])), # Store list as JSON string
            
            # Data for Relationships
            "experience_history": json.dumps(experience_history), # Store list as JSON string
            "education_history": json.dumps(education_history)   # Store list as JSON string
        }

    except (json.JSONDecodeError, TypeError, AttributeError):
        # If JSON is malformed or data is missing, return a structure with None values
        # This prevents the script from crashing and helps identify problematic rows
        return {
            "id": None, "name": row.get("name"), "linkedin_profile": row.get("linkedin_profile"),
            "email": row.get("email"), "phone": row.get("phone"), "location": None,
            "headline": None, "summary": None, "followers_count": None,
            "total_experience_months": None, "skills": None, "experience_history": None,
            "education_history": None
        }

# Apply the function to each row of the DataFrame
processed_records = data.apply(extract_knowledge_graph_data, axis=1)

# Convert the list of dictionaries into a new DataFrame
processed_df = pd.DataFrame(processed_records.tolist())

# Save the final, clean data to a new CSV file
processed_df.to_csv(output_file, index=False)

print(f"✅ Successfully processed the data and saved it to '{output_file}'")