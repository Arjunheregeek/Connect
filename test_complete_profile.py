#!/usr/bin/env python3
"""
Test script to verify get_person_complete_profile returns headline and summary.
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Optional dotenv import
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed, using environment variables directly")

from src.graph_db import GraphDB
from src.query import QueryManager

def test_complete_profile():
    """Test the get_person_complete_profile query."""
    
    # Initialize database connection
    uri = os.getenv("NEO_URI") or os.getenv("NEO4J_URI")
    username = os.getenv("NEO_USERNAME") or os.getenv("NEO4J_USER")
    password = os.getenv("NEO_PASSWORD") or os.getenv("NEO4J_PASSWORD")
    
    print(f"🔌 Connecting to Neo4j at {uri}...")
    
    db = GraphDB(uri, username, password)
    query_manager = QueryManager(db)
    
    print("\n" + "="*80)
    print("TEST 1: Get Complete Profile by Name (Ashray Malhotra)")
    print("="*80)
    
    # Test 1: Get by name
    results = query_manager.get_person_complete_profile(person_name="Ashray Malhotra")
    
    if results and len(results) > 0:
        person = results[0]
        print(f"\n✅ FOUND COMPLETE PROFILE")
        print(f"\n📋 BASIC INFO:")
        print(f"  • Person ID: {person.get('person_id')}")
        print(f"  • Name: {person.get('name')}")
        print(f"  • Headline: {person.get('headline')}")
        print(f"  • Summary: {person.get('summary')}")
        print(f"  • Email: {person.get('email')}")
        print(f"  • Phone: {person.get('phone')}")
        print(f"  • Location: {person.get('location')}")
        print(f"  • LinkedIn: {person.get('linkedin_profile')}")
        
        print(f"\n💼 CURRENT POSITION:")
        print(f"  • Company: {person.get('current_company')}")
        print(f"  • Title: {person.get('current_title')}")
        print(f"  • Total Experience: {person.get('total_experience_months')} months")
        
        print(f"\n🛠️ SKILLS:")
        print(f"  • Technical: {person.get('technical_skills')}")
        print(f"  • Secondary: {person.get('secondary_skills')}")
        print(f"  • Domain Knowledge: {person.get('domain_knowledge')}")
        
        work_history = person.get('work_history', [])
        print(f"\n📊 WORK HISTORY ({len(work_history)} positions):")
        for i, job in enumerate(work_history, 1):
            print(f"\n  Job #{i}:")
            print(f"    • Company: {job.get('company')}")
            print(f"    • Title: {job.get('title')}")
            print(f"    • Current: {job.get('is_current')}")
            print(f"    • Duration: {job.get('duration_months')} months")
            print(f"    • Location: {job.get('location')}")
            if job.get('description'):
                desc = job['description'][:100] + "..." if len(job['description']) > 100 else job['description']
                print(f"    • Description: {desc}")
        
        education = person.get('education_history', [])
        print(f"\n🎓 EDUCATION ({len(education)} institutions):")
        for i, edu in enumerate(education, 1):
            print(f"  {i}. {edu.get('institution')} - {edu.get('degree')} in {edu.get('field_of_study')}")
        
        print(f"\n🔍 OTHER PROPERTIES:")
        print(f"  • Industry: {person.get('industry')}")
        print(f"  • Seniority: {person.get('seniority_level')}")
        print(f"  • Function: {person.get('function')}")
        print(f"  • Remote Preference: {person.get('remote_work_preference')}")
        print(f"  • Actively Looking: {person.get('actively_looking')}")
        print(f"  • Open to Opportunities: {person.get('open_to_opportunities')}")
        
    else:
        print("❌ No results found")
    
    print("\n" + "="*80)
    print("TEST 2: Get Complete Profile by Person ID")
    print("="*80)
    
    # Test 2: Get by person_id (using Ashray's ID from previous test)
    if results and len(results) > 0:
        person_id = results[0].get('person_id')
        print(f"\n🔍 Looking up person_id: {person_id}")
        
        results2 = query_manager.get_person_complete_profile(person_id=person_id)
        
        if results2 and len(results2) > 0:
            person2 = results2[0]
            print(f"\n✅ FOUND BY PERSON ID")
            print(f"  • Person ID: {person2.get('person_id')}")
            print(f"  • Name: {person2.get('name')}")
            print(f"  • Headline: {person2.get('headline')}")
            print(f"  • Summary: {person2.get('summary')}")
            print(f"  • Work History: {len(person2.get('work_history', []))} positions")
            print(f"  • Education: {len(person2.get('education_history', []))} institutions")
        else:
            print("❌ No results found by person_id")
    
    # Close connection
    db.close()
    print("\n✅ Test complete!\n")

if __name__ == "__main__":
    test_complete_profile()
