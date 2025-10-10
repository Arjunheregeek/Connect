# Query Types and Their Return Values

This document provides an in-depth overview of the query types available in the `src/query.py` file, including their descriptions, arguments, and return values.

## Query Types

### 1. `get_person_complete_profile`
- **Description**: Retrieves the complete profile of a person, including all properties, work history, and education history.
- **Arguments**:
  - `person_id` (optional): The unique person ID (preferred).
  - `person_name` (optional): The person's name (alternative identifier).
- **Return Values**: All 35 properties of the person node, work history, and education history.

### 2. `find_person_by_name`
- **Description**: Finds a person by their full name (case-insensitive).
- **Arguments**:
  - `name`: The full name of the person to search for.
- **Return Values**: Lightweight profile with `person_id`, `name`, `headline`, `summary`, `linkedin_profile`, `email`, `location`, `current_company`, `current_title`, and `total_experience_months`.

### 3. `find_people_by_skill`
- **Description**: Finds all people who have a specific skill.
- **Arguments**:
  - `skill`: The skill to search for.
- **Return Values**: Lightweight profile with `person_id`, `name`, `headline`, `summary`, `current_company`, `current_title`, `technical_skills`, `secondary_skills`, `domain_knowledge`, and `total_experience_months`.

### 4. `find_people_by_company`
- **Description**: Finds all people who have worked at a specific company (current or past).
- **Arguments**:
  - `company_name`: The name of the company to search for.
- **Return Values**: Lightweight profile with `person_id`, `name`, `headline`, `summary`, `company_name`, `title`, `is_current`, `start_date`, `end_date`, and `location`.

### 5. `find_colleagues_at_company`
- **Description**: Finds colleagues of a specific person at a given company.
- **Arguments**:
  - `person_id`: The unique ID of the person.
  - `company_name`: The name of the company.
- **Return Values**: Lightweight profile with `person_id`, `colleague_name`, `colleague_headline`, `colleague_summary`, `current_company`, `current_title`, `email`, `linkedin_profile`, and `company_name`.

### 6. `find_people_by_institution`
- **Description**: Finds all people who studied at a specific institution.
- **Arguments**:
  - `institution_name`: The name of the institution to search for.
- **Return Values**: Lightweight profile with `person_id`, `name`, `headline`, `summary`, `current_company`, `current_title`, `location`, `email`, `linkedin_profile`, and `institution_name`.

### 7. `find_people_by_location`
- **Description**: Finds all people in a specific location.
- **Arguments**:
  - `location`: The location to search for.
- **Return Values**: Lightweight profile with `person_id`, `name`, `headline`, `summary`, `location`, `current_company`, `current_title`, `email`, `linkedin_profile`, and `total_experience_months`.

### 8. `get_person_skills`
- **Description**: Retrieves all skills for a specific person.
- **Arguments**:
  - `person_id` (optional): The unique person ID.
  - `person_name` (optional): The person's name.
- **Return Values**: `person_id`, `name`, `headline`, `summary`, `technical_skills`, `secondary_skills`, and `domain_knowledge`.

### 9. `find_people_with_multiple_skills`
- **Description**: Finds people who have multiple skills from their skill arrays.
- **Arguments**:
  - `skills_list`: List of skills to search for.
  - `match_type`: "any" to match any skill, "all" to match all skills.
- **Return Values**: Lightweight profile with `person_id` and matched skills.

### 10. `get_person_colleagues`
- **Description**: Retrieves all colleagues of a person across all companies they worked at.
- **Arguments**:
  - `person_id` (optional): The unique person ID.
  - `person_name` (optional): The person's name.
- **Return Values**: Lightweight profile with `person_id` for each colleague.

### 11. `find_people_by_experience_level`
- **Description**: Finds people based on their total experience in months.
- **Arguments**:
  - `min_months` (optional): Minimum experience in months.
  - `max_months` (optional): Maximum experience in months.
- **Return Values**: Lightweight profile with `person_id`, `name`, `headline`, `summary`, `experience_months`, `current_company`, `current_title`, `location`, `email`, and `linkedin_profile`.

### 12. `get_company_employees`
- **Description**: Retrieves all employees (past and present) of a specific company.
- **Arguments**:
  - `company_name`: The name of the company.
- **Return Values**: Lightweight profile with `person_id`, `name`, `headline`, `summary`, `company_name`, `title`, `is_current`, `start_date`, `end_date`, and `location`.

### 13. `get_skill_popularity`
- **Description**: Retrieves the most popular skills by counting how many people have each skill.
- **Arguments**:
  - `limit`: The maximum number of skills to return (default: 20).
- **Return Values**: Skill name and count of people with that skill.

### 14. `get_person_details`
- **Description**: Retrieves comprehensive details about a person, including skills, companies, and education.
- **Arguments**:
  - `person_id` (optional): The unique person ID.
  - `person_name` (optional): The person's name.
- **Return Values**: `person_id`, `name`, `headline`, `summary`, `location`, `linkedin_profile`, `email`, `experience_months`, `technical_skills`, `secondary_skills`, `domain_knowledge`, `companies`, and `institutions`.

### 15. `get_person_job_descriptions`
- **Description**: Retrieves all job descriptions for a person with company and role details.
- **Arguments**:
  - `person_id` (optional): The unique person ID.
  - `person_name` (optional): The person's name.
- **Return Values**: `person_id`, `name`, `headline`, `summary`, `company_name`, `job_title`, `job_description`, `start_date`, `end_date`, `duration_months`, `job_location`, and `is_current`.

### 16. `search_job_descriptions_by_keywords`
- **Description**: Searches for people based on keywords in their job descriptions.
- **Arguments**:
  - `keywords`: List of keywords to search for in job descriptions.
  - `match_type`: "any" to match any keyword, "all" to match all keywords.
- **Return Values**: `person_id`, `name`, `headline`, `summary`, `company_name`, `job_title`, `job_description`, `is_current`, `email`, and `location`.

### 17. `find_technical_skills_in_descriptions`
- **Description**: Finds people who mention specific technical skills in their job descriptions.
- **Arguments**:
  - `tech_keywords`: List of technical terms to search for.
- **Return Values**: `person_id`, `name`, `headline`, `summary`, `company_name`, `job_title`, `job_description`, `start_date`, `end_date`, `is_current`, and `location`.

### 18. `find_leadership_indicators`
- **Description**: Finds people with leadership indicators in their job descriptions.
- **Arguments**: None.
- **Return Values**: `person_id`, `name`, `headline`, `summary`, `company_name`, `job_title`, `job_description`, `duration_months`, `is_current`, and `location`.

### 19. `find_achievement_patterns`
- **Description**: Finds people with quantifiable achievements in their job descriptions.
- **Arguments**: None.
- **Return Values**: `person_id`, `name`, `headline`, `summary`, `company_name`, `job_title`, `job_description`, `start_date`, `end_date`, `is_current`, and `location`.

### 20. `analyze_career_progression`
- **Description**: Analyzes a person's career progression by examining job titles and descriptions over time.
- **Arguments**:
  - `person_id` (optional): The unique person ID.
  - `person_name` (optional): The person's name.
- **Return Values**: `person_id`, `name`, `headline`, `summary`, `company_name`, `job_title`, `job_description`, `start_date`, `end_date`, `duration_months`, `job_location`, and `is_current`.

### 21. `find_domain_experts`
- **Description**: Finds people with deep domain expertise based on job description analysis.
- **Arguments**:
  - `domain_keywords`: List of domain-specific terms.
- **Return Values**: `person_id`, `name`, `headline`, `summary`, `domain_jobs`, `companies`, `roles`, `total_experience`, `location`, and `email`.

### 22. `find_similar_career_paths`
- **Description**: Finds people with similar career paths to a reference person.
- **Arguments**:
  - `reference_person_id` (optional): The person ID to compare against.
  - `reference_person_name` (optional): The person name to compare against.
  - `similarity_threshold`: Minimum number of similar elements (default: 2).
- **Return Values**: `person_id` and similarity metrics.

### 23. `find_role_transition_patterns`
- **Description**: Finds patterns in role transitions based on job descriptions.
- **Arguments**:
  - `from_role_keywords`: List of keywords for the starting role.
  - `to_role_keywords`: List of keywords for the target role.
- **Return Values**: Transition patterns and related metrics.