"""
Add 7 missing attributes to Final_Merged_Knowledge_Graph.csv
Sets them as null/empty for Neo4j compatibility
"""

import pandas as pd
import numpy as np

print("📝 Adding Missing Attributes to Dataset...")
print("="*70)

# Load the current dataset
df = pd.read_csv('data/Final_Merged_Knowledge_Graph.csv')

print(f"\n📊 Current dataset: {len(df)} profiles, {len(df.columns)} columns")

# Create backup
backup_file = 'data/Final_Merged_Knowledge_Graph_before_attributes.csv'
df.to_csv(backup_file, index=False)
print(f"💾 Backup created: {backup_file}")

# Add the 7 missing attributes with null values
missing_attributes = [
    'current_goals',
    'current_challenges',
    'resources_needed',
    'availability_hiring',
    'availability_roles',
    'availability_cofounder',
    'availability_advisory'
]

print(f"\n➕ Adding {len(missing_attributes)} attributes:")

for attr in missing_attributes:
    # Add column with NaN (null) values
    # NaN is better than empty string for Neo4j as it's truly null
    df[attr] = np.nan
    print(f"   ✓ Added: {attr}")

# Reorder columns to place new attributes in a logical position
# Put them after domain_knowledge and before degrees

# Define desired column order
column_order = [
    'person_id',
    'name',
    'linkedin_profile',
    'email',
    'phone',
    'current_location',
    'headline',
    'summary',
    'followers_count',
    'trustworthiness_score',
    'perceived_expertise_level',
    'competence_score',
    'current_title',
    'current_company',
    'industry',
    'seniority_level',
    'years_of_experience',
    'employment_type',
    'professional_status',
    'primary_expertise',
    'technical_skills',
    'secondary_skills',
    'domain_knowledge',
    # New aspirational/availability attributes
    'current_goals',
    'current_challenges',
    'resources_needed',
    'availability_hiring',
    'availability_roles',
    'availability_cofounder',
    'availability_advisory',
    # Education and other fields
    'degrees',
    'skills',
    'total_experience_months',
    'experience_history',
    'education_history'
]

# Reorder columns
df = df[column_order]

# Save updated dataset
output_file = 'data/Final_Merged_Knowledge_Graph.csv'
df.to_csv(output_file, index=False)

print(f"\n✅ Update Complete!")
print(f"="*70)
print(f"\n📊 Updated dataset:")
print(f"   Profiles: {len(df)}")
print(f"   Total columns: {len(df.columns)} (was {len(df.columns) - len(missing_attributes)})")
print(f"   Added attributes: {len(missing_attributes)}")

print(f"\n📋 New Column Structure:")
print("-"*70)
for i, col in enumerate(df.columns, 1):
    # Check if it's a new column
    is_new = col in missing_attributes
    marker = " 🆕" if is_new else ""
    non_null = df[col].notna().sum()
    coverage = (non_null / len(df)) * 100
    print(f"{i:2}. {col:35} - {non_null:3}/{len(df)} ({coverage:5.1f}%){marker}")

print(f"\n💾 Saved: {output_file}")
print(f"🎉 Dataset ready for Neo4j import with complete schema!")
