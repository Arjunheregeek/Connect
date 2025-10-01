import pandas as pd
import json

# Define the input and output file paths
input_file = "d:/Downloads/Connect/People for People Table v1 (1).csv"
output_file = "d:/Downloads/Connect/Processed_People_Table.csv"

# Read the CSV file
data = pd.read_csv(input_file)

# Update the function to include 'id' and 'parent_id' fields
def extract_fields(raw_data, existing_name, existing_linkedin):
    try:
        # Parse the JSON data
        parsed_data = json.loads(raw_data)
        return {
            "id": parsed_data.get("id"),
            "parent_id": parsed_data.get("parent_id"),
            "name": existing_name if pd.notna(existing_name) else parsed_data.get("full_name"),
            "linkedin_profile": existing_linkedin if pd.notna(existing_linkedin) else parsed_data.get("linkedin_url"),
            "email": parsed_data.get("primary_professional_email"),
            "location": parsed_data.get("location_full"),
            "headline": parsed_data.get("headline"),
            "summary": parsed_data.get("summary"),
            "followers": parsed_data.get("followers_count"),
            "current_role": parsed_data.get("active_experience_title"),
            "current_company": parsed_data.get("company_name"),
            "skills": parsed_data.get("inferred_skills"),
            "education": parsed_data.get("education"),
        }
    except (json.JSONDecodeError, TypeError):
        # Return None for rows with invalid JSON data
        return {
            "id": None,
            "parent_id": None,
            "name": existing_name,
            "linkedin_profile": existing_linkedin,
            "email": None,
            "location": None,
            "headline": None,
            "summary": None,
            "followers": None,
            "current_role": None,
            "current_company": None,
            "skills": None,
            "education": None,
        }

# Apply the updated extraction function to the coresignal_raw column
extracted_data = data.apply(
    lambda row: extract_fields(row["coresignal_raw"], row.get("name"), row.get("linkedin_profile")), axis=1
)

# Convert the extracted data into a DataFrame
extracted_df = pd.DataFrame(extracted_data.tolist())

# Combine the original data with the extracted fields
processed_data = pd.concat([data, extracted_df], axis=1)

# Drop the original coresignal_raw column and duplicate columns
processed_data = processed_data.drop(columns=["coresignal_raw", "name", "linkedin_profile", "email"], errors='ignore')

# Ensure 'name', 'linkedin_profile', and 'li_slug' columns remain unchanged
processed_data['name'] = data['name']
processed_data['linkedin_profile'] = data['linkedin_profile']
processed_data['li_slug'] = data['li_slug']

# Rearrange columns to keep 'name', 'linkedin_profile', 'id', and 'parent_id' at the start
columns_order = ['name', 'linkedin_profile', 'id', 'parent_id'] + [col for col in processed_data.columns if col not in ['name', 'linkedin_profile', 'id', 'parent_id']]
processed_data = processed_data[columns_order]

# Save the processed data to the output file
processed_data.to_csv(output_file, index=False)

print(f"Processed data has been updated and saved to {output_file}")