"""
Merge Rule-Based and LLM-Enriched datasets
- Extract location → current_location
- Drop profiles with empty education
- Merge based on person_id
- Set trustworthiness_score = 1 for all
"""

import pandas as pd
import json

print("🔄 Starting Dataset Merge Process...")
print("="*70)

# Load both datasets
rule_based = pd.read_csv('Data/Processed_People_Knowledge_Graph.csv')
llm_enriched = pd.read_csv('data/LLM_Enriched_People_Knowledge_Graph.csv')

print(f"\n📊 Initial Counts:")
print(f"   Rule-based: {len(rule_based)} profiles")
print(f"   LLM-enriched: {len(llm_enriched)} profiles")

# Filter out profiles with empty education from rule-based
print(f"\n🔍 Filtering profiles with empty education...")
rule_based['has_education'] = rule_based['degrees'].notna() & (rule_based['degrees'] != '[]') & (rule_based['degrees'] != '')
rule_based_filtered = rule_based[rule_based['has_education']].copy()
dropped_count = len(rule_based) - len(rule_based_filtered)
print(f"   Dropped {dropped_count} profiles without education")
print(f"   Remaining: {len(rule_based_filtered)} profiles")

# Rename columns for clarity
rule_based_filtered = rule_based_filtered.rename(columns={
    'id': 'person_id',
    'location': 'current_location'
})

# Merge datasets on person_id
print(f"\n🔗 Merging datasets on person_id...")
merged = pd.merge(
    rule_based_filtered,
    llm_enriched,
    on='person_id',
    how='inner',
    suffixes=('_rule', '_llm')
)

print(f"   Merged records: {len(merged)}")

# Select and organize final columns
print(f"\n📋 Building final dataset with priority attributes...")

final_df = pd.DataFrame()

# Core Identity
final_df['person_id'] = merged['person_id']
final_df['name'] = merged['name_rule']  # Use rule-based name (more reliable)
final_df['linkedin_profile'] = merged['linkedin_profile']
final_df['email'] = merged['email']
final_df['phone'] = merged['phone']
final_df['current_location'] = merged['current_location']
final_df['headline'] = merged['headline']
final_df['summary'] = merged['summary']
final_df['followers_count'] = merged['followers_count']

# NEW: Trustworthiness Score (set to 1 for all)
final_df['trustworthiness_score'] = 1

# LLM-Enriched Attributes (Priority)
final_df['perceived_expertise_level'] = merged['perceived_expertise_level']
final_df['competence_score'] = merged['competence_score']

# Current Position (from rule-based)
final_df['current_title'] = merged['current_title']
final_df['current_company'] = merged['current_company']

# Industry (from LLM - higher quality)
final_df['industry'] = merged['industry_refined']

# Seniority & Experience
final_df['seniority_level'] = merged['seniority_level_llm']  # Use LLM version (higher quality)
final_df['years_of_experience'] = merged['years_of_experience']

# Employment Status (from rule-based)
final_df['employment_type'] = merged['employment_type']
final_df['professional_status'] = merged['professional_status']

# Skills & Expertise
final_df['primary_expertise'] = merged['primary_expertise_llm']  # Use LLM version (higher quality)
final_df['technical_skills'] = merged['technical_skills_refined']  # Use LLM refined skills
final_df['secondary_skills'] = merged['secondary_skills_llm']  # Use LLM version

# Domain & Education
final_df['domain_knowledge'] = merged['domain_knowledge_llm']  # Use LLM version
final_df['degrees'] = merged['degrees']

# Combined Skills (from rule-based - all skills combined)
final_df['skills'] = merged['skills']

# Additional Context
final_df['total_experience_months'] = merged['total_experience_months']

# Experience and Education History (from rule-based)
final_df['experience_history'] = merged['experience_history']
final_df['education_history'] = merged['education_history']

# Save merged dataset
output_file = 'data/Final_Merged_Knowledge_Graph.csv'
final_df.to_csv(output_file, index=False)

print(f"\n✅ Merge Complete!")
print(f"   Output file: {output_file}")
print(f"   Final records: {len(final_df)}")
print(f"   Total columns: {len(final_df.columns)}")

# Print summary statistics
print(f"\n📊 Final Dataset Summary:")
print(f"   Profiles with current_location: {final_df['current_location'].notna().sum()}")
print(f"   Profiles with trustworthiness_score: {final_df['trustworthiness_score'].notna().sum()}")
print(f"   Profiles with perceived_expertise: {final_df['perceived_expertise_level'].notna().sum()}")
print(f"   Profiles with competence_score: {final_df['competence_score'].notna().sum()}")
print(f"   Profiles with current_title: {final_df['current_title'].notna().sum()}")
print(f"   Profiles with degrees: {final_df['degrees'].notna().sum()}")

print(f"\n📈 Coverage of Target Attributes:")
target_attrs = [
    'trustworthiness_score', 'perceived_expertise_level', 'competence_score',
    'current_title', 'current_company', 'industry', 'seniority_level',
    'years_of_experience', 'employment_type', 'professional_status',
    'primary_expertise', 'secondary_skills', 'technical_skills',
    'domain_knowledge', 'degrees', 'current_location', 'skills'
]

coverage_count = sum(1 for attr in target_attrs if attr in final_df.columns)
print(f"   Covered: {coverage_count}/{len(target_attrs)} attributes ({coverage_count/len(target_attrs)*100:.1f}%)")

for attr in target_attrs:
    if attr in final_df.columns:
        count = final_df[attr].notna().sum()
        pct = (count/len(final_df))*100
        print(f"   ✅ {attr}: {count}/{len(final_df)} ({pct:.1f}%)")
    else:
        print(f"   ❌ {attr}: NOT IN DATASET")

print(f"\n🎉 Dataset merge successful! Ready for Neo4j import.")
