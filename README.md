# Professional Network Knowledge Graph: Data Preprocessing

This document outlines the data preparation and cleaning process undertaken to transform a raw CSV of professional profiles into a structured, graph-ready dataset. The goal of this phase was to extract key entities and relationship data from a complex, nested JSON structure and format it for seamless ingestion into a graph database.

## 1. Project Overview

The primary objective is to build a professional network knowledge graph from a dataset of ~200 LinkedIn-style profiles. This involves modeling individuals, companies, skills, and educational institutions as nodes, and their connections (e.g., WORKS_AT, HAS_SKILL) as relationships. This preprocessing step is the foundational phase of the project.

## 2. The Raw Dataset

**Source File:** People for People Table v1 (1).csv  
**Format:** A CSV file where each row represents a professional profile.  
**Key Challenge:** The most valuable data, including work history, skills, and education, was nested within a single column named `coresignal_raw`. This column contained a large, complex JSON object, making it unsuitable for direct analysis or graph import.

## 3. The Preprocessing Script

A Python script was developed to parse the raw data and create a clean, structured output file.

**Tools Used:** Python with the `pandas` and `json` libraries.  
**Core Logic:** The script iterates through each row of the input CSV, applying a function to parse the JSON string in the `coresignal_raw` column.

### Key Extraction Steps:

The script was designed to extract the following specific data points, which correspond to the nodes and relationships planned for the knowledge graph:

#### Core Identity Attributes (for the Person node):
- `id`: Unique identifier from the raw data.
- `name`, `linkedin_profile`, `email`, `phone`: Core contact information.
- `location`, `headline`, `summary`, `followers_count`: Key profile summary details.

#### Key Filtering Attributes (for the Person node):
- `total_experience_months`: A calculated numeric value, perfect for quickly filtering candidates by overall experience level.
- `skills`: The list of `inferred_skills` was extracted.

#### Data for Graph Relationships:
- `experience_history`: The script iterates through the experience array in the JSON. For each job, it extracts a clean subset of data: `company_name`, `company_linkedin_url`, `title`, `description`, `start_date`, `end_date`, and `duration_months`.
- `education_history`: Similarly, it parses the education array to extract `institution_name`, `institution_url`, `degree`, `start_year`, and `end_year`.

### Data Formatting:
To store structured data like work history in a flat CSV, the lists of dictionaries for `skills`, `experience_history`, and `education_history` were converted into JSON strings. This format preserves the structure and is easily parsable during the graph import phase.

### Error Handling:
A try...except block was implemented to handle any rows with missing or malformed JSON, preventing script failure and ensuring all valid rows were processed.

## 4. The Final Processed Dataset

**Output File:** Processed_People_Knowledge_Graph.csv  
**Structure:** A clean, flat CSV file where each row is ready to be transformed into a person's profile in the knowledge graph.

### Key Columns in the Output File:

| Column Name | Data Type | Purpose |
|-------------|-----------|---------|
| id | Integer | Unique identifier for the Person node. |
| name | String | Full name of the individual. |
| linkedin_profile | String | URL to the person's LinkedIn profile. |
| email, phone | String | Contact information. |
| location | String | Full location string. |
| total_experience_months | Integer | A single value for easy filtering. |
| skills | JSON String | A list of skills. |
| experience_history | JSON String | A list of dictionaries, each representing a job. |
| education_history | JSON String | A list of dictionaries, each representing an educational record. |

This final, processed file is now perfectly structured to serve as the single source of truth for building the knowledge graph.