"""
Find people in merged database with matching phone numbers in Google Contacts
where email is missing in merged database but available in Google Contacts
"""

import pandas as pd
import re

print("🔍 Finding Missing Emails from Google Contacts...")
print("="*70)

# Load datasets
print("\n📊 Loading datasets...")
merged_df = pd.read_csv('data/Final_Merged_Knowledge_Graph.csv')
google_contacts_df = pd.read_csv('data/Google Contacts (2).csv')

print(f"   Merged database: {len(merged_df)} profiles")
print(f"   Google Contacts: {len(google_contacts_df)} contacts")

# Function to normalize phone numbers (remove spaces, dashes, +91, etc.)
def normalize_phone(phone):
    """Normalize phone number by removing special characters and country codes"""
    if pd.isna(phone):
        return None
    
    # Convert to string and remove all non-digit characters
    phone_str = str(phone)
    digits_only = re.sub(r'\D', '', phone_str)
    
    # Remove leading country codes (91 for India)
    if digits_only.startswith('91') and len(digits_only) > 10:
        digits_only = digits_only[2:]
    
    # Keep only last 10 digits (Indian mobile numbers)
    if len(digits_only) >= 10:
        return digits_only[-10:]
    
    return digits_only if digits_only else None

# Function to extract all phone numbers from Google Contacts (multiple phone columns)
def extract_google_phones(row):
    """Extract all phone numbers from a Google Contacts row"""
    phones = []
    phone_columns = [col for col in google_contacts_df.columns if 'Phone' in col and 'Value' in col]
    
    for col in phone_columns:
        phone = row[col]
        normalized = normalize_phone(phone)
        if normalized:
            phones.append(normalized)
    
    return phones

# Function to extract all emails from Google Contacts (multiple email columns)
def extract_google_emails(row):
    """Extract all emails from a Google Contacts row"""
    emails = []
    email_columns = [col for col in google_contacts_df.columns if 'E-mail' in col and 'Value' in col]
    
    for col in email_columns:
        email = row[col]
        if pd.notna(email) and str(email).strip() != '':
            emails.append(str(email).strip())
    
    return emails

print("\n🔧 Processing phone numbers and emails...")

# Create normalized phone columns for merged database
merged_df['normalized_phone'] = merged_df['phone'].apply(normalize_phone)

# Create a dictionary of Google Contacts: {phone: [emails]}
google_phone_to_emails = {}
google_phone_to_name = {}

for idx, row in google_contacts_df.iterrows():
    phones = extract_google_phones(row)
    emails = extract_google_emails(row)
    
    # Get name from Google Contacts
    first_name = str(row.get('First Name', '')).strip() if pd.notna(row.get('First Name')) else ''
    middle_name = str(row.get('Middle Name', '')).strip() if pd.notna(row.get('Middle Name')) else ''
    last_name = str(row.get('Last Name', '')).strip() if pd.notna(row.get('Last Name')) else ''
    full_name = f"{first_name} {middle_name} {last_name}".strip()
    
    # Map each phone to emails and name
    for phone in phones:
        if phone not in google_phone_to_emails:
            google_phone_to_emails[phone] = set()
            google_phone_to_name[phone] = full_name
        google_phone_to_emails[phone].update(emails)

print(f"   Processed {len(google_phone_to_emails)} unique phone numbers from Google Contacts")

# Find matches where email is missing in merged but available in Google
matches = []

for idx, row in merged_df.iterrows():
    merged_phone = row['normalized_phone']
    merged_email = row['email']
    merged_name = row['name']
    
    # Check if phone exists in merged database
    if pd.isna(merged_phone):
        continue
    
    # Check if email is missing in merged database
    if pd.notna(merged_email) and str(merged_email).strip() != '':
        continue
    
    # Check if this phone exists in Google Contacts
    if merged_phone in google_phone_to_emails:
        google_emails = list(google_phone_to_emails[merged_phone])
        
        if google_emails:  # If Google Contacts has email(s)
            google_name = google_phone_to_name[merged_phone]
            
            matches.append({
                'person_id': row['person_id'],
                'merged_name': merged_name,
                'google_name': google_name,
                'phone': row['phone'],
                'normalized_phone': merged_phone,
                'current_email': merged_email,
                'google_emails': ', '.join(google_emails),
                'num_google_emails': len(google_emails)
            })

# Create results dataframe
results_df = pd.DataFrame(matches)

print(f"\n✅ Analysis Complete!")
print(f"="*70)
print(f"\n📊 Summary:")
print(f"   Total profiles in merged database: {len(merged_df)}")
print(f"   Profiles with missing emails: {merged_df['email'].isna().sum()}")
print(f"   Profiles with matching phone in Google Contacts: {len(matches)}")
print(f"   Emails that can be recovered: {len(matches)}")

if len(matches) > 0:
    # Save results
    output_file = 'data/Missing_Emails_Recovery.csv'
    results_df.to_csv(output_file, index=False)
    print(f"\n💾 Results saved to: {output_file}")
    
    # Display sample matches
    print(f"\n📋 Sample Matches (first 10):")
    print("-"*70)
    
    for i, match in enumerate(matches[:10]):
        print(f"\n{i+1}. {match['merged_name']} (ID: {match['person_id']})")
        print(f"   Phone: {match['phone']}")
        print(f"   Google Name: {match['google_name']}")
        print(f"   Available Email(s): {match['google_emails']}")
    
    # Statistics
    print(f"\n📈 Recovery Statistics:")
    print(f"   Total recoverable emails: {results_df['num_google_emails'].sum()}")
    print(f"   Avg emails per profile: {results_df['num_google_emails'].mean():.2f}")
    print(f"   Profiles with 1 email: {(results_df['num_google_emails'] == 1).sum()}")
    print(f"   Profiles with 2+ emails: {(results_df['num_google_emails'] > 1).sum()}")
    
else:
    print(f"\n⚠️  No matches found where emails can be recovered from Google Contacts")

print(f"\n🎉 Script completed successfully!")
