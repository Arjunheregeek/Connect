"""
Update missing emails in Final_Merged_Knowledge_Graph.csv 
using recovered emails from Google Contacts
"""

import pandas as pd

print("📧 Updating Missing Emails in Merged Database...")
print("="*70)

# Load datasets
print("\n📊 Loading datasets...")
merged_df = pd.read_csv('data/Final_Merged_Knowledge_Graph.csv')
recovery_df = pd.read_csv('data/Missing_Emails_Recovery.csv')

print(f"   Merged database: {len(merged_df)} profiles")
print(f"   Recoverable emails: {len(recovery_df)} profiles")

# Create a backup before updating
backup_file = 'data/Final_Merged_Knowledge_Graph_backup.csv'
merged_df.to_csv(backup_file, index=False)
print(f"\n💾 Backup created: {backup_file}")

# Track updates
updates = []
emails_before = merged_df['email'].notna().sum()

print(f"\n🔄 Updating emails...")

# Update emails based on person_id
for idx, recovery_row in recovery_df.iterrows():
    person_id = recovery_row['person_id']
    google_emails = recovery_row['google_emails']
    
    # Get the first email if multiple emails are present
    primary_email = google_emails.split(',')[0].strip() if pd.notna(google_emails) else None
    
    if primary_email:
        # Find the matching row in merged_df
        mask = merged_df['person_id'] == person_id
        
        if mask.any():
            # Get the person's name for logging
            person_name = merged_df.loc[mask, 'name'].values[0]
            old_email = merged_df.loc[mask, 'email'].values[0]
            
            # Update the email
            merged_df.loc[mask, 'email'] = primary_email
            
            updates.append({
                'person_id': person_id,
                'name': person_name,
                'old_email': old_email,
                'new_email': primary_email
            })
            
            print(f"   ✓ Updated {person_name} (ID: {person_id})")
            print(f"     Email: {primary_email}")

# Save updated dataset
output_file = 'data/Final_Merged_Knowledge_Graph.csv'
merged_df.to_csv(output_file, index=False)

emails_after = merged_df['email'].notna().sum()

print(f"\n✅ Update Complete!")
print(f"="*70)
print(f"\n📊 Summary:")
print(f"   Profiles updated: {len(updates)}")
print(f"   Emails before: {emails_before}/{len(merged_df)} ({emails_before/len(merged_df)*100:.1f}%)")
print(f"   Emails after: {emails_after}/{len(merged_df)} ({emails_after/len(merged_df)*100:.1f}%)")
print(f"   Improvement: +{emails_after - emails_before} emails")

if len(updates) > 0:
    print(f"\n📋 Updated Profiles:")
    print("-"*70)
    
    for i, update in enumerate(updates, 1):
        print(f"\n{i}. {update['name']} (ID: {update['person_id']})")
        print(f"   Old: {update['old_email']}")
        print(f"   New: {update['new_email']}")

print(f"\n💾 Updated file: {output_file}")
print(f"🎉 Script completed successfully!")
