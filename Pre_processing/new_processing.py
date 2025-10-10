import pandas as pd
import json
import re

# Define the input and output file paths
# Make sure to update this path to where your file is located
input_file = "Data/People for People Table v1 (1).csv"
output_file = "Data/Processed_People_Knowledge_Graph.csv"

# Technical skill keywords for filtering
TECHNICAL_KEYWORDS = [
    'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'go', 'rust', 'swift', 'kotlin',
    'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch',
    'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'spring', 'express',
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins',
    'machine learning', 'deep learning', 'ai', 'nlp', 'computer vision', 'tensorflow', 'pytorch',
    'data science', 'data analysis', 'tableau', 'power bi', 'spark', 'hadoop',
    'api', 'rest', 'graphql', 'microservices', 'devops', 'ci/cd',
    'git', 'github', 'gitlab', 'jira', 'agile', 'scrum',
    'html', 'css', 'sass', 'webpack', 'babel',
    'algorithms', 'data structures', 'system design', 'software engineering',
    'matlab', 'r', 'scala', 'php', 'perl',
    'opencv', 'scikit-learn', 'keras', 'pandas', 'numpy',
    'ui/ux', 'figma', 'sketch', 'photoshop', 'illustrator'
]

# Soft skill keywords for secondary_skills
SOFT_SKILL_KEYWORDS = [
    'leadership', 'management', 'communication', 'teamwork', 'collaboration',
    'problem solving', 'critical thinking', 'creativity', 'adaptability',
    'project management', 'strategic planning', 'business development',
    'sales', 'marketing', 'customer service', 'negotiation',
    'presentation', 'public speaking', 'writing', 'teaching', 'mentoring',
    'analytics', 'research', 'planning', 'organization', 'coordination'
]

# Founder/startup keywords for employment_type detection
FOUNDER_KEYWORDS = [
    'founder', 'co-founder', 'cofounder', 'ceo', 'cto', 'coo', 'cfo',
    'co-ceo', 'co-cto', 'chief executive', 'chief technology', 'chief operating'
]

# Read the original CSV file
try:
    data = pd.read_csv(input_file)
except FileNotFoundError:
    print(f"Error: The input file was not found at '{input_file}'")
    exit()

def extract_technical_skills(inferred_skills):
    """
    Filter technical skills from the inferred_skills list.
    Returns a list of technical skills.
    """
    if not inferred_skills or not isinstance(inferred_skills, list):
        return []
    
    technical_skills = []
    for skill in inferred_skills:
        skill_lower = skill.lower()
        # Check if skill matches any technical keyword
        for keyword in TECHNICAL_KEYWORDS:
            if keyword in skill_lower:
                technical_skills.append(skill)
                break
    
    return technical_skills

def derive_primary_expertise(department, technical_skills, inferred_skills):
    """
    Derive primary expertise from department and skills.
    Returns a string representing the primary expertise area.
    """
    # Map departments to expertise areas
    if department:
        dept_lower = department.lower()
        if 'engineering' in dept_lower or 'technical' in dept_lower:
            # Check for specific technical domains
            all_skills_lower = ' '.join([s.lower() for s in (technical_skills + inferred_skills)[:10]])
            
            if any(kw in all_skills_lower for kw in ['machine learning', 'ai', 'deep learning', 'computer vision', 'nlp']):
                return 'Artificial Intelligence & Machine Learning'
            elif any(kw in all_skills_lower for kw in ['data science', 'data analysis', 'analytics', 'tableau', 'spark']):
                return 'Data Science & Analytics'
            elif any(kw in all_skills_lower for kw in ['aws', 'azure', 'cloud', 'devops', 'kubernetes', 'docker']):
                return 'Cloud & DevOps'
            elif any(kw in all_skills_lower for kw in ['react', 'angular', 'vue', 'frontend', 'ui', 'ux']):
                return 'Frontend Development'
            elif any(kw in all_skills_lower for kw in ['backend', 'api', 'microservices', 'node.js', 'django']):
                return 'Backend Development'
            else:
                return 'Software Engineering'
        elif 'product' in dept_lower:
            return 'Product Management'
        elif 'data' in dept_lower:
            return 'Data Science & Analytics'
        elif 'design' in dept_lower:
            return 'Design & UX'
        elif 'marketing' in dept_lower:
            return 'Marketing'
        elif 'sales' in dept_lower:
            return 'Sales & Business Development'
        elif 'c-suite' in dept_lower or 'founder' in dept_lower:
            return 'Leadership & Strategy'
        elif 'research' in dept_lower:
            return 'Research & Development'
    
    # Fallback: check technical skills
    if technical_skills:
        return 'Technology'
    
    return 'General Management'

def extract_current_company(experience_list):
    """
    Extract current company name from experience array.
    Returns company name where active_experience == 1.
    """
    if not experience_list or not isinstance(experience_list, list):
        return None
    
    for job in experience_list:
        if job.get('active_experience') == 1:
            return job.get('company_name')
    
    return None

def extract_industry(experience_list):
    """
    Extract industry from active experience.
    Returns industry string from company where active_experience == 1.
    """
    if not experience_list or not isinstance(experience_list, list):
        return None
    
    for job in experience_list:
        if job.get('active_experience') == 1:
            return job.get('company_industry')
    
    return None

def extract_employment_type(current_title, is_working):
    """
    Determine employment type based on current title and working status.
    Returns: 'Startup/Self-employed', 'Full-time Job', or 'Not Employed'.
    """
    if not current_title:
        return 'Not Employed' if is_working == 0 else 'Full-time Job'
    
    title_lower = current_title.lower()
    
    # Check for founder/startup keywords
    for keyword in FOUNDER_KEYWORDS:
        if keyword in title_lower:
            return 'Startup/Self-employed'
    
    # Check working status
    if is_working == 0:
        return 'Not Employed'
    
    return 'Full-time Job'

def extract_professional_status(is_working, current_title):
    """
    Determine professional status based on working status and title.
    Returns: 'Actively Employed', 'Founder/Entrepreneur', or 'Between Opportunities'.
    """
    if not current_title:
        return 'Between Opportunities' if is_working == 0 else 'Actively Employed'
    
    title_lower = current_title.lower()
    
    # Check for founder/entrepreneur keywords
    if any(keyword in title_lower for keyword in FOUNDER_KEYWORDS):
        return 'Founder/Entrepreneur'
    
    # Check working status
    if is_working == 0:
        return 'Between Opportunities'
    
    return 'Actively Employed'

def extract_secondary_skills(inferred_skills, technical_skills):
    """
    Extract soft/secondary skills by filtering out technical skills.
    Returns list of non-technical skills.
    """
    if not inferred_skills or not isinstance(inferred_skills, list):
        return []
    
    # Convert technical skills to lowercase for comparison
    technical_lower = [skill.lower() for skill in technical_skills]
    
    secondary_skills = []
    for skill in inferred_skills:
        skill_lower = skill.lower()
        
        # Skip if it's a technical skill
        if skill_lower in technical_lower:
            continue
        
        # Check if it matches soft skill keywords
        for soft_keyword in SOFT_SKILL_KEYWORDS:
            if soft_keyword in skill_lower:
                secondary_skills.append(skill)
                break
    
    return secondary_skills

def extract_domain_knowledge(experience_list, degrees):
    """
    Derive domain knowledge from work experience industries and education.
    Returns list of domain areas.
    """
    domains = set()
    
    # Extract from work experience industries
    if experience_list and isinstance(experience_list, list):
        for job in experience_list:
            industry = job.get('company_industry')
            if industry:
                industry_lower = industry.lower()
                
                # Map industries to domain knowledge areas
                if 'software' in industry_lower or 'technology' in industry_lower:
                    domains.add('Technology')
                if 'financial' in industry_lower or 'bank' in industry_lower:
                    domains.add('FinTech')
                if 'healthcare' in industry_lower or 'medical' in industry_lower or 'pharma' in industry_lower:
                    domains.add('Healthcare')
                if 'e-learning' in industry_lower or 'education' in industry_lower:
                    domains.add('EdTech')
                if 'retail' in industry_lower or 'e-commerce' in industry_lower or 'consumer' in industry_lower:
                    domains.add('E-commerce & Retail')
                if 'entertainment' in industry_lower or 'media' in industry_lower:
                    domains.add('Media & Entertainment')
                if 'consulting' in industry_lower:
                    domains.add('Consulting')
                if 'manufacturing' in industry_lower or 'industrial' in industry_lower:
                    domains.add('Manufacturing')
    
    # Extract from education
    if degrees and isinstance(degrees, list):
        degrees_text = ' '.join([str(d).lower() for d in degrees])
        
        if 'business' in degrees_text or 'mba' in degrees_text:
            domains.add('Business Management')
        if 'engineering' in degrees_text:
            domains.add('Engineering')
        if 'computer' in degrees_text or 'software' in degrees_text:
            domains.add('Computer Science')
        if 'data' in degrees_text or 'analytics' in degrees_text:
            domains.add('Data Science')
        if 'design' in degrees_text:
            domains.add('Design')
    
    return list(domains) if domains else ['General']

def extract_knowledge_graph_data(row):
    """
    Parses the raw JSON data from the 'coresignal_raw' column to extract
    structured fields for the knowledge graph.
    Now includes 7 new priority attributes.
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

        # --- Extract NEW 7 Priority Attributes ---
        
        # 1. current_title - directly from active_experience_title
        current_title = parsed_data.get("active_experience_title")
        
        # 2. current_company - extract from experience array where active_experience == 1
        experience_data = parsed_data.get("experience")
        current_company = extract_current_company(experience_data)
        
        # 3. years_of_experience - convert months to years
        total_months = parsed_data.get("total_experience_duration_months")
        years_of_experience = round(total_months / 12, 1) if total_months else None
        
        # 4. degrees - directly from education_degrees (pre-extracted list)
        degrees = parsed_data.get("education_degrees", [])
        
        # 5. technical_skills - filter from inferred_skills
        inferred_skills = parsed_data.get("inferred_skills", [])
        technical_skills = extract_technical_skills(inferred_skills)
        
        # 6. primary_expertise - derive from department + skills
        active_department = parsed_data.get("active_experience_department")
        primary_expertise = derive_primary_expertise(active_department, technical_skills, inferred_skills)
        
        # 7. seniority_level - directly from active_experience_management_level
        seniority_level = parsed_data.get("active_experience_management_level")

        # --- Extract NEW 5 Additional Attributes (Phase 1) ---
        
        # 8. industry - from active experience company
        industry = extract_industry(experience_data)
        
        # 9. employment_type - based on current_title keywords
        is_working = parsed_data.get("is_working")
        employment_type = extract_employment_type(current_title, is_working)
        
        # 10. professional_status - from is_working + founder detection
        professional_status = extract_professional_status(is_working, current_title)
        
        # 11. secondary_skills - non-technical skills
        secondary_skills = extract_secondary_skills(inferred_skills, technical_skills)
        
        # 12. domain_knowledge - from industries + education
        domain_knowledge = extract_domain_knowledge(experience_data, degrees)

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
            
            # NEW 7 Priority Attributes (Batch 1)
            "current_title": current_title,
            "current_company": current_company,
            "years_of_experience": years_of_experience,
            "degrees": json.dumps(degrees) if degrees else None,  # Store as JSON string
            "technical_skills": json.dumps(technical_skills) if technical_skills else None,  # Store as JSON string
            "primary_expertise": primary_expertise,
            "seniority_level": seniority_level,
            
            # NEW 5 Additional Attributes (Phase 1 - Batch 2)
            "industry": industry,
            "employment_type": employment_type,
            "professional_status": professional_status,
            "secondary_skills": json.dumps(secondary_skills) if secondary_skills else None,  # Store as JSON string
            "domain_knowledge": json.dumps(domain_knowledge) if domain_knowledge else None,  # Store as JSON string
            
            # Key Attributes for Filtering (Person Node Properties)
            "total_experience_months": parsed_data.get("total_experience_duration_months"),
            "skills": json.dumps(parsed_data.get("inferred_skills", [])), # Store list as JSON string
            
            # Data for Relationships
            "experience_history": json.dumps(experience_history), # Store list as JSON string
            "education_history": json.dumps(education_history)   # Store list as JSON string
        }

    except (json.JSONDecodeError, TypeError, AttributeError) as e:
        # If JSON is malformed or data is missing, return a structure with None values
        # This prevents the script from crashing and helps identify problematic rows
        print(f"Error processing row {row.get('name', 'Unknown')}: {str(e)}")
        return {
            "id": None, "name": row.get("name"), "linkedin_profile": row.get("linkedin_profile"),
            "email": row.get("email"), "phone": row.get("phone"), "location": None,
            "headline": None, "summary": None, "followers_count": None,
            "current_title": None, "current_company": None, "years_of_experience": None,
            "degrees": None, "technical_skills": None, "primary_expertise": None, "seniority_level": None,
            "industry": None, "employment_type": None, "professional_status": None,
            "secondary_skills": None, "domain_knowledge": None,
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
print(f"📊 Total records processed: {len(processed_df)}")
print(f"📋 Total columns: {len(processed_df.columns)}")

# Print sample statistics for the new attributes
print("\n--- Batch 1: Priority Attributes (7) ---")
print(f"Records with current_title: {processed_df['current_title'].notna().sum()}")
print(f"Records with current_company: {processed_df['current_company'].notna().sum()}")
print(f"Records with years_of_experience: {processed_df['years_of_experience'].notna().sum()}")
print(f"Records with degrees: {processed_df['degrees'].notna().sum()}")
print(f"Records with technical_skills: {processed_df['technical_skills'].notna().sum()}")
print(f"Records with primary_expertise: {processed_df['primary_expertise'].notna().sum()}")
print(f"Records with seniority_level: {processed_df['seniority_level'].notna().sum()}")

print("\n--- Batch 2: Phase 1 Attributes (5) ---")
print(f"Records with industry: {processed_df['industry'].notna().sum()}")
print(f"Records with employment_type: {processed_df['employment_type'].notna().sum()}")
print(f"Records with professional_status: {processed_df['professional_status'].notna().sum()}")
print(f"Records with secondary_skills: {processed_df['secondary_skills'].notna().sum()}")
print(f"Records with domain_knowledge: {processed_df['domain_knowledge'].notna().sum()}")

# Show sample employment types distribution
print("\n--- Employment Type Distribution ---")
print(processed_df['employment_type'].value_counts())

print("\n--- Professional Status Distribution ---")
print(processed_df['professional_status'].value_counts())
