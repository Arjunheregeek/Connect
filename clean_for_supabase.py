#!/usr/bin/env python3
"""
Final, definitive script to clean and prepare CSV data for Supabase import.
This version uses a robust parser to correctly handle all known data issues,
including unescaped quotes within JSON string values.
"""

import pandas as pd
import json
import ast
import csv
import re
from typing import Any, Optional

# --- Configuration ---
input_file = 'data/Final_Merged_Knowledge_Graph.csv' 
output_file = 'data/Cleaned_For_Supabase_FINAL.csv'

jsonb_columns = [
    'technical_skills', 'secondary_skills', 'domain_knowledge',
    'degrees', 'skills', 'experience_history', 'education_history'
]
boolean_columns = [
    'availability_hiring', 'availability_cofounder', 'availability_advisory'
]
# ---------------------


def clean_json_value(value: Any) -> Optional[str]:
    """
    ## FINAL, DEFINITIVE VERSION ##
    This function correctly cleans all known formats in the CSV, including the
    difficult unescaped quotes inside JSON values (e.g., "Go-to-Market").
    """
    if pd.isna(value) or not isinstance(value, str):
        return None
    
    s = value.strip()
    if not s:
        return None

    # First, handle the simple Python-style lists, as they are the most common.
    if s.startswith("['") and s.endswith("']"):
        try:
            py_obj = ast.literal_eval(s)
            return json.dumps(py_obj, ensure_ascii=False)
        except:
            # Fallback for complex cases
            pass
    
    # Handle the complex, escaped JSON objects.
    try:
        # Step 1: Normalize the outer structure and common escape patterns.
        s_cleaned = s.replace('""', '"')
        if s_cleaned.startswith('"') and s_cleaned.endswith('"'):
            s_cleaned = s_cleaned[1:-1]
        
        # Step 2: Use regex to find and escape the problematic unescaped quotes
        # that are *inside* the text values.
        # This finds a quote that is not properly surrounded by JSON structural characters.
        s_fixed = re.sub(r'(?<![\[\{\s,:"\'])\s*"\s*(?![\]\}\s,:])', r'\\"', s_cleaned)
        
        # Step 3: The string should now be valid.
        parsed = json.loads(s_fixed)
        return json.dumps(parsed, ensure_ascii=False)
    except Exception:
        print(f"⚠️  Warning: A field was malformed and is being set to NULL. Value: {s[:80]}...")
        return None


def convert_to_boolean(value: Any) -> Optional[bool]:
    if pd.isna(value) or value in ['', None]: return None
    if isinstance(value, str):
        val_lower = value.lower().strip()
        if val_lower in ['true', 't', 'yes', 'y', '1', '1.0']: return True
        if val_lower in ['false', 'f', 'no', 'n', '0', '0.0']: return False
    try: return bool(float(value))
    except (ValueError, TypeError): return None


def convert_to_integer(value: Any) -> Optional[int]:
    if pd.isna(value) or value in ['', None]: return None
    try: return int(float(value))
    except (ValueError, TypeError): return None


def convert_to_float(value: Any) -> Optional[float]:
    if pd.isna(value) or value in ['', None]: return None
    try: return float(value)
    except (ValueError, TypeError): return None


def clean_text(value: Any) -> Optional[str]:
    if pd.isna(value) or not isinstance(value, str): return None
    cleaned = value.strip()
    return cleaned if cleaned else None


def main():
    print("="*70)
    print("🚀 SUPABASE DATA CLEANER (DEFINITIVE VERSION)")
    print("="*70)
    try:
        print(f"\n📖 Reading data from '{input_file}'...")
        df = pd.read_csv(input_file, engine='python', on_bad_lines='warn')
        print(f"✅ Loaded {len(df)} rows.\n")
        
        for col in jsonb_columns:
            if col in df.columns: df[col] = df[col].apply(clean_json_value)
        
        for col in boolean_columns:
            if col in df.columns: df[col] = df[col].apply(convert_to_boolean)
        
        numeric_conversions = {
            'person_id': convert_to_integer, 'followers_count': convert_to_integer,
            'perceived_expertise_level': convert_to_integer, 'competence_score': convert_to_integer,
            'total_experience_months': convert_to_integer, 'trustworthiness_score': convert_to_float,
            'years_of_experience': convert_to_float
        }
        for col, conv in numeric_conversions.items():
            if col in df.columns: df[col] = df[col].apply(conv)

        processed = set(jsonb_columns) | set(boolean_columns) | set(numeric_conversions.keys())
        for col in list(set(df.columns) - processed):
            df[col] = df[col].apply(clean_text)
        
        print(f"\n💾 Saving cleaned data to '{output_file}'...")
        df.to_csv(output_file, index=False, quoting=csv.QUOTE_NONNUMERIC)
        print(f"✅ Successfully saved {len(df)} cleaned rows.\n")
        
        print("="*70)
        print("🎉 SUCCESS! Your file is now clean and ready for import.")
        print("="*70)
        print(f"\n📁 IMPORTANT: Upload this specific file to Supabase: '{output_file}'")
        
    except FileNotFoundError:
        print(f"\n❌ ERROR: Input file '{input_file}' not found! Make sure it's in the same folder as the script.")
    except Exception as e:
        print(f"\n❌ ERROR: An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()