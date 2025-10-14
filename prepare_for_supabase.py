#!/usr/bin/env python3
"""
Script to prepare Final_Merged_Knowledge_Graph.csv for Supabase upload.
Handles data type conversions, JSONB formatting, NULL values, and validation.
"""

import pandas as pd
import json
import re
import ast
from typing import Any, Optional
import sys


def safe_parse_json(value: Any) -> Optional[Any]:
    """
    Safely parse JSON-like strings or Python lists/dicts.
    Returns None for empty/invalid values.
    """
    if pd.isna(value) or value == '' or value is None:
        return None
    
    if isinstance(value, (list, dict)):
        return value
    
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None
        
        try:
            # Try parsing as JSON first
            parsed = json.loads(value)
            return parsed
        except json.JSONDecodeError:
            try:
                # Try parsing as Python literal (handles single quotes)
                parsed = ast.literal_eval(value)
                return parsed
            except (ValueError, SyntaxError):
                # If it looks like it should be a list but failed to parse
                if value.startswith('[') and value.endswith(']'):
                    return None
                # Return as-is if it's a simple string
                return value
    
    return value


def convert_to_bigint(value: Any) -> Optional[int]:
    """Convert value to BIGINT (PostgreSQL 64-bit integer)."""
    if pd.isna(value) or value == '' or value is None:
        return None
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


def convert_to_integer(value: Any) -> Optional[int]:
    """Convert value to INTEGER."""
    if pd.isna(value) or value == '' or value is None:
        return None
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


def convert_to_float(value: Any) -> Optional[float]:
    """Convert value to FLOAT8 (double precision)."""
    if pd.isna(value) or value == '' or value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def convert_to_boolean(value: Any) -> Optional[bool]:
    """Convert value to BOOLEAN."""
    if pd.isna(value) or value == '' or value is None:
        return None
    
    if isinstance(value, bool):
        return value
    
    if isinstance(value, str):
        value_lower = value.lower().strip()
        if value_lower in ['true', 't', 'yes', 'y', '1']:
            return True
        elif value_lower in ['false', 'f', 'no', 'n', '0']:
            return False
    
    try:
        return bool(int(value))
    except (ValueError, TypeError):
        return None


def convert_to_text(value: Any) -> Optional[str]:
    """Convert value to TEXT, handling None and empty strings."""
    if pd.isna(value) or value == '' or value is None:
        return None
    try:
        text = str(value).strip()
        return text if text else None
    except (AttributeError, TypeError):
        return None


def clean_jsonb_field(value: Any) -> Optional[str]:
    """
    Clean and validate JSONB fields.
    Returns JSON string or None.
    """
    parsed = safe_parse_json(value)
    if parsed is None:
        return None
    
    try:
        # Ensure valid JSON serialization
        return json.dumps(parsed, ensure_ascii=False)
    except (TypeError, ValueError):
        return None


def validate_email(email: Any) -> Optional[str]:
    """Basic email validation."""
    if pd.isna(email) or email == '' or email is None:
        return None
    
    try:
        email = str(email).strip()
        if not email:
            return None
        # Basic email regex pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(pattern, email):
            return email
    except (AttributeError, TypeError):
        return None
    return None


def validate_phone(phone: Any) -> Optional[str]:
    """Clean and validate phone numbers."""
    if pd.isna(phone) or phone == '' or phone is None:
        return None
    
    try:
        phone = str(phone).strip()
        if not phone:
            return None
        # Remove common separators and keep only digits and +
        phone = re.sub(r'[^\d+]', '', phone)
        
        if phone and len(phone) >= 10:
            return phone
    except (AttributeError, TypeError):
        return None
    return None


def validate_url(url: Any) -> Optional[str]:
    """Basic URL validation."""
    if pd.isna(url) or url == '' or url is None:
        return None
    
    try:
        url = str(url).strip()
        if not url:
            return None
        if url.startswith('http://') or url.startswith('https://'):
            return url
    except (AttributeError, TypeError):
        return None
    return None


def process_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process the entire dataframe according to Supabase schema.
    """
    print("Starting data processing...")
    
    # Create a copy to avoid modifying original
    df = df.copy()
    
    # BIGINT fields
    print("Converting BIGINT fields...")
    df['person_id'] = df['person_id'].apply(convert_to_bigint)
    
    # TEXT fields with validation
    print("Converting TEXT fields...")
    df['name'] = df['name'].apply(convert_to_text)
    df['linkedin_profile'] = df['linkedin_profile'].apply(validate_url)
    df['email'] = df['email'].apply(validate_email)
    df['phone'] = df['phone'].apply(validate_phone)
    df['current_location'] = df['current_location'].apply(convert_to_text)
    df['headline'] = df['headline'].apply(convert_to_text)
    df['summary'] = df['summary'].apply(convert_to_text)
    df['current_title'] = df['current_title'].apply(convert_to_text)
    df['current_company'] = df['current_company'].apply(convert_to_text)
    df['industry'] = df['industry'].apply(convert_to_text)
    df['seniority_level'] = df['seniority_level'].apply(convert_to_text)
    df['employment_type'] = df['employment_type'].apply(convert_to_text)
    df['professional_status'] = df['professional_status'].apply(convert_to_text)
    df['primary_expertise'] = df['primary_expertise'].apply(convert_to_text)
    df['current_goals'] = df['current_goals'].apply(convert_to_text)
    df['current_challenges'] = df['current_challenges'].apply(convert_to_text)
    df['resources_needed'] = df['resources_needed'].apply(convert_to_text)
    df['availability_roles'] = df['availability_roles'].apply(convert_to_text)
    
    # INTEGER fields
    print("Converting INTEGER fields...")
    df['followers_count'] = df['followers_count'].apply(convert_to_integer)
    df['perceived_expertise_level'] = df['perceived_expertise_level'].apply(convert_to_integer)
    df['competence_score'] = df['competence_score'].apply(convert_to_integer)
    df['total_experience_months'] = df['total_experience_months'].apply(convert_to_integer)
    
    # FLOAT8 fields
    print("Converting FLOAT8 fields...")
    df['trustworthiness_score'] = df['trustworthiness_score'].apply(convert_to_float)
    df['years_of_experience'] = df['years_of_experience'].apply(convert_to_float)
    
    # BOOLEAN fields
    print("Converting BOOLEAN fields...")
    df['availability_hiring'] = df['availability_hiring'].apply(convert_to_boolean)
    df['availability_cofounder'] = df['availability_cofounder'].apply(convert_to_boolean)
    df['availability_advisory'] = df['availability_advisory'].apply(convert_to_boolean)
    
    # JSONB fields
    print("Converting JSONB fields...")
    df['technical_skills'] = df['technical_skills'].apply(clean_jsonb_field)
    df['secondary_skills'] = df['secondary_skills'].apply(clean_jsonb_field)
    df['domain_knowledge'] = df['domain_knowledge'].apply(clean_jsonb_field)
    df['degrees'] = df['degrees'].apply(clean_jsonb_field)
    df['skills'] = df['skills'].apply(clean_jsonb_field)
    df['experience_history'] = df['experience_history'].apply(clean_jsonb_field)
    df['education_history'] = df['education_history'].apply(clean_jsonb_field)
    
    print("Data processing completed!")
    return df


def validate_data(df: pd.DataFrame) -> dict:
    """
    Validate the processed data and return statistics.
    """
    print("\n" + "="*60)
    print("DATA VALIDATION REPORT")
    print("="*60)
    
    stats = {
        'total_rows': len(df),
        'null_counts': {},
        'invalid_emails': 0,
        'invalid_phones': 0,
        'invalid_urls': 0,
        'json_errors': [],
    }
    
    # Check for required fields
    required_fields = ['person_id', 'name']
    for field in required_fields:
        null_count = df[field].isna().sum()
        if null_count > 0:
            print(f"⚠️  WARNING: {null_count} NULL values in required field '{field}'")
    
    # Count nulls for all fields
    print("\nNULL Value Summary:")
    for col in df.columns:
        null_count = df[col].isna().sum()
        if null_count > 0:
            stats['null_counts'][col] = null_count
            percentage = (null_count / len(df)) * 100
            print(f"  {col}: {null_count} ({percentage:.1f}%)")
    
    # Validate email format
    email_col = df['email'].dropna()
    stats['invalid_emails'] = len(email_col) - email_col.apply(lambda x: '@' in str(x)).sum()
    
    # Validate JSONB fields
    jsonb_fields = ['technical_skills', 'secondary_skills', 'domain_knowledge', 
                    'degrees', 'skills', 'experience_history', 'education_history']
    
    print("\nJSONB Field Validation:")
    for field in jsonb_fields:
        valid_json_count = 0
        null_count = df[field].isna().sum()
        
        for idx, val in df[field].items():
            if pd.notna(val) and val is not None:
                try:
                    json.loads(val)
                    valid_json_count += 1
                except json.JSONDecodeError:
                    stats['json_errors'].append(f"Row {idx}, Field: {field}")
        
        total_non_null = len(df) - null_count
        print(f"  {field}: {valid_json_count}/{total_non_null} valid JSON objects")
    
    # Data type validation
    print("\nData Type Validation:")
    print(f"  person_id: {df['person_id'].dtype}")
    print(f"  followers_count: {df['followers_count'].dtype}")
    print(f"  years_of_experience: {df['years_of_experience'].dtype}")
    
    print("\n" + "="*60)
    print(f"✅ Total rows processed: {stats['total_rows']}")
    print("="*60 + "\n")
    
    return stats


def main():
    """Main execution function."""
    input_file = 'data/Final_Merged_Knowledge_Graph.csv'
    output_file = 'data/Final_Merged_Knowledge_Graph_supabase_ready.csv'
    
    try:
        print(f"Reading input file: {input_file}")
        df = pd.read_csv(input_file, low_memory=False)
        print(f"Loaded {len(df)} rows with {len(df.columns)} columns")
        
        # Process the dataframe
        df_processed = process_dataframe(df)
        
        # Validate the processed data
        stats = validate_data(df_processed)
        
        # Save the processed data
        print(f"Saving processed data to: {output_file}")
        # Use quoting=1 (QUOTE_ALL) and doublequote=True to properly handle JSON in CSV
        df_processed.to_csv(output_file, index=False, escapechar=None, doublequote=True)
        print(f"✅ Successfully saved {len(df_processed)} rows to {output_file}")
        
        # Generate SQL-ready format (optional)
        json_output_file = 'data/Final_Merged_Knowledge_Graph_supabase_ready.json'
        print(f"\nGenerating JSON format for direct import: {json_output_file}")
        
        # Convert to records and handle NaN values
        records = []
        for _, row in df_processed.iterrows():
            record = {}
            for col in df_processed.columns:
                val = row[col]
                if pd.isna(val):
                    record[col] = None
                elif col in ['technical_skills', 'secondary_skills', 'domain_knowledge', 
                           'degrees', 'skills', 'experience_history', 'education_history']:
                    # Parse JSON strings back to objects for JSON output
                    try:
                        record[col] = json.loads(val) if val else None
                    except (json.JSONDecodeError, TypeError):
                        record[col] = None
                else:
                    record[col] = val
            records.append(record)
        
        with open(json_output_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Successfully saved JSON format to {json_output_file}")
        
        print("\n" + "="*60)
        print("🎉 DATA PREPARATION COMPLETE!")
        print("="*60)
        print("\nNext steps:")
        print("1. Review the output files:")
        print(f"   - CSV: {output_file}")
        print(f"   - JSON: {json_output_file}")
        print("2. Create a table in Supabase with the schema you provided")
        print("3. Import the data using Supabase dashboard or SQL")
        print("\nFor CSV import in Supabase:")
        print("  - Go to Table Editor > Import data from CSV")
        print(f"  - Upload: {output_file}")
        print("\nFor JSON import, you can use the Supabase API or SQL:")
        print("  - Use INSERT statements with the JSON data")
        
    except FileNotFoundError:
        print(f"❌ Error: Input file '{input_file}' not found!")
        print("Please ensure the file exists in the correct location.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error during processing: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
