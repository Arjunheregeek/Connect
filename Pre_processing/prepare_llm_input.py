"""
Prepare LLM Input Dataset
==========================
This script creates a clean, focused CSV file containing ONLY the fields needed
for LLM-based attribute enrichment. 

It extracts from the original CSV:
- Basic identity (name, email, location)
- Current role information (title, company, industry)
- Complete work experience with job descriptions
- Education details
- Skills (all inferred skills)
- Profile metadata (headline, summary, followers)
- Years of experience

Output: A new CSV file with one row per person, containing rich context for LLM processing.
"""

import pandas as pd
import json

# File paths
INPUT_FILE = "Data/People for People Table v1 (1).csv"
OUTPUT_FILE = "Data/LLM_Input_Profiles.csv"

def extract_llm_relevant_data(row):
    """
    Extract only the fields needed for LLM enrichment from the raw data.
    
    Returns a clean dictionary with:
    - person_id
    - name
    - email
    - location
    - headline
    - summary
    - current_title
    - current_company
    - current_industry
    - years_of_experience
    - all_job_descriptions (JSON string)
    - education_details (JSON string)
    - all_skills (JSON string)
    - followers_count
    """
    try:
        # Parse the coresignal_raw JSON
        raw_data = row["coresignal_raw"]
        if isinstance(raw_data, str):
            parsed_data = json.loads(raw_data)
        else:
            parsed_data = raw_data
        
        # Extract basic info
        person_id = parsed_data.get("id")
        name = row.get("name", parsed_data.get("full_name"))
        headline = parsed_data.get("headline")
        summary = parsed_data.get("summary")
        followers_count = parsed_data.get("followers_count")
        
        # Extract current role
        current_title = parsed_data.get("active_experience_title")
        
        # Extract current company and industry from active experience
        current_company = None
        current_industry = None
        experience_list = parsed_data.get("experience", [])
        
        for job in experience_list:
            if job.get("active_experience") == 1:
                current_company = job.get("company_name")
                current_industry = job.get("company_industry")
                break
        
        # Calculate years of experience
        total_months = parsed_data.get("total_experience_duration_months")
        years_of_experience = round(total_months / 12, 1) if total_months else None
        
        # Extract ALL job descriptions with context
        # Sort by order (most recent first based on active_experience and dates)
        all_job_descriptions = []
        if experience_list and isinstance(experience_list, list):
            # Experience list is already ordered from most recent to oldest
            for idx, job in enumerate(experience_list, start=1):
                job_entry = {
                    "order": idx,  # 1 = most recent, 2 = second most recent, etc.
                    "company_name": job.get("company_name"),
                    "company_industry": job.get("company_industry"),
                    "title": job.get("position_title"),
                    "description": job.get("description"),
                    "department": job.get("department"),
                    "management_level": job.get("management_level"),
                    "duration_months": job.get("duration_months"),
                    "is_current": job.get("active_experience") == 1
                }
                all_job_descriptions.append(job_entry)
        
        # Extract education details
        education_details = []
        education_list = parsed_data.get("education", [])
        if education_list and isinstance(education_list, list):
            for edu in education_list:
                edu_entry = {
                    "institution_name": edu.get("institution_name"),
                    "degree": edu.get("degree"),
                    "field_of_study": edu.get("field_of_study"),
                    "start_year": edu.get("date_from_year"),
                    "end_year": edu.get("date_to_year"),
                    "activities": edu.get("activities_and_societies")
                }
                education_details.append(edu_entry)
        
        # Also get pre-extracted degrees
        education_degrees = parsed_data.get("education_degrees", [])
        
        # Extract ALL skills (inferred skills from LinkedIn)
        all_skills = parsed_data.get("inferred_skills", [])
        
        return {
            "person_id": person_id,
            "name": name,
            "headline": headline,
            "summary": summary,
            "current_title": current_title,
            "current_company": current_company,
            "current_industry": current_industry,
            "years_of_experience": years_of_experience,
            "all_job_descriptions": json.dumps(all_job_descriptions),  # Store as JSON string
            "education_details": json.dumps(education_details),  # Store as JSON string
            "education_degrees": json.dumps(education_degrees),  # Store as JSON string
            "all_skills": json.dumps(all_skills),  # Store as JSON string
            "followers_count": followers_count
        }
    
    except (json.JSONDecodeError, TypeError, AttributeError, KeyError) as e:
        print(f"Error processing row {row.get('name', 'Unknown')}: {str(e)}")
        return {
            "person_id": None,
            "name": row.get("name"),
            "headline": None,
            "summary": None,
            "current_title": None,
            "current_company": None,
            "current_industry": None,
            "years_of_experience": None,
            "all_job_descriptions": None,
            "education_details": None,
            "education_degrees": None,
            "all_skills": None,
            "followers_count": None
        }


def main():
    print("🔧 Preparing LLM Input Dataset...\n")
    
    # Read the original CSV
    try:
        print(f"📂 Reading from: {INPUT_FILE}")
        data = pd.read_csv(INPUT_FILE)
        print(f"✅ Loaded {len(data)} profiles")
    except FileNotFoundError:
        print(f"❌ Error: File not found at '{INPUT_FILE}'")
        return
    
    # Extract relevant data for each person
    print("\n🔍 Extracting relevant fields for LLM enrichment...")
    llm_input_records = data.apply(extract_llm_relevant_data, axis=1)
    
    # Convert to DataFrame
    llm_input_df = pd.DataFrame(llm_input_records.tolist())
    
    # Filter out profiles with no education degrees
    print("\n🎓 Filtering profiles with education data...")
    initial_count = len(llm_input_df)
    
    # Remove profiles where education_degrees is null, empty string, or empty JSON array
    llm_input_df = llm_input_df[llm_input_df['education_degrees'].notna()]
    llm_input_df = llm_input_df[llm_input_df['education_degrees'] != '[]']
    llm_input_df = llm_input_df[llm_input_df['education_degrees'] != 'null']
    
    filtered_count = len(llm_input_df)
    removed_count = initial_count - filtered_count
    
    print(f"✅ Kept {filtered_count} profiles with education")
    print(f"❌ Removed {removed_count} profiles without education degrees")
    
    # Save to new CSV
    llm_input_df.to_csv(OUTPUT_FILE, index=False)
    
    print(f"\n✅ Successfully created LLM input dataset!")
    print(f"💾 Saved to: {OUTPUT_FILE}")
    print(f"📊 Total profiles: {len(llm_input_df)}")
    print(f"📋 Columns: {len(llm_input_df.columns)}")
    
    # Show statistics
    print("\n--- Field Coverage Statistics ---")
    print(f"Profiles with current_title: {llm_input_df['current_title'].notna().sum()} ({llm_input_df['current_title'].notna().sum() / len(llm_input_df) * 100:.1f}%)")
    print(f"Profiles with current_company: {llm_input_df['current_company'].notna().sum()} ({llm_input_df['current_company'].notna().sum() / len(llm_input_df) * 100:.1f}%)")
    print(f"Profiles with summary: {llm_input_df['summary'].notna().sum()} ({llm_input_df['summary'].notna().sum() / len(llm_input_df) * 100:.1f}%)")
    print(f"Profiles with headline: {llm_input_df['headline'].notna().sum()} ({llm_input_df['headline'].notna().sum() / len(llm_input_df) * 100:.1f}%)")
    print(f"Profiles with job descriptions: {llm_input_df['all_job_descriptions'].notna().sum()} ({llm_input_df['all_job_descriptions'].notna().sum() / len(llm_input_df) * 100:.1f}%)")
    print(f"Profiles with education: {llm_input_df['education_details'].notna().sum()} ({llm_input_df['education_details'].notna().sum() / len(llm_input_df) * 100:.1f}%)")
    print(f"Profiles with skills: {llm_input_df['all_skills'].notna().sum()} ({llm_input_df['all_skills'].notna().sum() / len(llm_input_df) * 100:.1f}%)")
    
    # Show sample record
    print("\n--- Sample Record (First Profile) ---")
    sample = llm_input_df.iloc[0]
    print(f"Name: {sample['name']}")
    print(f"Current Role: {sample['current_title']} at {sample['current_company']}")
    print(f"Industry: {sample['current_industry']}")
    print(f"Years of Experience: {sample['years_of_experience']}")
    print(f"Headline: {sample['headline'][:100] if sample['headline'] else 'N/A'}...")
    
    # Show how many job descriptions they have
    if sample['all_job_descriptions']:
        jobs = json.loads(sample['all_job_descriptions'])
        jobs_with_desc = [j for j in jobs if j.get('description')]
        print(f"Job Descriptions Available: {len(jobs_with_desc)}/{len(jobs)} roles")
    
    print("\n✨ Ready for LLM enrichment!")


if __name__ == "__main__":
    main()
